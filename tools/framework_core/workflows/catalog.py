"""Read-only routing over the fifteen documented workflows.

The catalog mirrors the fifteen rows of the tutorial table
`docs/guide/from-zero-to-one.md`「15 条一览」. Every reason a flow lands in
a bucket cites that row, so a route can be traced back to the source table.
Project role comes from target files only; a request never grants one.
"""
import json
from pathlib import Path

REQUEST_SCHEMA = 'workflow-request/v1'
CATALOG_SCHEMA = 'workflow-catalog/v1'
REPORT_SCHEMA = 'workflow-report/v1'
TASK_CATEGORIES = ('read_only_audit', 'pure_doc', 'spec_fix', 'new_behavior',
                   'knowledge_ingestion', 'device_release')
DEVELOPMENT_CATEGORIES = ('read_only_audit', 'pure_doc', 'spec_fix', 'new_behavior')
BUCKETS = ('main', 'conditional', 'not_applicable', 'needs_confirmation')
ROLE_LABELS = {'business': '业务工程', 'shell': '公共工程壳', 'unknown': '未知项目角色'}
ROLE_SCOPES = {'business': '业务工程', 'shell': '公共工程壳'}


def _catalog():
    data = json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf-8'))
    if data.get('schema') != CATALOG_SCHEMA:
        raise ValueError('INVALID_CATALOG: unexpected catalog schema')
    flows = data.get('flows') or []
    if [flow['row'] for flow in flows] != list(range(1, 16)):
        raise ValueError('INVALID_CATALOG: catalog must hold the fifteen tutorial rows')
    return flows


def entries():
    """The fifteen catalog entries in tutorial order."""
    return _catalog()


def development_routes():
    """The four development routes inside flow-02."""
    data = json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf-8'))
    return data.get('development_routes') or []


def catalog_scope(category):
    """Flows that take a task category outside the four development routes."""
    data = json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf-8'))
    return (data.get('catalog_scope') or {}).get(category)


def local_rules(root, target):
    """Rule files that apply to a target path, from the project root down."""
    root = Path(root).resolve()
    if not target:
        return []
    base = (root / target).resolve() if not Path(target).is_absolute() else Path(target).resolve()
    if not base.is_relative_to(root):
        return []
    rules = []
    current = base if base.is_dir() else base.parent
    while current.is_relative_to(root):
        candidate = current / 'AGENTS.md'
        if candidate.is_file():
            rules.append(candidate.relative_to(root).as_posix())
        if current == root:
            break
        current = current.parent
    return sorted(rules)


def classify_development(root, request):
    """Route a development task by facts, not by the request's self-description."""
    request = request or {}
    category = request.get('task_category')
    scope = catalog_scope(category)
    if scope:
        return {
            'route': 'catalog',
            'flows': list(scope['flows']),
            'reason': scope['reason'],
            'next_actions': ['按工作流目录对应的入口推进，日常开发四类不承接该任务'],
        }
    impact = request.get('acceptance_impact')
    scenario = request.get('existing_scenario')
    modifies = bool(request.get('modifies_files'))
    if impact in ('interface', 'acceptance'):
        route = 'new_behavior'
    elif scenario:
        route = 'spec_fix'
    elif not modifies:
        route = 'read_only_audit'
    elif impact == 'none':
        route = 'pure_doc'
    else:
        route = 'needs_confirmation'
    rules = {item['route']: item for item in development_routes()}
    if route == 'needs_confirmation':
        return {
            'route': route,
            'flows': ['flow-02'],
            'reason': '验收影响与改动范围不足以判定任务类别',
            'next_actions': ['只读读取目标目录的规则与现状', '只读列出候选场景与受影响范围',
                             '确认验收影响后再选择路径'],
            'local_rules': local_rules(root, request.get('target')),
        }
    item = rules[route]
    return {
        'route': route,
        'flows': ['flow-02'],
        'reason': '%s：%s' % (item['name'], item['path']),
        'path': item['path'],
        'evidence': item['evidence'],
        'next_actions': list(item['next_actions']),
        'local_rules': local_rules(root, request.get('target')),
    }


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError('INVALID_REQUEST: request must be a JSON object')
    if request.get('schema') != REQUEST_SCHEMA:
        raise ValueError('INVALID_REQUEST: schema must be ' + REQUEST_SCHEMA)
    if request.get('operation') != 'route':
        raise ValueError('INVALID_REQUEST: operation must be route')
    return request


def detect_role(root):
    """Project role from target facts only. Returns (role, source, problem)."""
    root = Path(root)
    business = (root / 'framework-project.json').is_file()
    shell = (root / 'framework-manifest.json').is_file()
    if business and shell:
        return 'unknown', None, '目标工程同时存在 framework-project.json 与 framework-manifest.json，项目角色无法判定'
    if business:
        return 'business', 'framework-project.json', None
    if shell:
        return 'shell', 'framework-manifest.json', None
    return 'unknown', None, '目标工程没有 framework-project.json，也没有 framework-manifest.json，项目角色无法判定'


def _bucket_for(flow, role, category, initialized, reverse_requested):
    """Return (bucket, why) for one flow, or (None, None) when it still applies."""
    row = flow['row']
    role_specific = set(flow['roles']) != {'business', 'shell'}
    if role_specific:
        if role == 'unknown':
            return 'needs_confirmation', '项目角色未知，无法判定是否适用（教程第 %d 行：%s）' % (row, flow['scope'])
        if role not in flow['roles']:
            return 'not_applicable', '属于%s范围，当前项目角色是%s（教程第 %d 行：%s）' % (
                ROLE_SCOPES.get(flow['roles'][0], flow['roles'][0]),
                ROLE_LABELS.get(role, role), row, flow['scope'])
    if flow['id'] == 'flow-01' and initialized:
        return 'not_applicable', '工程已接入，教程第 %d 行：%s 已完成' % (row, flow['name'])
    if flow.get('intent_gate') == 'reverse_requested' and not reverse_requested:
        return 'not_applicable', '未明确提出逆向要求（教程第 %d 行：%s）' % (row, flow['enters_when'])
    if category is None:
        return 'needs_confirmation', '任务类别未确定，意图不足以区分普通文档与验收变更（教程第 %d 行：%s）' % (
            row, flow['enters_when'])
    return None, None


def route(root, request):
    """Classify the fifteen workflows for one task. Writes nothing."""
    validate_request(request)
    flows = _catalog()
    root = Path(root)
    role, source, role_problem = detect_role(root)
    claim = request.get('project_role')
    role_conflict = None
    if claim and claim != role:
        role_conflict = '请求声明的项目角色 %s 与目标资料判定的 %s 冲突' % (
            claim, ROLE_LABELS.get(role, role))
    category = request.get('task_category')
    if category is not None and category not in TASK_CATEGORIES:
        category = None
    initialized = (root / 'framework-project.json').is_file()
    reverse_requested = bool(request.get('reverse_requested'))
    effective_role = 'unknown' if role_conflict else role

    classification = {bucket: [] for bucket in BUCKETS}
    for flow in flows:
        bucket, why = _bucket_for(flow, effective_role, category, initialized, reverse_requested)
        if bucket is None:
            enters = (category in flow.get('main_for', [])
                      or effective_role in flow.get('always_in_roles', [])
                      or 'reverse_requested' in flow.get('main_when_intent', [])
                      or (flow['id'] == 'flow-01' and not initialized))
            if enters:
                bucket = 'main'
                why = '当前任务进入此流程（教程第 %d 行：%s）' % (flow['row'], flow['enters_when'])
            else:
                bucket = 'conditional'
                why = '满足条件后进入：%s（教程第 %d 行）' % (
                    flow.get('condition') or flow['enters_when'], flow['row'])
        classification[bucket].append({
            'id': flow['id'], 'name': flow['name'], 'row': flow['row'], 'why': why,
        })

    next_actions = []
    for entry in classification['main']:
        flow = next(f for f in flows if f['id'] == entry['id'])
        next_actions.extend(flow['entries'])
    if classification['needs_confirmation']:
        next_actions.extend([
            '只读读取目标目录的 AGENTS.md 与适用局部规则，确认任务性质',
            '只读列出目标工程已有流程产物与 OpenSpec 状态',
            '补充 task_category 或更明确的 intent 后重新路由',
        ])
    development = None
    if category in DEVELOPMENT_CATEGORIES:
        development = classify_development(root, request)
        next_actions.extend(development['next_actions'])
    return {
        'schema': REPORT_SCHEMA,
        'operation': 'route',
        'status': 'READY',
        'read_only': True,
        'project_role': role,
        'project_role_source': source,
        'project_role_problem': role_problem,
        'role_conflict': role_conflict,
        'task_category': category,
        'classification': classification,
        'development': development,
        'next_actions': next_actions,
    }
