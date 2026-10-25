"""Pure input validation and planning; configuration never grants permission."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata

CAPABILITIES = {'write', 'agent', 'index', 'index-install', 'hooks', 'clone', 'local-clone', 'openspec', 'auth', 'reverse', 'reverse-install', 'package'}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def identity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', value):
        raise ValueError('INVALID_ID')
    return value


def build_plan(root, config, action):
    root = Path(root).absolute()
    if root.resolve() in (Path('/'), Path.home().resolve()):
        raise ValueError('UNSAFE_TARGET')
    identity(config.get('project_id'))
    # Host label only. Any coding agent coordinates; this field never selects a CLI.
    if not isinstance(config.get('agent'), str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,31}', config['agent']):
        raise ValueError('INVALID_AGENT_LABEL')
    for flag in ('index', 'hooks', 'openspec'):
        if flag in config and not isinstance(config[flag], bool):
            raise ValueError('INVALID_CAPABILITY: ' + flag)
    if not isinstance(config.get('modules', []), list) or not isinstance(config.get('discovery_roots', []), list):
        raise ValueError('INVALID_MODULE_LIST')
    for rel in config.get('discovery_roots', []):
        if not isinstance(rel, str) or Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('INVALID_DISCOVERY_ROOT')
    capabilities = ['write']
    for name in ('index', 'hooks', 'openspec'):
        if config.get(name):
            capabilities.append(name)
    ids, paths = set(), set()
    for module in config.get('modules', []):
        if not isinstance(module, dict):
            raise ValueError('INVALID_MODULE')
        mid = identity(module.get('id'))
        path = module.get('path', '')
        if not path or Path(path).is_absolute() or '..' in Path(path).parts:
            raise ValueError('INVALID_MODULE_PATH')
        normalized_id = mid.casefold()
        normalized_path = unicodedata.normalize('NFC', Path(path).as_posix()).casefold()
        if normalized_id in ids or normalized_path in paths:
            raise ValueError('DUPLICATE_ID_OR_PATH')
        ids.add(normalized_id)
        paths.add(normalized_path)
    return {'schema_version': 1, 'action': action, 'target': str(root),
            'config': config, 'required_capabilities': sorted(capabilities),
            'actions': ['generate framework', 'register modules', 'check navigation'],
            'conflicts': [], 'input_hashes': {}}


def approval_check(artifacts, confirmed_hashes):
    missing = []
    for name in ('requirements', 'design', 'plan'):
        content = artifacts.get(name)
        if not content or confirmed_hashes.get(name) != hashlib.sha256(content.encode()).hexdigest():
            missing.append(name)
    return missing
