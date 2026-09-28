"""Evidence-backed project dossiers and bounded, human-preserving document writes."""
import hashlib
import os
from pathlib import Path

from .config import digest, encoded
from .handoff import current_sources, require
from .storage import apply_files, fingerprint, owned_changes, project_lock, read_json, safe_path

STATE = '.framework/local-state/project-docs.json'
BEGIN, END = '<!-- FRAMEWORK_DOC_START -->', '<!-- FRAMEWORK_DOC_END -->'
PROJECT_FIELDS = ('goal', 'non_goals', 'architecture', 'interfaces', 'integration_order', 'constraints', 'resources')
MODULE_FIELDS = ('purpose', 'non_responsibilities', 'entrypoints', 'inputs', 'outputs', 'dependencies', 'internal_roles', 'commands', 'limitations', 'knowledge')
LABELS = dict(zip(PROJECT_FIELDS + MODULE_FIELDS,
    ('目标', '非目标', '设计与实际架构', '模块接口与调用双方', '集成顺序', '项目约束', '资源',
     '用途', '非职责', '真实入口', '输入', '输出', '依赖与调用方向', '内部职责', '命令与前提', '限制', '知识关联')))


def meaningful(value):
    return (isinstance(value, str) and bool(value.strip())
            and not any(x in value.lower() for x in ('todo', 'tbd', 'awaiting confirmation', '待填写', '<placeholder>'))
            and BEGIN not in value and END not in value)


def evidence_valid(root, items, allowed):
    if not isinstance(items, list) or not items:
        return False
    for item in items:
        try:
            rel, anchor = item['path'], item['anchor']
            if rel not in allowed or not meaningful(anchor):
                return False
            path = safe_path(root, rel)
            if not path.is_file() or path.stat().st_size > 1048576 or fingerprint(path) != item['sha256']:
                return False
            if anchor not in path.read_text():
                return False
        except (OSError, ValueError, KeyError, TypeError):
            return False
    return True


def validate_project_docs(root, catalog, dossier):
    if (not isinstance(dossier, dict) or set(dossier) != {'project', 'modules', 'blockers', 'rule_conflicts', 'planning_refs'}
            or not isinstance(dossier.get('project'), dict) or not isinstance(dossier.get('modules'), list)):
        return ['INCOMPLETE_DOCUMENTATION']
    errors = []
    if len(encoded(dossier).encode()) > 1048576:
        return ['DOCUMENTATION_BUDGET_EXCEEDED']
    refs = dossier['planning_refs']
    if not isinstance(refs, list):
        return ['INVALID_EVIDENCE']
    allowed = {p for module in catalog['modules'].values() for p in module['sources']}
    generated = {'docs/project/'+name+'.md' for name in
                 ('overview', 'architecture', 'collaboration', 'constraints', 'resources', 'handoff')}
    generated.update('docs/project/modules/'+mid+'.md' for mid in catalog['modules'])
    # Explicit public planning files only; never private launch or local-state data.
    for ref in refs:
        if (not isinstance(ref, dict) or not isinstance(ref.get('path'), str)
                or not ref['path'].startswith(('docs/project/', 'openspec/')) or not ref['path'].endswith('.md')):
            return ['INVALID_EVIDENCE']
        allowed.add(ref['path'])
        if ref['path'] in generated:
            errors.append('SELF_REFERENTIAL_EVIDENCE')
    if refs and not evidence_valid(root, refs, allowed):
        errors.append('INVALID_EVIDENCE')
    if not isinstance(dossier['blockers'], list) or any(not meaningful(b) for b in dossier['blockers']):
        errors.append('INVALID_BLOCKERS')
    if not isinstance(dossier['rule_conflicts'], list):
        return ['INVALID_CONFLICTS']
    for conflict in dossier['rule_conflicts']:
        if (not isinstance(conflict, dict) or not isinstance(conflict.get('module_id'), str)
                or conflict['module_id'] not in catalog['modules'] or not meaningful(conflict.get('description'))):
            errors.append('INVALID_CONFLICTS')
    mids = [m.get('id') for m in dossier['modules'] if isinstance(m, dict)]
    if len(mids) != len(catalog['modules']) or any(not isinstance(mid, str) for mid in mids) or set(mids) != set(catalog['modules']):
        errors.append('INCOMPLETE_DOCUMENTATION')
    groups = [(dossier['project'], PROJECT_FIELDS)] + [(m, MODULE_FIELDS) for m in dossier['modules']]
    for group, fields in groups:
        if not isinstance(group, dict) or set(group) != set(fields) | ({'id'} if fields == MODULE_FIELDS else set()):
            errors.append('INCOMPLETE_DOCUMENTATION')
            continue
        for key in fields:
            field = group[key]
            if not isinstance(field, dict) or set(field) - {'value', 'status', 'provenance', 'evidence', 'reason'}:
                errors.append('INCOMPLETE_DOCUMENTATION')
                continue
            status = field.get('status')
            if status not in ('KNOWN', 'NOT_VERIFIED', 'NOT_CONFIGURED', 'NOT_APPLICABLE') or field.get('provenance') not in ('STATIC_SUPPORTED', 'DECLARED', 'INFERRED'):
                errors.append('INVALID_EVIDENCE')
            value = field.get('value')
            if key == 'commands' and status != 'NOT_APPLICABLE':
                if not isinstance(value, list) or not value:
                    errors.append('INCOMPLETE_DOCUMENTATION')
                    continue
                for command in value:
                    try:
                        if set(command) != {'command', 'cwd', 'prerequisites', 'execution'} or not all(meaningful(command[k]) for k in ('command', 'cwd', 'prerequisites')) or command['execution'] != 'NOT_RUN':
                            raise ValueError('INVALID_COMMAND')
                        safe_path(root, command['cwd'])
                    except (ValueError, TypeError, KeyError):
                        errors.append('INVALID_COMMAND')
                if status != 'NOT_VERIFIED':
                    errors.append('UNVERIFIED_COMMAND')
            elif not meaningful(value):
                errors.append('INCOMPLETE_DOCUMENTATION')
            if status in ('NOT_CONFIGURED', 'NOT_APPLICABLE'):
                if not meaningful(field.get('reason')) or (status == 'NOT_CONFIGURED' and key not in ('knowledge', 'resources')):
                    errors.append('INCOMPLETE_DOCUMENTATION')
                evidence = field.get('evidence', [])
                if not isinstance(evidence, list) or (evidence and not evidence_valid(root, evidence, allowed)):
                    errors.append('INVALID_EVIDENCE')
            elif not evidence_valid(root, field.get('evidence'), allowed):
                errors.append('INVALID_EVIDENCE')
            elif field['provenance'] == 'DECLARED' and any(e['path'] not in {r['path'] for r in refs} for e in field['evidence']):
                errors.append('INVALID_EVIDENCE')
    return sorted(set(errors))


def render_fields(fields, keys):
    lines = []
    for key in keys:
        field = fields[key]
        value = field['value']
        lines += ['## '+LABELS[key], '', encoded(value).strip() if isinstance(value, list) else value,
                  '', '来源类型：'+field['provenance']+'；状态：'+field['status']+'。']
        if field.get('reason'):
            lines.append('原因：'+field['reason'])
        for evidence in field.get('evidence', []):
            lines.append('证据：`'+evidence['path']+'`；sha256='+evidence['sha256']+'；锚点：'+evidence['anchor'].replace('\n', ' '))
        lines.append('')
    return '\n'.join(lines)


def project_doc_outputs(root, catalog, dossier):
    errors = validate_project_docs(root, catalog, dossier)
    if errors:
        raise ValueError('INVALID_EVIDENCE: '+','.join(errors))
    project = dossier['project']
    outputs = {}
    for name, fields in {'overview': ('goal', 'non_goals'), 'architecture': ('architecture', 'interfaces'),
                         'collaboration': ('integration_order',), 'constraints': ('constraints',), 'resources': ('resources',)}.items():
        outputs['docs/project/'+name+'.md'] = render_fields(project, fields)
    conflicts = {c['module_id'] for c in dossier['rule_conflicts']}
    for module in dossier['modules']:
        mid = module['id']
        observed = catalog['modules'][mid]
        rel = 'docs/project/modules/'+mid+'.md'
        body = '# '+mid+'\n\n模块路径：`'+observed['path']+'`。\n\n'+render_fields(module, MODULE_FIELDS)
        writable = observed.get('writable') and observed['path'] != '.' and observed['presence'] == 'present'
        outputs[rel] = body + '\n'+('模块目录可写。' if writable else '模块只读或使用根入口；本页为完整局部开发入口，不写入模块目录。')+'\n'
        if writable and mid not in conflicts:
            agent_rel = observed['path']+'/AGENTS.md'
            link = os.path.relpath(root/rel, (root/agent_rel).parent)
            outputs[agent_rel] = body+'\n项目侧资料：['+mid+']('+link+')。遵循项目根流程。\n'
    handoff = ['# 开发交接', '', '资料不授予业务实现、安装、发布或知识写入权限。', '',
               '下一步：检查doctor、当前用户批准范围与OpenSpec规格/计划后选择任务。', '', '## 阻塞与规则冲突', '']
    handoff += dossier['blockers'] + [c['module_id']+': '+c['description'] for c in dossier['rule_conflicts']]
    outputs['docs/project/handoff.md'] = '\n'.join(handoff)+'\n'
    return outputs


def managed_document(root, rel, body, old):
    path = safe_path(root, rel)
    text = path.read_bytes().decode('utf-8') if path.exists() else ''
    block = BEGIN+'\n'+body+'\n'+END
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(END) < text.index(BEGIN):
            raise ValueError('RULE_CONFLICT: '+rel)
        previous = text[text.index(BEGIN):text.index(END)+len(END)]
        if digest(previous) != old.get(rel):
            raise ValueError('RULE_CONFLICT: '+rel)
        updated = text.replace(previous, block, 1)
    else:
        if rel in old:
            raise ValueError('RULE_CONFLICT: managed block removed: '+rel)
        # Replace only pristine machine-owned skeletons; append to all human text.
        owned = read_json(root, '.framework/local-state/owned.json', {})
        if path.exists() and owned.get(rel) == fingerprint(path):
            text = ''
        updated = text + ('\n\n' if text else '') + block+'\n'
    return updated, digest(block)


def build_handoff(config, catalog, dossier, checks):
    blocked = list(dossier.get('blockers', [])) + [c['description'] for c in dossier.get('rule_conflicts', [])]
    has_sources = any(m.get('sources') for m in catalog.get('modules', {}).values())
    if blocked:
        status = 'BLOCKED'
    elif not has_sources and not checks.get('approved_design'):
        status = 'NEEDS_DESIGN_APPROVAL'
    else:
        status = 'READY_FOR_PLANNING'
    return {'status': status, 'project_id': config.get('project_id'),
            'goal': dossier.get('project', {}).get('goal', {}).get('value', ''),
            'modules': {mid: {'path': m['path'], 'source_digest': digest(m.get('sources', {})),
                             'repo_id': m.get('repo_id')} for mid, m in catalog.get('modules', {}).items()},
            'versions': checks.get('versions', {}), 'planning_refs': dossier.get('planning_refs', []),
            'approved_design': checks.get('approved_design'), 'blockers': blocked,
            'next_action': 'Review design with user' if status == 'NEEDS_DESIGN_APPROVAL' else
                ('Resolve listed blockers' if blocked else 'Read current OpenSpec status and approved plan; select next task'),
            'needed_permissions': ['Current request must authorize the selected implementation scope'],
            'verification': 'Use module command prerequisites and approved Scenario tests; runtime NOT_RUN'}


def repository_versions(root, catalog):
    from .acquisition import git_call
    versions = {}
    for rid, repo in catalog.get('repos', {}).items():
        path = safe_path(root, repo['root'])
        result = git_call(['rev-parse', '--verify', 'HEAD'], path, set())
        versions[rid] = {'root': repo['root'], 'head': result['stdout'].strip() if not result['exit_code'] else None}
    return versions


def publish_project_docs(root, catalog, dossier, grants, approvals=None):
    require(grants)
    root = Path(root)
    with project_lock(root):
        if catalog != read_json(root, 'module-catalog.generated.json'):
            raise ValueError('STALE_CATALOG')
        sources = current_sources(root, catalog)
        errors = validate_project_docs(root, catalog, dossier)
        if errors:
            raise ValueError('INVALID_EVIDENCE: '+','.join(errors))
        outputs = project_doc_outputs(root, catalog, dossier)
        old = read_json(root, STATE, {})
        approved_design = old.get('approved_design')
        refs = {r['sha256'] for r in dossier['planning_refs']}
        if approved_design not in refs:
            approved_design = None
        if approvals:
            if set(approvals) != {'design'} or approvals['design'] not in refs:
                raise ValueError('INVALID_DESIGN_APPROVAL')
            approved_design = approvals['design']
        config = read_json(root, 'framework-project.json', {})
        versions = repository_versions(root, catalog)
        handoff = build_handoff(config, catalog, dossier, {'approved_design': approved_design, 'versions': versions})
        outputs['docs/project/handoff.md'] += '\n## 当前交接状态\n\n'+encoded(handoff)
        blocks = dict(old.get('blocks', {}))
        changes, files = [], {}
        for rel, body in sorted(outputs.items()):
            before = fingerprint(safe_path(root, rel))
            content, blocks[rel] = managed_document(root, rel, body, old.get('blocks', {}))
            files[rel] = hashlib.sha256(content.encode()).hexdigest()
            changes.append({'path': rel, 'before_sha256': before, 'content': content})
        report = {'status': 'PARTIAL' if dossier['blockers'] or dossier['rule_conflicts'] else 'COMPLETE',
                  'catalog_digest': digest(catalog), 'source_digest': digest(sources), 'blocks': blocks,
                  'files': files, 'dossier': dossier, 'config_digest': digest(config),
                  'approved_design': approved_design, 'versions': versions}
        report['handoff_digest'] = digest(handoff)
        changes += owned_changes(root, {STATE: encoded(report), '.framework/local-state/handoff.json': encoded(handoff)})
        if current_sources(root, catalog) != sources or validate_project_docs(root, catalog, dossier):
            raise ValueError('STALE_SOURCE')
        apply_files(root, changes, 'project-docs')
        return {'status': report['status'], 'files': sorted(files)}


def completion_checks(root, config, catalog, sources, report):
    """Additive read-only gates; never infer permission from persisted decisions."""
    from .analysis_batches import framework_digest
    record = read_json(root, STATE, {})
    dossier = record.get('dossier', {})
    documentation = {'status': 'MISSING', 'errors': ['INCOMPLETE_DOCUMENTATION']}
    if record:
        errors = validate_project_docs(root, catalog, dossier)
        changed = (record.get('source_digest') != digest(sources) or record.get('catalog_digest') != digest(catalog)
                   or record.get('config_digest') != digest(config)
                   or record.get('versions') != repository_versions(root, catalog)
                   or any(fingerprint(safe_path(root, p)) != sha for p, sha in record.get('files', {}).items()))
        documentation = {'status': 'STALE' if changed or errors else record['status'], 'errors': errors}
    coverage = read_json(root, '.framework/local-state/analysis-coverage.json', {'status': 'MISSING'})
    if not sources:
        coverage = {'status': 'NOT_APPLICABLE'}
    elif (coverage.get('source_digest') != digest(sources) or coverage.get('catalog_digest') != digest(catalog)
          or coverage.get('framework_digest') != framework_digest(root)):
        coverage = dict(coverage, status='STALE' if coverage.get('session_id') else 'MISSING')
    handoff = read_json(root, '.framework/local-state/handoff.json')
    if not handoff:
        handoff = build_handoff(config, catalog, dossier, {})
        if record:
            handoff = dict(handoff, status='MISSING', next_action='Reaccept current dossier to restore persisted handoff')
    elif record.get('handoff_digest') != digest(handoff):
        handoff = dict(handoff, status='STALE')
    missing_modules = any(m.get('presence') != 'present' or not safe_path(root, m['path']).exists() for m in catalog['modules'].values())
    indexes_ok = not config.get('index') or all(s in ('READY', 'NOT_APPLICABLE') for s in report['indexes'].values())
    hooks_ok = not config.get('hooks') or report['hooks']['status'] in ('READY', 'NOT_APPLICABLE')
    good = (documentation['status'] == 'COMPLETE' and coverage['status'] in ('COMPLETE', 'NOT_APPLICABLE')
            and handoff['status'] == 'READY_FOR_PLANNING' and report['scaffold'] == 'READY'
            and not missing_modules and not report.get('candidates') and indexes_ok and hooks_ok
            and (not sources or report['maps']['status'] == 'READY'))
    return {'documentation': documentation, 'coverage': coverage, 'handoff': handoff,
            'initialization': 'COMPLETE' if good else 'PARTIAL'}
