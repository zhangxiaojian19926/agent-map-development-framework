"""Resumable capability stages; persistent observations are not execution grants."""
from .config import encoded, digest
from .storage import apply_files, owned_changes, read_json, safe_path
from .modules import discover, catalog_update, find_candidates
from .adapters import ensure_index
from .hooks import hook_plan
from .readiness import inspect_project


def save(root, outputs, stage):
    changes = owned_changes(root, outputs)
    if changes:
        apply_files(root, changes, stage)


def sync_catalog(root, config):
    declarations = config.get('modules', [])
    catalog = catalog_update(read_json(root, 'module-catalog.generated.json', {}), declarations,
                             discover(root, [m['path'] for m in declarations], 12))
    registered = {m['path'] for m in declarations}
    registered.update(r['root'] for r in catalog['repos'].values())
    catalog['candidates'] = [c for c in find_candidates(root, config.get('discovery_roots', [])) if c['path'] not in registered]
    save(root, {'module-catalog.generated.json': encoded(catalog)}, 'catalog')
    return catalog


def refresh(root, config, grants):
    catalog = sync_catalog(root, config)
    previous = read_json(root, '.framework/local-state/indexes.json', {})
    if config.get('index'):
        for iid, index in catalog['indexes'].items():
            cached = previous.get(iid, {})
            if cached.get('adapter_revision') == 'scope-v4' and cached.get('verified') and cached.get('source_digest') == digest(index['sources']) and safe_path(root, index['root'] + '/.codegraph/codegraph.db').exists():
                continue
            previous[iid] = ensure_index(root, index, grants)
        save(root, {'.framework/local-state/indexes.json': encoded(previous)}, 'indexes')
    if config.get('hooks'):
        states = []
        hook_paths = []
        for repo in catalog['repos'].values():
            plan = hook_plan(safe_path(root, repo['root']), root)
            states.append(plan['status'])
            if plan['status'] == 'READY':
                save(root, {c['path']: c['content'] for c in plan['changes']}, 'hooks')
                for change in plan['changes']:
                    safe_path(root, change['path']).chmod(0o755)
                    hook_paths.append(change['path'])
        state = 'HOOK_CONFLICT' if 'HOOK_CONFLICT' in states else ('READY' if states else 'NOT_APPLICABLE')
        save(root, {'.framework/local-state/hooks.json': encoded({'status': state, 'repos': states, 'paths': hook_paths})}, 'hook-report')
    return inspect_project(root)
