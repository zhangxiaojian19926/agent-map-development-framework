"""Registered reverse adapters and append-only automatic observation evidence."""
import hashlib
import json
from pathlib import Path
import string

from .reverse_request import canonical
from .reverse_v2 import encoded, sha_text
from .storage import atomic, safe_path


BEHAVIOR_SCHEMA = 'reverse-behavior/v1'
PLACEHOLDERS = {'tool_path', 'jdk_path', 'target_path', 'output_path', 'snapshot_path'}
WEB_OPERATIONS = {
    'observe-dom': ('browser', 'browser-observe'),
    'observe-console': ('browser', 'browser-observe'),
    'screenshot': ('browser', 'browser-observe'),
    'capture-har': ('network', 'network-capture'),
}


def auto_root(request_id):
    return '.framework/local-state/reverse/auto/' + request_id


def observation_path(root, request_id, observation_id):
    return auto_root(request_id) + '/observations/' + observation_id + '.json'


def read_observation(root, request_id, observation_id):
    path = safe_path(root, observation_path(root, request_id, observation_id))
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def validate_argv(spec):
    argv = spec.get('argv', [])
    if not isinstance(argv, list) or any(not isinstance(part, str) or not part for part in argv):
        raise ValueError('INVALID_ADAPTER')
    for part in argv:
        for unused, field, format_spec, conversion in string.Formatter().parse(part):
            del unused
            if field is not None and (field not in PLACEHOLDERS or format_spec or conversion):
                raise ValueError('INVALID_PLACEHOLDER')
    return argv


def render_argv(spec, values):
    argv = validate_argv(spec)
    rendered = []
    for part in argv:
        fields = [field for unused, field, format_spec, conversion in string.Formatter().parse(part)
                  if field is not None]
        if fields and (len(fields) != 1 or part != '{' + fields[0] + '}'):
            raise ValueError('INVALID_PLACEHOLDER')
        rendered.append(str(values[fields[0]]) if fields else part)
    if any('\x00' in part for part in rendered):
        raise ValueError('INVALID_ARGUMENT')
    return rendered


def adapter_for(catalog, capability, target_kind, action):
    registered = catalog['capabilities'].get(capability)
    if not registered or target_kind not in registered['targets']:
        raise ValueError('CAPABILITY_TARGET_MISMATCH')
    adapter_name = registered['adapter']
    spec = catalog['adapters'].get(adapter_name)
    if not spec or spec.get('action') not in ('static', 'browser', 'network'):
        raise ValueError('INVALID_ADAPTER')
    if action == 'static' and spec['action'] != 'static':
        raise ValueError('INVALID_OPERATION')
    if action in ('browser', 'network') and spec['provider'] != 'browser':
        raise ValueError('INVALID_OPERATION')
    validate_argv(spec)
    return adapter_name, spec


def selected_capabilities(request, plan, observation):
    if observation['action'] in ('browser', 'network'):
        return ['web.dynamic.dom' if observation['action'] == 'browser' else 'web.dynamic.network']
    if 'capability' in observation:
        if observation['capability'] not in plan['capabilities']:
            raise ValueError('INVALID_CAPABILITY')
        return [observation['capability']]
    if plan['target']['kind'] == 'web_snapshot' and 'web.static.resources' in plan['capabilities']:
        return ['web.static.resources']
    candidates = [name for name in plan['capabilities']
                  if not name.startswith('web.dynamic.')]
    if not candidates:
        raise ValueError('INVALID_OPERATION')
    return candidates


def tool_paths(root, plan, tools, spec):
    paths = {}
    for name in spec.get('tools', []):
        planned = next((item for item in plan['tools'] if item['tool_id'] == name), None)
        installed = tools.get(name)
        if not planned or not installed or installed.get('version') != planned['version']:
            raise ValueError('TOOL_NOT_READY')
        paths[name] = installed
    return paths


def output_location(root, request, observation, adapter_name):
    base = auto_root(request['id']) + '/outputs/' + observation['id']
    if adapter_name == 'binary.static.ghidra':
        return safe_path(root, base + '/ghidra-project')
    if adapter_name == 'android.static.jadx':
        return safe_path(root, base + '/jadx')
    if adapter_name == 'android.static.apktool':
        return safe_path(root, base + '/apktool')
    return safe_path(root, base + '/output.txt')


def static_targets(root, request, capability, manifest):
    if capability != 'wasm.static':
        return [Path(request['target'].get('path', ''))]
    if manifest is not None:
        from .reverse_web import snapshot_bytes, snapshot_root
        base = snapshot_root(manifest['id'], manifest['snapshot_sha256'])
        return [safe_path(root, base + '/' + item['path']) for item, content in snapshot_bytes(root, manifest)
                if content.startswith(b'\x00asm') or item['url'].lower().split('?')[0].endswith('.wasm')]
    target = Path(request['target'].get('path', ''))
    if target.is_file():
        return [target]
    return [path for path in sorted(target.rglob('*')) if path.is_file() and not path.is_symlink()
            and (path.suffix.lower() == '.wasm' or path.read_bytes()[:4] == b'\x00asm')]


def invoke_static(root, request, plan, observation, grants, tools, runner, catalog, manifest):
    from .process import run as bounded_run
    results, commands, versions = [], [], {}
    for capability in selected_capabilities(request, plan, observation):
        adapter_name, spec = adapter_for(catalog, capability, plan['target']['kind'], 'static')
        if spec['grant'] not in grants:
            results.append({'status': 'NOT_AUTHORIZED', 'stdout': '', 'exit_code': None})
            commands.append(['adapter:' + adapter_name])
            continue
        if spec.get('provider') == 'builtin-web-static':
            from .reverse_web import static_local, static_resources
            output = (static_resources(root, manifest) if manifest is not None
                      else static_local(request['target']['path']))
            results.append({'status': 'RECORDED', 'stdout': json.dumps(output, sort_keys=True),
                            'exit_code': 0, 'timed_out': False, 'output_limit': False})
            commands.append(['provider:builtin-web-static'])
            continue
        installed = tool_paths(root, plan, tools, spec)
        primary = spec['tools'][0]
        source = Path(request['target'].get('path', ''))
        if request['target']['kind'] == 'file' and (
                not source.is_file() or source.is_symlink()
                or hashlib.sha256(source.read_bytes()).hexdigest() != plan['target'].get('target_sha256')):
            raise ValueError('STALE_TARGET')
        targets = static_targets(root, request, capability, manifest)
        if not targets:
            raise ValueError('WASM_TARGET_MISSING')
        for target in targets:
            output_path = output_location(root, request, observation, adapter_name)
            if len(targets) > 1:
                output_path = Path(str(output_path) + '.' + hashlib.sha256(
                    str(target).encode()).hexdigest()[:16] + '.wat')
            values = {'tool_path': installed[primary]['bin'], 'target_path': target,
                      'output_path': output_path}
            if 'temurin-jdk' in installed:
                values['jdk_path'] = installed['temurin-jdk']['bin']
            command = render_argv(spec, values)
            run = runner or (lambda argv, cwd, timeout, env=None: bounded_run(argv, cwd, timeout, env or {}))
            env = {}
            if 'jdk_path' in values:
                env['JAVA_HOME'] = str(Path(values['jdk_path']).parent.parent)
            result = run(command, root, spec['timeout'], env)
            results.append(result)
            commands.append(command)
            versions.update({name: value['version'] for name, value in installed.items()})
    return results, commands, versions


def invoke_dynamic(request, plan, observation, grants, provider, catalog, manifest):
    operation = observation.get('operation')
    if operation not in WEB_OPERATIONS or WEB_OPERATIONS[operation][0] != observation['action']:
        raise ValueError('INVALID_OPERATION')
    capability = selected_capabilities(request, plan, observation)[0]
    adapter_name, spec = adapter_for(catalog, capability, plan['target']['kind'], observation['action'])
    required = {'browser-observe', WEB_OPERATIONS[operation][1]}
    if request.get('auth', {}).get('use_session'):
        required.add('web-auth')
    if not required <= grants:
        return ([{'status': 'NOT_AUTHORIZED', 'stdout': '', 'exit_code': None}],
                [['provider:browser']], {}, sorted(required - grants))
    if provider is None:
        return ([{'status': 'PROVIDER_MISSING', 'stdout': '', 'exit_code': None}],
                [['provider:browser']], {}, [])
    if manifest is None:
        raise ValueError('SNAPSHOT_REQUIRED')
    context = {'operation': operation, 'snapshot_sha256': manifest['snapshot_sha256'],
               'origins': list(manifest['network']['origins']), 'timeout': spec['timeout'],
               'isolated_session': True, 'use_session': request.get('auth', {}).get('use_session', False),
               'max_resources': manifest['network']['max_resources'],
               'max_bytes': manifest['network']['max_bytes']}
    result = provider(context)
    if not isinstance(result, dict):
        raise ValueError('INVALID_PROVIDER_RESULT')
    return [result], [['provider:browser', operation]], {'browser': str(result.get('browser_version', 'unknown'))}, []


def observation_status(result):
    if result.get('status') in ('NOT_AUTHORIZED', 'PROVIDER_MISSING'):
        return result['status']
    if result.get('timed_out'):
        return 'TIMEOUT'
    if result.get('output_limit'):
        return 'OUTPUT_LIMIT'
    if result.get('status') == 'RECORDED' or result.get('exit_code') == 0:
        return 'RECORDED'
    return 'FAILED'


def observation_request_sha256(request, plan, observation):
    semantic_plan = {'target': plan['target'], 'capabilities': plan['capabilities'],
                     'tools': [{key: item.get(key) for key in
                                ('tool_id', 'version', 'artifact_sha256', 'source', 'entrypoint')}
                               for item in plan['tools']],
                     'network_origins': plan.get('network_origins', [])}
    identity = {'observation': observation, 'semantic_plan': semantic_plan,
                'evidence': request['evidence']}
    return sha_text(canonical(identity))


def store_observation(root, request, plan, observation, results, commands, versions):
    existing = read_observation(root, request['id'], observation['id'])
    request_sha256 = observation_request_sha256(request, plan, observation)
    if existing and existing['request_sha256'] != request_sha256:
        raise ValueError('OBSERVATION_CONFLICT')
    statuses = [observation_status(result) for result in results]
    status = 'RECORDED' if all(item == 'RECORDED' for item in statuses) else (
        statuses[0] if len(set(statuses)) == 1 else 'PARTIAL')
    chunks = [result.get('stdout') or '' for result in results]
    output = '\n'.join(chunks)
    record = {'schema': 'reverse-observation/v1', 'id': observation['id'],
              'question': observation['question'], 'action': observation['action'],
              'request_sha256': request_sha256, 'plan_sha256': plan['plan_sha256'],
              'target_sha256': plan['target'].get('target_sha256'), 'status': status,
              'adapter_statuses': statuses, 'tool_versions': versions,
              'command': commands, 'runtime_validation': 'NOT_RUN',
              'provenance': 'STATIC_SUPPORTED' if observation['action'] == 'static' else 'DYNAMIC_OBSERVED',
              'raw_status': ('NO_OUTPUT' if not output else
                             'RAW_RETAINED' if request['evidence']['raw'] == 'retain' else 'RAW_DISCARDED')}
    if existing:
        record['attempts'] = existing.get('attempts', []) + [existing['status']]
    if output:
        record['raw_sha256'] = sha_text(output)
        if request['evidence']['raw'] == 'retain':
            rel = auto_root(request['id']) + '/raw/' + observation['id'] + '.txt'
            atomic(root, rel, output)
            record['raw_path'] = rel
    atomic(root, observation_path(root, request['id'], observation['id']), encoded(record))
    return record


def execute_observation(root, request, plan, observation, grants, tools=None, runner=None,
                        provider=None, catalog=None, manifest=None):
    from .reverse_planner import load_catalog
    catalog = catalog or load_catalog()
    tools = tools or {}
    existing = read_observation(root, request['id'], observation['id'])
    request_sha256 = observation_request_sha256(request, plan, observation)
    if existing:
        if existing['request_sha256'] != request_sha256:
            raise ValueError('OBSERVATION_CONFLICT')
        if existing['status'] == 'RECORDED':
            return existing
    if observation['action'] == 'static':
        results, commands, versions = invoke_static(root, request, plan, observation, grants, tools,
                                                    runner, catalog, manifest)
        missing = []
    else:
        results, commands, versions, missing = invoke_dynamic(request, plan, observation, grants,
                                                              provider, catalog, manifest)
    record = store_observation(root, request, plan, observation, results, commands, versions)
    if missing:
        record['required_grants'] = missing
    return record


def behavior_contract(request, plan, records):
    by_id = {record['id']: record for record in records}
    for item in request['behavior']['capabilities']:
        for observation_id in item['observations']:
            record = by_id.get(observation_id)
            if not record or record['status'] != 'RECORDED' or record['provenance'] != item['provenance']:
                raise ValueError('INVALID_BEHAVIOR')
    return {'schema': BEHAVIOR_SCHEMA, 'id': request['id'], 'goal': request['goal'],
            'target': dict(plan['target']), 'plan_sha256': plan['plan_sha256'],
            'capabilities': request['behavior']['capabilities'],
            'constraints': list(request['behavior']['constraints']),
            'inferences': [{'value': value, 'provenance': 'INFERRED'}
                           for value in request['behavior']['inferences']],
            'observations': [record['id'] for record in records],
            'acceptance': list(request['acceptance']), 'runtime_validation': 'NOT_RUN',
            'source_map_evidence': False, 'implementation_approved': False}


def public_summary(request, plan, records, toolchain_status):
    statuses = ','.join(record['id'] + '=' + record['status'] for record in records)
    raw_states = ','.join(sorted({record['raw_status'] for record in records}))
    lines = ['# Reverse observation ' + request['id'], '',
             'Goal: ' + request['goal'], '',
             'Schema: `reverse-request/v1`', '',
             'Target kind: `' + plan['target']['kind'] + '`', '',
             'Target fingerprint: `' + str(plan['target'].get('target_sha256')) + '`', '',
             'Plan fingerprint: `' + plan['plan_sha256'] + '`', '',
             'Toolchain: `' + toolchain_status + '`', '',
             'Observations: `' + statuses + '`', '',
             'Runtime validation: `NOT_RUN`', '',
             'Raw evidence: `' + raw_states + '`', '',
             'Raw web/tool output is private; secrets and response bodies are not copied here.', '',
             'Reverse evidence is not source-map evidence and does not approve implementation.', '']
    return '\n'.join(lines)
