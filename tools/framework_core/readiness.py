"""Read-only checks; never repair, spawn models, or run project tests."""
from .config import digest
from .storage import read_json, safe_path, fingerprint
from .modules import source_files, find_candidates
from .maps import validate_map, design_mismatches


def inspect_project(root):
    config = read_json(root, 'framework-project.json', {})
    catalog = read_json(root, 'module-catalog.generated.json', {})
    observed = read_json(root, 'docs/project/relationships.generated.json')
    report = {'schema_version': 1, 'status': 'WAITING_AGENT',
              'scaffold': 'READY' if config and catalog else 'BLOCKED',
              'agent': {'status': 'WAITING_AGENT'}, 'maps': {'status': 'NOT_RUN'},
              'indexes': {}, 'hooks': read_json(root, '.framework/local-state/hooks.json', {'status': 'NOT_CONFIGURED'}),
              'runtime': 'NOT_RUN', 'next_actions': []}
    if not config or not catalog:
        report['status'] = 'BLOCKED'
        report['next_actions'] = ['init --target <project>']
        return report
    current_sources = {}
    stale = False
    for mid, module in catalog.get('modules', {}).items():
        current = source_files(root, module['path'])
        current_sources.update(current)
        if current != module.get('sources', {}) or not safe_path(root, module['path']).exists():
            stale = True
    if observed:
        errors = validate_map(root, catalog, observed)
        if observed.get('source_digest') != digest(current_sources):
            stale = True
        mismatch = design_mismatches(config, observed)
        agent_record = read_json(root, '.framework/local-state/agent-status.json', {})
        executed = agent_record.get('status') == 'ANALYZED' and agent_record.get('source_digest') == digest(current_sources)
        report['agent']['status'] = 'ANALYZED' if executed else 'WAITING_AGENT'
        report['maps'] = {'status': 'STALE' if stale or errors else ('SPEC_MISMATCH' if mismatch else 'READY'),
                          'errors': errors, 'design_mismatches': mismatch}
        report['status'] = 'PARTIAL' if stale or errors or mismatch else 'READY'
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
        if stale and index['sources']:
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
        report['next_actions'] = ['refresh --target <project> --yes --allow write [--allow agent] [--allow index] [--allow hooks]']
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
    return report
