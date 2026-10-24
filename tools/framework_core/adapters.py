"""Version-bounded external integrations. No global installation or configuration."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .config import encoded, digest
from .process import run
from .storage import safe_path, owned_changes, apply_files
from .storage import read_json, fingerprint

CG_ENV = {'CODEGRAPH_NO_DOWNLOAD': '1', 'CODEGRAPH_NO_WATCH': '0',
          'CODEGRAPH_FORCE_WATCH': '1', 'CODEGRAPH_TELEMETRY': '0', 'DO_NOT_TRACK': '1'}
LOCAL_BIN = '.framework/tools/codegraph/node_modules/.bin/codegraph'


def codegraph_lock():
    return json.loads((Path(__file__).resolve().parent / 'codegraph.lock.json').read_text())


def supported_version(text):
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', text or '')
    return bool(match) and int(match.group(1)) == 1


def installed_metadata(root, spec):
    lock_path = safe_path(root, '.framework/tools/codegraph/package-lock.json')
    if not lock_path.is_file():
        return None, None
    entry = json.loads(lock_path.read_text()).get('packages', {}).get('node_modules/' + spec['package'], {})
    return entry.get('version'), entry.get('integrity')


def install_codegraph(root, runner):
    """Install the locked CLI under the target project. Never a global prefix."""
    node = runner(['node', '--version'], root, 15, {})
    if node['exit_code']:
        return {'status': 'NODE_MISSING'}
    npm = runner(['npm', '--version'], root, 15, {})
    if npm['exit_code']:
        return {'status': 'NODE_MISSING'}
    spec = codegraph_lock()
    if spec['package'].startswith('-') or spec['version'].startswith('-') or not spec['integrity'].startswith('sha512-'):
        raise ValueError('INVALID_LOCK')
    prefix = safe_path(root, '.framework/tools/codegraph')
    prefix.mkdir(parents=True, exist_ok=True)
    argv = ['npm', 'install', '--prefix', str(prefix), '--ignore-scripts', '--no-audit', '--no-fund',
            '--save-exact', spec['package'] + '@' + spec['version']]
    if any(flag in argv for flag in ('-g', '--global')):
        raise ValueError('REFUSING_GLOBAL_INSTALL')
    result = runner(argv, prefix, 180, {'npm_config_ignore_scripts': 'true'})
    if result['exit_code']:
        return {'status': 'INSTALL_FAILED', 'exit_code': result['exit_code']}
    version, integrity = installed_metadata(root, spec)
    if version != spec['version'] or integrity != spec['integrity']:
        return {'status': 'INTEGRITY_MISMATCH', 'version': version}
    binary = safe_path(root, LOCAL_BIN)
    if not binary.is_file():
        return {'status': 'INSTALL_FAILED', 'reason': 'BINARY_MISSING'}
    probed = runner([str(binary), '--version'], root, 15, CG_ENV)
    if probed['exit_code'] or not supported_version(probed['stdout']):
        return {'status': 'UNSUPPORTED_VERSION', 'version': probed['stdout'].strip()}
    return {'status': 'READY', 'bin': str(binary), 'version': probed['stdout'].strip(), 'installed': True}


def resolve_codegraph(root, consent, runner):
    """Use a compatible PATH or project CLI. Download only with index-install."""
    unsupported = None
    local = safe_path(root, LOCAL_BIN)
    candidates = ['codegraph'] + ([str(local)] if local.is_file() else [])
    for binary in candidates:
        version = runner([binary, '--version'], root, 15, CG_ENV)
        if version['exit_code'] == 0 and supported_version(version['stdout']):
            return {'status': 'READY', 'bin': binary, 'version': version['stdout'].strip()}
        if version['exit_code'] == 0 and version['stdout'].strip():
            unsupported = version['stdout'].strip()
    if 'index-install' in consent:
        return install_codegraph(root, runner)
    if unsupported:
        return {'status': 'UNSUPPORTED_VERSION', 'version': unsupported}
    return {'status': 'DEPENDENCY_MISSING', 'required': ['index-install']}


def ensure_openspec(root, consent, runner=run):
    if 'openspec' not in consent:
        raise ValueError('CONSENT_REQUIRED: openspec')
    safe_path(root, 'openspec/config.yaml')
    if not (root / 'openspec/config.yaml').is_file():
        result = runner(['openspec', 'init', '--tools', 'none', '--language', 'zh',
                         '--no-animation', '--no-copilot-cloud', str(root)], root, 60,
                        {'OPENSPEC_TELEMETRY': '0', 'DO_NOT_TRACK': '1'})
        if result['exit_code']:
            raise ValueError('OPENSPEC_INIT_FAILED')
    context = runner(['openspec', 'context', '--json'], root, 30, {'OPENSPEC_TELEMETRY': '0'})
    if context['exit_code'] or Path(json.loads(context['stdout'])['root']['path']).resolve() != root.resolve():
        raise ValueError('ROOT_MISMATCH')
    return json.loads(context['stdout'])


def validate_clone_url(url, consent):
    if not url or url.startswith('-') or '::' in url or any(c in url for c in '\n\r\x00'):
        raise ValueError('INVALID_CLONE_URL')
    parsed = urlsplit(url)
    if parsed.password or (parsed.scheme == 'https' and parsed.username) or parsed.query or parsed.fragment:
        raise ValueError('CREDENTIAL_OR_QUERY_IN_URL')
    if parsed.scheme in ('https', 'ssh') and parsed.hostname:
        return url
    if re.fullmatch(r'[\w.-]+@[\w.-]+:[\w./-]+', url):
        return url
    if 'local-clone' in consent and Path(url).is_absolute() and Path(url).is_dir():
        return url
    raise ValueError('UNSUPPORTED_CLONE_PROTOCOL')


def clone(root, url, rel, ref, consent, runner=run):
    if not {'clone', 'write'} <= consent:
        raise ValueError('CONSENT_REQUIRED: clone/write')
    validate_clone_url(url, consent)
    path = safe_path(root, rel)
    if path.exists():
        raise ValueError('CONFLICT: clone target exists')
    path.parent.mkdir(parents=True, exist_ok=True)
    argv = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'protocol.ext.allow=never',
            '-c', 'protocol.file.allow=' + ('always' if 'local-clone' in consent else 'never'),
            'clone', '--template=', '--no-recurse-submodules']
    if ref:
        if ref.startswith('-'):
            raise ValueError('INVALID_REF')
        argv += ['--branch', ref]
    return runner(argv + ['--', url, str(path)], root, 300,
                  {'GIT_TERMINAL_PROMPT': '0', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'})


def ensure_index(root, index, consent, runner=run):
    result = {'id': index['id'], 'status': 'NOT_APPLICABLE', 'verified': False,
              'source_digest': digest(index['sources']), 'calls': [], 'adapter_revision': 'scope-v4'}
    if not index['sources']:
        return result
    if 'index' not in consent:
        result['status'] = 'CONSENT_REQUIRED'
        return result
    path = safe_path(root, index['root'])
    resolved = resolve_codegraph(root, consent, runner)
    if resolved['status'] != 'READY':
        result['status'] = resolved['status']
        result['version'] = resolved.get('version', '')
        result['required'] = resolved.get('required', [])
        return result
    binary = resolved['bin']
    result['version'] = resolved['version']
    result['installed'] = bool(resolved.get('installed'))
    # Protect the exclusion file rather than modifying unknown user policy.
    allowed = {safe_path(root, rel).relative_to(path).as_posix() for rel in index['sources']}
    # CodeGraph 1.6.0 uses node-ignore: default-deny, then exact ancestor/file
    # exceptions. New unapproved siblings stay excluded, even before refresh.
    ancestors = {p.as_posix() for rel in allowed for p in Path(rel).parents if str(p) != '.'}
    def literal(value):
        if value != value.strip() or any(c in value for c in '\n\r\\'):
            raise ValueError('UNSUPPORTED_INDEX_FILENAME')
        return re.sub(r'([*?\[\]!#])', r'\\\1', value)
    exclusions = ['**']
    exclusions += ['!/' + literal(p) + '/' for p in sorted(ancestors, key=lambda p: (p.count('/'), p))]
    exclusions += ['!/' + literal(p) for p in sorted(allowed)]
    config_path = path / 'codegraph.json'
    rel = config_path.relative_to(Path(root).resolve()).as_posix()
    safe_path(root, rel)
    if config_path.exists():
        existing = json.loads(config_path.read_text())
        owned = read_json(root, '.framework/local-state/owned.json', {})
        if owned.get(rel) == fingerprint(config_path):
            apply_files(root, owned_changes(root, {rel: encoded({'exclude': exclusions})}), 'index-config')
        elif existing.get('exclude') != exclusions:
            result['status'] = 'CONFIG_CONFLICT'
            return result
    else:
        apply_files(root, owned_changes(root, {rel: encoded({'exclude': exclusions})}), 'index-config')
    safe_path(root, index['root'] + '/.codegraph')
    action = 'sync' if (path / '.codegraph').is_dir() else 'init'
    command = [binary, action, str(path)]
    # No --yes: the audited FORCE_WATCH policy suppresses hook fallback on this version.
    step = runner(command, path, 300, CG_ENV)
    result['calls'].append(dict(command=command, **step))
    if step['exit_code'] != 0:
        result['status'] = 'INDEX_FAILED'
        return result
    symbol = None
    for rel in sorted(index['sources']):
        text = safe_path(root, rel).read_text(errors='replace')
        match = re.search(r'(?:def|class|function|fn|func)\s+(\w+)', text)
        if match:
            symbol = match.group(1)
            break
    if not symbol:
        result['status'] = 'QUERY_NOT_VERIFIED'
        return result
    for argv in ([binary, 'status', str(path), '--json'],
                 [binary, 'query', symbol, '--path', str(path), '--json']):
        check = runner(argv, path, 30, CG_ENV)
        result['calls'].append(dict(command=argv, **check))
        if check['exit_code'] != 0:
            result['status'] = 'QUERY_FAILED'
            return result
    try:
        status = json.loads(result['calls'][-2]['stdout'])
        nodes = json.loads(check['stdout'])
        status_ok = (status.get('initialized') is True and status.get('fileCount', 0) > 0 and
                     Path(status.get('projectPath', '')).resolve() == path.resolve() and
                     status.get('index', {}).get('state') == 'complete')
        result['verified'] = status_ok and isinstance(nodes, list) and any(
            isinstance(n, dict) and n.get('node', {}).get('name') == symbol and
            n.get('node', {}).get('filePath') in allowed for n in nodes)
    except (ValueError, TypeError, AttributeError):
        result['verified'] = False
    result['status'] = 'READY' if result['verified'] else 'EMPTY_QUERY'
    result['query_symbol'] = symbol
    result['excluded'] = exclusions
    return result


