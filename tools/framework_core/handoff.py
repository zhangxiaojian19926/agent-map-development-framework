"""Host-neutral, bounded current-agent requests and deterministic result checks."""
import uuid

from .config import digest, encoded
from .maps import map_outputs, validate_map
from .modules import source_files
from .storage import apply_files, owned_changes, project_lock, read_json, safe_path

REQUEST = '.framework/local-state/analysis-request.json'


def require(grants):
    if not {'write', 'agent'} <= grants:
        raise ValueError('CONSENT_REQUIRED: write/agent')


def current_sources(root, catalog):
    sources = {}
    for module in catalog['modules'].values():
        observed = source_files(root, module['path'])
        if observed != module['sources']:
            raise ValueError('STALE_SOURCE')
        sources.update(observed)
    return sources


def make_analysis_request(root, catalog, grants):
    require(grants)
    with project_lock(root):
        if catalog != read_json(root, 'module-catalog.generated.json'):
            raise ValueError('STALE_CATALOG')
        sources = current_sources(root, catalog)
        packet = {'schema_version': 1, 'request_id': uuid.uuid4().hex,
                  'catalog_digest': digest(catalog), 'source_digest': digest(sources),
                  'modules': [{'id': mid, 'path': m['path']} for mid, m in catalog['modules'].items()],
                  'sources': [], 'runtime': 'NOT_RUN'}
        size = 0
        for path, sha in sorted(sources.items()):
            source = safe_path(root, path)
            size += source.stat().st_size
            if size > 200000:
                raise ValueError('SOURCE_BUDGET_EXCEEDED')
            packet['sources'].append({'path': path, 'sha256': sha, 'content': source.read_text()})
        if len(encoded(packet).encode()) > 220000:
            raise ValueError('SOURCE_BUDGET_EXCEEDED')
        if current_sources(root, catalog) != sources:
            raise ValueError('STALE_SOURCE')
        # Persist binding only, not a duplicate of potentially private source.
        binding = {k: v for k, v in packet.items() if k != 'sources'}
        apply_files(root, owned_changes(root, {REQUEST: encoded(binding)}), 'analysis-request')
        return packet


def accept_analysis(root, envelope, grants):
    require(grants)
    if not isinstance(envelope, dict) or set(envelope) != {'request_id', 'source_digest', 'result'} or len(encoded(envelope)) > 1024 * 1024:
        raise ValueError('INVALID_EVIDENCE: envelope')
    with project_lock(root):
        current = read_json(root, REQUEST, {})
        if current.get('request_id') != envelope['request_id'] or current.get('consumed'):
            raise ValueError('STALE_REQUEST')
        catalog = read_json(root, 'module-catalog.generated.json', {})
        if digest(catalog) != current.get('catalog_digest'):
            raise ValueError('STALE_CATALOG')
        sources = current_sources(root, catalog)
        if digest(sources) != current.get('source_digest') or envelope['source_digest'] != digest(sources):
            raise ValueError('STALE_SOURCE')
        result = envelope['result']
        try:
            errors = validate_map(root, catalog, result)
        except (TypeError, KeyError, AttributeError, ValueError):
            errors = ['INVALID_SCHEMA']
        if errors:
            raise ValueError('INVALID_EVIDENCE: ' + ','.join(errors))
        result = dict(result, source_digest=digest(sources), schema_version=1)
        agent = {'status': 'ANALYZED', 'execution': 'current-session',
                 'source_digest': digest(sources), 'analysis_revision': 'map-v2',
                 'request_id': current['request_id']}
        outputs = map_outputs(root, catalog, result)
        outputs['.framework/local-state/agent-status.json'] = encoded(agent)
        outputs[REQUEST] = encoded(dict(current, consumed=True))
        # Revalidate after validation/rendering, immediately before publication.
        current_sources(root, catalog)
        apply_files(root, owned_changes(root, outputs), 'current-analysis')
        return {'status': 'ANALYZED', 'agent': agent, 'runtime': 'NOT_RUN'}
