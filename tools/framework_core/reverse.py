"""Optional REA toolchain. Normal project setup never installs it."""
import hashlib
import json
from pathlib import Path
import sys

from .storage import atomic, safe_path


def load_lock():
    return json.loads((Path(__file__).resolve().parent / 'rea-tools.lock.json').read_text(encoding='utf-8'))


def host_name(platform=None):
    name = platform or sys.platform
    if name == 'darwin':
        return 'darwin'
    if name.startswith('linux'):
        return 'linux'
    return ''


def bundle_for(platform=None):
    lock = load_lock()
    host = host_name(platform)
    if host not in lock['bundles']:
        raise ValueError('HOST_UNSUPPORTED')
    return list(lock['bundles'][host])


def pinned_download(spec):
    sha = spec.get('sha256') or ''
    return spec.get('url') and len(sha) == 64


def default_runner(argv, cwd):
    from .process import run
    return run(argv, cwd, 180, {'npm_config_ignore_scripts': 'true'})


def prepare_reverse(root, scope, grants, runner=None, platform=None, present=None):
    """Plan or install the host bundle. Downloads only entries with a checksum."""
    runner = runner or default_runner
    grants = set(grants or ())
    if 'reverse' not in grants:
        return {'status': 'NOT_CONFIGURED', 'reverse': 'NOT_CONFIGURED', 'install': []}
    if 'write' not in grants:
        raise ValueError('CONSENT_REQUIRED')
    names = bundle_for(platform)
    known = set(present or ())
    missing = [name for name in names if name not in known]
    report = {'status': 'READY' if not missing else 'DEPENDENCY_MISSING', 'bundle': names,
              'missing': missing, 'install': [], 'skipped': []}
    if missing and 'reverse-install' not in grants:
        return report
    lock = load_lock()
    for name in missing:
        if name == 'rea-agents':
            installed = install_rea(root, lock['rea-agents'], runner)
        else:
            installed = install_named(root, name, lock['tools'][name], runner)
        if installed['status'] == 'INTEGRITY_UNPINNED':
            report['skipped'].append(name)
            continue
        if installed['status'] != 'INSTALLED':
            report['status'] = installed['status']
            report['failed'] = name
            break
        report['install'].append(name)
    if report.get('failed'):
        pass
    elif report['skipped']:
        report['status'] = 'PROVIDER_MISSING'
        report['missing'] = list(report['skipped'])
    else:
        report['missing'] = []
        report['status'] = 'READY'
    if report['status'] == 'READY' and scope is not None:
        report['observation'] = record_scope(root, scope)
    marker = {'status': report['status'], 'install': report['install'], 'bundle': names}
    atomic(root, '.framework/local-state/reverse-bundle.json', json.dumps(marker, indent=2) + '\n')
    return report


def install_rea(root, spec, runner):
    if not str(spec.get('integrity', '')).startswith('sha512-'):
        return {'status': 'INTEGRITY_UNPINNED'}
    prefix = safe_path(root, '.framework/tools/rea')
    prefix.mkdir(parents=True, exist_ok=True)
    argv = ['npm', 'install', '--prefix', str(prefix), '--ignore-scripts', '--no-audit', '--no-fund',
            '--save-exact', spec['package'] + '@' + spec['version']]
    if any(flag in argv for flag in ('-g', '--global')):
        raise ValueError('REFUSING_GLOBAL_INSTALL')
    result = runner(argv, prefix)
    if result['exit_code']:
        return {'status': 'INSTALL_FAILED'}
    lock_path = prefix / 'package-lock.json'
    if not lock_path.is_file():
        return {'status': 'INTEGRITY_MISMATCH'}
    packages = json.loads(lock_path.read_text(encoding='utf-8')).get('packages', {})
    matches = [value for key, value in packages.items() if key.endswith('node_modules/' + spec['package'])]
    if (len(matches) != 1 or matches[0].get('version') != spec['version']
            or matches[0].get('integrity') != spec['integrity']):
        return {'status': 'INTEGRITY_MISMATCH'}
    return {'status': 'INSTALLED', 'version': spec['version']}


def install_named(root, name, spec, runner):
    if not pinned_download(spec):
        return {'status': 'INTEGRITY_UNPINNED'}
    dest = safe_path(root, '.framework/tools/' + name)
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / 'download'
    result = runner(['download', spec['url'], str(archive)], dest)
    if result['exit_code'] or not archive.is_file():
        return {'status': 'INSTALL_FAILED'}
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != spec['sha256']:
        archive.unlink()
        return {'status': 'INTEGRITY_MISMATCH'}
    return {'status': 'INSTALLED', 'version': spec['version']}


def record_scope(root, scope):
    required = {'id', 'target', 'sha256', 'question', 'action'}
    if not isinstance(scope, dict) or set(scope) != required:
        raise ValueError('INVALID_SCOPE')
    if scope['action'] not in ('static', 'run', 'network'):
        raise ValueError('INVALID_SCOPE')
    if not isinstance(scope['id'], str) or '/' in scope['id'] or scope['id'] in ('.', '..'):
        raise ValueError('INVALID_SCOPE')
    target = Path(scope['target'])
    if not target.is_file() or target.is_symlink():
        raise ValueError('INVALID_SCOPE')
    if hashlib.sha256(target.read_bytes()).hexdigest() != scope['sha256']:
        raise ValueError('STALE_TARGET')
    payload = dict(scope, limitations=['REA observation is not source evidence and runtime_validation is NOT_RUN'])
    atomic(root, '.framework/local-state/rea/' + scope['id'] + '.json', json.dumps(payload, indent=2) + '\n')
    summary = '# Reverse observation %s\n\nQuestion: %s\n\nAction: %s\n\nTarget sha256: `%s`\n\nThis summary does not include decompiler output.\n' % (
        scope['id'], scope['question'], scope['action'], scope['sha256'])
    atomic(root, 'docs/project/reverse/' + scope['id'] + '.md', summary)
    return {'id': scope['id'], 'status': 'RECORDED'}


def reverse_report(root):
    try:
        marker_path = safe_path(root, '.framework/local-state/reverse-bundle.json')
        if not marker_path.is_file():
            return {'status': 'NOT_CONFIGURED'}
        marker = json.loads(marker_path.read_text(encoding='utf-8'))
        folder = safe_path(root, '.framework/local-state/rea')
        if folder.is_dir():
            for path in folder.glob('*.json'):
                recorded = json.loads(path.read_text(encoding='utf-8'))
                target = Path(recorded['target'])
                if (not target.is_file() or target.is_symlink()
                        or hashlib.sha256(target.read_bytes()).hexdigest() != recorded['sha256']):
                    return {'status': 'STALE', 'id': recorded['id']}
        if marker.get('status') != 'READY':
            return {'status': 'PROVIDER_MISSING', 'missing': marker.get('skipped', [])}
        return {'status': 'READY'}
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return {'status': 'PROVIDER_MISSING'}
