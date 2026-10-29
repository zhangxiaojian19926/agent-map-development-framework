"""Offline adaptation of READY candidates into explicit channel artifacts."""
import hashlib
import json
from os import replace
from pathlib import Path
import re
import shutil
import tempfile

from .delivery_release_candidate import generate as candidate_generate, read_json as candidate_read_json
from .product_recon import depth_within
from .reverse_v2 import canonical, encoded, sha_text, valid_id
from .storage import atomic, safe_path


SCHEMA = 'release-channel-request/v1'
MANIFEST_SCHEMA = 'release-channel-manifest/v1'
RECEIPT_SCHEMA = 'release-channel-receipt/v1'
REQUEST_FIELDS = {'schema', 'id', 'candidate', 'channel', 'assets'}
CANDIDATE_FIELDS = {'id', 'request', 'request_sha256', 'report_sha256'}
CHANNEL_FIELDS = {'type', 'repository', 'tag', 'title', 'draft', 'prerelease'}
ASSET_FIELDS = {'path', 'name'}
RECEIPT_FIELDS = {
    'schema', 'id', 'request_sha256', 'directory', 'files', 'report',
    'report_sha256', 'publish', 'execution',
}
SHA256 = re.compile(r'[0-9a-f]{64}')
REPOSITORY = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')
TAG = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
ASSET_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
PRIVATE_MARKERS = (
    '.framework/', '.git/', 'docs/project/reverse/', 'reverse/raw/',
    'reverse/output/', 'local-state/rea/', 'local-state/product',
)
RESERVED_NAMES = {'release-notes.md', 'channel-manifest.json'}
MAX_BYTES = 1024 * 1024
MAX_ASSETS = 100
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def input_error():
    raise ValueError('CHANNEL_INPUT')


def conflict():
    raise ValueError('CHANNEL_CONFLICT')


def stale():
    raise ValueError('CHANNEL_STALE')


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        input_error()


def public_text(value, maximum=1000):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(char) < 32 or ord(char) == 127 for char in value)
            or '<!--' in value or '-->' in value):
        input_error()
    normalized = value.replace('\\', '/').lower()
    if any(marker in normalized for marker in PRIVATE_MARKERS):
        input_error()
    return value


def valid_hash(value):
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(root, value):
    if not isinstance(value, (str, Path)) or not str(value):
        input_error()
    path = Path(value)
    try:
        if path.is_absolute():
            if path.is_symlink():
                raise ValueError('SYMLINK: ' + str(path))
            rel = path.resolve().relative_to(Path(root).resolve())
        else:
            rel = path
        safe_path(root, str(rel))
        return rel.as_posix()
    except (ValueError, OSError) as exc:
        if 'SYMLINK' in str(exc) or 'PATH_ESCAPE' in str(exc):
            raise
        input_error()


def read_json(root, path):
    rel = relative(root, path)
    try:
        source = safe_path(root, rel)
        if not source.is_file() or source.stat().st_size > MAX_BYTES:
            input_error()
        value = json.loads(source.read_bytes().decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        input_error()
    if not depth_within(value):
        raise ValueError('CHANNEL_LIMIT')
    return rel, value


def validate_request(request):
    exact(request, REQUEST_FIELDS)
    if request['schema'] != SCHEMA or not valid_id(request['id']):
        input_error()
    candidate = request['candidate']
    exact(candidate, CANDIDATE_FIELDS)
    if (not valid_id(candidate['id']) or not isinstance(candidate['request'], str)
            or not candidate['request'] or not valid_hash(candidate['request_sha256'])
            or not valid_hash(candidate['report_sha256'])):
        input_error()
    public_text(candidate['request'])
    channel = request['channel']
    exact(channel, CHANNEL_FIELDS)
    if channel['type'] != 'github-release':
        raise ValueError('CHANNEL_UNSUPPORTED')
    repository = channel['repository']
    if (not isinstance(repository, str) or not REPOSITORY.fullmatch(repository)
            or any(part in {'.', '..'} for part in repository.split('/'))):
        input_error()
    if not isinstance(channel['tag'], str) or not TAG.fullmatch(channel['tag']):
        input_error()
    public_text(channel['title'], 200)
    if not isinstance(channel['draft'], bool) or not isinstance(channel['prerelease'], bool):
        input_error()
    if not isinstance(request['assets'], list) or not request['assets']:
        input_error()
    if len(request['assets']) > MAX_ASSETS:
        raise ValueError('CHANNEL_LIMIT')


def load_ready_candidate(root, reference):
    try:
        result = candidate_generate(root, reference['request'], dry_run=True)
        unused_rel, candidate_request = candidate_read_json(root, reference['request'])
        del unused_rel
        receipt_rel = '.framework/local-state/delivery/' + reference['id'] + '.json'
        receipt = json.loads(safe_path(root, receipt_rel).read_text(encoding='utf-8'))
    except (ValueError, OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError):
        stale()
    if result['overall'] != 'READY':
        raise ValueError('CHANNEL_NOT_READY')
    if (result['id'] if 'id' in result else reference['id']) != reference['id']:
        stale()
    if (result['report'] != 'docs/delivery/' + reference['id'] + '-candidate.md'
            or result['report_sha256'] != reference['report_sha256']
            or receipt.get('request_sha256') != reference['request_sha256']):
        stale()
    return result, candidate_request


def select_assets(root, requested, candidate_assets):
    available = {item['path']: item for item in candidate_assets}
    selected, seen_paths, seen_names = [], set(), set()
    total = 0
    for item in requested:
        exact(item, ASSET_FIELDS)
        path, name = item['path'], item['name']
        public_text(path)
        if (not isinstance(name, str) or not ASSET_NAME.fullmatch(name)
                or name.casefold() in RESERVED_NAMES):
            input_error()
        folded = name.casefold()
        if path in seen_paths or folded in seen_names or path not in available:
            input_error()
        source = available[path]
        current = safe_path(root, path)
        try:
            if not current.is_file() or file_hash(current) != source['sha256']:
                stale()
        except OSError:
            stale()
        size = current.stat().st_size
        if size != source['size']:
            stale()
        total += size
        if total > MAX_TOTAL_BYTES:
            raise ValueError('CHANNEL_LIMIT')
        selected.append({'path': path, 'name': name, 'size': size, 'sha256': source['sha256']})
        seen_paths.add(path)
        seen_names.add(folded)
    return selected


def github_adapt(request, candidate_request, assets, request_sha256):
    notes = candidate_request['notes']
    lines = ['# ' + request['channel']['title'], '', notes['summary'], '', '## 变化', '']
    lines.extend('- ' + item for item in notes['changes'])
    lines.extend(['', '## 已知限制', ''])
    lines.extend('- ' + item for item in notes['known_limits'])
    lines.append('')
    manifest = {
        'schema': MANIFEST_SCHEMA, 'id': request['id'], 'request_sha256': request_sha256,
        'candidate': dict(request['candidate']), 'channel': dict(request['channel']),
        'assets': assets, 'publish': 'NOT_RUN', 'execution': 'NOT_RUN',
    }
    return '\n'.join(lines), manifest


ADAPTERS = {'github-release': github_adapt}


def render_report(request, manifest, report_sha256=None):
    del report_sha256
    lines = [
        '<!-- release-channel:' + request['id'] + ' -->',
        '# 发布渠道适配报告', '',
        '本报告只证明本地渠道产物已按请求生成，不代表远端发布已经执行。', '',
        '- 请求 ID：`' + request['id'] + '`',
        '- 请求 SHA-256：`' + manifest['request_sha256'] + '`',
        '- 候选 ID：`' + request['candidate']['id'] + '`',
        '- 候选请求 SHA-256：`' + request['candidate']['request_sha256'] + '`',
        '- 候选报告 SHA-256：`' + request['candidate']['report_sha256'] + '`',
        '- 渠道：`github-release`',
        '- 仓库：`' + request['channel']['repository'] + '`',
        '- Tag：`' + request['channel']['tag'] + '`',
        '- Draft：`' + str(request['channel']['draft']).lower() + '`',
        '- Prerelease：`' + str(request['channel']['prerelease']).lower() + '`',
        '- publish=NOT_RUN',
        '- execution=NOT_RUN', '',
        '## 渠道资产', '',
        '| 来源 | 公开名称 | 字节数 | SHA-256 |',
        '|---|---|---:|---|',
    ]
    for asset in manifest['assets']:
        lines.append('| ' + asset['path'] + ' | ' + asset['name'] + ' | '
                     + str(asset['size']) + ' | ' + asset['sha256'] + ' |')
    lines.extend([
        '', '## 后续门禁', '',
        '人工核对渠道目录、Release 说明和目标后，真实发布仍需独立规格与本次明确授权。',
        '本适配不访问网络，不执行 Git、上传、打 tag、创建 Release 或部署。',
        '<!-- release-channel:end -->', '',
    ])
    return '\n'.join(lines)


def directory_files(root, directory_rel):
    directory = safe_path(root, directory_rel)
    files = {}
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            conflict()
        files[path.name] = file_hash(path)
    return files


def existing(root, request_id, directory_rel, report_rel, receipt_rel):
    directory = safe_path(root, directory_rel)
    report_path = safe_path(root, report_rel)
    receipt_path = safe_path(root, receipt_rel)
    if not directory.exists() and not report_path.exists() and not receipt_path.exists():
        return None
    if not directory.is_dir() or not report_path.is_file() or not receipt_path.is_file():
        conflict()
    try:
        document = report_path.read_text(encoding='utf-8')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        conflict()
    if (not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS
            or receipt['schema'] != RECEIPT_SCHEMA or receipt['id'] != request_id
            or not valid_hash(receipt['request_sha256']) or receipt['directory'] != directory_rel
            or receipt['report'] != report_rel or receipt['report_sha256'] != sha_text(document)
            or receipt['publish'] != 'NOT_RUN' or receipt['execution'] != 'NOT_RUN'
            or not isinstance(receipt['files'], dict)
            or any(not isinstance(name, str) or not valid_hash(value)
                   for name, value in receipt['files'].items())
            or document.count('<!-- release-channel:' + request_id + ' -->') != 1
            or document.count('<!-- release-channel:end -->') != 1):
        conflict()
    if directory_files(root, directory_rel) != receipt['files']:
        conflict()
    return {'document': document, 'receipt': receipt}


def prepare_directory(root, directory_rel, assets, notes, manifest, expected_files):
    directory = safe_path(root, directory_rel)
    directory.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.' + directory.name + '.staging-', dir=str(directory.parent)))
    try:
        for asset in assets:
            source = safe_path(root, asset['path'])
            target = safe_path(root, staging.relative_to(root) / asset['name'])
            target.write_bytes(source.read_bytes())
        (staging / 'release-notes.md').write_text(notes, encoding='utf-8')
        (staging / 'channel-manifest.json').write_text(encoded(manifest), encoding='utf-8')
        if directory_files(root, staging.relative_to(root).as_posix()) != expected_files:
            raise OSError('CHANNEL_STAGE_MISMATCH')
        return staging
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def commit(root, old, request_id, directory_rel, report_rel, receipt_rel,
           assets, notes, manifest, document, receipt, expected_files):
    directory = safe_path(root, directory_rel)
    staging = prepare_directory(root, directory_rel, assets, notes, manifest, expected_files)
    backup = staging.with_name(staging.name.replace('.staging-', '.backup-'))
    old_moved = False
    directory_committed = False
    completed = False
    try:
        if old is not None:
            replace(directory, backup)
            old_moved = True
        replace(staging, directory)
        directory_committed = True
        atomic(root, report_rel, document)
        atomic(root, receipt_rel, encoded(receipt))
        completed = True
    except (OSError, ValueError):
        if directory_committed and directory.exists():
            shutil.rmtree(directory)
        if old_moved and backup.exists():
            replace(backup, directory)
        if old is None:
            safe_path(root, report_rel).unlink(missing_ok=True)
            safe_path(root, receipt_rel).unlink(missing_ok=True)
        else:
            atomic(root, report_rel, old['document'])
            atomic(root, receipt_rel, encoded(old['receipt']))
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        if completed and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)


def generate(root, request_path, dry_run=False):
    root = Path(root).resolve()
    try:
        request_rel, request = read_json(root, request_path)
        validate_request(request)
        candidate_result, candidate_request = load_ready_candidate(root, request['candidate'])
        assets = select_assets(root, request['assets'], candidate_result['artifacts'])
        request_sha256 = sha_text(canonical(request))
        adapter = ADAPTERS[request['channel']['type']]
        notes, manifest = adapter(request, candidate_request, assets, request_sha256)
        document = render_report(request, manifest)
        report_sha256 = sha_text(document)
        directory_rel = 'dist/delivery/' + request['id']
        report_rel = 'docs/delivery/' + request['id'] + '-channel.md'
        receipt_rel = '.framework/local-state/delivery/' + request['id'] + '-channel.json'
        expected_files = {asset['name']: asset['sha256'] for asset in assets}
        expected_files['release-notes.md'] = sha_text(notes)
        expected_files['channel-manifest.json'] = sha_text(encoded(manifest))
        receipt = {
            'schema': RECEIPT_SCHEMA, 'id': request['id'], 'request_sha256': request_sha256,
            'directory': directory_rel, 'files': expected_files, 'report': report_rel,
            'report_sha256': report_sha256, 'publish': 'NOT_RUN', 'execution': 'NOT_RUN',
        }
        old = existing(root, request['id'], directory_rel, report_rel, receipt_rel)
        result = {
            'status': 'DRY_RUN' if dry_run else None, 'id': request['id'],
            'request': request_rel, 'request_sha256': request_sha256,
            'candidate': request['candidate']['id'], 'channel': request['channel']['type'],
            'directory': directory_rel, 'report': report_rel, 'receipt': receipt_rel,
            'manifest_sha256': expected_files['channel-manifest.json'],
            'report_sha256': report_sha256, 'files': expected_files,
            'publish': 'NOT_RUN', 'execution': 'NOT_RUN',
        }
        if dry_run:
            return dict(result, write='NOT_RUN')
        if old is not None and old['document'] == document and old['receipt'] == receipt:
            return dict(result, status='UNCHANGED', write='UNCHANGED')
        status = 'UPDATED' if old is not None else 'RECORDED'
        commit(root, old, request['id'], directory_rel, report_rel, receipt_rel,
               assets, notes, manifest, document, receipt, expected_files)
        return dict(result, status=status, write=status)
    except ValueError as exc:
        message = str(exc)
        if message.startswith('CHANNEL_') or 'SYMLINK' in message or 'PATH_ESCAPE' in message:
            raise
        raise ValueError('CHANNEL_INPUT') from exc
    except (KeyError, TypeError) as exc:
        raise ValueError('CHANNEL_INPUT') from exc
