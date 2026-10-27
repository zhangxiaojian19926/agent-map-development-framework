"""Strict automatic reverse requests and non-executing local/URL profilers."""
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import zipfile
from urllib.parse import urlsplit

from .reverse_v2 import IDENTITY, canonical, sha_text


SCHEMA = 'reverse-request/v1'
BASE = {'schema', 'id', 'goal', 'target', 'intent', 'acceptance', 'observations', 'evidence', 'behavior'}
OPTIONAL = {'network', 'auth', 'capabilities'}
NETWORK_FIELDS = {'origins', 'allow_private', 'allow_http', 'max_resources', 'max_bytes', 'timeout'}


def strings(value, allow_empty=False):
    return isinstance(value, list) and (allow_empty or bool(value)) and all(
        isinstance(item, str) and item.strip() for item in value)


def valid_id(value):
    return isinstance(value, str) and bool(IDENTITY.fullmatch(value))


def origin(value, allow_path=False):
    parsed = urlsplit(value)
    if (parsed.username or parsed.password or not parsed.hostname
            or (not allow_path and (parsed.fragment or parsed.query or parsed.path not in ('', '/')))):
        raise ValueError('INVALID_ORIGIN')
    port = parsed.port or (443 if parsed.scheme == 'https' else 80 if parsed.scheme == 'http' else None)
    if parsed.scheme not in ('http', 'https') or not port:
        raise ValueError('INVALID_ORIGIN')
    return parsed.scheme + '://' + parsed.hostname.lower() + ':' + str(port)


def private_host(host):
    if host.lower() == 'localhost' or host.lower().endswith(('.local', '.internal', '.localhost')):
        return True
    try:
        address = ipaddress.ip_address(host.strip('[]'))
        return not address.is_global
    except ValueError:
        return False


def validate_network(request):
    target_url = request['target'].get('url') if request['target']['kind'] == 'url' else None
    default_origin = origin(target_url, allow_path=True) if target_url else None
    network = request.get('network') or {
        'origins': [default_origin] if default_origin else [], 'allow_private': False,
        'allow_http': False, 'max_resources': 100, 'max_bytes': 32 * 1024 * 1024, 'timeout': 30}
    if set(network) != NETWORK_FIELDS or not isinstance(network['origins'], list):
        raise ValueError('INVALID_NETWORK')
    if len(set(network['origins'])) != len(network['origins']):
        raise ValueError('INVALID_NETWORK')
    normalized = [origin(item) for item in network['origins']]
    for flag in ('allow_private', 'allow_http'):
        if not isinstance(network[flag], bool):
            raise ValueError('INVALID_NETWORK')
    for key, upper in (('max_resources', 10000), ('max_bytes', 1024 * 1024 * 1024), ('timeout', 300)):
        if not isinstance(network[key], int) or isinstance(network[key], bool) or not 0 < network[key] <= upper:
            raise ValueError('INVALID_NETWORK')
    result = dict(network)
    result['origins'] = normalized
    if default_origin and default_origin not in normalized:
        raise ValueError('TARGET_OUT_OF_SCOPE')
    return result


def validate_request(request):
    if not isinstance(request, dict) or set(request) - BASE - OPTIONAL:
        raise ValueError('INVALID_REQUEST')
    if not BASE <= set(request) or request.get('schema') != SCHEMA or not valid_id(request.get('id')):
        raise ValueError('INVALID_REQUEST')
    if not isinstance(request.get('goal'), str) or not request['goal'].strip():
        raise ValueError('INVALID_REQUEST')
    if request.get('intent') not in ('static', 'deep-static', 'dynamic'):
        raise ValueError('INVALID_INTENT')
    if not strings(request.get('acceptance')):
        raise ValueError('INVALID_REQUEST')
    if 'capabilities' in request and not strings(request['capabilities']):
        raise ValueError('INVALID_CAPABILITIES')
    evidence = request.get('evidence')
    if (not isinstance(evidence, dict) or set(evidence) != {'raw', 'public'}
            or evidence['raw'] not in ('retain', 'discard') or not isinstance(evidence['public'], bool)):
        raise ValueError('INVALID_EVIDENCE')
    if 'auth' in request and (set(request['auth']) != {'use_session'}
                              or not isinstance(request['auth']['use_session'], bool)):
        raise ValueError('INVALID_AUTH')
    behavior = request.get('behavior')
    if (not isinstance(behavior, dict) or set(behavior) != {'capabilities', 'constraints', 'inferences'}
            or not isinstance(behavior['capabilities'], list)
            or not strings(behavior['constraints'], allow_empty=True)
            or not strings(behavior['inferences'], allow_empty=True)):
        raise ValueError('INVALID_BEHAVIOR')
    for item in behavior['capabilities']:
        if (not isinstance(item, dict) or set(item) != {'name', 'provenance', 'observations'}
                or not isinstance(item['name'], str)
                or item['provenance'] not in ('STATIC_SUPPORTED', 'DYNAMIC_OBSERVED', 'INFERRED')
                or not isinstance(item['observations'], list)):
            raise ValueError('INVALID_BEHAVIOR')
    observations = request.get('observations')
    if not isinstance(observations, list) or not observations:
        raise ValueError('INVALID_OBSERVATION')
    seen = set()
    for item in observations:
        if not isinstance(item, dict) or not valid_id(item.get('id')) or item['id'] in seen:
            raise ValueError('INVALID_OBSERVATION')
        seen.add(item['id'])
        if not isinstance(item.get('question'), str) or not item['question'].strip():
            raise ValueError('INVALID_OBSERVATION')
        action = item.get('action')
        common = {'id', 'question', 'action'}
        if action == 'static':
            if (set(item) not in (common, common | {'capability'})
                    or ('capability' in item and not valid_id(item['capability']))):
                raise ValueError('INVALID_OBSERVATION')
        elif action in ('browser', 'network'):
            if set(item) != common | {'operation'} or not valid_id(item.get('operation')):
                raise ValueError('INVALID_OBSERVATION')
        else:
            raise ValueError('INVALID_OBSERVATION')
    for item in behavior['capabilities']:
        if (not isinstance(item['name'], str) or not item['name'].strip()
                or any(observation not in seen for observation in item['observations'])
                or (item['provenance'] == 'INFERRED' and bool(item['observations']))
                or (item['provenance'] != 'INFERRED' and not item['observations'])):
            raise ValueError('INVALID_BEHAVIOR')
    target = request.get('target')
    if not isinstance(target, dict) or target.get('kind') not in ('file', 'directory', 'url'):
        raise ValueError('INVALID_TARGET')
    if target['kind'] == 'url':
        if set(target) != {'kind', 'url'} or not isinstance(target['url'], str):
            raise ValueError('INVALID_TARGET')
    else:
        if set(target) != {'kind', 'path', 'sha256'} or not isinstance(target['path'], str):
            raise ValueError('INVALID_TARGET')
        path = Path(target['path'])
        if path.is_symlink() or len(target['sha256']) != 64 or not re.fullmatch(r'[0-9a-f]{64}', target['sha256']):
            raise ValueError('INVALID_TARGET')
        if target['kind'] == 'file' and not path.is_file():
            raise ValueError('INVALID_TARGET')
        if target['kind'] == 'directory' and not path.is_dir():
            raise ValueError('INVALID_TARGET')
    validate_network(request)
    return request


def preprofile_url(request, grants=(), opener=None):
    del opener  # URL pre-profiling is deliberately offline.
    validate_request(request)
    network = validate_network(request)
    parsed = urlsplit(request['target']['url'])
    if parsed.scheme not in ('http', 'https') or parsed.username or parsed.password or not parsed.hostname:
        raise ValueError('INVALID_URL')
    if parsed.scheme == 'http' and not network['allow_http']:
        raise ValueError('HTTP_NOT_ALLOWED')
    if private_host(parsed.hostname) and not network['allow_private']:
        raise ValueError('PRIVATE_NETWORK')
    capabilities = ['web.static.resources']
    if request['intent'] == 'dynamic' or any(item['action'] == 'browser' for item in request['observations']):
        capabilities.append('web.dynamic.dom')
    if any(item['action'] == 'network' for item in request['observations']):
        capabilities.append('web.dynamic.network')
    return {'status': 'SNAPSHOT_REQUIRED', 'kind': 'url', 'format': 'url',
            'url_sha256': sha_text(request['target']['url']), 'capabilities': capabilities,
            'facts': ['url-parsed-offline'], 'network': network,
            'required_grants': [] if 'web-fetch' in grants else ['web-fetch']}


def profile_file(request):
    target = request['target']
    path = Path(target['path'])
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != target['sha256']:
        raise ValueError('STALE_TARGET')
    head = raw[:8192]
    kind, fmt = 'unknown', 'unknown'
    capabilities, facts = [], []
    if head.startswith(b'\x7fELF'):
        kind, fmt, facts = 'native', 'ELF', ['magic:ELF']
    elif head.startswith(b'MZ'):
        kind, fmt, facts = 'native', 'PE', ['magic:MZ']
    elif head[:4] in (b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xfe\xed\xfa\xce'):
        kind, fmt, facts = 'native', 'Mach-O', ['magic:Mach-O']
    elif head.startswith(b'\x00asm'):
        kind, fmt, facts = 'wasm', 'WASM', ['magic:wasm']
    elif head.startswith(b'PK'):
        try:
            with zipfile.ZipFile(path) as packed:
                names = set(packed.namelist())
            if 'AndroidManifest.xml' in names or 'classes.dex' in names:
                kind, fmt, facts = 'android', 'APK', ['zip:AndroidManifest.xml/classes.dex']
        except zipfile.BadZipFile:
            pass
    lower = head.lower()
    if kind == 'unknown' and (b'<html' in lower or b'<!doctype html' in lower or b'<script' in lower):
        kind, fmt, facts = 'web_snapshot', 'HTML', ['text:html']
    if kind == 'unknown' and path.suffix.lower() in ('.js', '.mjs', '.css', '.html'):
        kind, fmt, facts = 'web_snapshot', path.suffix.lower()[1:].upper(), ['text:' + path.suffix.lower()]
    if kind == 'native':
        capabilities = ['binary.static.native' if request['intent'] == 'deep-static' else 'binary.static.generic']
    elif kind == 'android':
        capabilities = ['android.static.bytecode', 'android.static.resources']
    elif kind == 'wasm':
        capabilities = ['wasm.static']
    elif kind == 'web_snapshot':
        capabilities = ['web.static.resources']
        if request['intent'] == 'dynamic' or any(item['action'] == 'browser' for item in request['observations']):
            capabilities.append('web.dynamic.dom')
        if any(item['action'] == 'network' for item in request['observations']):
            capabilities.append('web.dynamic.network')
    return {'status': 'PROFILED' if kind != 'unknown' else 'PROFILE_UNKNOWN', 'kind': kind, 'format': fmt,
            'target_sha256': actual, 'capabilities': capabilities, 'facts': facts or ['content:unknown']}


def profile_directory(request):
    target = request['target']
    base = Path(target['path'])
    entries = []
    capabilities = ['web.static.resources']
    total = 0
    for path in sorted(base.rglob('*')):
        if path.is_symlink():
            raise ValueError('INVALID_TARGET')
        if not path.is_file():
            continue
        if len(entries) >= 10000:
            raise ValueError('PROFILE_LIMIT')
        raw = path.read_bytes()
        total += len(raw)
        if total > 128 * 1024 * 1024:
            raise ValueError('PROFILE_LIMIT')
        rel = path.relative_to(base).as_posix()
        entries.append(rel + ':' + hashlib.sha256(raw).hexdigest())
        if path.suffix.lower() == '.wasm' or raw.startswith(b'\x00asm'):
            capabilities.append('wasm.static')
    actual = sha_text('\n'.join(entries))
    if actual != target['sha256']:
        raise ValueError('STALE_TARGET')
    if request['intent'] == 'dynamic' or any(item['action'] == 'browser' for item in request['observations']):
        capabilities.append('web.dynamic.dom')
    if any(item['action'] == 'network' for item in request['observations']):
        capabilities.append('web.dynamic.network')
    return {'status': 'PROFILED', 'kind': 'web_snapshot', 'format': 'directory',
            'target_sha256': actual, 'capabilities': sorted(set(capabilities)),
            'facts': ['files:' + str(len(entries))]}


def profile_request(request):
    validate_request(request)
    kind = request['target']['kind']
    if kind == 'url':
        return preprofile_url(request)
    if kind == 'directory':
        return profile_directory(request)
    return profile_file(request)
