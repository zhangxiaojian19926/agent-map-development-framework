"""Deterministic capability-to-tool resolution and canonical approval plans."""
import copy
import hashlib
import json
from pathlib import Path

from .reverse_downloads import artifact_for
from .reverse_install import inspect_installed
from .reverse_request import canonical, validate_network


CATALOG_PATH = Path(__file__).resolve().parent / 'reverse-catalog.json'
LOCK_PATH = Path(__file__).resolve().parent / 'rea-tools.lock.json'


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('INVALID_CATALOG')
        result[key] = value
    return result


def loads_catalog(text):
    try:
        return json.loads(text, object_pairs_hook=no_duplicates)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError('INVALID_CATALOG') from exc


def load_lock():
    return json.loads(LOCK_PATH.read_text(encoding='utf-8'), object_pairs_hook=no_duplicates)


def validate_catalog(catalog, lock):
    if not isinstance(catalog, dict) or catalog.get('schema') != 'reverse-catalog/v1':
        raise ValueError('INVALID_CATALOG')
    if set(catalog) != {'schema', 'tools', 'capabilities', 'adapters'}:
        raise ValueError('INVALID_CATALOG')
    tools, capabilities, adapters = catalog['tools'], catalog['capabilities'], catalog['adapters']
    if not all(isinstance(value, dict) for value in (tools, capabilities, adapters)):
        raise ValueError('INVALID_CATALOG')
    for name, spec in tools.items():
        source = lock['rea-agents'] if name == 'rea-agents' else lock['tools'].get(name)
        if not source or spec.get('installer') not in ('npm', 'archive'):
            raise ValueError('INVALID_TOOLCHAIN')
        if not isinstance(spec.get('requires'), list) or any(item not in tools for item in spec['requires']):
            raise ValueError('INVALID_TOOLCHAIN')
        if not isinstance(spec.get('entrypoint', ''), str) and name != 'temurin-jdk':
            raise ValueError('INVALID_TOOLCHAIN')
        if not isinstance(spec.get('probe'), bool):
            raise ValueError('INVALID_TOOLCHAIN')
    for name, spec in capabilities.items():
        if (not isinstance(spec.get('tools'), list) or any(item not in tools for item in spec['tools'])
                or spec.get('adapter') not in adapters or not isinstance(spec.get('targets'), list)):
            raise ValueError('INVALID_TOOLCHAIN')
        adapter = adapters[spec['adapter']]
        if any(item not in adapter.get('tools', []) for item in spec['tools']):
            raise ValueError('INVALID_TOOLCHAIN')
    for name, spec in adapters.items():
        if (spec.get('action') not in ('static', 'browser', 'network')
                or not isinstance(spec.get('grant'), str)
                or not isinstance(spec.get('timeout'), int) or spec['timeout'] <= 0
                or any(item not in tools for item in spec.get('tools', []))):
            raise ValueError('INVALID_TOOLCHAIN')
        if not spec.get('provider') and not isinstance(spec.get('argv'), list):
            raise ValueError('INVALID_TOOLCHAIN')
    return catalog


def load_catalog(lock=None):
    catalog = loads_catalog(CATALOG_PATH.read_text(encoding='utf-8'))
    return validate_catalog(catalog, lock or load_lock())


def tool_spec(name, catalog, lock, platform):
    base = copy.deepcopy(lock['rea-agents'] if name == 'rea-agents' else lock['tools'][name])
    registered = catalog['tools'][name]
    base.update({key: value for key, value in registered.items() if key not in ('entrypoints', 'requires', 'installer')})
    if 'entrypoints' in registered:
        base['entrypoint'] = registered['entrypoints'].get(platform)
    return base


def artifact_status(spec, installer, platform, machine):
    if installer == 'npm':
        return None if str(spec.get('integrity', '')).startswith('sha512-') else 'INTEGRITY_UNPINNED'
    chosen = artifact_for(spec, platform, machine)
    if chosen:
        return None
    artifacts = spec.get('artifacts') or {}
    key = platform + '-' + machine
    if key not in artifacts and not spec.get('url'):
        return 'HOST_UNSUPPORTED'
    return 'INTEGRITY_UNPINNED'


def dependency_closure(capability_names, catalog):
    ordered = []

    def add_tool(name):
        if name in ordered:
            return
        for dependency in catalog['tools'][name]['requires']:
            add_tool(dependency)
        ordered.append(name)

    for capability in capability_names:
        if capability not in catalog['capabilities']:
            raise ValueError('INVALID_CAPABILITY')
        for name in catalog['capabilities'][capability]['tools']:
            add_tool(name)
    return ordered


def build_plan(root, request, profile, catalog=None, lock=None, platform='darwin', machine='arm64',
               runner=None, probe=False):
    catalog = validate_catalog(catalog or load_catalog(), lock or load_lock())
    lock = lock or load_lock()
    if profile.get('status') == 'PROFILE_UNKNOWN':
        return {'schema': 'toolchain-plan/v1', 'status': 'PROFILE_UNKNOWN', 'tools': [],
                'capabilities': [], 'profile': profile}
    capabilities = list(request.get('capabilities') or profile.get('capabilities') or [])
    for name in capabilities:
        if name not in catalog['capabilities']:
            raise ValueError('INVALID_CAPABILITY')
        if profile['kind'] not in catalog['capabilities'][name]['targets']:
            raise ValueError('CAPABILITY_TARGET_MISMATCH')
    names = dependency_closure(capabilities, catalog)
    tools = []
    errors = []
    origins = set(validate_network(request)['origins'])
    for name in names:
        registered = catalog['tools'][name]
        spec = tool_spec(name, catalog, lock, platform)
        error = artifact_status(spec, registered['installer'], platform, machine)
        chosen = artifact_for(spec, platform, machine) if registered['installer'] == 'archive' else None
        artifact = chosen['sha256'] if chosen else spec.get('integrity', '')
        if error:
            action, reason = 'BLOCK', error
            errors.append(error)
        else:
            inspected = inspect_installed(root, name, spec, runner=runner, probe=probe)
            if inspected['status'] == 'READY':
                action, reason = 'REUSE', 'HEALTHY'
            elif inspected['status'] == 'MISSING':
                action, reason = 'INSTALL', 'MISSING'
            else:
                action, reason = 'REPAIR', inspected['status']
        source = chosen['url'] if chosen else 'npm:' + spec.get('package', name)
        if chosen:
            from urllib.parse import urlsplit
            parsed = urlsplit(source)
            origins.add(parsed.scheme + '://' + str(parsed.hostname) + ':' + str(parsed.port or 443))
        tools.append({'tool_id': name, 'version': spec['version'], 'installer': registered['installer'],
                      'requires': list(registered['requires']), 'artifact_sha256': artifact,
                      'source': source, 'entrypoint': spec.get('entrypoint'), 'action': action, 'reason': reason,
                      'expected_download_bytes': (chosen or {}).get('size', 0)})
    grants = {'write', 'reverse'}
    if request['target']['kind'] == 'url':
        grants.add('web-fetch')
    for capability in capabilities:
        grant = catalog['capabilities'][capability].get('grant')
        if grant:
            grants.add(grant)
    if any(item['action'] in ('INSTALL', 'REPAIR') for item in tools):
        grants.add('reverse-install')
    if request.get('auth', {}).get('use_session'):
        grants.add('web-auth')
    status = 'READY'
    for candidate in ('INTEGRITY_UNPINNED', 'HOST_UNSUPPORTED', 'INVALID_TOOLCHAIN'):
        if candidate in errors:
            status = candidate
            break
    plan = {
        'schema': 'toolchain-plan/v1', 'status': status,
        'request_sha256': hashlib.sha256(canonical(request).encode()).hexdigest(),
        'profile_sha256': hashlib.sha256(canonical(profile).encode()).hexdigest(),
        'target': {'kind': profile['kind'], 'format': profile.get('format'),
                   'target_sha256': profile.get('target_sha256')},
        'host': platform, 'machine': machine, 'capabilities': capabilities, 'tools': tools,
        'required_grants': sorted(grants), 'network_origins': sorted(origins),
        'expected_download_bytes': sum(item['expected_download_bytes'] for item in tools),
        'side_effects': sorted({item['action'].lower() + ':' + item['tool_id'] for item in tools
                                if item['action'] in ('INSTALL', 'REPAIR')})
    }
    plan['plan_sha256'] = hashlib.sha256(canonical(plan).encode()).hexdigest()
    return plan
