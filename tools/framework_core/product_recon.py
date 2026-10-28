"""Validated, evidence-bound product observations derived from automatic reverse runs."""
import copy
import hashlib
import json
from pathlib import Path
import re

from .storage import atomic, safe_path


DRAFT_SCHEMA = 'product-recon-draft/v1'
PRODUCT_SCHEMA = 'product-recon/v1'
MAX_BYTES = 1024 * 1024
MAX_DEPTH = 32
MAX_ITEMS = 250
MAX_TOTAL_ITEMS = 1000
MAX_STRING = 4000
MAX_REFERENCES = 100
COLLECTIONS = ('screens', 'flows', 'components', 'entities')
ID_PREFIX = {'screens': 'S', 'flows': 'F', 'components': 'C', 'entities': 'E'}
PROVENANCES = {'STATIC_SUPPORTED', 'DYNAMIC_OBSERVED', 'INFERRED'}
CONFIDENCE = {'HIGH', 'MEDIUM', 'LOW'}
EXCLUSION_KINDS = {
    'LICENSED_CONTENT', 'NETWORK_EFFECT', 'PRIVATE_DATA', 'PARTNER',
    'HARDWARE', 'REGULATED', 'OUT_OF_SCOPE', 'OTHER',
}


def invalid():
    raise ValueError('INVALID_PRODUCT_RECON')


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        invalid()


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_STRING:
        invalid()
    return value


def text_list(value, maximum=MAX_REFERENCES, unique=False):
    if not isinstance(value, list) or len(value) > maximum:
        invalid()
    for item in value:
        text(item)
    if unique and len(set(value)) != len(value):
        invalid()
    return list(value)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def sha_value(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def product_sha256(product):
    return hashlib.sha256(encoded(product).encode('utf-8')).hexdigest()


def depth_within(value, maximum=MAX_DEPTH):
    stack = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        if depth > maximum:
            return False
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return True


def read_product_draft(path):
    path = Path(path)
    try:
        if path.is_symlink() or not path.is_file():
            invalid()
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('PRODUCT_RECON_LIMIT')
        raw = path.read_bytes()
        try:
            value = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            invalid()
        except RecursionError:
            raise ValueError('PRODUCT_RECON_LIMIT')
    except OSError:
        invalid()
    if not depth_within(value):
        raise ValueError('PRODUCT_RECON_LIMIT')
    return value


def validate_evidence(value, declared, records):
    exact(value, ('provenance', 'observations', 'confidence'))
    provenance = value['provenance']
    if provenance not in PROVENANCES or value['confidence'] not in CONFIDENCE:
        invalid()
    observations = text_list(value['observations'], unique=True)
    if provenance == 'INFERRED':
        if observations:
            invalid()
        return
    if not observations:
        invalid()
    for observation_id in observations:
        action = declared.get(observation_id)
        if action is None:
            raise ValueError('PRODUCT_RECON_EVIDENCE')
        expected = 'STATIC_SUPPORTED' if action == 'static' else 'DYNAMIC_OBSERVED'
        if provenance != expected:
            raise ValueError('PRODUCT_RECON_EVIDENCE')
        if records is not None:
            record = records.get(observation_id)
            if (not record or record.get('status') != 'RECORDED'
                    or record.get('provenance') != provenance):
                raise ValueError('PRODUCT_RECON_EVIDENCE')


def validate_product_draft(draft, request, plan, records=None):
    exact(draft, ('schema', 'id', 'plan_sha256', 'screens', 'flows', 'components',
                  'entities', 'exclusions'))
    if (draft['schema'] != DRAFT_SCHEMA or draft['id'] != request['id']
            or draft['plan_sha256'] != plan['plan_sha256'] or not depth_within(draft)):
        if not depth_within(draft):
            raise ValueError('PRODUCT_RECON_LIMIT')
        invalid()
    if canonical(draft).encode('utf-8').__len__() > MAX_BYTES:
        raise ValueError('PRODUCT_RECON_LIMIT')
    collections = {}
    total = 0
    for name in COLLECTIONS + ('exclusions',):
        value = draft[name]
        if not isinstance(value, list) or len(value) > MAX_ITEMS:
            raise ValueError('PRODUCT_RECON_LIMIT')
        total += len(value)
        collections[name] = value
    if total > MAX_TOTAL_ITEMS:
        raise ValueError('PRODUCT_RECON_LIMIT')

    declared = {item['id']: item['action'] for item in request['observations']}
    record_map = None
    if records is not None:
        record_map = {}
        for record in records:
            if record.get('plan_sha256') != plan['plan_sha256']:
                raise ValueError('PRODUCT_RECON_EVIDENCE')
            record_map[record.get('id')] = record

    normalized = copy.deepcopy(draft)
    identifiers = {}
    for name in COLLECTIONS:
        seen = set()
        for item in normalized[name]:
            if not isinstance(item, dict) or 'id' not in item:
                invalid()
            identifier = text(item['id'])
            if not re.fullmatch(ID_PREFIX[name] + r'[0-9]{2,}', identifier) or identifier in seen:
                invalid()
            seen.add(identifier)
            validate_evidence(item.get('evidence'), declared, record_map)
        identifiers[name] = seen

    for screen in normalized['screens']:
        exact(screen, ('id', 'name', 'purpose', 'component_ids', 'states_observed',
                       'states_unobserved', 'evidence'))
        text(screen['name'])
        text(screen['purpose'])
        observed = text_list(screen['states_observed'], maximum=50, unique=True)
        unobserved = text_list(screen['states_unobserved'], maximum=50, unique=True)
        if set(observed) & set(unobserved):
            invalid()
        for component_id in text_list(screen['component_ids'], unique=True):
            if component_id not in identifiers['components']:
                invalid()
    for flow in normalized['flows']:
        exact(flow, ('id', 'name', 'goal', 'screen_ids', 'steps', 'evidence'))
        text(flow['name'])
        text(flow['goal'])
        text_list(flow['steps'])
        for screen_id in text_list(flow['screen_ids'], unique=True):
            if screen_id not in identifiers['screens']:
                invalid()
    for component in normalized['components']:
        exact(component, ('id', 'name', 'kind', 'states_observed', 'states_unobserved', 'evidence'))
        text(component['name'])
        text(component['kind'])
        observed = text_list(component['states_observed'], maximum=50, unique=True)
        unobserved = text_list(component['states_unobserved'], maximum=50, unique=True)
        if set(observed) & set(unobserved):
            invalid()
    for entity in normalized['entities']:
        exact(entity, ('id', 'name', 'fields', 'relationships', 'evidence'))
        text(entity['name'])
        text_list(entity['fields'])
        text_list(entity['relationships'])

    all_ids = set().union(*identifiers.values())
    for exclusion in normalized['exclusions']:
        exact(exclusion, ('kind', 'reason', 'related_ids'))
        if exclusion['kind'] not in EXCLUSION_KINDS:
            invalid()
        text(exclusion['reason'])
        for identifier in text_list(exclusion['related_ids'], unique=True):
            if identifier not in all_ids:
                invalid()
    for name in COLLECTIONS:
        normalized[name].sort(key=lambda item: item['id'])
    normalized['exclusions'].sort(key=lambda item: (item['kind'], item['reason'], item['related_ids']))
    return normalized


def preview_product_recon(draft, request, plan):
    normalized = validate_product_draft(draft, request, plan)
    return {
        'status': 'READY', 'schema': DRAFT_SCHEMA, 'draft_sha256': sha_value(normalized),
        'counts': {name: len(normalized[name]) for name in COLLECTIONS},
        'exclusions': len(normalized['exclusions']), 'write': 'NOT_RUN',
    }


def generate_product_recon(root, request, plan, contract, records, draft):
    if (not isinstance(contract, dict) or contract.get('id') != request['id']
            or contract.get('plan_sha256') != plan['plan_sha256']):
        raise ValueError('PRODUCT_RECON_EVIDENCE')
    normalized = validate_product_draft(draft, request, plan, records=records)
    product = {
        'schema': PRODUCT_SCHEMA, 'id': request['id'], 'plan_sha256': plan['plan_sha256'],
        'behavior_contract_sha256': sha_value(contract), 'draft_sha256': sha_value(normalized),
        **{name: normalized[name] for name in COLLECTIONS + ('exclusions',)},
        'runtime_validation': 'NOT_RUN', 'source_map_evidence': False,
        'implementation_approved': False,
    }
    rel = '.framework/local-state/reverse/auto/' + request['id'] + '/product-recon.json'
    path = safe_path(root, rel)
    if path.is_symlink():
        raise ValueError('INVALID_PRODUCT_RECON')
    content = encoded(product)
    sha256 = hashlib.sha256(content.encode('utf-8')).hexdigest()
    existed = path.is_file()
    if existed and path.read_text(encoding='utf-8') == content:
        status = 'UNCHANGED'
    else:
        atomic(root, rel, content)
        status = 'UPDATED' if existed else 'RECORDED'
    return {'status': status, 'path': rel, 'sha256': sha256, 'product': product}


def product_public_block(product):
    exact(product, ('schema', 'id', 'plan_sha256', 'behavior_contract_sha256', 'draft_sha256',
                    'screens', 'flows', 'components', 'entities', 'exclusions',
                    'runtime_validation', 'source_map_evidence', 'implementation_approved'))
    lines = [
        '<!-- product-recon:start -->', '## Product behavior recon', '',
        'Schema: `product-recon/v1`', '',
        'Artifact SHA-256: `' + product_sha256(product) + '`', '',
        'Counts: `screens={screens}, flows={flows}, components={components}, entities={entities}, exclusions={exclusions}`'.format(
            **{name: len(product[name]) for name in COLLECTIONS + ('exclusions',)}), '',
    ]
    for name in COLLECTIONS:
        for item in product[name]:
            evidence = item['evidence']
            line = '- ' + item['id'] + ': `' + evidence['provenance'] + '` / `' + evidence['confidence'] + '`'
            if name in ('screens', 'components'):
                line += '; observed=' + str(len(item['states_observed'])) + ', unobserved=' + str(len(item['states_unobserved']))
            lines.append(line)
    if product['exclusions']:
        counts = {}
        for item in product['exclusions']:
            counts[item['kind']] = counts.get(item['kind'], 0) + 1
        lines.append('Exclusion classes: `' + ','.join(
            key + '=' + str(counts[key]) for key in sorted(counts)) + '`')
    lines.extend([
        '', 'Runtime validation: `NOT_RUN`; source-map evidence: `False`; implementation approved: `False`.',
        'Private free text and raw evidence are not copied into this public section.',
        '<!-- product-recon:end -->', '',
    ])
    return '\n'.join(lines)
