"""Owned file transactions. Never roll back unrelated or edited files."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .config import encoded, identity

_held_root = ContextVar('framework_write_lock', default=None)


def safe_path(root, rel):
    root = Path(root).absolute()
    if root.is_symlink():
        raise ValueError('SYMLINK: ' + str(root))
    root = root.resolve()
    rel = Path(rel)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('PATH_ESCAPE: ' + str(rel))
    target = root / rel
    for part in (target, *target.parents):
        if part.is_symlink():
            raise ValueError('SYMLINK: ' + str(part))
        if part == root:
            break
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('PATH_ESCAPE: ' + str(rel))
    return target


def fingerprint(path):
    if path.is_symlink():
        raise ValueError('SYMLINK: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def atomic(root, rel, content):
    path = safe_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path = safe_path(root, rel)
    fd, tmp = tempfile.mkstemp(prefix='.framework-tmp-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(root, rel)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextmanager
def project_lock(root):
    path = safe_path(root, '.framework/local-state/lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError('LOCKED: another writer or interrupted run; inspect lock owner before removal')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(str(os.getpid()))
        token = _held_root.set(Path(root).resolve())
        try:
            yield
        finally:
            _held_root.reset(token)
    finally:
        path.unlink()


def apply_files(root, changes, run_id, locked=False):
    locked = locked or _held_root.get() == Path(root).resolve()
    if not locked:
        with project_lock(root):
            return apply_files(root, changes, run_id, locked=True)
    identity(run_id)
    journal = '.framework/local-state/runs/' + run_id + '.json'
    for change in changes:
        path = safe_path(root, change['path'])
        actual = fingerprint(path)
        after = hashlib.sha256(change['content'].encode()).hexdigest()
        if actual not in (change['before_sha256'], after):
            raise ValueError('CONFLICT: ' + change['path'])
    record = {'schema_version': 1, 'run_id': run_id, 'changes': changes, 'completed': [], 'status': 'APPLYING'}
    atomic(root, journal, encoded(record))
    for change in changes:
        path = safe_path(root, change['path'])
        actual = fingerprint(path)
        after = hashlib.sha256(change['content'].encode()).hexdigest()
        if actual != after:
            if actual != change['before_sha256']:
                raise ValueError('CONFLICT: ' + change['path'])
            atomic(root, change['path'], change['content'])
        record['completed'].append({'path': change['path'], 'sha256': after})
        atomic(root, journal, encoded(record))
    record['status'] = 'COMPLETE'
    atomic(root, journal, encoded(record))
    return record


def resume_run(root, run_id, consent):
    if 'write' not in consent:
        raise ValueError('CONSENT_REQUIRED: write')
    identity(run_id)
    path = safe_path(root, '.framework/local-state/runs/' + run_id + '.json')
    record = json.loads(path.read_text())
    if record.get('schema_version') != 1 or record.get('run_id') != run_id:
        raise ValueError('INVALID_JOURNAL')
    for change in record['changes']:
        parts = Path(change['path']).parts
        if '.git' in parts:
            # Hook location/worktree ownership must be re-planned, not replayed from a journal.
            raise ValueError('CONSENT_REQUIRED: use refresh --allow hooks to revalidate hook scope')
        if 'openspec' in parts and 'openspec' not in consent:
            raise ValueError('CONSENT_REQUIRED: openspec')
        if Path(change['path']).name == 'codegraph.json' and 'index' not in consent:
            raise ValueError('CONSENT_REQUIRED: index')
    for item in record['completed']:
        if fingerprint(safe_path(root, item['path'])) != item['sha256']:
            raise ValueError('CONFLICT: ' + item['path'])
    return apply_files(root, record['changes'], run_id)


def read_json(root, rel, default=None):
    p = safe_path(root, rel)
    return json.loads(p.read_text()) if p.exists() else default


def owned_changes(root, outputs):
    """Generator owns only hashes it wrote. Existing manual content is a conflict."""
    registry = read_json(root, '.framework/local-state/owned.json', {})
    changes = []
    for rel, content in sorted(outputs.items()):
        actual = fingerprint(safe_path(root, rel))
        after = hashlib.sha256(content.encode()).hexdigest()
        if actual == after:
            registry[rel] = after
            continue
        if actual is not None and registry.get(rel) != actual:
            raise ValueError('CONFLICT: ' + rel)
        changes.append({'path': rel, 'before_sha256': actual, 'content': content})
        registry[rel] = after
    rel = '.framework/local-state/owned.json'
    content = encoded(registry)
    if fingerprint(safe_path(root, rel)) != hashlib.sha256(content.encode()).hexdigest():
        changes.append({'path': rel, 'before_sha256': fingerprint(safe_path(root, rel)), 'content': content})
    return changes
