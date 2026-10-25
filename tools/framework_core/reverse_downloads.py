"""Per-tool downloaders. Callers must already hold reverse and reverse-install."""
import hashlib
import tarfile
import urllib.request
import zipfile
from pathlib import Path


class IntegrityError(ValueError):
    pass


def fetch_verified(url, dest, sha256, opener=None):
    """Download one URL and keep it only when the SHA-256 matches."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + '.partial')
    digest = hashlib.sha256()
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(url, timeout=180) as response, partial.open('wb') as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                handle.write(chunk)
        if digest.hexdigest() != sha256:
            partial.unlink(missing_ok=True)
            raise IntegrityError('INTEGRITY_MISMATCH')
        partial.replace(dest)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return dest


def artifact_for(spec, platform, machine):
    artifacts = spec.get('artifacts') or {}
    key = platform + '-' + machine
    chosen = artifacts.get(key)
    if not chosen or not chosen.get('url') or len(chosen.get('sha256') or '') != 64:
        return None
    return chosen


def install_archive(root, name, spec, platform, machine, opener=None):
    chosen = artifact_for(spec, platform, machine)
    if chosen is None and spec.get('url') and len(spec.get('sha256') or '') == 64:
        chosen = {'url': spec['url'], 'sha256': spec['sha256'], 'kind': spec.get('kind', 'zip')}
    if chosen is None:
        return {'status': 'INTEGRITY_UNPINNED'}
    dest = Path(root) / '.framework' / 'tools' / name
    marker = dest / '.sha256'
    if marker.is_file() and marker.read_text(encoding='utf-8').strip() == chosen['sha256']:
        return {'status': 'INSTALLED', 'version': spec.get('version', '')}
    archive = dest / 'archive'
    fetch_verified(chosen['url'], archive, chosen['sha256'], opener)
    kind = chosen.get('kind', 'zip')
    if kind == 'zip':
        with zipfile.ZipFile(archive) as packed:
            packed.extractall(dest)
    elif kind == 'tar':
        with tarfile.open(archive) as packed:
            packed.extractall(dest, filter='data')
    elif kind != 'file':
        archive.unlink()
        return {'status': 'INSTALL_FAILED'}
    marker.write_text(chosen['sha256'] + '\n', encoding='utf-8')
    return {'status': 'INSTALLED', 'version': spec.get('version', '')}
