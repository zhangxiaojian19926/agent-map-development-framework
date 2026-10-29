"""Evidence-bound release candidate reports. Never builds, tests, or releases."""
import hashlib
import json
from pathlib import Path
import re

from .product_recon import depth_within
from .reverse_v2 import canonical, encoded, sha_text, valid_id
from .storage import atomic, safe_path


SCHEMA = 'release-candidate-request/v1'
EVIDENCE_SCHEMA = 'delivery-evidence/v1'
RECEIPT_SCHEMA = 'release-candidate-receipt/v1'
REQUEST_FIELDS = {'schema', 'id', 'version', 'source_revision', 'evidence', 'artifacts', 'notes'}
RECORD_FIELDS = {'id', 'category', 'result', 'test', 'environment', 'artifact', 'reason'}
CATEGORIES = {'BUILD', 'FUNCTION', 'INTEGRATION'}
RESULTS = {'PASS', 'FAIL', 'NOT_RUN', 'INFRA_ERROR', 'N/A'}
MAX_BYTES = 1024 * 1024
MAX_ITEMS = 1000
SHA256 = re.compile(r'[0-9a-f]{64}')
REASON = re.compile(r'[A-Z][A-Z0-9_]{0,79}$')
PRIVATE_PARTS = {'.framework', '.git', 'node_modules'}
SENSITIVE_NAMES = {'.env', 'credentials', 'credentials.json', 'secrets', 'secrets.json', 'id_rsa', 'id_ed25519'}


def input_error():
    raise ValueError('CANDIDATE_INPUT')


def evidence_error():
    raise ValueError('CANDIDATE_EVIDENCE')


def conflict():
    raise ValueError('CANDIDATE_CONFLICT')


def exact(value, fields, error=input_error):
    if not isinstance(value, dict) or set(value) != fields:
        error()


def public_text(value, maximum=500, error=input_error):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        error()
    return value


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


def source_ref(value, error=input_error):
    exact(value, {'path', 'sha256'}, error)
    if not isinstance(value['path'], str) or not isinstance(value['sha256'], str) or not SHA256.fullmatch(value['sha256']):
        error()


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
        raise ValueError('CANDIDATE_LIMIT')
    return rel, value


def bound_file(root, ref, prefix=None, error=None):
    source_ref(ref)
    rel = relative(root, ref['path'])
    if prefix is not None and not rel.startswith(prefix):
        input_error()
    try:
        path = safe_path(root, rel)
        if not path.is_file():
            raise OSError(rel)
        raw = path.read_bytes()
    except OSError:
        raise error or ValueError('CANDIDATE_STALE')
    if len(raw) > MAX_BYTES:
        raise ValueError('CANDIDATE_LIMIT')
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise error or ValueError('CANDIDATE_STALE')
    return rel, raw


def validate_notes(value):
    exact(value, {'summary', 'changes', 'known_limits'})
    public_text(value['summary'], 1000)
    for field in ('changes', 'known_limits'):
        if not isinstance(value[field], list) or len(value[field]) > 100:
            input_error()
        for item in value[field]:
            public_text(item, 1000)


def validate_artifacts(root, refs):
    if not isinstance(refs, list) or not refs or len(refs) > MAX_ITEMS:
        input_error()
    artifacts, hashes, seen = [], {}, set()
    for ref in refs:
        source_ref(ref)
        rel, unused = bound_file(root, ref, 'dist/')
        del unused
        parts = Path(rel).parts
        name = parts[-1].lower()
        if (rel in seen or set(parts) & PRIVATE_PARTS or name in SENSITIVE_NAMES
                or name.endswith(('.pem', '.key', '.p12', '.pfx'))
                or 'docs/project/reverse/' in rel or 'local-state/rea/' in rel):
            input_error()
        seen.add(rel)
        path = safe_path(root, rel)
        item = {'path': rel, 'sha256': ref['sha256'], 'size': path.stat().st_size}
        artifacts.append(item)
        hashes[rel] = ref['sha256']
    artifacts.sort(key=lambda item: item['path'])
    return artifacts, hashes


def validate_evidence(root, refs, source_revision):
    if not isinstance(refs, list) or not refs or len(refs) > MAX_ITEMS:
        input_error()
    records, hashes = [], {}
    for ref in refs:
        rel, raw = bound_file(root, ref, 'docs/verification/')
        hashes[rel] = ref['sha256']
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            evidence_error()
        if not depth_within(payload):
            raise ValueError('CANDIDATE_LIMIT')
        exact(payload, {'schema', 'source_revision', 'records'}, evidence_error)
        if payload['schema'] != EVIDENCE_SCHEMA or payload['source_revision'] != source_revision:
            evidence_error()
        if not isinstance(payload['records'], list) or not payload['records'] or len(payload['records']) > MAX_ITEMS:
            evidence_error()
        for record in payload['records']:
            exact(record, RECORD_FIELDS, evidence_error)
            if (not valid_id(record['id']) or record['category'] not in CATEGORIES
                    or record['result'] not in RESULTS
                    or not public_text(record['test'], 500, evidence_error)
                    or not public_text(record['environment'], 200, evidence_error)
                    or any(existing['id'] == record['id'] for existing in records)):
                evidence_error()
            artifact = record['artifact']
            if artifact is not None:
                source_ref(artifact, evidence_error)
                artifact_rel, unused = bound_file(root, artifact, 'docs/verification/')
                del unused
                hashes[artifact_rel] = artifact['sha256']
                artifact = dict(artifact, path=artifact_rel)
            if record['result'] == 'PASS' and artifact is None:
                evidence_error()
            reason = record['reason']
            if record['result'] in {'INFRA_ERROR', 'N/A'}:
                if not isinstance(reason, str) or not REASON.fullmatch(reason):
                    evidence_error()
            elif reason is not None:
                evidence_error()
            records.append(dict(record, artifact=artifact))
    records.sort(key=lambda item: (item['category'], item['id']))
    return records, hashes


def derive(records):
    gaps = []
    for record in records:
        if record['result'] == 'FAIL':
            gaps.append({'code': record['category'] + '_FAILED', 'evidence_id': record['id']})
        elif record['result'] != 'PASS':
            gap = {'code': record['result'], 'evidence_id': record['id'], 'category': record['category']}
            if record['reason'] is not None:
                gap['reason'] = record['reason']
            gaps.append(gap)
    for category in ('BUILD', 'FUNCTION'):
        if not any(record['category'] == category and record['result'] == 'PASS' for record in records):
            gaps.append({'code': 'MISSING_' + category + '_PASS'})
    if any(record['result'] == 'FAIL' for record in records):
        overall = 'FAILED'
    elif gaps:
        overall = 'GAPS_OPEN'
    else:
        overall = 'READY'
    gaps.sort(key=lambda item: (item['code'], item.get('evidence_id', '')))
    return overall, gaps


def render(request, source_hashes, records, artifacts, gaps, overall):
    lines = ['<!-- delivery-release-candidate:' + request['id'] + ' -->', '# 发布候选报告', '',
             '- 候选 ID：`' + request['id'] + '`', '- 版本：`' + request['version'] + '`',
             '- 源码版本：`' + request['source_revision'] + '`', '- 整体结果：`' + overall + '`',
             '- release=NOT_RUN', '- 构建与测试执行：NOT_RUN（仅核验既有声明证据）', '',
             '## 来源指纹', '']
    for path, digest in sorted(source_hashes.items()):
        lines.append('- `' + path + '`：`' + digest + '`')
    lines.extend(['', '## 证据记录', '', '| ID | 类别 | 结果 | 环境 | 公开附件 |',
                  '|---|---|---|---|---|'])
    for record in records:
        lines.append('| ' + record['id'] + ' | ' + record['category'] + ' | ' + record['result']
                     + ' | ' + record['environment'] + ' | '
                     + (record['artifact']['path'] if record['artifact'] else '无') + ' |')
    lines.extend(['', '## 候选产物', '', '| 路径 | 字节数 | SHA-256 |', '|---|---:|---|'])
    for artifact in artifacts:
        lines.append('| ' + artifact['path'] + ' | ' + str(artifact['size']) + ' | '
                     + artifact['sha256'] + ' |')
    lines.extend(['', '## 差距', ''])
    if gaps:
        for gap in gaps:
            suffix = '；证据 `' + gap['evidence_id'] + '`' if 'evidence_id' in gap else ''
            lines.append('- `' + gap['code'] + '`' + suffix)
    else:
        lines.append('- 无。')
    notes = request['notes']
    lines.extend(['', '## 发布说明草案', '', notes['summary'], '', '### 变化', ''])
    lines.extend('- ' + item for item in notes['changes'])
    lines.extend(['', '### 已知限制', ''])
    lines.extend('- ' + item for item in notes['known_limits'])
    lines.extend(['', '候选就绪不代表已经发布；证据真实性由验证责任方和适用评审确认。',
                  '<!-- delivery-release-candidate:end -->', ''])
    return '\n'.join(lines)


def existing(root, report_rel, receipt_rel, identifier):
    report_path, receipt_path = safe_path(root, report_rel), safe_path(root, receipt_rel)
    if not report_path.exists() and not receipt_path.exists():
        return None, None
    if not report_path.is_file() or not receipt_path.is_file():
        conflict()
    try:
        document = report_path.read_text(encoding='utf-8')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        conflict()
    fields = {'schema', 'id', 'request_sha256', 'input_hashes', 'report', 'report_sha256', 'execution'}
    if (not isinstance(receipt, dict) or set(receipt) != fields or receipt['schema'] != RECEIPT_SCHEMA
            or receipt['id'] != identifier or receipt['report'] != report_rel
            or receipt['execution'] != 'NOT_RUN' or receipt['report_sha256'] != sha_text(document)
            or not isinstance(receipt['request_sha256'], str) or not isinstance(receipt['input_hashes'], dict)
            or document.count('<!-- delivery-release-candidate:' + identifier + ' -->') != 1
            or document.count('<!-- delivery-release-candidate:end -->') != 1):
        conflict()
    return document, receipt


def generate(root, request_path, dry_run=False):
    root = Path(root).resolve()
    try:
        request_rel, request = read_json(root, request_path)
        exact(request, REQUEST_FIELDS)
        if request['schema'] != SCHEMA or not valid_id(request['id']):
            input_error()
        public_text(request['version'], 100)
        public_text(request['source_revision'], 200)
        validate_notes(request['notes'])
        artifacts, artifact_hashes = validate_artifacts(root, request['artifacts'])
        records, evidence_hashes = validate_evidence(root, request['evidence'], request['source_revision'])
        overall, gaps = derive(records)
        source_hashes = {request_rel: sha_text(canonical(request)), **evidence_hashes, **artifact_hashes}
        document = render(request, source_hashes, records, artifacts, gaps, overall)
        report_sha256 = sha_text(document)
        report_rel = 'docs/delivery/' + request['id'] + '-candidate.md'
        receipt_rel = '.framework/local-state/delivery/' + request['id'] + '.json'
        receipt = {'schema': RECEIPT_SCHEMA, 'id': request['id'],
                   'request_sha256': sha_text(canonical(request)), 'input_hashes': source_hashes,
                   'report': report_rel, 'report_sha256': report_sha256, 'execution': 'NOT_RUN'}
        old_document, old_receipt = existing(root, report_rel, receipt_rel, request['id'])
        result = {'status': 'DRY_RUN' if dry_run else None, 'overall': overall, 'gaps': gaps,
                  'records': records, 'artifacts': artifacts, 'report': report_rel, 'receipt': receipt_rel,
                  'report_sha256': report_sha256, 'request': request_rel, 'release': 'NOT_RUN',
                  'execution': 'NOT_RUN'}
        if dry_run:
            return dict(result, write='NOT_RUN')
        if old_document == document and old_receipt == receipt:
            return dict(result, status='UNCHANGED', write='UNCHANGED')
        status = 'UPDATED' if old_document is not None else 'RECORDED'
        try:
            atomic(root, report_rel, document)
            atomic(root, receipt_rel, encoded(receipt))
        except (OSError, ValueError):
            if old_document is None:
                safe_path(root, report_rel).unlink(missing_ok=True)
            else:
                atomic(root, report_rel, old_document)
            raise
        return dict(result, status=status, write=status)
    except ValueError as exc:
        message = str(exc)
        if message.startswith('CANDIDATE_') or 'SYMLINK' in message or 'PATH_ESCAPE' in message:
            raise
        if 'STALE' in message:
            raise ValueError('CANDIDATE_STALE') from exc
        raise ValueError('CANDIDATE_INPUT') from exc
    except (KeyError, TypeError) as exc:
        raise ValueError('CANDIDATE_INPUT') from exc
