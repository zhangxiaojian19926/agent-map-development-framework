"""Versioned, append-only reverse observations with explicit evidence states."""
import hashlib
import json
from pathlib import Path
import re

from .storage import atomic, safe_path


SCHEMA = 'reverse-scope/v2'
BEHAVIOR_SCHEMA = 'device-behavior/v1'
IDENTITY = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$')
BASE_FIELDS = {'schema', 'id', 'goal', 'target', 'acceptance', 'observations', 'evidence', 'behavior', 'device_plan'}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def valid_id(value):
    return isinstance(value, str) and bool(IDENTITY.fullmatch(value))


def is_v2(scope):
    return isinstance(scope, dict) and scope.get('schema') == SCHEMA


def load_operations():
    path = Path(__file__).resolve().parent / 'reverse-operations.lock.json'
    payload = json.loads(path.read_text(encoding='utf-8'))
    if payload.get('schema') != 'reverse-operations/v1':
        raise ValueError('INVALID_OPERATION')
    return payload['operations']


def operation_for(operations, name, action, read_only=True):
    spec = operations.get(name)
    if (not isinstance(spec, dict) or spec.get('action') != action
            or spec.get('read_only') is not read_only
            or not isinstance(spec.get('grant'), str) or not isinstance(spec.get('timeout'), int)):
        raise ValueError('INVALID_OPERATION')
    argv = spec.get('argv', [])
    if (not isinstance(argv, list) or any(not isinstance(part, str) for part in argv)
            or any('{' in part and part != '{device_id}' for part in argv)):
        raise ValueError('INVALID_OPERATION')
    if not argv and not spec.get('provider'):
        raise ValueError('INVALID_OPERATION')
    return spec


def operation_argv(spec, device_id):
    return [device_id if part == '{device_id}' else part for part in spec.get('argv', [])]


def _strings(value, allow_empty=False):
    return isinstance(value, list) and (allow_empty or bool(value)) and all(
        isinstance(item, str) and item.strip() for item in value)


def validate_scope(scope, lock, platform):
    if not isinstance(scope, dict) or set(scope) - BASE_FIELDS:
        raise ValueError('INVALID_SCOPE')
    required = BASE_FIELDS - {'device_plan'}
    if not required <= set(scope):
        raise ValueError('INVALID_SCOPE')
    if scope.get('schema') != SCHEMA or not valid_id(scope.get('id')):
        raise ValueError('INVALID_SCOPE')
    if not isinstance(scope.get('goal'), str) or not scope['goal'].strip():
        raise ValueError('INVALID_SCOPE')
    if not _strings(scope.get('acceptance')):
        raise ValueError('INVALID_SCOPE')
    target = scope.get('target')
    if not isinstance(target, dict):
        raise ValueError('INVALID_SCOPE')
    kind = target.get('kind')
    if kind == 'file':
        if set(target) != {'kind', 'path', 'sha256', 'tools'}:
            raise ValueError('INVALID_SCOPE')
        path = Path(target['path'])
        if not path.is_file() or path.is_symlink():
            raise ValueError('INVALID_SCOPE')
        if len(target['sha256']) != 64:
            raise ValueError('INVALID_SCOPE')
        if hashlib.sha256(path.read_bytes()).hexdigest() != target['sha256']:
            raise ValueError('STALE_TARGET')
    elif kind == 'device':
        if set(target) != {'kind', 'device_id', 'baseline_sha256', 'baseline_operation', 'tools'}:
            raise ValueError('INVALID_SCOPE')
        if not valid_id(target['device_id']) or len(target['baseline_sha256']) != 64:
            raise ValueError('INVALID_SCOPE')
        if not valid_id(target['baseline_operation']):
            raise ValueError('INVALID_SCOPE')
    else:
        raise ValueError('INVALID_SCOPE')
    if (not isinstance(target['tools'], list) or not target['tools']
            or len(set(target['tools'])) != len(target['tools'])) and kind == 'file':
        raise ValueError('INVALID_SCOPE')
    if kind == 'device' and (not isinstance(target['tools'], list) or len(set(target['tools'])) != len(target['tools'])):
        raise ValueError('INVALID_SCOPE')
    host_tools = set(lock['bundles'][platform])
    if any(not isinstance(name, str) or name not in host_tools for name in target['tools']):
        raise ValueError('INVALID_SCOPE')
    evidence = scope.get('evidence')
    if (not isinstance(evidence, dict) or set(evidence) != {'raw', 'public'}
            or evidence['raw'] not in ('retain', 'discard') or not isinstance(evidence['public'], bool)):
        raise ValueError('INVALID_SCOPE')
    observations = scope.get('observations')
    if not isinstance(observations, list) or not observations:
        raise ValueError('INVALID_SCOPE')
    seen = set()
    for item in observations:
        if not isinstance(item, dict) or not valid_id(item.get('id')) or item['id'] in seen:
            raise ValueError('INVALID_SCOPE')
        seen.add(item['id'])
        action = item.get('action')
        common = {'id', 'question', 'action'}
        if action == 'static':
            if set(item) != common or kind != 'file':
                raise ValueError('INVALID_SCOPE')
        elif action in ('device', 'network'):
            fields = common | {'operation'} | ({'endpoint'} if action == 'network' else set())
            if set(item) != fields or kind != 'device' or not valid_id(item['operation']):
                raise ValueError('INVALID_SCOPE')
            if action == 'network' and (not isinstance(item['endpoint'], str) or not item['endpoint'].strip()):
                raise ValueError('INVALID_SCOPE')
        else:
            raise ValueError('INVALID_SCOPE')
        if not isinstance(item['question'], str) or not item['question'].strip():
            raise ValueError('INVALID_SCOPE')
    behavior = scope.get('behavior')
    if (not isinstance(behavior, dict) or set(behavior) != {'capabilities', 'constraints', 'inferences'}
            or not isinstance(behavior['capabilities'], list)
            or not _strings(behavior['constraints'], allow_empty=True)
            or not _strings(behavior['inferences'], allow_empty=True)):
        raise ValueError('INVALID_SCOPE')
    for capability in behavior['capabilities']:
        if (not isinstance(capability, dict) or set(capability) != {'name', 'provenance', 'observations'}
                or not isinstance(capability['name'], str) or not capability['name'].strip()
                or capability['provenance'] not in ('STATIC_SUPPORTED', 'DYNAMIC_OBSERVED', 'INFERRED')
                or not isinstance(capability['observations'], list)
                or any(observation not in seen for observation in capability['observations'])):
            if isinstance(capability, dict) and any(
                    observation not in seen for observation in capability.get('observations', [])):
                raise ValueError('INVALID_BEHAVIOR')
            raise ValueError('INVALID_SCOPE')
        if capability['provenance'] == 'INFERRED' and capability['observations']:
            raise ValueError('INVALID_BEHAVIOR')
        if capability['provenance'] != 'INFERRED' and not capability['observations']:
            raise ValueError('INVALID_BEHAVIOR')
    if 'device_plan' in scope and not isinstance(scope['device_plan'], dict):
        raise ValueError('INVALID_SCOPE')
    return list(target['tools'])


def state_root(scope_id):
    return '.framework/local-state/reverse/v2/' + scope_id


def save_scope(root, scope):
    rel = state_root(scope['id']) + '/scope.json'
    path = safe_path(root, rel)
    if path.is_file():
        previous = json.loads(path.read_text(encoding='utf-8'))
        old_base = {key: value for key, value in previous.items() if key != 'observations'}
        new_base = {key: value for key, value in scope.items() if key != 'observations'}
        if old_base != new_base:
            old_plan = previous.get('device_plan')
            new_plan = scope.get('device_plan')
            action_only = (isinstance(old_plan, dict) and isinstance(new_plan, dict)
                           and old_plan['action'] in ('pilot', 'rollback', 'rollout')
                           and new_plan['action'] in ('pilot', 'rollback', 'rollout')
                           and {**old_plan, 'action': new_plan['action']} == new_plan)
            comparable_old = dict(previous)
            comparable_new = dict(scope)
            if action_only:
                comparable_old['device_plan'] = dict(old_plan, action=new_plan['action'])
            old_base = {key: value for key, value in comparable_old.items() if key != 'observations'}
            new_base = {key: value for key, value in comparable_new.items() if key != 'observations'}
            if old_base != new_base:
                raise ValueError('SCOPE_CONFLICT')
        if previous['observations'] != scope['observations'][:len(previous['observations'])]:
            same_ids = [item['id'] for item in previous['observations']] == [
                item['id'] for item in scope['observations'][:len(previous['observations'])]]
            raise ValueError('OBSERVATION_CONFLICT' if same_ids else 'SCOPE_CONFLICT')
    atomic(root, rel, encoded(scope))


def tool_versions(scope, lock):
    versions = {}
    for name in scope['target']['tools']:
        spec = lock['rea-agents'] if name == 'rea-agents' else lock['tools'][name]
        versions[name] = spec['version']
    return versions


def observation_record_path(root, scope_id, observation_id):
    return state_root(scope_id) + '/observations/' + observation_id + '.json'


def read_record(root, scope_id, observation_id):
    path = safe_path(root, observation_record_path(root, scope_id, observation_id))
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def raw_status(scope, output):
    if not output:
        return 'NO_OUTPUT'
    return 'RAW_RETAINED' if scope['evidence']['raw'] == 'retain' else 'RAW_DISCARDED'


def store_observation(root, scope, observation, result, command, lock):
    existing = read_record(root, scope['id'], observation['id'])
    request_sha256 = sha_text(canonical(observation))
    if existing is not None:
        if existing['request_sha256'] != request_sha256:
            raise ValueError('OBSERVATION_CONFLICT')
        return existing
    output = result.get('stdout') or ''
    target = scope['target']
    target_sha256 = target['sha256'] if target['kind'] == 'file' else target['baseline_sha256']
    failed = result.get('exit_code', 1) != 0
    status = 'FAILED' if failed else 'RECORDED'
    if result.get('timed_out'):
        status = 'TIMEOUT'
    if result.get('output_limit'):
        status = 'OUTPUT_LIMIT'
    record = {
        'id': observation['id'], 'question': observation['question'], 'action': observation['action'],
        'request_sha256': request_sha256, 'target_sha256': target_sha256,
        'tool_versions': tool_versions(scope, lock), 'status': status,
        'exit_code': result.get('exit_code', 1), 'command': command,
        'provenance': 'STATIC_SUPPORTED' if observation['action'] == 'static' else 'DYNAMIC_OBSERVED',
        'runtime_validation': 'NOT_RUN', 'raw_status': raw_status(scope, output)
    }
    if output:
        record['raw_sha256'] = sha_text(output)
        if scope['evidence']['raw'] == 'retain':
            raw_rel = state_root(scope['id']) + '/raw/' + observation['id'] + '.txt'
            atomic(root, raw_rel, output)
            record['raw_path'] = raw_rel
    atomic(root, observation_record_path(root, scope['id'], observation['id']), encoded(record))
    return record


def record_not_run(root, scope, observation, status, lock):
    existing = read_record(root, scope['id'], observation['id'])
    request_sha256 = sha_text(canonical(observation))
    if existing is not None:
        if existing['request_sha256'] != request_sha256:
            raise ValueError('OBSERVATION_CONFLICT')
        return existing
    target = scope['target']
    record = {
        'id': observation['id'], 'question': observation['question'], 'action': observation['action'],
        'request_sha256': request_sha256,
        'target_sha256': target.get('sha256', target.get('baseline_sha256')),
        'tool_versions': tool_versions(scope, lock), 'status': status,
        'exit_code': None, 'command': [], 'runtime_validation': 'NOT_RUN', 'raw_status': 'NO_OUTPUT'
    }
    atomic(root, observation_record_path(root, scope['id'], observation['id']), encoded(record))
    return record


def run_static(root, scope, observation, runner):
    target = Path(scope['target']['path'])
    rea = safe_path(root, '.framework/tools/rea/node_modules/.bin/rea')
    command = [str(rea) if rea.is_file() else 'rea', 'analyze', str(target), '--json']
    result = runner(command, root)
    return result, command


def build_behavior_contract(scope, records):
    by_id = {record['id']: record for record in records}
    capabilities = []
    for item in scope['behavior']['capabilities']:
        provenance = item['provenance']
        for observation_id in item['observations']:
            record = by_id.get(observation_id)
            if not record or record['status'] != 'RECORDED':
                raise ValueError('INVALID_BEHAVIOR')
            expected = 'STATIC_SUPPORTED' if record['action'] == 'static' else 'DYNAMIC_OBSERVED'
            if provenance != expected:
                raise ValueError('INVALID_BEHAVIOR')
        capabilities.append(dict(item))
    return {
        'schema': BEHAVIOR_SCHEMA, 'id': scope['id'], 'goal': scope['goal'],
        'target': {'kind': scope['target']['kind'],
                   'baseline_sha256': scope['target'].get('sha256', scope['target'].get('baseline_sha256'))},
        'capabilities': capabilities, 'constraints': list(scope['behavior']['constraints']),
        'inferences': [{'value': value, 'provenance': 'INFERRED'} for value in scope['behavior']['inferences']],
        'observations': [record['id'] for record in records],
        'acceptance': list(scope['acceptance']), 'runtime_validation': 'NOT_RUN'
    }


def public_summary(scope, records, observation_status, device_status='NOT_REQUESTED', runtime='NOT_RUN'):
    raw_states = sorted({record.get('raw_status', 'NO_OUTPUT') for record in records})
    lines = [
        '# Reverse observation ' + scope['id'], '',
        'Goal: ' + scope['goal'], '',
        'Schema: `' + SCHEMA + '`', '',
        'Target kind: `' + scope['target']['kind'] + '`', '',
        'Target baseline: `' + scope['target'].get('sha256', scope['target'].get('baseline_sha256')) + '`', '',
        'Observation: `' + observation_status + '`', '',
        'Runtime validation: `' + runtime + '`', '',
        'Device change: `' + device_status + '`', '',
        'Raw evidence: `' + ','.join(raw_states) + '`', '',
        'Raw evidence is private and is not copied here when retained.', '',
        'Reverse evidence is not source evidence and does not approve implementation.', ''
    ]
    return '\n'.join(lines)


def observation_grants(observation, spec):
    required = {spec['grant']}
    if observation['action'] == 'device':
        required.add('device-connect')
    return required


def check_baseline(root, scope, grants, operation_runner, operations):
    target = scope['target']
    spec = operation_for(operations, target['baseline_operation'], 'device')
    required = {'device-connect', spec['grant']}
    if not required <= grants:
        return 'NOT_AUTHORIZED'
    command = operation_argv(spec, target['device_id'])
    result = operation_runner(command, root, spec['timeout'])
    output = result.get('stdout') or ''
    if output:
        atomic(root, state_root(scope['id']) + '/baseline.txt', output)
    if result.get('exit_code', 1) != 0 or result.get('timed_out') or result.get('output_limit'):
        return 'FAILED'
    return None if sha_text(output) == target['baseline_sha256'] else 'STALE'


def execute_v2(root, scope, grants, runner, lock, device_executor=None, operation_runner=None):
    operations = load_operations()
    for observation in scope['observations']:
        if observation['action'] != 'static':
            operation_for(operations, observation['operation'], observation['action'])
    if scope['target']['kind'] == 'device':
        operation_for(operations, scope['target']['baseline_operation'], 'device')
    operation_runner = operation_runner or (lambda argv, cwd, timeout: runner(argv, cwd))
    if 'device_plan' in scope:
        from .reverse_device import validate_plan
        validate_plan(scope, operations)
    save_scope(root, scope)
    records = []
    baseline_status = None
    baseline_checked = False
    for observation in scope['observations']:
        existing = read_record(root, scope['id'], observation['id'])
        if existing is not None:
            if existing['request_sha256'] != sha_text(canonical(observation)):
                raise ValueError('OBSERVATION_CONFLICT')
            records.append(existing)
            continue
        if observation['action'] == 'static':
            result, command = run_static(root, scope, observation, runner)
            records.append(store_observation(root, scope, observation, result, command, lock))
            continue
        spec = operation_for(operations, observation['operation'], observation['action'])
        if not observation_grants(observation, spec) <= grants:
            records.append(record_not_run(root, scope, observation, 'NOT_AUTHORIZED', lock))
            continue
        if spec.get('provider') and device_executor is None:
            records.append(record_not_run(root, scope, observation, 'PROVIDER_MISSING', lock))
            continue
        if observation['action'] == 'device' and not baseline_checked:
            baseline_status = check_baseline(root, scope, grants, operation_runner, operations)
            baseline_checked = True
        if baseline_status:
            records.append(record_not_run(root, scope, observation, baseline_status, lock))
            continue
        if spec.get('provider'):
            result = device_executor(spec, scope['target'], observation.get('endpoint'))
            command = ['provider:' + spec['provider']]
        else:
            command = operation_argv(spec, scope['target']['device_id'])
            result = operation_runner(command, root, spec['timeout'])
        records.append(store_observation(root, scope, observation, result, command, lock))
    statuses = {record['status'] for record in records}
    if statuses == {'RECORDED'}:
        observation_status = 'RECORDED'
    elif 'RECORDED' in statuses:
        observation_status = 'PARTIAL'
    elif len(statuses) == 1:
        observation_status = next(iter(statuses))
    else:
        observation_status = 'PARTIAL'
    device_status = 'NOT_REQUESTED'
    runtime = 'NOT_RUN'
    if 'device_plan' in scope:
        from .reverse_device import execute_device, load_state
        persisted = load_state(root, scope['id'])
        failed_replay = scope['device_plan']['action'] == 'pilot' and persisted and persisted['state'] == 'FAILED'
        if not baseline_checked and not failed_replay:
            baseline_status = check_baseline(root, scope, grants, operation_runner, operations)
        device_status, runtime = execute_device(root, scope, grants, operation_runner, operations, baseline_status)
    contract = None
    if observation_status == 'RECORDED':
        contract = build_behavior_contract(scope, records)
        contract['runtime_validation'] = runtime
        atomic(root, state_root(scope['id']) + '/behavior-contract.json', encoded(contract))
    if scope['evidence']['public']:
        atomic(root, 'docs/project/reverse/' + scope['id'] + '.md',
               public_summary(scope, records, observation_status, device_status, runtime))
    return {
        'observation_status': observation_status,
        'runtime_validation': runtime, 'device_change_status': device_status,
        'observations': [{'id': record['id'], 'status': record['status']} for record in records],
        'behavior_contract': BEHAVIOR_SCHEMA if contract else 'NOT_READY'
    }


def report_v2(root):
    base = safe_path(root, '.framework/local-state/reverse/v2')
    if not base.is_dir():
        return None
    for scope_path in sorted(base.glob('*/scope.json')):
        scope = json.loads(scope_path.read_text(encoding='utf-8'))
        target = scope['target']
        if target['kind'] == 'file':
            path = Path(target['path'])
            if (not path.is_file() or path.is_symlink()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != target['sha256']):
                return {'status': 'STALE', 'id': scope['id']}
        else:
            baseline = base / scope['id'] / 'baseline.txt'
            if baseline.is_file() and sha_text(baseline.read_text(encoding='utf-8')) != target['baseline_sha256']:
                return {'status': 'STALE', 'id': scope['id']}
        for record_path in sorted((base / scope['id'] / 'observations').glob('*.json')):
            record = json.loads(record_path.read_text(encoding='utf-8'))
            if record.get('raw_path'):
                raw = safe_path(root, record['raw_path'])
                if not raw.is_file() or sha_text(raw.read_text(encoding='utf-8')) != record['raw_sha256']:
                    return {'status': 'STALE', 'id': scope['id'], 'observation': record['id']}
    return {'status': 'READY'}
