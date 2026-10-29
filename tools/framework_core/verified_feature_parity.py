"""Evidence-bound feature parity reports. This module never executes verification."""
import hashlib
import json
from pathlib import Path
import re

from .product_design_handoff import load_valid_source
from .product_recon import depth_within
from .reverse_adapters import auto_root
from .reverse_v2 import canonical, encoded, sha_text, valid_id
from .storage import atomic, safe_path


SCHEMA = 'feature-parity-request/v1'
EVIDENCE_SCHEMA = 'verification-evidence/v1'
RECEIPT_SCHEMA = 'feature-parity-receipt/v1'
MAX_BYTES = 1024 * 1024
MAX_ITEMS = 1000
TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$')
REQUEST_FIELDS = {'schema', 'id', 'change', 'product_collections', 'specs', 'tasks', 'evidence',
                  'items', 'product_exclusions', 'scenario_exclusions', 'severity_policy'}
ITEM_FIELDS = {'id', 'product_id', 'priority', 'requirement', 'scenarios', 'tasks'}
RECORD_FIELDS = {'id', 'requirement', 'scenario', 'task', 'test', 'environment', 'result',
                 'category', 'artifact', 'reason'}
FINDING_FIELDS = {'id', 'severity', 'status', 'category', 'evidence_id'}
PRIORITIES = {'MUST', 'SHOULD', 'COULD'}
CATEGORIES = {'FUNCTION', 'VISUAL', 'ACCESSIBILITY', 'BRAND'}
RESULTS = {'PASS', 'FAIL', 'NOT_RUN', 'INFRA_ERROR', 'N/A'}
EXCLUSION_KINDS = {'OUT_OF_SCOPE', 'DEFERRED', 'NOT_APPLICABLE'}


def input_error():
    raise ValueError('PARITY_INPUT')


def evidence_error():
    raise ValueError('PARITY_EVIDENCE')


def conflict():
    raise ValueError('PARITY_CONFLICT')


def token(value):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        input_error()
    return value


def relative(root, path):
    try:
        candidate = Path(path)
        rel = candidate.relative_to(Path(root).absolute()) if candidate.is_absolute() else candidate
        safe_path(root, str(rel))
        return rel.as_posix()
    except (ValueError, OSError) as exc:
        if 'SYMLINK' in str(exc) or 'PATH_ESCAPE' in str(exc):
            raise
        input_error()


def read_json(root, path, error=input_error):
    rel = relative(root, path)
    try:
        source = safe_path(root, rel)
        if not source.is_file():
            error()
        if source.stat().st_size > MAX_BYTES:
            raise ValueError('PARITY_LIMIT')
        value = json.loads(source.read_bytes().decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        error()
    except OSError:
        error()
    if not depth_within(value):
        raise ValueError('PARITY_LIMIT')
    return rel, value


def exact(value, fields, error=input_error):
    if not isinstance(value, dict) or set(value) != fields:
        error()


def source_ref(value):
    exact(value, {'path', 'sha256'})
    if (not isinstance(value['path'], str) or not isinstance(value['sha256'], str)
            or not re.fullmatch(r'[0-9a-f]{64}', value['sha256'])):
        input_error()


def bound_file(root, ref, prefix, error=ValueError('PARITY_STALE')):
    source_ref(ref)
    rel = relative(root, ref['path'])
    if not rel.startswith(prefix):
        input_error()
    try:
        raw = safe_path(root, rel).read_bytes()
    except OSError:
        raise error
    if len(raw) > MAX_BYTES:
        raise ValueError('PARITY_LIMIT')
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise error
    return rel, raw


def parse_specs(root, refs, change):
    if not isinstance(refs, list) or not refs or len(refs) > MAX_ITEMS:
        input_error()
    scenarios = {}
    hashes = {}
    for ref in refs:
        rel, raw = bound_file(root, ref, 'openspec/changes/' + change + '/')
        if not rel.endswith('.md'):
            input_error()
        hashes[rel] = ref['sha256']
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            input_error()
        requirement = None
        for line in text.splitlines():
            if line.startswith('### Requirement:'):
                requirement = line[len('### Requirement:'):].strip()
                if not requirement or len(requirement) > 200:
                    input_error()
            elif line.startswith('#### Scenario:'):
                scenario = line[len('#### Scenario:'):].strip()
                key = (requirement, scenario)
                if not requirement or not scenario or len(scenario) > 200 or key in scenarios:
                    input_error()
                scenarios[key] = {'requirement': requirement, 'scenario': scenario, 'source': rel}
    if not scenarios:
        input_error()
    return scenarios, hashes


def parse_tasks(root, ref, change):
    source_ref(ref)
    rel, raw = bound_file(root, ref, 'openspec/changes/' + change + '/')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        input_error()
    tasks = {}
    pattern = re.compile(r'^- \[([ xX])\] ([A-Za-z0-9][A-Za-z0-9_.-]{0,79})(?:\s|$)')
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            identifier = match.group(2)
            if identifier in tasks:
                input_error()
            tasks[identifier] = match.group(1).lower() == 'x'
    return tasks, {rel: ref['sha256']}


def validate_items(request, products, scenarios, tasks):
    if not isinstance(request['items'], list) or len(request['items']) > MAX_ITEMS:
        input_error()
    item_ids, product_ids, scenario_ids, task_ids = set(), set(), set(), set()
    for item in request['items']:
        exact(item, ITEM_FIELDS)
        identifier = token(item['id'])
        if identifier in item_ids or item['priority'] not in PRIORITIES:
            input_error()
        item_ids.add(identifier)
        product_id = item['product_id']
        if product_id is not None:
            token(product_id)
            if product_id not in products or product_id in product_ids:
                input_error()
            product_ids.add(product_id)
        if not isinstance(item['requirement'], str) or not isinstance(item['scenarios'], list) or not item['scenarios']:
            input_error()
        if not isinstance(item['tasks'], list) or len(item['tasks']) > MAX_ITEMS:
            input_error()
        for scenario in item['scenarios']:
            key = (item['requirement'], scenario)
            if key not in scenarios or key in scenario_ids:
                input_error()
            scenario_ids.add(key)
        for task in item['tasks']:
            token(task)
            if task not in tasks or task in task_ids:
                input_error()
            task_ids.add(task)
    return product_ids, scenario_ids, task_ids


def validate_exclusions(request, products, scenarios, mapped_products, mapped_scenarios):
    product_exclusions = {}
    if not isinstance(request['product_exclusions'], list) or len(request['product_exclusions']) > MAX_ITEMS:
        input_error()
    for entry in request['product_exclusions']:
        exact(entry, {'product_id', 'kind'})
        identifier = token(entry['product_id'])
        if (identifier not in products or identifier in mapped_products
                or identifier in product_exclusions or entry['kind'] not in EXCLUSION_KINDS):
            input_error()
        product_exclusions[identifier] = entry['kind']
    scenario_exclusions = {}
    if not isinstance(request['scenario_exclusions'], list) or len(request['scenario_exclusions']) > MAX_ITEMS:
        input_error()
    for entry in request['scenario_exclusions']:
        exact(entry, {'requirement', 'scenario', 'priority', 'kind'})
        key = (entry['requirement'], entry['scenario'])
        if (key not in scenarios or key in mapped_scenarios or key in scenario_exclusions
                or entry['priority'] not in PRIORITIES - {'MUST'} or entry['kind'] not in EXCLUSION_KINDS):
            input_error()
        scenario_exclusions[key] = entry
    return product_exclusions, scenario_exclusions


def validate_evidence(root, request, scenarios, tasks):
    records, findings, hashes = {}, {}, {}
    if not isinstance(request['evidence'], list) or len(request['evidence']) > MAX_ITEMS:
        input_error()
    for ref in request['evidence']:
        rel, raw = bound_file(root, ref, 'docs/verification/' + request['change'] + '/', ValueError('PARITY_EVIDENCE'))
        hashes[rel] = ref['sha256']
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            evidence_error()
        if not depth_within(payload):
            raise ValueError('PARITY_LIMIT')
        exact(payload, {'schema', 'change', 'records', 'findings'}, evidence_error)
        if payload['schema'] != EVIDENCE_SCHEMA or payload['change'] != request['change']:
            evidence_error()
        if (not isinstance(payload['records'], list) or not isinstance(payload['findings'], list)
                or len(payload['records']) > MAX_ITEMS or len(payload['findings']) > MAX_ITEMS):
            evidence_error()
        for record in payload['records']:
            exact(record, RECORD_FIELDS, evidence_error)
            identifier = record['id']
            key = (record['requirement'], record['scenario'])
            if (not isinstance(identifier, str) or not TOKEN.fullmatch(identifier) or identifier in records
                    or key not in scenarios or record['task'] not in tasks
                    or not isinstance(record['test'], str) or not record['test'].strip()
                    or not isinstance(record['environment'], str) or not record['environment'].strip()
                    or len(record['test']) > 500 or len(record['environment']) > 200
                    or record['result'] not in RESULTS or record['category'] not in CATEGORIES):
                evidence_error()
            artifact = record['artifact']
            if artifact is not None:
                exact(artifact, {'path', 'sha256'}, evidence_error)
                try:
                    artifact_rel, unused = bound_file(root, artifact,
                        'docs/verification/' + request['change'] + '/', ValueError('PARITY_STALE'))
                    del unused
                except ValueError as exc:
                    if 'PARITY_STALE' in str(exc):
                        raise
                    evidence_error()
                record['artifact'] = dict(artifact, path=artifact_rel)
            if record['result'] == 'PASS' and artifact is None:
                evidence_error()
            if record['result'] in ('INFRA_ERROR', 'N/A'):
                if not isinstance(record['reason'], str) or not TOKEN.fullmatch(record['reason']):
                    evidence_error()
            elif record['reason'] is not None:
                evidence_error()
            records[identifier] = record
        for finding in payload['findings']:
            exact(finding, FINDING_FIELDS, evidence_error)
            identifier = finding['id']
            if (not isinstance(identifier, str) or not TOKEN.fullmatch(identifier) or identifier in findings
                    or finding['severity'] not in {'S1', 'S2', 'S3', 'S4'}
                    or finding['status'] not in {'OPEN', 'CLOSED'} or finding['category'] not in CATEGORIES
                    or finding['evidence_id'] not in records):
                evidence_error()
            findings[identifier] = finding
    return records, findings, hashes


def derive(request, products, scenarios, tasks, records, findings, product_exclusions, scenario_exclusions):
    items, gaps, diagnostics = [], [], []
    by_key = {}
    for record in records.values():
        by_key.setdefault((record['requirement'], record['scenario']), []).append(record)
        if record['category'] != 'FUNCTION':
            diagnostics.append({'id': record['id'], 'category': record['category'], 'result': record['result'],
                                'artifact': record['artifact']['path'] if record['artifact'] else None})
    for item in request['items']:
        product_id = item['product_id']
        provenance = None if product_id is None else products[product_id]['evidence']['provenance']
        target = ('NOT_OBSERVED' if provenance is None else
                  'INFERRED' if provenance == 'INFERRED' else 'OBSERVED')
        done = [tasks[task] for task in item['tasks']]
        implementation = 'IMPLEMENTED' if done and all(done) else ('PARTIAL' if any(done) else 'DECLARED')
        matched = [record for scenario in item['scenarios']
                   for record in by_key.get((item['requirement'], scenario), [])
                   if record['task'] in item['tasks']]
        functional = [record for record in matched if record['category'] == 'FUNCTION']
        if any(record['result'] == 'FAIL' for record in functional):
            verification = 'FAILED'
        elif all(any(record['result'] == 'PASS' and tasks[record['task']]
                     for record in by_key.get((item['requirement'], scenario), [])
                     if record['category'] == 'FUNCTION' and record['task'] in item['tasks'])
                 for scenario in item['scenarios']):
            verification = 'VERIFIED'
        else:
            verification = 'NOT_RUN'
        evidence_ids = sorted(record['id'] for record in matched)
        items.append({'id': item['id'], 'product_id': product_id, 'priority': item['priority'],
                      'target_evidence': target, 'implementation': implementation,
                      'verification': verification, 'evidence_ids': evidence_ids})
        if item['priority'] == 'MUST' and implementation != 'IMPLEMENTED':
            gaps.append({'code': 'UNIMPLEMENTED_MUST', 'id': item['id']})
        if item['priority'] == 'MUST' and verification == 'NOT_RUN':
            gaps.append({'code': 'UNVERIFIED_MUST', 'id': item['id']})
        for record in functional:
            if record['result'] in ('INFRA_ERROR', 'N/A'):
                gaps.append({'code': record['result'], 'id': item['id'], 'evidence_id': record['id'],
                             'reason': record['reason']})
    mapped_products = {item['product_id'] for item in request['items'] if item['product_id'] is not None}
    for identifier in sorted(set(products) - mapped_products - set(product_exclusions)):
        gaps.append({'code': 'UNMAPPED_TARGET', 'id': identifier})
    mapped_scenarios = {(item['requirement'], scenario) for item in request['items'] for scenario in item['scenarios']}
    for requirement, scenario in sorted(set(scenarios) - mapped_scenarios - set(scenario_exclusions)):
        gaps.append({'code': 'MISSING_SCENARIO', 'id': scenarios[(requirement, scenario)]['source']})
    for index, identifier in enumerate(sorted(product_exclusions), 1):
        items.append({'id': 'X' + str(index).zfill(2), 'product_id': identifier, 'priority': 'SKIP',
                      'target_evidence': 'SKIP', 'implementation': 'DECLARED',
                      'verification': 'NOT_RUN', 'evidence_ids': []})
    if not isinstance(request['severity_policy'], dict) or set(request['severity_policy']) != {'S1', 'S2', 'S3', 'S4'}:
        input_error()
    if any(value not in {'BLOCK', 'REPORT'} for value in request['severity_policy'].values()):
        input_error()
    for finding in sorted(findings.values(), key=lambda value: value['id']):
        if finding['status'] == 'OPEN':
            policy = request['severity_policy'][finding['severity']]
            gaps.append({'code': ('OPEN_' if policy == 'BLOCK' else 'REPORT_') + finding['severity'],
                         'id': finding['id'], 'evidence_id': finding['evidence_id']})
    if any(item['verification'] == 'FAILED' for item in items):
        overall = 'FAILED'
    elif any(gap['code'] in {'UNIMPLEMENTED_MUST', 'UNVERIFIED_MUST', 'UNMAPPED_TARGET', 'MISSING_SCENARIO',
                             'OPEN_S1', 'OPEN_S2', 'OPEN_S3', 'OPEN_S4'} for gap in gaps):
        overall = 'GAPS_OPEN'
    else:
        overall = 'PASS'
    return items, gaps, diagnostics, overall


def render(change, source_hashes, items, gaps, diagnostics, overall, severity_policy):
    lines = ['<!-- verified-feature-parity:' + change + ' -->', '# 功能差距报告', '',
             '- Change：`' + change + '`', '- 整体结果：`' + overall + '`',
             '- 执行声明：`NOT_RUN`（本报告只核验既有结构化证据）', '', '## 来源指纹', '']
    for path, digest in sorted(source_hashes.items()):
        lines.append('- `' + path + '`：`' + digest + '`')
    lines.extend(['', '## 三维状态', '', '| ID | 目标证据 | 实现 | 验证 | 证据索引 |',
                  '|---|---|---|---|---|'])
    for item in items:
        lines.append('| ' + item['id'] + ' | ' + item['target_evidence'] + ' | ' + item['implementation']
                     + ' | ' + item['verification'] + ' | ' + (', '.join(item['evidence_ids']) or '无') + ' |')
    lines.extend(['', '## 差距与严重问题策略', '',
                  '- 策略：`' + canonical(severity_policy) + '`'])
    if gaps:
        for gap in gaps:
            suffix = '；证据 `' + gap['evidence_id'] + '`' if 'evidence_id' in gap else ''
            lines.append('- `' + gap['code'] + '`：`' + gap['id'] + '`' + suffix)
    else:
        lines.append('- 无。')
    lines.extend(['', '## 独立诊断', ''])
    if diagnostics:
        for diagnostic in diagnostics:
            lines.append('- `' + diagnostic['id'] + '`：`' + diagnostic['category'] + '` / `'
                         + diagnostic['result'] + '`；不参与功能验证。')
    else:
        lines.append('- 无。')
    lines.extend(['', '本报告不证明测试曾在当前环境执行；证据真实性由验证责任方和适用评审确认。',
                  '<!-- verified-feature-parity:end -->', ''])
    return '\n'.join(lines)


def existing(root, report_rel, receipt_rel, source_id, change):
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
    fields = {'schema', 'id', 'change', 'request_sha256', 'input_hashes', 'report',
              'report_sha256', 'execution'}
    if (not isinstance(receipt, dict) or set(receipt) != fields or receipt['schema'] != RECEIPT_SCHEMA
            or receipt['change'] != change or receipt['id'] != source_id or receipt['report'] != report_rel
            or receipt['execution'] != 'NOT_RUN' or receipt['report_sha256'] != sha_text(document)
            or not isinstance(receipt['input_hashes'], dict) or not isinstance(receipt['request_sha256'], str)
            or document.count('<!-- verified-feature-parity:' + change + ' -->') != 1
            or document.count('<!-- verified-feature-parity:end -->') != 1):
        conflict()
    return document, receipt


def generate(root, request_path, dry_run=False):
    root = Path(root).absolute()
    try:
        request_rel, request = read_json(root, request_path)
        exact(request, REQUEST_FIELDS)
        if request['schema'] != SCHEMA or not valid_id(request['id']) or not valid_id(request['change']):
            input_error()
        if not isinstance(request['product_collections'], list) or not request['product_collections']:
            input_error()
        if (len(set(request['product_collections'])) != len(request['product_collections'])
                or not set(request['product_collections']) <= {'screens', 'flows', 'components', 'entities'}):
            input_error()
        unused_request, plan, unused_contract, product = load_valid_source(root, request['id'])
        del unused_request, unused_contract
        if product['id'] != request['id']:
            input_error()
        products = {}
        for collection in request['product_collections']:
            for entry in product[collection]:
                if entry['id'] in products:
                    input_error()
                products[entry['id']] = entry
        scenarios, spec_hashes = parse_specs(root, request['specs'], request['change'])
        tasks, task_hashes = parse_tasks(root, request['tasks'], request['change'])
        mapped_products, mapped_scenarios, unused_tasks = validate_items(request, products, scenarios, tasks)
        del unused_tasks
        product_exclusions, scenario_exclusions = validate_exclusions(
            request, products, scenarios, mapped_products, mapped_scenarios)
        records, findings, evidence_hashes = validate_evidence(root, request, scenarios, tasks)
        items, gaps, diagnostics, overall = derive(request, products, scenarios, tasks, records, findings,
                                                    product_exclusions, scenario_exclusions)
        product_rel = auto_root(request['id']) + '/product-recon.json'
        source_hashes = {**spec_hashes, **task_hashes, **evidence_hashes,
                         product_rel: sha_text(safe_path(root, product_rel).read_text(encoding='utf-8')),
                         'plan': plan['plan_sha256']}
        document = render(request['change'], source_hashes, items, gaps, diagnostics, overall,
                          request['severity_policy'])
        report_sha256 = sha_text(document)
        report_rel = 'docs/verification/' + request['change'] + '-parity.md'
        receipt_rel = '.framework/local-state/parity/' + request['change'] + '.json'
        receipt = {'schema': RECEIPT_SCHEMA, 'id': request['id'], 'change': request['change'],
                   'request_sha256': sha_text(canonical(request)), 'input_hashes': source_hashes,
                   'report': report_rel, 'report_sha256': report_sha256, 'execution': 'NOT_RUN'}
        old_document, old_receipt = existing(root, report_rel, receipt_rel, request['id'], request['change'])
        result = {'status': 'DRY_RUN' if dry_run else None, 'overall': overall, 'items': items,
                  'gaps': gaps, 'diagnostics': diagnostics, 'report': report_rel,
                  'receipt': receipt_rel, 'report_sha256': report_sha256, 'request': request_rel,
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
        if message.startswith('PARITY_') or 'SYMLINK' in message or 'PATH_ESCAPE' in message:
            raise
        if 'STALE' in message:
            raise ValueError('PARITY_STALE') from exc
        if 'CONFLICT' in message:
            raise ValueError('PARITY_CONFLICT') from exc
        if 'LIMIT' in message:
            raise ValueError('PARITY_LIMIT') from exc
        raise ValueError('PARITY_EVIDENCE') from exc
    except (KeyError, TypeError) as exc:
        raise ValueError('PARITY_INPUT') from exc
