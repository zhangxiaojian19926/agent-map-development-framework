"""Record hashes of an already built dist directory. Does not run a build."""
import json
from pathlib import Path

from .storage import atomic, fingerprint, safe_path


def package_project(root, grants):
    if not {'package', 'write'} <= set(grants or ()):
        raise ValueError('CONSENT_REQUIRED')
    root = Path(root).resolve()
    dist = safe_path(root, 'dist')
    if not dist.is_dir() or dist.is_symlink():
        return {'status': 'NOTHING_TO_PACKAGE', 'runtime': 'NOT_RUN'}
    files = []
    for path in sorted(dist.rglob('*')):
        if path.is_symlink():
            raise ValueError('UNSAFE_PACKAGE')
        if not path.is_file():
            continue
        rel = path.resolve().relative_to(root).as_posix()
        if '.framework/' in rel or 'docs/project/reverse/' in rel or 'local-state/rea/' in rel:
            raise ValueError('UNSAFE_PACKAGE')
        files.append({'path': rel, 'sha256': fingerprint(path)})
    manifest = {'status': 'PACKAGED', 'files': files, 'runtime': 'NOT_RUN'}
    atomic(root, '.framework/local-state/package-manifest.json', json.dumps(manifest, indent=2) + '\n')
    return manifest
