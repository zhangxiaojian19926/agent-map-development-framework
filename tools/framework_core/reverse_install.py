"""Transactional, project-local reverse tool installation and health receipts."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from .storage import atomic, safe_path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def component(value, label='tool'):
    if not isinstance(value, str) or not value or value in ('.', '..') or '/' in value or '\\' in value:
        raise ValueError('INVALID_' + label.upper())
    return value


def final_path(root, name, version):
    component(name)
    component(version, 'version')
    return safe_path(root, '.framework/tools/' + name + '/' + version)


def state_path(root, name):
    component(name)
    return '.framework/local-state/reverse/installs/' + name + '.json'


@contextmanager
def tool_lock(root, name):
    component(name)
    rel = '.framework/local-state/reverse/install-locks/' + name + '.lock'
    path = safe_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError('LOCKED: ' + name)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


def default_runner(argv, cwd):
    from .process import run
    cache = safe_path(cwd, '.framework/cache/npm') if not Path(cwd).name.startswith('payload') else None
    env = {'npm_config_ignore_scripts': 'true'}
    if cache is not None:
        env['npm_config_cache'] = str(cache)
    return run(argv, cwd, 60, env)


def receipt_for(name, spec, platform, machine, artifact_sha256, entrypoint):
    receipt = {
        'schema': 'reverse-install-receipt/v1', 'name': name, 'version': spec['version'],
        'platform': platform, 'machine': machine, 'artifact_sha256': artifact_sha256,
        'install_path': '.framework/tools/' + name + '/' + spec['version'],
        'entrypoint': entrypoint, 'status': 'READY'
    }
    if 'probe_expect' in spec:
        receipt['probe_expect'] = spec['probe_expect']
    return receipt


def check_tree(tree, receipt, runner=None, probe=False):
    entrypoint = receipt.get('entrypoint')
    binary = None
    if entrypoint:
        rel = Path(entrypoint)
        if rel.is_absolute() or '..' in rel.parts:
            return {'status': 'CORRUPT', 'reason': 'INVALID_ENTRYPOINT'}
        binary = tree / rel
        if binary.is_symlink():
            resolved = binary.resolve()
            internal_npm_link = (entrypoint.startswith('node_modules/.bin/')
                                 and resolved.is_relative_to(tree.resolve()) and resolved.is_file())
            if not internal_npm_link:
                return {'status': 'CORRUPT', 'reason': 'BINARY_MISSING'}
        elif not binary.is_file():
            return {'status': 'CORRUPT', 'reason': 'BINARY_MISSING'}
        if probe:
            run = runner or default_runner
            result = run([str(binary), '--version'], tree)
            if result.get('exit_code') or result.get('timed_out'):
                return {'status': 'CORRUPT', 'reason': 'PROBE_FAILED', 'bin': str(binary)}
            output = (result.get('stdout') or '') + (result.get('stderr') or '')
            if receipt.get('probe_expect', receipt['version']) not in output:
                return {'status': 'UNSUPPORTED_VERSION', 'version': output.strip(),
                        'bin': str(binary)}
    return {'status': 'READY', 'bin': str(binary) if binary else None,
            'version': receipt['version']}


def inspect_installed(root, name, spec, platform=None, machine=None, runner=None, probe=False):
    """Inspect only owned receipts; probing is opt-in and never used by doctor."""
    if isinstance(spec, str):
        spec = {'version': spec}
    version = spec['version']
    final = final_path(root, name, version)
    if not final.is_dir():
        return {'status': 'MISSING', 'version': version}
    receipt_path = final / 'install-receipt.json'
    state = safe_path(root, state_path(root, name))
    if not receipt_path.is_file() or not state.is_file():
        return {'status': 'CORRUPT', 'reason': 'RECEIPT_MISSING', 'version': version}
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        marker = json.loads(state.read_text(encoding='utf-8'))
        actual_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        expected = receipt_for(name, spec, receipt['platform'], receipt['machine'],
                               receipt['artifact_sha256'], receipt.get('entrypoint'))
        if receipt != expected or marker.get('receipt_sha256') != actual_hash:
            return {'status': 'CORRUPT', 'reason': 'RECEIPT_MISMATCH', 'version': version}
        if platform is not None and receipt['platform'] != platform:
            return {'status': 'CORRUPT', 'reason': 'PLATFORM_MISMATCH', 'version': version}
        if machine is not None and receipt['machine'] != machine:
            return {'status': 'CORRUPT', 'reason': 'MACHINE_MISMATCH', 'version': version}
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return {'status': 'CORRUPT', 'reason': 'RECEIPT_INVALID', 'version': version}
    result = check_tree(final, receipt, runner, probe)
    result.update({'receipt': receipt, 'install_path': str(final)})
    return result


def activate(root, name, spec, staging, receipt, repair=False):
    final = final_path(root, name, spec['version'])
    final.parent.mkdir(parents=True, exist_ok=True)
    previous = staging.parent / 'previous'
    had_previous = final.exists()
    if had_previous:
        if not repair:
            return {'status': 'CONFLICT', 'version': spec['version']}
        os.replace(final, previous)
    try:
        os.replace(staging, final)
        marker = {'schema': 'reverse-install-state/v1', 'name': name, 'version': spec['version'],
                  'receipt_sha256': hashlib.sha256((final / 'install-receipt.json').read_bytes()).hexdigest()}
        atomic(root, state_path(root, name), encoded(marker))
    except Exception:
        if final.exists() and had_previous:
            shutil.rmtree(final)
        if previous.exists():
            os.replace(previous, final)
        raise
    return {'status': 'INSTALLED', 'action': 'REPAIR' if had_previous else 'INSTALL',
            'version': spec['version'], 'install_path': str(final)}


def workspace(root, name):
    base = safe_path(root, '.framework/tmp/install')
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=component(name) + '-' + uuid.uuid4().hex[:8] + '-', dir=base))


def install_archive(root, name, spec, platform, machine, opener=None, runner=None,
                    repair=False, max_bytes=512 * 1024 * 1024, max_files=10000,
                    max_extract_bytes=1024 * 1024 * 1024):
    from .reverse_downloads import IntegrityError, artifact_for, extract_archive, fetch_verified
    chosen = artifact_for(spec, platform, machine)
    if chosen is None:
        return {'status': 'INTEGRITY_UNPINNED', 'version': spec.get('version', '')}
    run = runner or default_runner
    try:
        with tool_lock(root, name):
            existing = inspect_installed(root, name, spec, platform, machine, run, probe=True)
            if (existing['status'] == 'READY'
                    and existing['receipt']['artifact_sha256'] == chosen['sha256']):
                return {'status': 'INSTALLED', 'action': 'REUSE', 'version': spec['version'],
                        'install_path': existing['install_path'], 'bin': existing.get('bin')}
            if existing['status'] == 'READY':
                existing['status'] = 'CORRUPT'
            final = final_path(root, name, spec['version'])
            if final.exists() and not repair:
                status = 'CORRUPT' if (final / 'install-receipt.json').exists() else 'CONFLICT'
                return {'status': status, 'version': spec['version']}
            work = workspace(root, name)
            try:
                staging = work / 'payload'
                staging.mkdir()
                archive = work / 'artifact'
                fetch_verified(chosen['url'], archive, chosen['sha256'], opener, max_bytes=max_bytes)
                kind = chosen.get('kind', 'zip')
                if kind == 'file':
                    os.replace(archive, staging / spec.get('filename', name))
                else:
                    extract_archive(archive, kind, staging, max_files=max_files,
                                    max_extract_bytes=max_extract_bytes)
                entrypoint = spec.get('entrypoint')
                if entrypoint:
                    candidate = staging / entrypoint
                    if candidate.is_file():
                        candidate.chmod(candidate.stat().st_mode | 0o100)
                receipt = receipt_for(name, spec, platform, machine, chosen['sha256'], entrypoint)
                healthy = check_tree(staging, receipt, run,
                                     probe=bool(entrypoint) and spec.get('probe', True))
                if healthy['status'] != 'READY':
                    return {'status': 'INSTALL_FAILED' if healthy['status'] == 'CORRUPT' else healthy['status'],
                            'reason': healthy.get('reason'), 'version': spec['version']}
                (staging / 'install-receipt.json').write_text(encoded(receipt), encoding='utf-8')
                return activate(root, name, spec, staging, receipt, repair)
            finally:
                shutil.rmtree(work, ignore_errors=True)
    except ValueError as exc:
        if str(exc).startswith('LOCKED'):
            return {'status': 'LOCKED', 'version': spec['version']}
        raise


def npm_metadata(prefix, spec):
    path = prefix / 'package-lock.json'
    if not path.is_file():
        return None
    packages = json.loads(path.read_text(encoding='utf-8')).get('packages', {})
    matches = [value for key, value in packages.items() if key.endswith('node_modules/' + spec['package'])]
    if len(matches) != 1:
        return None
    return matches[0]


def install_npm(root, name, spec, runner=None, repair=False):
    if not str(spec.get('integrity', '')).startswith('sha512-'):
        return {'status': 'INTEGRITY_UNPINNED', 'version': spec.get('version', '')}
    run = runner or (lambda argv, cwd: default_runner(argv, Path(root)))
    try:
        with tool_lock(root, name):
            existing = inspect_installed(root, name, spec, runner=run, probe=True)
            if (existing['status'] == 'READY'
                    and existing['receipt']['artifact_sha256'] == spec['integrity']):
                return {'status': 'INSTALLED', 'action': 'REUSE', 'version': spec['version'],
                        'install_path': existing['install_path'], 'bin': existing.get('bin')}
            if existing['status'] == 'READY':
                existing['status'] = 'CORRUPT'
            final = final_path(root, name, spec['version'])
            if final.exists() and not repair:
                return {'status': 'CORRUPT' if (final / 'install-receipt.json').exists() else 'CONFLICT',
                        'version': spec['version']}
            for runtime in ('node', 'npm'):
                result = run([runtime, '--version'], root)
                if result.get('exit_code'):
                    return {'status': 'NODE_MISSING', 'version': spec['version']}
            work = workspace(root, name)
            try:
                staging = work / 'payload'
                staging.mkdir()
                cache = safe_path(root, '.framework/cache/npm')
                argv = ['npm', 'install', '--prefix', str(staging), '--ignore-scripts',
                        '--cache', str(cache), '--no-audit', '--no-fund', '--save-exact',
                        spec['package'] + '@' + spec['version']]
                result = run(argv, staging)
                if result.get('exit_code'):
                    return {'status': 'INSTALL_FAILED', 'version': spec['version']}
                metadata = npm_metadata(staging, spec)
                if not metadata or metadata.get('version') != spec['version'] or metadata.get('integrity') != spec['integrity']:
                    return {'status': 'INTEGRITY_MISMATCH', 'version': spec['version']}
                entrypoint = 'node_modules/.bin/rea' if spec['package'] == 'rea-agents' else 'node_modules/.bin/' + spec['package']
                binary = staging / entrypoint
                if binary.is_file():
                    binary.chmod(binary.stat().st_mode | 0o100)
                receipt = receipt_for(name, spec, 'any', 'any', spec['integrity'], entrypoint)
                healthy = check_tree(staging, receipt, run, probe=True)
                if healthy['status'] != 'READY':
                    return {'status': 'INSTALL_FAILED' if healthy['status'] == 'CORRUPT' else healthy['status'],
                            'version': spec['version']}
                (staging / 'install-receipt.json').write_text(encoded(receipt), encoding='utf-8')
                return activate(root, name, spec, staging, receipt, repair)
            finally:
                shutil.rmtree(work, ignore_errors=True)
    except ValueError as exc:
        if str(exc).startswith('LOCKED'):
            return {'status': 'LOCKED', 'version': spec['version']}
        raise
