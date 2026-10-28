"""Evidence-checked, privacy-bounded handoff from product observations to design input."""
import hashlib
import json
from pathlib import Path
import re

from .product_recon import (COLLECTIONS, DRAFT_SCHEMA, MAX_BYTES, depth_within,
                            product_public_block, sha_value, validate_product_draft)
from .reverse_adapters import auto_root, behavior_contract, observation_request_sha256
from .reverse_request import canonical, profile_request, valid_id
from .reverse_v2 import encoded, sha_text
from .reverse_web import load_snapshot
from .storage import atomic, safe_path


SCHEMA = 'product-design-handoff/v1'
DESIGN_INPUT = 'docs/project/design-input.md'
TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}')


def integrity():
    raise ValueError('PRODUCT_HANDOFF_INTEGRITY')


def stale():
    raise ValueError('PRODUCT_HANDOFF_STALE')


def conflict():
    raise ValueError('PRODUCT_HANDOFF_CONFLICT')


def read_bounded(root, rel):
    try:
        path = safe_path(root, rel)
        if not path.is_file():
            integrity()
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('PRODUCT_HANDOFF_LIMIT')
        raw = path.read_bytes()
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, KeyError, TypeError):
        integrity()
    except OSError:
        integrity()
    if not depth_within(value):
        raise ValueError('PRODUCT_HANDOFF_LIMIT')
    return value


def validate_record(root, request, plan, observation, record):
    if (not isinstance(record, dict) or record.get('schema') != 'reverse-observation/v1'
            or record.get('id') != observation['id'] or record.get('status') != 'RECORDED'
            or record.get('plan_sha256') != plan['plan_sha256']
            or record.get('target_sha256') != plan['target'].get('target_sha256')):
        stale()
    expected_provenance = 'STATIC_SUPPORTED' if observation['action'] == 'static' else 'DYNAMIC_OBSERVED'
    if record.get('provenance') != expected_provenance:
        integrity()
    if record.get('request_sha256') != observation_request_sha256(request, plan, observation):
        integrity()
    raw_status = record.get('raw_status')
    if raw_status == 'RAW_RETAINED':
        rel = auto_root(request['id']) + '/raw/' + observation['id'] + '.txt'
        if (request['evidence']['raw'] != 'retain' or record.get('raw_path') != rel
                or not valid_hash(record.get('raw_sha256'))):
            integrity()
        try:
            raw = safe_path(root, rel).read_bytes()
        except OSError:
            stale()
        if hashlib.sha256(raw).hexdigest() != record['raw_sha256']:
            stale()
    elif raw_status == 'NO_OUTPUT':
        if record.get('raw_path') or record.get('raw_sha256'):
            integrity()
    elif raw_status == 'RAW_DISCARDED':
        if request['evidence']['raw'] != 'discard' or record.get('raw_path'):
            integrity()
    else:
        integrity()


def valid_hash(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[0-9a-f]{64}', value))


def validate_target(root, request, plan):
    try:
        if request['target']['kind'] == 'url':
            snapshot_sha = plan['target'].get('target_sha256')
            if not valid_hash(snapshot_sha):
                integrity()
            manifest = load_snapshot(root, request['id'], snapshot_sha)
            if manifest.get('id') != request['id'] or manifest.get('original_url') != request['target']['url']:
                integrity()
        else:
            profile = profile_request(request)
            if profile.get('target_sha256') != plan['target'].get('target_sha256'):
                stale()
    except ValueError as exc:
        if 'STALE' in str(exc):
            stale()
        integrity()


def load_valid_source(root, request_id):
    if not valid_id(request_id):
        raise ValueError('INVALID_PRODUCT_HANDOFF')
    base = auto_root(request_id)
    request = read_bounded(root, base + '/request.json')
    product = read_bounded(root, base + '/product-recon.json')
    try:
        from .reverse_request import validate_request
        validate_request(request)
    except (ValueError, KeyError, TypeError):
        integrity()
    if request['id'] != request_id or product.get('plan_sha256') is None:
        integrity()
    plan_sha = product['plan_sha256']
    if not valid_hash(plan_sha):
        integrity()
    plan = read_bounded(root, base + '/plans/' + plan_sha + '.json')
    body = {key: value for key, value in plan.items() if key != 'plan_sha256'}
    if (plan.get('schema') != 'toolchain-plan/v1' or plan.get('status') != 'READY'
            or plan.get('plan_sha256') != plan_sha or sha_text(canonical(body)) != plan_sha):
        integrity()
    contract = read_bounded(root, base + '/behavior-contract.json')
    if product.get('behavior_contract_sha256') != sha_value(contract):
        integrity()
    records = []
    for observation in request['observations']:
        record = read_bounded(root, base + '/observations/' + observation['id'] + '.json')
        validate_record(root, request, plan, observation, record)
        records.append(record)
    try:
        expected_contract = behavior_contract(request, plan, records)
    except (ValueError, KeyError, TypeError):
        integrity()
    if sha_value(contract) != sha_value(expected_contract):
        integrity()
    draft = {'schema': DRAFT_SCHEMA, 'id': request_id, 'plan_sha256': plan_sha,
             **{name: product.get(name) for name in COLLECTIONS + ('exclusions',)}}
    try:
        normalized = validate_product_draft(draft, request, plan, records=records)
    except ValueError as exc:
        if 'LIMIT' in str(exc):
            raise ValueError('PRODUCT_HANDOFF_LIMIT') from exc
        integrity()
    if (product.get('schema') != 'product-recon/v1' or product.get('id') != request_id
            or product.get('draft_sha256') != sha_value(normalized)
            or product.get('runtime_validation') != 'NOT_RUN'
            or product.get('source_map_evidence') is not False
            or product.get('implementation_approved') is not False):
        integrity()
    try:
        product_public_block(product)
        canonical_product = safe_path(root, base + '/product-recon.json').read_bytes()
    except (ValueError, KeyError, TypeError, OSError):
        integrity()
    if canonical_product != encoded(product).encode('utf-8'):
        integrity()
    validate_target(root, request, plan)
    return request, plan, contract, product


def public_token(value):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        integrity()
    return value


def render_design(product, product_sha256):
    lines = [
        '<!-- product-design-handoff:' + product['id'] + ' -->',
        '# 产品观察设计输入（待确认）', '',
        '本草案仅用于后续 DISCOVERY 与 OpenSpec 设计讨论，不是已批准需求或实现证明。', '',
        '## 来源与门禁', '',
        '- 逆向 ID：`' + product['id'] + '`',
        '- 产品视图 SHA-256：`' + product_sha256 + '`',
        '- 设计批准：`NEEDS_DESIGN_APPROVAL`',
        '- 运行验证：`NOT_RUN`；源码地图证据：`False`；实现批准：`False`。', '',
        '## 产品结构与证据', '',
    ]
    for name in COLLECTIONS:
        for item in product[name]:
            proof = item['evidence']
            line = ('- `' + item['id'] + '`（' + name + '）：`' + proof['provenance']
                    + '` / `' + proof['confidence'] + '`')
            if name in ('screens', 'components'):
                observed = [public_token(value) for value in item['states_observed']]
                unobserved = [public_token(value) for value in item['states_unobserved']]
                line += '；已观察=' + (','.join(observed) or '无')
                line += '；未观察=' + (','.join(unobserved) or '无')
            lines.append(line)
    lines.extend(['', '## 排除范围', ''])
    if product['exclusions']:
        for item in product['exclusions']:
            lines.append('- `' + item['kind'] + '`：关联 ' + str(len(item['related_ids'])) + ' 项；私有原因不公开。')
    else:
        lines.append('- 无已声明排除项。')
    lines.extend([
        '', '## 后续流程', '',
        '人工确认设计后，依次进入 DISCOVERY、OpenSpec SPEC/PLAN、TDD、评审和适用环境验证。',
        '未观察、排除及推断内容不得自动转为已实现或已验证事实。',
        '完整私有自由文本和原始证据不复制到本草案。',
        '<!-- product-design-handoff:end -->', '',
    ])
    return '\n'.join(lines)


def receipt_for(product, product_sha256, design_sha256):
    return {
        'schema': SCHEMA, 'id': product['id'], 'plan_sha256': product['plan_sha256'],
        'product_sha256': product_sha256, 'draft_sha256': product['draft_sha256'],
        'behavior_contract_sha256': product['behavior_contract_sha256'],
        'design_input': DESIGN_INPUT, 'design_input_sha256': design_sha256,
        'design_approval': 'NEEDS_DESIGN_APPROVAL', 'runtime_validation': 'NOT_RUN',
        'source_map_evidence': False, 'implementation_approved': False,
    }


def check_existing(root, receipt_rel, product):
    design_path = safe_path(root, DESIGN_INPUT)
    receipt_path = safe_path(root, receipt_rel)
    if not design_path.exists() and not receipt_path.exists():
        return None, None
    if not design_path.is_file() or not receipt_path.is_file():
        conflict()
    try:
        previous = read_bounded(root, receipt_rel)
        document = design_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError, ValueError):
        conflict()
    expected_fields = {
        'schema', 'id', 'plan_sha256', 'product_sha256', 'draft_sha256',
        'behavior_contract_sha256', 'design_input', 'design_input_sha256',
        'design_approval', 'runtime_validation', 'source_map_evidence', 'implementation_approved',
    }
    if (not isinstance(previous, dict) or set(previous) != expected_fields
            or previous.get('schema') != SCHEMA or previous.get('id') != product['id']
            or previous.get('plan_sha256') != product['plan_sha256']
            or previous.get('behavior_contract_sha256') != product['behavior_contract_sha256']
            or not valid_hash(previous.get('product_sha256'))
            or not valid_hash(previous.get('draft_sha256'))
            or previous.get('design_input') != DESIGN_INPUT
            or previous.get('design_input_sha256') != sha_text(document)
            or previous.get('design_approval') != 'NEEDS_DESIGN_APPROVAL'
            or previous.get('runtime_validation') != 'NOT_RUN'
            or previous.get('source_map_evidence') is not False
            or previous.get('implementation_approved') is not False
            or document.count('<!-- product-design-handoff:' + product['id'] + ' -->') != 1
            or document.count('<!-- product-design-handoff:end -->') != 1):
        conflict()
    return document, previous


def handoff(root, request_id, dry_run=False):
    root = Path(root)
    unused_request, unused_plan, unused_contract, product = load_valid_source(root, request_id)
    del unused_request, unused_plan, unused_contract
    product_rel = auto_root(request_id) + '/product-recon.json'
    product_sha256 = hashlib.sha256(safe_path(root, product_rel).read_bytes()).hexdigest()
    document = render_design(product, product_sha256)
    design_sha256 = sha_text(document)
    receipt = receipt_for(product, product_sha256, design_sha256)
    receipt_rel = auto_root(request_id) + '/design-handoff.json'
    old_document, old_receipt = check_existing(root, receipt_rel, product)
    result = {
        'design_approval': 'NEEDS_DESIGN_APPROVAL', 'product_sha256': product_sha256,
        'design_input': DESIGN_INPUT, 'design_input_sha256': design_sha256,
        'handoff_receipt': receipt_rel, 'runtime_validation': 'NOT_RUN',
        'source_map_evidence': False, 'implementation_approved': False,
        'next_action': 'Review design input, then enter ordinary DISCOVERY and OpenSpec planning',
    }
    if dry_run:
        return dict(result, status='DRY_RUN', write='NOT_RUN')
    if old_document == document and old_receipt == receipt:
        return dict(result, status='UNCHANGED', write='UNCHANGED')
    status = 'UPDATED' if old_document is not None else 'RECORDED'
    receipt_text = encoded(receipt)
    try:
        atomic(root, DESIGN_INPUT, document)
        atomic(root, receipt_rel, receipt_text)
    except (OSError, ValueError):
        if old_document is None:
            safe_path(root, DESIGN_INPUT).unlink(missing_ok=True)
        else:
            atomic(root, DESIGN_INPUT, old_document)
        raise
    return dict(result, status=status, write=status)
