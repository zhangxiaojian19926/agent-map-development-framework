"""Bounded URL snapshots and passive, offline web-resource profiling."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import tempfile
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .reverse_request import canonical, origin, private_host, validate_network, validate_request
from .reverse_v2 import sha_text
from .storage import atomic, safe_path


SCHEMA = 'web-snapshot/v1'
MAX_REDIRECTS = 5


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for attribute in ('src', 'href', 'poster'):
            if values.get(attribute):
                self.items.append({'tag': tag, 'attribute': attribute, 'url': values[attribute]})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def default_opener(request, timeout):
    return build_opener(NoRedirect()).open(request, timeout=timeout)


def snapshot_root(request_id, snapshot_sha256):
    return '.framework/local-state/reverse/auto/' + request_id + '/snapshots/' + snapshot_sha256


def write_bytes(root, rel, content):
    path = safe_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, safe_path(root, rel))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def resolved_addresses(host, port, resolver=None):
    resolve = resolver or socket.getaddrinfo
    try:
        answers = resolve(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError('DNS_FAILED') from exc
    addresses = {item[4][0] for item in answers}
    if not addresses:
        raise ValueError('DNS_FAILED')
    return addresses


def check_url(value, network, resolver=None):
    parsed = urlsplit(value)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname
            or parsed.username or parsed.password):
        raise ValueError('URL_OUT_OF_SCOPE')
    try:
        normalized = origin(value, allow_path=True)
    except (ValueError, TypeError) as exc:
        raise ValueError('URL_OUT_OF_SCOPE') from exc
    if normalized not in network['origins']:
        raise ValueError('ORIGIN_OUT_OF_SCOPE')
    if parsed.scheme == 'http' and not network['allow_http']:
        raise ValueError('HTTP_NOT_ALLOWED')
    addresses = resolved_addresses(parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80), resolver)
    if not network['allow_private']:
        if private_host(parsed.hostname):
            raise ValueError('PRIVATE_NETWORK')
        for address in addresses:
            if not ipaddress.ip_address(address).is_global:
                raise ValueError('PRIVATE_NETWORK')
    return normalized


def response_meta(response, final_url):
    headers = getattr(response, 'headers', {}) or {}
    status = getattr(response, 'status', None)
    if status is None:
        status = response.getcode()
    return {'status': status, 'final_url': final_url,
            'content_type': headers.get('Content-Type', ''),
            'content_length': headers.get('Content-Length')}


def fetch_one(url, network, opener, resolver, budget):
    current = url
    for redirects in range(MAX_REDIRECTS + 1):
        if budget['resources'] >= network['max_resources']:
            raise ValueError('RESOURCE_LIMIT')
        check_url(current, network, resolver)
        request = Request(current, method='GET', headers={'User-Agent': 'ProjectReverseSnapshot/1'})
        try:
            response = opener(request, timeout=network['timeout'])
        except TimeoutError as exc:
            raise ValueError('NETWORK_TIMEOUT') from exc
        except Exception as exc:
            from urllib.error import URLError
            if isinstance(exc, URLError) and isinstance(exc.reason, TimeoutError):
                raise ValueError('NETWORK_TIMEOUT') from exc
            if isinstance(exc, URLError):
                raise ValueError('NETWORK_FAILED') from exc
            raise
        with response:
            final_url = response.geturl() or current
            check_url(final_url, network, resolver)
            meta = response_meta(response, final_url)
            status = meta['status'] or 0
            if 300 <= status < 400:
                if redirects == MAX_REDIRECTS:
                    raise ValueError('REDIRECT_LIMIT')
                location = response.headers.get('Location')
                if not location:
                    raise ValueError('REDIRECT_INVALID')
                current = urljoin(final_url, location)
                check_url(current, network, resolver)
                continue
            if status != 200:
                raise ValueError('HTTP_ERROR')
            if meta['content_length']:
                try:
                    declared = int(meta['content_length'])
                except ValueError as exc:
                    raise ValueError('INVALID_RESPONSE') from exc
                if declared < 0 or declared > budget['remaining']:
                    raise ValueError('RESOURCE_LIMIT')
            content = response.read(budget['remaining'] + 1)
            if len(content) > budget['remaining']:
                raise ValueError('RESOURCE_LIMIT')
            budget['remaining'] -= len(content)
            budget['resources'] += 1
            if budget['resources'] > network['max_resources']:
                raise ValueError('RESOURCE_LIMIT')
            return {'url': current, 'content': content, 'response': meta}
    raise ValueError('REDIRECT_LIMIT')


def parse_references(content):
    parser = References()
    parser.feed(content.decode('utf-8', errors='replace'))
    parser.close()
    return parser.items


def snapshot_identity(original_url, resources):
    core = {'original_url': original_url,
            'resources': [{'url': item['url'], 'final_url': item['response']['final_url'],
                           'sha256': hashlib.sha256(item['content']).hexdigest(),
                           'size': len(item['content']), 'response': item['response']}
                          for item in resources]}
    return sha_text(canonical(core)), core


def fetch_snapshot(root, request, grants, opener=None, resolver=None, now=None):
    validate_request(request)
    if request['target']['kind'] != 'url':
        raise ValueError('INVALID_TARGET')
    if 'web-fetch' not in grants:
        return {'status': 'NOT_AUTHORIZED', 'required': ['web-fetch']}
    network = validate_network(request)
    open_url = opener or default_opener
    budget = {'remaining': network['max_bytes'], 'resources': 0}
    original = request['target']['url']
    resources = [fetch_one(original, network, open_url, resolver, budget)]
    references = parse_references(resources[0]['content'])
    seen = {resources[0]['url']}
    for reference in references:
        value = urljoin(resources[0]['response']['final_url'], reference['url'])
        if urlsplit(value).scheme not in ('http', 'https') or value in seen:
            continue
        check_url(value, network, resolver)
        seen.add(value)
        item = fetch_one(value, network, open_url, resolver, budget)
        item['reference'] = reference
        resources.append(item)
    root_sha256, core = snapshot_identity(original, resources)
    base = snapshot_root(request['id'], root_sha256)
    manifest_path = base + '/snapshot-manifest.json'
    if safe_path(root, manifest_path).is_file():
        return load_snapshot(root, request['id'], root_sha256)
    entries = []
    for index, item in enumerate(resources):
        digest = hashlib.sha256(item['content']).hexdigest()
        rel = 'document.html' if index == 0 else 'resources/' + digest + '.bin'
        write_bytes(root, base + '/' + rel, item['content'])
        entry = {'path': rel, 'url': item['url'], 'final_url': item['response']['final_url'],
                 'sha256': digest, 'size': len(item['content']), 'response': item['response']}
        if 'reference' in item:
            entry['reference'] = item['reference']
        entries.append(entry)
    manifest = {'schema': SCHEMA, 'id': request['id'], 'snapshot_sha256': root_sha256,
                'original_url': original, 'fetched_at': now or datetime.now(timezone.utc).isoformat(),
                'network': network, 'resources': entries}
    actual = snapshot_identity(original, [
        {'url': item['url'], 'content': item['content'], 'response': item['response']}
        for item in resources])[0]
    if actual != root_sha256:
        raise ValueError('SNAPSHOT_CONFLICT')
    atomic(root, manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    return manifest


def load_snapshot(root, request_id, snapshot_sha256):
    base = snapshot_root(request_id, snapshot_sha256)
    path = safe_path(root, base + '/snapshot-manifest.json')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('schema') != SCHEMA or manifest.get('snapshot_sha256') != snapshot_sha256:
        raise ValueError('INVALID_SNAPSHOT')
    resources = []
    for item in manifest['resources']:
        content = safe_path(root, base + '/' + item['path']).read_bytes()
        if hashlib.sha256(content).hexdigest() != item['sha256'] or len(content) != item['size']:
            raise ValueError('STALE_SNAPSHOT')
        resources.append({'url': item['url'], 'content': content, 'response': item['response']})
    expected, unused = snapshot_identity(manifest['original_url'], resources)
    del unused
    if expected != snapshot_sha256:
        raise ValueError('STALE_SNAPSHOT')
    return manifest


def snapshot_bytes(root, manifest):
    base = snapshot_root(manifest['id'], manifest['snapshot_sha256'])
    result = []
    for item in manifest['resources']:
        content = safe_path(root, base + '/' + item['path']).read_bytes()
        if hashlib.sha256(content).hexdigest() != item['sha256']:
            raise ValueError('STALE_SNAPSHOT')
        result.append((item, content))
    return result


def profile_snapshot(root, request, manifest):
    if manifest.get('id') != request['id'] or manifest.get('original_url') != request['target'].get('url'):
        raise ValueError('SNAPSHOT_TARGET_MISMATCH')
    capabilities = ['web.static.resources']
    wasm = False
    for item, content in snapshot_bytes(root, manifest):
        if content.startswith(b'\x00asm') or urlsplit(item['url']).path.lower().endswith('.wasm'):
            wasm = True
    if wasm:
        capabilities.append('wasm.static')
    if request['intent'] == 'dynamic' or any(item['action'] == 'browser' for item in request['observations']):
        capabilities.append('web.dynamic.dom')
    if any(item['action'] == 'network' for item in request['observations']):
        capabilities.append('web.dynamic.network')
    return {'status': 'PROFILED', 'kind': 'web_snapshot', 'format': 'HTML',
            'target_sha256': manifest['snapshot_sha256'], 'snapshot_sha256': manifest['snapshot_sha256'],
            'capabilities': capabilities, 'facts': ['snapshot:' + str(len(manifest['resources'])),
                                                   'wasm:' + str(wasm).lower()]}


def static_resources(root, manifest):
    scripts, styles, wasm, references = [], [], [], []
    for item, content in snapshot_bytes(root, manifest):
        url = item['final_url']
        if content.startswith(b'\x00asm') or urlsplit(url).path.lower().endswith('.wasm'):
            wasm.append(url)
        if 'html' in item['response'].get('content_type', '').lower() or item['path'] == 'document.html':
            for reference in parse_references(content):
                resolved = urljoin(url, reference['url'])
                references.append({'source': url, 'target': resolved,
                                   'tag': reference['tag'], 'attribute': reference['attribute']})
                if reference['tag'] == 'script':
                    scripts.append(resolved)
                if reference['tag'] == 'link':
                    styles.append(resolved)
    return {'snapshot_sha256': manifest['snapshot_sha256'], 'scripts': scripts,
            'styles': styles, 'wasm': wasm, 'references': references,
            'resource_count': len(manifest['resources'])}


def static_local(target):
    """Passively inspect a local HTML file or an already hash-bound snapshot directory."""
    target = Path(target)
    files = [target] if target.is_file() else sorted(path for path in target.rglob('*') if path.is_file())
    scripts, styles, wasm, references = [], [], [], []
    for path in files:
        if path.is_symlink():
            raise ValueError('STALE_TARGET')
        content = path.read_bytes()
        name = path.as_posix()
        if content.startswith(b'\x00asm') or path.suffix.lower() == '.wasm':
            wasm.append(name)
        if path.suffix.lower() not in ('.html', '.htm') and not (
                path.is_file() and (b'<html' in content[:8192].lower() or b'<!doctype html' in content[:8192].lower())):
            continue
        for reference in parse_references(content):
            references.append({'source': name, 'target': reference['url'],
                               'tag': reference['tag'], 'attribute': reference['attribute']})
            if reference['tag'] == 'script':
                scripts.append(reference['url'])
            if reference['tag'] == 'link':
                styles.append(reference['url'])
    return {'snapshot_sha256': None, 'scripts': scripts, 'styles': styles, 'wasm': wasm,
            'references': references, 'resource_count': len(files)}
