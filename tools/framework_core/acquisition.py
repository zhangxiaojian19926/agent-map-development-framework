"""Named, resumable Git acquisition. All source code remains inert data."""
import os
from pathlib import Path
import re
import stat
import tempfile

from .config import encoded
from .intake import validate_plan, validate_source
from .process import run
from .storage import atomic, fingerprint, project_lock, read_json, safe_path


def git_call(args, cwd, grants, runner=run, auth=None, timeout=30):
    # process.run merges the host environment: env -i removes Git command/config
    # injection, SSH commands, credential helpers and filter configuration.
    env = ['PATH=' + os.defpath, 'GIT_CONFIG_NOSYSTEM=1', 'GIT_CONFIG_GLOBAL=/dev/null',
           'GIT_TERMINAL_PROMPT=0', 'GIT_LFS_SKIP_SMUDGE=1', 'GIT_OPTIONAL_LOCKS=0',
           'GIT_SSH_COMMAND=ssh -F /dev/null -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentityFile=none']
    if auth:
        if set(auth) != {'ssh_agent'} or 'auth' not in grants:
            raise ValueError('CONSENT_REQUIRED: auth')
        sock = Path(auth['ssh_agent'])
        if not sock.is_absolute() or not stat.S_ISSOCK(sock.stat().st_mode) or sock.stat().st_uid != os.getuid():
            raise ValueError('AUTH_REQUIRED: verified current-user SSH agent socket')
        env.append('SSH_AUTH_SOCK=' + str(sock))
    prefix = ['/usr/bin/env', '-i', *env, 'git', '-c', 'core.hooksPath=/dev/null',
              '-c', 'core.fsmonitor=false', '-c', 'credential.helper=',
              '-c', 'protocol.ext.allow=never', '-c', 'protocol.file.allow=' + ('always' if 'local-clone' in grants else 'never')]
    return runner(prefix + list(args), cwd, timeout, {})


def failure(result):
    error = result.get('stderr', '').lower()
    code = 'AUTH_REQUIRED' if any(x in error for x in ('authentication', 'permission denied', 'could not read username', 'publickey')) else 'NETWORK_ERROR'
    if result.get('exit_code') == 127:
        code = 'DEPENDENCY_MISSING'
    return {'state': 'FAILED', 'error_code': code, 'timed_out': bool(result.get('timed_out'))}


def resolve_source(module, grants, runner=run, auth=None):
    if 'clone' not in grants:
        raise ValueError('CONSENT_REQUIRED: clone')
    url = validate_source(module['source_url'], grants)
    with tempfile.TemporaryDirectory(prefix='framework-refs-') as scratch:
        result = git_call(['ls-remote', '--symref', '--', url], scratch, grants, runner, auth)
    if result['exit_code']:
        return failure(result)
    refs, head_ref = {}, None
    for line in result['stdout'].splitlines():
        fields = line.split('\t')
        if len(fields) != 2:
            return {'state': 'FAILED', 'error_code': 'REF_UNRESOLVED'}
        value, name = fields
        if value.startswith('ref: ') and name == 'HEAD':
            head_ref = value[5:]
        elif re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', value):
            refs[name] = value
    requested = module.get('requested_ref')
    if requested:
        kind, value = requested['kind'], requested['value']
        if kind == 'commit':
            if not re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}', value):
                raise ValueError('INVALID_REF')
            return {'state': 'RESOLVED', 'resolved_ref': value, 'resolved_commit': value.lower()}
        key = ('refs/heads/' if kind == 'branch' else 'refs/tags/') + value
        if key not in refs:
            return {'state': 'FAILED', 'error_code': 'REF_NOT_FOUND'}
        return {'state': 'RESOLVED', 'resolved_ref': key, 'resolved_commit': refs.get(key + '^{}', refs[key])}
    if not refs:
        return {'state': 'EMPTY', 'resolved_ref': None, 'resolved_commit': None}
    if not head_ref or 'HEAD' not in refs:
        return {'state': 'FAILED', 'error_code': 'REF_UNRESOLVED'}
    return {'state': 'RESOLVED', 'resolved_ref': head_ref, 'resolved_commit': refs['HEAD']}


def verify_checkout(path, module, saved, grants, runner):
    if not (path/'.git').is_dir() or (path/'.git').is_symlink():
        return False
    # Refuse changed repository configuration before any Git command reads it.
    if fingerprint(safe_path(path, '.git/config')) != saved.get('git_config_sha256'):
        return False
    def read(*args):
        result = git_call(args, path, grants, runner)
        return result['stdout'].strip() if not result['exit_code'] else None
    return (read('rev-parse', '--show-toplevel') == str(path) and
            read('remote', 'get-url', 'origin') == module['source_url'] and
            read('rev-parse', 'HEAD') == saved.get('resolved_commit') and
            read('status', '--porcelain', '--untracked-files=all') == '')


def acquire_modules(plan, grants, runner=run, auth=None):
    if not {'clone', 'write'} <= grants:
        raise ValueError('CONSENT_REQUIRED: clone/write')
    validate_plan(plan)
    target, staging = Path(plan['target']), Path(plan['staging'])
    with project_lock(staging), project_lock(target):
        validate_plan(plan)
        report = read_json(staging, 'acquisition.json', {'schema_version': 1, 'modules': {}})
        def record(mid, state):
            report['modules'][mid] = state
            atomic(staging, 'acquisition.json', encoded(report))
        for module in plan['request']['modules']:
            mid = module['id']
            path = safe_path(target, module['path'])
            saved = report['modules'].get(mid, {})
            if path.exists():
                good = (saved.get('owned') == plan['plan_id'] and
                        saved.get('source_url') == module['source_url'] and
                        saved.get('state') == 'REGISTERED' and
                        verify_checkout(path, module, saved, grants, runner))
                if not good:
                    record(mid, dict(saved, state='CONFLICT', error_code='SOURCE_CONFLICT'))
                continue
            resolved = resolve_source(module, grants, runner, auth)
            state = dict(module, **resolved, owned=plan['plan_id'])
            record(mid, state)
            if resolved['state'] != 'RESOLVED':
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path = safe_path(target, module['path'])
            record(mid, dict(state, state='FETCHING'))
            result = git_call(['clone', '--template=', '--no-recurse-submodules', '--no-checkout',
                               '--', module['source_url'], str(path)], target, grants, runner, auth, 300)
            if result['exit_code']:
                record(mid, dict(state, **failure(result)))
                continue
            requested = module.get('requested_ref')
            ref = resolved['resolved_ref']
            check_ref = ('refs/remotes/origin/' + ref[len('refs/heads/'):] if ref.startswith('refs/heads/') else ref)
            checked = git_call(['rev-parse', '--verify', check_ref + '^{commit}'], path, grants, runner)
            if checked['exit_code'] or checked['stdout'].strip() != resolved['resolved_commit']:
                record(mid, dict(state, state='FAILED', error_code='REF_NOT_FOUND' if requested and requested['kind'] == 'commit' else 'SOURCE_MOVED'))
                continue
            checked = git_call(['checkout', '--detach', resolved['resolved_commit']], path, grants, runner)
            if checked['exit_code']:
                record(mid, dict(state, state='FAILED', error_code='CHECKOUT_FAILED'))
                continue
            state.update(state='REGISTERED', git_config_sha256=fingerprint(safe_path(path, '.git/config')))
            record(mid, state)
        report['status'] = 'COMPLETE' if all(s['state'] in ('REGISTERED', 'EMPTY') for s in report['modules'].values()) else 'PARTIAL'
        atomic(staging, 'acquisition.json', encoded(report))
        return report
