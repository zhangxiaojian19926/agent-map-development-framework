"""Read-only, human-readable summaries derived from existing reports and metadata."""
from pathlib import Path

from .storage import read_json, safe_path


HEADINGS = ('一、结果', '二、当前流程产物', '三、条件性未生成',
            '四、未执行与限制', '五、提交与本机状态', '六、下一步')


def present(root, relative, directory=False):
    path = safe_path(root, relative)
    return path.is_dir() if directory else path.is_file()


def lines_or_none(items, empty='  无。'):
    return items or [empty]


def ordinary_next(report):
    handoff = report.get('handoff', {}).get('status', 'MISSING')
    documentation = report.get('documentation', {}).get('status', 'MISSING')
    coverage = report.get('coverage', {}).get('status', 'MISSING')
    if handoff == 'NEEDS_DESIGN_APPROVAL':
        return '确认 docs/project/design-input.md 中的设计草案，再完成开发交接。'
    if documentation != 'COMPLETE':
        return '按 doctor 列出的资料缺口刷新项目事实与证据。'
    if coverage not in ('COMPLETE', 'NOT_APPLICABLE'):
        return '完成当前源码建图与覆盖交接。'
    if handoff != 'READY_FOR_PLANNING':
        return '解决 handoff 中的阻塞与权限缺口。'
    if report.get('initialization') == 'COMPLETE':
        return '为首个已批准能力创建 OpenSpec change。'
    return '按 doctor 缺口完成初始化后重新检查。'


def render_ordinary(root, report):
    root = Path(root)
    config = read_json(root, 'framework-project.json', {})
    catalog = read_json(root, 'module-catalog.generated.json', {'modules': {}})
    result = [
        'initialization=' + str(report.get('initialization', 'PARTIAL')),
        'documentation=' + str(report.get('documentation', {}).get('status', 'MISSING')),
        'coverage=' + str(report.get('coverage', {}).get('status', 'MISSING')),
        'handoff=' + str(report.get('handoff', {}).get('status', 'MISSING')),
        'runtime=' + str(report.get('runtime', 'NOT_RUN')),
    ]
    artifacts = []
    for rel in ('AGENTS.md', 'framework-project.json', 'module-catalog.generated.json',
                'llm-wiki-aliases.json'):
        if present(root, rel):
            artifacts.append('  ' + rel)
    for rel, label in (('.agent-framework', '固定版本公共运行包'),
                       ('knowledge/project', '知识库空壳或已授权知识内容')):
        if present(root, rel, directory=True):
            artifacts.append('  ' + rel + '/：' + label)
    for name in ('overview', 'architecture', 'collaboration', 'constraints', 'resources',
                 'design-input', 'handoff'):
        rel = 'docs/project/' + name + '.md'
        if present(root, rel):
            artifacts.append('  ' + rel)
    for name in ('module-map.generated.md', 'relationships.generated.md',
                 'relationships.generated.json'):
        rel = 'docs/project/' + name
        if present(root, rel):
            artifacts.append('  ' + rel)
    for module_id in sorted(catalog.get('modules', {})):
        rel = 'docs/project/modules/' + module_id + '.md'
        if present(root, rel):
            artifacts.append('  ' + rel)
    for name in ('intake.json', 'owned.json', 'agent-entry.json', 'project-docs.json',
                 'handoff.json', 'analysis-session.json', 'analysis-coverage.json',
                 'indexes.json', 'hooks.json'):
        rel = '.framework/local-state/' + name
        if present(root, rel):
            artifacts.append('  ' + rel + '（本机）')

    missing = []
    for rel, directory, reason in (
            ('modules', True, '没有已创建的业务模块；拟议模块不以空目录冒充实现'),
            ('docs/project/design-input.md', False, '尚无新工程设计草案；已有源码项目不需要'),
            ('docs/project/module-map.generated.md', False, '无白名单源码或尚未发布地图'),
            ('openspec', True, '尚未进入或初始化 OpenSpec 流程'),
            ('docs/runbooks', True, '尚无已核实的运行内容'),
            ('docs/verification', True, '尚无最终验证内容'),
            ('dist', True, '初始化不构建业务项目'),
            ('.codegraph', True, '未请求或尚未建立索引'),
            ('docs/project/reverse', True, '未请求逆向观察')):
        if not present(root, rel, directory=directory):
            missing.append('  ' + rel + ('/' if directory else '') + '：' + reason)
    missing.append('  以上缺项是条件性状态，不单独构成初始化失败。')
    limits = [
        '  业务运行：' + str(report.get('runtime', 'NOT_RUN')) + '；初始化不执行业务实现或验收。',
        '  静态地图不证明业务运行成功；知识库空壳不等于已摄入知识。',
        '  摘要只描述当前流程产物，不追踪或声称本次命令新建了文件。',
    ]
    ownership = [
        '  建议提交：AGENTS.md、项目配置、.agent-framework/、docs/project/ 和按隐私策略管理的知识内容。',
        '  不提交：.framework/ 与目标外私有启动区。',
        '  initialization=COMPLETE 不代替业务 Scenario、集成验证或发布批准。',
    ]
    title = '工程初始化摘要：' + str(config.get('project_name') or config.get('project_id') or root.name)
    sections = [result, lines_or_none(artifacts), lines_or_none(missing), limits, ownership,
                ['  ' + ordinary_next(report)]]
    return title + '\n' + '=' * 60 + '\n\n' + '\n\n'.join(
        heading + '\n' + '\n'.join(body) for heading, body in zip(HEADINGS, sections)) + '\n'


def reverse_next(report):
    status = report.get('status')
    observations = report.get('observations', [])
    statuses = {item.get('status') for item in observations}
    if status in ('SNAPSHOT_REQUIRED', 'NOT_AUTHORIZED') and not observations:
        return '取得目标快照及相应授权后重新生成计划。'
    if status in ('PLAN_APPROVAL_REQUIRED', 'DRY_RUN'):
        return '核对并批准当前计划，再执行工具准备与观察。'
    if status in ('CONSENT_REQUIRED', 'PLAN_CONFLICT'):
        return '核对当前授权或计划差异后重新确认。'
    if (status in ('TOOLCHAIN_BLOCKED', 'INSTALL_FAILED', 'HEALTH_FAILED') or
            report.get('toolchain_status') not in (None, 'READY')):
        return '处理当前工具或平台缺口，暂不执行后续观察。'
    if 'PROVIDER_MISSING' in statuses:
        return '接入真实浏览器 provider 后恢复当前计划中的动态观察。'
    if 'NOT_AUTHORIZED' in statuses:
        return '补齐观察所需的明确授权后恢复当前计划。'
    if report.get('observation_status') == 'RECORDED' and report.get('behavior_contract') != 'NOT_READY':
        return '将行为契约交回普通工程的设计与 OpenSpec 开发流程。'
    if report.get('observation_status') == 'RECORDED':
        return '运行 doctor 核对已记录观察与行为契约的完整性。'
    return '处理未完成的观察项后恢复当前计划。'


def render_reverse(root, request, report):
    root = Path(root)
    request_id = request['id']
    auto = '.framework/local-state/reverse/auto/' + request_id
    result = [
        'status=' + str(report.get('status', 'UNKNOWN')),
        'toolchain_status=' + str(report.get('toolchain_status', 'NOT_RUN')),
        'observation_status=' + str(report.get('observation_status', 'NOT_RUN')),
        'runtime_validation=' + str(report.get('runtime_validation', 'NOT_RUN')),
    ]
    artifacts = []
    for rel, label in ((auto + '/request.json', '当前请求'),
                       (report.get('plan_path'), '当前批准计划')):
        if rel and present(root, rel):
            artifacts.append('  ' + rel + '：' + label)
    if present(root, auto + '/snapshots', directory=True):
        artifacts.append('  ' + auto + '/snapshots/：私有目标快照')
    for observation in request.get('observations', []):
        rel = auto + '/observations/' + observation['id'] + '.json'
        if present(root, rel):
            artifacts.append('  ' + rel)
        raw = auto + '/raw/' + observation['id'] + '.txt'
        if present(root, raw):
            artifacts.append('  ' + raw + '（私有原文，未读取）')
    if present(root, auto + '/outputs', directory=True):
        artifacts.append('  ' + auto + '/outputs/：工具输出（私有）')
    contract = auto + '/behavior-contract.json'
    contract_present = present(root, contract)
    if contract_present:
        artifacts.append('  ' + contract)
    product = report.get('product_recon')
    if product and product.get('path') and present(root, product['path']):
        artifacts.append('  ' + product['path'] + '：产品行为观察（私有派生视图，未验证）')
    public = 'docs/project/reverse/' + request_id + '.md'
    if present(root, public):
        artifacts.append('  ' + public + '（脱敏公开摘要）')

    tools = []
    planned = {item.get('tool_id'): item for item in report.get('plan', {}).get('tools', [])}
    installation = report.get('installation', report.get('actions', []))
    if isinstance(installation, list):
        for item in installation:
            name = item.get('tool_id', 'unknown')
            version = planned.get(name, {}).get('version')
            tools.append('  ' + name + (' ' + version if version else '') + '：' +
                         str(item.get('action', 'UNKNOWN')) + ' / ' + str(item.get('status', 'UNKNOWN')))
    elif report.get('plan', {}).get('tools'):
        tools.append('  工具仅在计划中，尚未安装：' + ', '.join(sorted(planned)))
    else:
        tools.append('  无外部工具动作；内置适配器或工具准备状态见上方结果。')

    missing = []
    if not contract_present:
        missing.append('  行为契约：未生成（全部指定观察记录成功后才可形成）。')
    if not present(root, public):
        missing.append('  公开摘要：未生成（未允许公开或当前流程尚未形成）。')
    if not present(root, auto + '/snapshots', directory=True):
        missing.append('  URL快照：不适用或尚未取得；本地目标不需要URL快照。')
    observations = ['  ' + item.get('id', 'unknown') + '：' + str(item.get('status', 'UNKNOWN'))
                    for item in report.get('observations', [])]
    if not observations:
        observations = ['  观察：NOT_RUN；当前没有已执行的观察结果。']
    raw_policy = request.get('evidence', {}).get('raw', 'discard')
    limits = observations + [
        '  原始证据策略：' + raw_policy + '；摘要只显示路径和状态，不读取原始正文。',
        '  工具READY不等于观察完成；观察完成不等于业务运行验证通过。',
        '  逆向证据不是源码地图证据，也不自动批准业务实现。',
    ]
    ownership = [
        '  不提交：.framework/tools/、.framework/local-state/reverse/ 及全部私有证据。',
        '  可提交：仅在已生成且符合隐私策略时提交 docs/project/reverse/' + request_id + '.md。',
    ] + tools
    sections = [result, lines_or_none(artifacts), lines_or_none(missing), limits, ownership,
                ['  ' + reverse_next(report)]]
    title = '逆向观察摘要：' + request_id
    return title + '\n' + '=' * 60 + '\n\n' + '\n\n'.join(
        heading + '\n' + '\n'.join(body) for heading, body in zip(HEADINGS, sections)) + '\n'
