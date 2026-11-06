"""Verifiable approval evidence for workflow gates.

An approval is an OpenSSH signature over a payload that binds the project,
the change, the approved file fingerprints and the approved scope. The
trusted public keys live outside the target project: a request may point at
an approval, but it can never point at the trust anchor or replace it.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from ..config import identity

APPROVAL_SCHEMA = 'workflow-approval/v1'
NAMESPACE = 'framework-workflow-approval/v1'
TRUST_ANCHOR = Path('/etc/framework/workflow-trust.allowed_signers')

VERIFIER = 'ssh-keygen'
MAX_PAYLOAD = 1024 * 1024


def trust_anchor():
    """The trust source is a fixed system path. No request and no environment may move it."""
    return TRUST_ANCHOR


def anchor_protected(path):
    """True when neither the trust source nor the directory holding it is writable here.

    A trust source the agent can rewrite is not a trust source: the agent reads
    the shipped source, learns the path and signs its own approval.
    """
    target = Path(path)
    if os.access(target, os.W_OK):
        return False
    return not os.access(target.parent, os.W_OK)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def change_dir(root, change):
    identity(change)
    return Path(root) / 'openspec' / 'changes' / change


def approved_files(change_root):
    """The approved surface: the change's specs and its plan."""
    files = {}
    for path in sorted(Path(change_root).glob('specs/**/*.md')):
        files[path.relative_to(change_root).as_posix()] = digest(path)
    plan = Path(change_root) / 'implementation-plan.md'
    if plan.is_file():
        files[plan.name] = digest(plan)
    return files


def current_facts(root, change):
    """Facts re-derived from the project; a request never supplies them."""
    project_file = Path(root) / 'framework-project.json'
    project = {}
    if project_file.is_file():
        project = json.loads(project_file.read_text(encoding='utf-8'))
    return {
        'project': project.get('project_id'),
        'change': change,
        'files': approved_files(change_dir(root, change)),
    }


def trusted_principals(trust_path):
    """Principals listed in an ssh-keygen allowed-signers file."""
    principals = []
    path = Path(trust_path)
    if not path.is_file():
        return principals
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        principals.extend(part for part in parts[0].split(',') if part)
    return principals


def verify_signature(payload_path, signature_path, trust_path=None):
    """Return the trusted principal that signed the payload."""
    trust = Path(trust_path) if trust_path else trust_anchor()
    if not trust.is_file():
        raise ValueError('TRUST_SOURCE_MISSING: 没有可用的信任来源文件')
    if not anchor_protected(trust):
        raise ValueError('TRUST_SOURCE_MUTABLE: 信任来源可被当前用户改写，不构成可核验授权')
    if shutil.which(VERIFIER) is None:
        raise ValueError('VERIFIER_MISSING: 缺少 ssh-keygen 验证器')
    payload = Path(payload_path)
    signature = Path(signature_path)
    if not payload.is_file() or not signature.is_file():
        raise ValueError('APPROVAL_MISSING: approval payload or signature is missing')
    if payload.stat().st_size > MAX_PAYLOAD:
        raise ValueError('APPROVAL_MISSING: approval payload is too large')
    message = payload.read_bytes()
    for principal in trusted_principals(trust):
        result = subprocess.run(
            [VERIFIER, '-Y', 'verify', '-f', str(trust), '-I', principal, '-n', NAMESPACE,
             '-s', str(signature)],
            input=message, capture_output=True)
        if result.returncode == 0:
            return principal
    raise ValueError('SIGNATURE_INVALID: no trusted key signed this approval')
