"""Read-only checks; never repair, spawn models, or run project tests."""
from .config import digest
from .storage import read_json, safe_path, fingerprint
from .modules import source_files, find_candidates
from .maps import validate_map, design_mismatches, map_needs_update


def inspect_project(root):
    config = read_json(root, 'framework-project.json', {})
    catalog = read_json(root, 'module-catalog.generated.json', {})
    observed = read_json(root, 'docs/project/relationships.generated.json')
    report = {'schema_version': 1, 'status': 'WAITING_AGENT',
              'scaffold': 'READY' if config and catalog else 'BLOCKED',
              'agent': {'status': 'WAITING_AGENT'}, 'maps': {'status': 'NOT_RUN'},
              'indexes': {}, 'hooks': read_json(root, '.framework/local-state/hooks.json', {'status': 'NOT_CONFIGURED'}),
              'runtime': 'NOT_RUN', 'onboarding': 'NOT_PREPARED',
              'understanding': 'NOT_RUN', 'development': 'NEEDS_DESIGN_APPROVAL', 'next_actions': [],
              'initialization': 'PARTIAL', 'documentation': {'status': 'MISSING'},
              'coverage': {'status': 'MISSING'}, 'handoff': {'status': 'BLOCKED'}}
    if not config or not catalog:
        report['status'] = 'BLOCKED'
        report['next_actions'] = ['init --target <project>']
        return report
    current_sources = {}
    source_drift = False
    for mid, module in catalog.get('modules', {}).items():
        current = source_files(root, module['path'])
        current_sources.update(current)
        if current != module.get('sources', {}) or not safe_path(root, module['path']).exists():
            source_drift = True
    map_shape = map_needs_update(root, catalog, observed) if observed or current_sources else 'NOT_APPLICABLE'
    if observed:
        errors = validate_map(root, catalog, observed)
        mismatch = design_mismatches(config, observed)
        agent_record = read_json(root, '.framework/local-state/agent-status.json', {})
        executed = agent_record.get('status') == 'ANALYZED' and map_shape == 'CURRENT'
        report['agent']['status'] = 'ANALYZED' if executed else 'WAITING_AGENT'
        report['maps'] = {'status': 'STALE' if map_shape == 'STRUCTURAL' else ('SPEC_MISMATCH' if mismatch else 'READY'),
                          'errors': [item for item in errors if item != 'STALE_EVIDENCE'],
                          'design_mismatches': mismatch, 'source_drift': source_drift}
        report['status'] = 'PARTIAL' if map_shape == 'STRUCTURAL' or mismatch else 'READY'
        if not executed:
            report['status'] = 'WAITING_AGENT'
    elif not current_sources:
        report['maps']['status'] = 'NOT_APPLICABLE'
    state = read_json(root, '.framework/local-state/indexes.json', {})
    for iid, index in catalog.get('indexes', {}).items():
        previous = state.get(iid, {})
        status = previous.get('status', 'NOT_RUN') if index['sources'] else 'NOT_APPLICABLE'
        if previous.get('source_digest') != digest(index['sources']) and index['sources']:
            status = 'STALE' if previous else 'NOT_RUN'
        if source_drift and index['sources']:
            status = 'STALE'
        if status == 'READY' and not safe_path(root, index['root'] + '/.codegraph/codegraph.db').is_file():
            status = 'MISSING_INDEX'
        report['indexes'][iid] = status
    if report['hooks']['status'] == 'READY':
        owned = read_json(root, '.framework/local-state/owned.json', {})
        hook_paths = report['hooks'].get('paths', [])
        if not hook_paths or any(fingerprint(safe_path(root, rel)) != owned.get(rel) or
                not safe_path(root, rel).is_file() or not (safe_path(root, rel).stat().st_mode & 0o111) for rel in hook_paths):
            report['hooks']['status'] = 'STALE'
    if config.get('index') and any(s not in ('READY', 'NOT_APPLICABLE') for s in report['indexes'].values()):
        if report['status'] == 'READY':
            report['status'] = 'PARTIAL'
    if config.get('hooks') and report['hooks']['status'] not in ('READY', 'NOT_APPLICABLE'):
        if report['status'] == 'READY':
            report['status'] = 'PARTIAL'
    if report['status'] != 'READY':
        report['next_actions'] = []
        if any(status not in ('READY', 'NOT_APPLICABLE') for status in report['indexes'].values()):
            report['next_actions'].append(
                'refresh --target <project> --index --yes --allow write --allow index --allow index-install')
    registered = {m['path'] for m in config.get('modules', [])}
    registered.update(r['root'] for r in catalog.get('repos', {}).values())
    report['candidates'] = [c for c in find_candidates(root, config.get('discovery_roots', [])) if c['path'] not in registered]
    if report['candidates']:
        report['status'] = 'PARTIAL'
        report['next_actions'].append('Review candidate IDs and use module add; discovery is not enablement')
    owned = read_json(root, '.framework/local-state/owned.json', {})
    bundled = {rel: sha for rel, sha in owned.items() if rel.startswith('.agent-framework/')}
    broken = [rel for rel, sha in bundled.items() if fingerprint(safe_path(root, rel)) != sha]
    if not bundled or not safe_path(root, '.agent-framework/tools/framework').is_file() or broken:
        report['scaffold'] = 'BLOCKED'
        report['status'] = 'BLOCKED'
        report['framework_errors'] = broken or ['Missing installed framework']
        report['next_actions'].append('Inspect installed bundle; use init from a verified distribution to repair owned files')
    report['onboarding'] = 'PREPARED' if report['scaffold'] == 'READY' else 'BLOCKED'
    report['understanding'] = report['maps']['status']
    if (config.get('onboarding_mode') == 'prepare' and not current_sources
            and report['scaffold'] == 'READY' and not report['candidates'] and not source_drift):
        report['status'] = 'PREPARED'
        report['next_actions'] = ['Review requirements and design with the current agent; business implementation is not approved']
    from .project_docs import completion_checks
    report.update(completion_checks(root, config, catalog, current_sources, report))
    if report['initialization'] != 'COMPLETE':
        if report['documentation']['status'] != 'COMPLETE':
            report['next_actions'].append('Current agent: complete evidence-backed project/module dossier and accept-docs')
        if report['coverage']['status'] == 'MISSING':
            report['next_actions'].append(
                'No relationship map yet: current agent must run map --target <project> --yes --allow write --allow agent, '
                'repeat map --batch-id --result for every batch, then map --result to publish.')
        elif report['maps']['status'] == 'STALE' or report['coverage']['status'] == 'STALE':
            report['next_actions'].append(
                'Module structure changed: current agent must run map --target <project> --yes --allow write --allow agent, '
                'repeat map --batch-id --result for every batch, then map --result to publish. '
                'Internal edits do not require a new map. CodeGraph sync does not publish the relationship map.')
        report['next_actions'].append(report['handoff'].get('next_action', 'Inspect saved handoff'))
    report['knowledge'] = knowledge_status(root)
    return report


def knowledge_status(root):
    """Shell presence only. Empty content is not ingested knowledge."""
    try:
        registry = safe_path(root, 'llm-wiki-aliases.json')
        if not registry.is_file():
            return {'status': 'NOT_CONFIGURED', 'ingestion': 'NOT_APPLICABLE'}
        data = read_json(root, 'llm-wiki-aliases.json', {})
        if not isinstance(data, dict) or data.get('project') != 'knowledge/project':
            return {'status': 'NOT_CONFIGURED', 'ingestion': 'NOT_APPLICABLE'}
        if not safe_path(root, 'knowledge/project/.wiki-schema.md').is_file():
            return {'status': 'CONFLICT', 'ingestion': 'NOT_APPLICABLE'}
        wiki = safe_path(root, 'knowledge/project/wiki')
        pages = [path for path in wiki.rglob('*.md') if path.is_file() and not path.is_symlink()] if wiki.is_dir() else []
        return {'status': 'SCAFFOLDED', 'ingestion': 'EMPTY' if not pages else 'PRESENT', 'alias': 'project'}
    except (OSError, ValueError):
        return {'status': 'CONFLICT', 'ingestion': 'NOT_APPLICABLE'}
