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


def is_required(name, lock):
    if name == 'rea-agents':
        return str(lock['rea-agents'].get('integrity', '')).startswith('sha512-')
    return pinned_download(lock['tools'].get(name, {}))


def checksums_for(spec):
    found = set()
    if len(spec.get('sha256') or '') == 64:
        found.add(spec['sha256'])
    for item in (spec.get('artifacts') or {}).values():
        if len(item.get('sha256') or '') == 64:
            found.add(item['sha256'])
    return found


def detect_installed(root, names, lock):
    found = set()
    lock_path = safe_path(root, '.framework/tools/rea/package-lock.json')
    if lock_path.is_file():
        packages = json.loads(lock_path.read_text(encoding='utf-8')).get('packages', {})
        spec = lock['rea-agents']
        matches = [value for key, value in packages.items() if key.endswith('node_modules/' + spec['package'])]
        if (len(matches) == 1 and matches[0].get('version') == spec['version']
                and matches[0].get('integrity') == spec['integrity']):
            found.add('rea-agents')
    for name in names:
        if name == 'rea-agents':
            continue
        marker = safe_path(root, '.framework/tools/' + name + '/.sha256')
        if marker.is_file() and marker.read_text(encoding='utf-8').strip() in checksums_for(lock['tools'].get(name, {})):
            found.add(name)
    return found


def machine_name(machine=None):
    name = (machine or __import__('platform').machine()).lower()
    if name in ('arm64', 'aarch64'):
        return 'arm64'
    if name in ('x86_64', 'amd64'):
        return 'x64'
    return name


def prepare_reverse(root, scope, grants, runner=None, platform=None, present=None, opener=None, machine=None):
    """Install required tools once, then record a static observation.

    Tools without a checksum are reported and do not block the observation.
    run and network actions are not executed.
    """
    runner = runner or default_runner
    grants = set(grants or ())
    if 'reverse' not in grants:
        return {'status': 'NOT_CONFIGURED', 'reverse': 'NOT_CONFIGURED', 'install': []}
    if 'write' not in grants:
        raise ValueError('CONSENT_REQUIRED')
    lock = load_lock()
    names = bundle_for(platform)
    known = set(present) if present is not None else detect_installed(root, names, lock)
    host = host_name(platform)
    machine = machine_name(machine)
    required = [name for name in names if is_required(name, lock)]
    optional = [name for name in names if name not in required]
    missing_required = [name for name in required if name not in known]
    skipped = []
    extra = []
    for name in optional:
        if name in known:
            continue
        spec = lock['tools'].get(name, {})
        if is_required(name, lock) or artifact_ready(spec, host, machine):
            extra.append(name)
        else:
            skipped.append(name)
    report = {'status': 'READY', 'bundle': names, 'missing': missing_required, 'install': [], 'skipped': skipped}
    if missing_required and 'reverse-install' not in grants:
        report['status'] = 'DEPENDENCY_MISSING'
        return report
    for name in missing_required + extra:
        if 'reverse-install' not in grants:
            break
        if name == 'rea-agents':
            installed = install_rea(root, lock['rea-agents'], runner)
        else:
            installed = install_named(root, name, lock['tools'][name], host, machine, opener)
        if installed['status'] != 'INSTALLED':
            if name in required:
                report['status'] = installed['status']
                report['failed'] = name
                break
            report['skipped'].append(name)
            continue
        report['install'].append(name)
        known.add(name)
    if not report.get('failed'):
        report['missing'] = [name for name in required if name not in known]
        report['status'] = 'READY' if not report['missing'] else 'PROVIDER_MISSING'
    if report['status'] == 'READY' and scope is not None:
        report['observation'] = record_scope(root, scope, runner)
    marker = {'status': report['status'], 'install': report['install'], 'bundle': names,
              'skipped': report['skipped']}
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


def artifact_ready(spec, platform, machine):
    from .reverse_downloads import artifact_for
    return artifact_for(spec, platform, machine) is not None


def install_named(root, name, spec, platform, machine, opener=None):
    from .reverse_downloads import IntegrityError, install_archive
    try:
        return install_archive(root, name, spec, platform, machine, opener)
    except IntegrityError:
        return {'status': 'INTEGRITY_MISMATCH'}
    except (OSError, ValueError):
        return {'status': 'INSTALL_FAILED'}


def record_scope(root, scope, runner):
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
    if scope['action'] == 'static':
        rea = safe_path(root, '.framework/tools/rea/node_modules/.bin/rea')
        command = [str(rea) if rea.is_file() else 'rea', 'analyze', str(target), '--json']
        result = runner(command, root)
        observed = 'RECORDED' if result.get('exit_code', 1) == 0 else 'FAILED'
    else:
        result = {'exit_code': 0, 'stdout': ''}
        command = []
        observed = 'NOT_EXECUTED'
    payload = {'id': scope['id'], 'target': scope['target'], 'sha256': scope['sha256'],
               'question': scope['question'], 'action': scope['action'], 'analysis': observed,
               'exit_code': result.get('exit_code', 1),
               'limitations': ['REA observation is not source evidence and runtime_validation is NOT_RUN',
                               'run and network actions are not executed by the shell']}
    if result.get('stdout'):
        payload['raw_sha256'] = hashlib.sha256(result['stdout'].encode()).hexdigest()
    atomic(root, '.framework/local-state/rea/' + scope['id'] + '.json', json.dumps(payload, indent=2) + '\n')
    summary = '\n'.join([
        '# Reverse observation %s' % scope['id'], '',
        'Question: %s' % scope['question'], '',
        'Requested action: %s' % scope['action'], '',
        'Analysis: %s' % observed, '',
        'Target sha256: `%s`' % scope['sha256'], '',
        'Raw REA output stays in local-state and is not copied here.', '',
        'Continue with the normal design, specification, plan, implementation and verification workflow.', ''])
    atomic(root, 'docs/project/reverse/' + scope['id'] + '.md', summary)
    return {'id': scope['id'], 'status': observed, 'command': command}


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
