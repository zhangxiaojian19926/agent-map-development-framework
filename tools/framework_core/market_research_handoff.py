"""Offline public-market research handoff. Never accesses or verifies sources."""
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .product_recon import depth_within
from .reverse_v2 import canonical, encoded, sha_text, valid_id
from .storage import atomic, safe_path


SCHEMA = 'market-research-request/v1'
RECEIPT_SCHEMA = 'market-research-receipt/v1'
REQUEST_FIELDS = {'schema', 'id', 'question', 'sources', 'facts', 'inferences', 'limitations', 'design'}
SOURCE_FIELDS = {'id', 'url', 'accessed_at', 'content_sha256'}
FACT_FIELDS = {'id', 'statement', 'source_ids'}
INFERENCE_FIELDS = {'id', 'statement', 'fact_ids', 'confidence'}
DESIGN_FIELDS = {'summary', 'opportunities', 'constraints'}
RECEIPT_FIELDS = {
    'schema', 'id', 'request_sha256', 'report', 'report_sha256',
    'design_status', 'source_verification', 'execution',
}
CONFIDENCE = {'HIGH', 'MEDIUM', 'LOW'}
SHA256 = re.compile(r'[0-9a-f]{64}')
ISO_DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
PRIVATE_MARKERS = (
    '.framework/', '.git/', 'docs/project/reverse/', 'reverse/raw/',
    'reverse/output/', 'local-state/rea/', 'local-state/product',
)
MAX_BYTES = 1024 * 1024
MAX_ITEMS = 1000


def input_error():
    raise ValueError('RESEARCH_INPUT')


def conflict():
    raise ValueError('RESEARCH_CONFLICT')


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        input_error()


def public_text(value, maximum=4000):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(char) < 32 or ord(char) == 127 for char in value)
            or '<!--' in value or '-->' in value):
        input_error()
    normalized = value.replace('\\', '/').lower()
    if any(marker in normalized for marker in PRIVATE_MARKERS):
        input_error()
    return value


def text_list(value, allow_empty=True):
    if not isinstance(value, list) or len(value) > MAX_ITEMS or (not allow_empty and not value):
        input_error()
    for item in value:
        public_text(item)
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
        raise ValueError('RESEARCH_LIMIT')
    return rel, value


def valid_url(value):
    if not isinstance(value, str) or len(value) > 4000 or any(ord(char) < 32 or ord(char) == 127 for char in value):
        input_error()
    public_text(value)
    try:
        parsed = urlsplit(value)
        if (parsed.scheme.lower() not in {'http', 'https'} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None):
            input_error()
        unused_port = parsed.port
        del unused_port
    except (ValueError, UnicodeError):
        input_error()
    return value


def validate_sources(sources):
    if not isinstance(sources, list) or not sources or len(sources) > MAX_ITEMS:
        input_error()
    records = {}
    for source in sources:
        exact(source, SOURCE_FIELDS)
        identifier = source['id']
        if not valid_id(identifier) or identifier in records:
            input_error()
        valid_url(source['url'])
        accessed_at = source['accessed_at']
        if not isinstance(accessed_at, str) or not ISO_DATE.fullmatch(accessed_at):
            input_error()
        try:
            date.fromisoformat(accessed_at)
        except ValueError:
            input_error()
        if not isinstance(source['content_sha256'], str) or not SHA256.fullmatch(source['content_sha256']):
            input_error()
        records[identifier] = source
    return records


def validate_facts(facts, sources):
    if not isinstance(facts, list) or len(facts) > MAX_ITEMS:
        input_error()
    records = {}
    for fact in facts:
        exact(fact, FACT_FIELDS)
        identifier = fact['id']
        if not valid_id(identifier) or identifier in records:
            input_error()
        public_text(fact['statement'])
        refs = fact['source_ids']
        if (not isinstance(refs, list) or not refs or len(refs) > MAX_ITEMS
                or any(not valid_id(ref) or ref not in sources for ref in refs)
                or len(set(refs)) != len(refs)):
            input_error()
        records[identifier] = fact
    return records


def validate_inferences(inferences, facts):
    if not isinstance(inferences, list) or len(inferences) > MAX_ITEMS:
        input_error()
    records = {}
    for inference in inferences:
        exact(inference, INFERENCE_FIELDS)
        identifier = inference['id']
        if not valid_id(identifier) or identifier in records:
            input_error()
        public_text(inference['statement'])
        refs = inference['fact_ids']
        if (not isinstance(refs, list) or not refs or len(refs) > MAX_ITEMS
                or any(not valid_id(ref) or ref not in facts for ref in refs)
                or len(set(refs)) != len(refs) or inference['confidence'] not in CONFIDENCE):
            input_error()
        records[identifier] = inference
    return records


def validate(request):
    exact(request, REQUEST_FIELDS)
    if request['schema'] != SCHEMA or not valid_id(request['id']):
        input_error()
    public_text(request['question'], 2000)
    sources = validate_sources(request['sources'])
    facts = validate_facts(request['facts'], sources)
    validate_inferences(request['inferences'], facts)
    text_list(request['limitations'])
    exact(request['design'], DESIGN_FIELDS)
    public_text(request['design']['summary'])
    text_list(request['design']['opportunities'])
    text_list(request['design']['constraints'])


def render(request, request_sha256):
    lines = [
        '<!-- market-research:' + request['id'] + ' -->',
        '# 市场研究交接（待确认）', '',
        '本报告只整理当前 Agent 提供的公开研究声明，不访问网络，不证明来源在线或内容真实。',
        '设计草案仍需经过 DISCOVERY、SPEC 和人工批准，不是需求、实现或发布授权。', '',
        '## 研究问题', '', request['question'], '',
        '- 研究 ID：`' + request['id'] + '`',
        '- 请求 SHA-256：`' + request_sha256 + '`',
        '- design_status=NEEDS_DESIGN_APPROVAL',
        '- source_verification=NOT_RUN',
        '- execution=NOT_RUN', '',
        '## 公开来源', '',
    ]
    for source in request['sources']:
        lines.extend([
            '### `' + source['id'] + '`', '',
            '- URL：' + source['url'],
            '- 访问日期：`' + source['accessed_at'] + '`',
            '- 声明内容 SHA-256：`' + source['content_sha256'] + '`',
            '- 在线核验：`NOT_RUN`', '',
        ])
    lines.extend(['## 来源事实', ''])
    if request['facts']:
        for fact in request['facts']:
            lines.append('- `' + fact['id'] + '`：' + fact['statement'])
            lines.append('  - 来源：' + '、'.join('`' + ref + '`' for ref in fact['source_ids']))
    else:
        lines.append('- 未声明来源事实。')
    lines.extend(['', '## Agent 推断', ''])
    if request['inferences']:
        for inference in request['inferences']:
            lines.append('- `' + inference['id'] + '`（置信度 `' + inference['confidence'] + '`）：' + inference['statement'])
            lines.append('  - 依据事实：' + '、'.join('`' + ref + '`' for ref in inference['fact_ids']))
    else:
        lines.append('- 未声明 Agent 推断。')
    lines.extend(['', '## 研究局限', ''])
    if request['limitations']:
        lines.extend('- ' + item for item in request['limitations'])
    else:
        lines.append('- 未声明；不代表没有局限。')
    design = request['design']
    lines.extend(['', '## 待确认设计草案', '', design['summary'], '', '### 机会', ''])
    lines.extend(('- ' + item for item in design['opportunities']) if design['opportunities'] else ['- 未声明。'])
    lines.extend(['', '### 约束', ''])
    lines.extend(('- ' + item for item in design['constraints']) if design['constraints'] else ['- 未声明。'])
    lines.extend([
        '', '## 后续门禁', '',
        '人工确认研究方向和设计草案后，才能进入普通 DISCOVERY 与 OpenSpec SPEC/PLAN 流程。',
        '本交接不创建或批准 OpenSpec，不覆盖 `docs/project/design-input.md`，不生成业务代码或发布证据。',
        '<!-- market-research:end -->', '',
    ])
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
    if (not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS
            or receipt['schema'] != RECEIPT_SCHEMA or receipt['id'] != identifier
            or not isinstance(receipt['request_sha256'], str) or not SHA256.fullmatch(receipt['request_sha256'])
            or receipt['report'] != report_rel or receipt['report_sha256'] != sha_text(document)
            or receipt['design_status'] != 'NEEDS_DESIGN_APPROVAL'
            or receipt['source_verification'] != 'NOT_RUN' or receipt['execution'] != 'NOT_RUN'
            or document.count('<!-- market-research:' + identifier + ' -->') != 1
            or document.count('<!-- market-research:end -->') != 1):
        conflict()
    return document, receipt


def generate(root, request_path, dry_run=False):
    root = Path(root).resolve()
    try:
        request_rel, request = read_json(root, request_path)
        validate(request)
        request_sha256 = sha_text(canonical(request))
        document = render(request, request_sha256)
        report_sha256 = sha_text(document)
        report_rel = 'docs/project/market-research/' + request['id'] + '.md'
        receipt_rel = '.framework/local-state/market-research/' + request['id'] + '.json'
        receipt = {
            'schema': RECEIPT_SCHEMA, 'id': request['id'], 'request_sha256': request_sha256,
            'report': report_rel, 'report_sha256': report_sha256,
            'design_status': 'NEEDS_DESIGN_APPROVAL', 'source_verification': 'NOT_RUN',
            'execution': 'NOT_RUN',
        }
        old_document, old_receipt = existing(root, report_rel, receipt_rel, request['id'])
        result = {
            'status': 'DRY_RUN' if dry_run else None,
            'id': request['id'], 'request': request_rel, 'request_sha256': request_sha256,
            'report': report_rel, 'receipt': receipt_rel, 'report_sha256': report_sha256,
            'design_status': 'NEEDS_DESIGN_APPROVAL', 'source_verification': 'NOT_RUN',
            'execution': 'NOT_RUN',
        }
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
        if message.startswith('RESEARCH_') or 'SYMLINK' in message or 'PATH_ESCAPE' in message:
            raise
        raise ValueError('RESEARCH_INPUT') from exc
    except (KeyError, TypeError) as exc:
        raise ValueError('RESEARCH_INPUT') from exc
