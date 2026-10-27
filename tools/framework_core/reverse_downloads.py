"""Per-tool downloaders. Callers must already hold reverse and reverse-install."""
import hashlib
import tarfile
import urllib.request
import zipfile
from pathlib import Path


class IntegrityError(ValueError):
    pass


def fetch_verified(url, dest, sha256, opener=None, max_bytes=512 * 1024 * 1024):
    """Download one URL with a hard size limit and keep only verified bytes."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + '.partial')
    digest = hashlib.sha256()
    total = 0
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(url, timeout=180) as response:
            declared = (getattr(response, 'headers', {}) or {}).get('Content-Length')
            if declared is not None and (not str(declared).isdigit() or int(declared) > max_bytes):
                raise ValueError('DOWNLOAD_LIMIT')
            with partial.open('wb') as handle:
                while True:
                    chunk = response.read(min(1024 * 1024, max_bytes - total + 1))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError('DOWNLOAD_LIMIT')
                    digest.update(chunk)
                    handle.write(chunk)
        if digest.hexdigest() != sha256:
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
    if not chosen and spec.get('url') and len(spec.get('sha256') or '') == 64:
        chosen = {'url': spec['url'], 'sha256': spec['sha256'], 'kind': spec.get('kind', 'zip')}
    if not chosen or not chosen.get('url') or len(chosen.get('sha256') or '') != 64:
        return None
    return chosen


def safe_member(name, size, limits):
    from pathlib import PurePosixPath
    path = PurePosixPath(name)
    if (not name or '\x00' in name or '\\' in name or path.is_absolute() or '..' in path.parts
            or size < 0):
        raise ValueError('ARCHIVE_UNSAFE')
    if limits['files'] >= limits['max_files']:
        raise ValueError('ARCHIVE_LIMIT')
    limits['files'] += 1
    limits['bytes'] += size
    if limits['bytes'] > limits['max_extract_bytes']:
        raise ValueError('ARCHIVE_LIMIT')


def extract_archive(archive, kind, staging, max_files=10000, max_extract_bytes=1024 * 1024 * 1024):
    """Validate every member before extracting into an owned staging directory."""
    import stat
    limits = {'files': 0, 'bytes': 0, 'max_files': max_files,
              'max_extract_bytes': max_extract_bytes}
    if kind == 'zip':
        with zipfile.ZipFile(archive) as packed:
            for item in packed.infolist():
                safe_member(item.filename, item.file_size, limits)
                mode = item.external_attr >> 16
                file_type = mode & 0o170000
                if stat.S_ISLNK(mode) or (file_type and not stat.S_ISREG(mode) and not stat.S_ISDIR(mode)):
                    raise ValueError('ARCHIVE_UNSAFE')
            packed.extractall(staging)
    elif kind == 'tar':
        with tarfile.open(archive) as packed:
            for item in packed.getmembers():
                safe_member(item.name, item.size, limits)
                if item.issym() or item.islnk() or not (item.isfile() or item.isdir()):
                    raise ValueError('ARCHIVE_UNSAFE')
            # Python 3.9 lacks the filter parameter; the member checks above remain mandatory.
            import inspect
            if 'filter' in inspect.signature(packed.extractall).parameters:
                packed.extractall(staging, filter='data')
            else:
                packed.extractall(staging)
    else:
        raise ValueError('INSTALL_FAILED')
    return staging


def install_archive(root, name, spec, platform, machine, opener=None, **kwargs):
    """Compatibility entry point; successful installs retain the legacy status."""
    from .reverse_install import install_archive as transaction
    result = transaction(root, name, spec, platform, machine, opener, **kwargs)
    if result['status'] == 'INSTALLED':
        return {'status': 'INSTALLED', 'version': spec.get('version', ''),
                'action': result.get('action'), 'install_path': result.get('install_path')}
    return result
