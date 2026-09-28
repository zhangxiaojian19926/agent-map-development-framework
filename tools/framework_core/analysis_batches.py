"""Bounded current-agent analysis; only a complete, current session publishes maps."""
import hashlib
from pathlib import Path
import uuid

from .config import digest, encoded
from .handoff import REQUEST, current_sources, require
from .maps import map_outputs, validate_map
from .modules import EXCLUDED, EXTENSIONS
from .storage import apply_files, fingerprint, owned_changes, project_lock, read_json, resume_run, safe_path

STATE = '.framework/local-state/analysis-session.json'
MAX_BYTES = 200000


def split_sources(sources, max_bytes=MAX_BYTES):
    """One contiguous file slice per packet; binary search includes JSON overhead."""
    packets = []
    for source in sorted(sources, key=lambda s: (s.get('module_id', ''), s['path'])):
        lines = source['content'].splitlines(keepends=True)
        start = 0
        while start < len(lines) or (not lines and start == 0):
            def packet(end):
                part = {'path': source['path'], 'file_sha256': source['sha256'],
                        'start_line': start + 1, 'end_line': end,
                        'content': ''.join(lines[start:end])}
                part['slice_id'] = digest(part)
                return {'schema_version': 2, 'session_id': '0'*32,
                        'batch_id': digest([part['slice_id']]), 'slices': [part]}
            lo, hi, chosen = start + (1 if lines else 0), len(lines), None
            while lo <= hi:
                end = (lo + hi) // 2
                candidate = packet(end)
                if len(encoded(candidate).encode('utf-8')) <= max_bytes:
                    chosen, lo = candidate, end + 1
                else:
                    hi = end - 1
            if chosen is None:
                raise ValueError('FILE_SLICE_TOO_LARGE: ' + source['path'])
            packets.append(chosen)
            if not lines:
                break
            start = chosen['slices'][0]['end_line']
    return packets


def framework_digest(root):
    installed = safe_path(root, '.agent-framework/framework-manifest.json')
    path = installed if installed.exists() else Path(__file__).resolve().parents[2]/'framework-manifest.json'
    return fingerprint(path)


def snapshot(root, catalog):
    if catalog != read_json(root, 'module-catalog.generated.json'):
        raise ValueError('STALE_CATALOG')
    sources = current_sources(root, catalog)
    metadata = []
    for path, sha in sources.items():
        body = safe_path(root, path).read_bytes()
        if hashlib.sha256(body).hexdigest() != sha:
            raise ValueError('STALE_SOURCE')
        owner = min(mid for mid, m in catalog['modules'].items() if path in m['sources'])
        packets = split_sources([{'path': path, 'sha256': sha, 'content': body.decode('utf-8'), 'module_id': owner}])
        for packet in packets:
            packet.pop('session_id')
            packet['slices'] = [{k: v for k, v in part.items() if k != 'content'} for part in packet['slices']]
            metadata.append(packet)
    if current_sources(root, catalog) != sources:
        raise ValueError('STALE_SOURCE')
    return sources, metadata


def save_state(root, state):
    apply_files(root, owned_changes(root, {STATE: encoded(state)}), 'analysis-session')


def begin_analysis(root, catalog, grants):
    require(grants)
    with project_lock(root):
        if catalog != read_json(root, 'module-catalog.generated.json'):
            raise ValueError('STALE_CATALOG')
        sources = current_sources(root, catalog)
        binding = {'schema_version': 2, 'catalog_digest': digest(catalog),
                   'source_digest': digest(sources), 'framework_digest': framework_digest(root)}
        old = read_json(root, STATE, {})
        active = read_json(root, REQUEST, {})
        if (all(old.get(k) == v for k, v in binding.items()) and old.get('session_id')
                and active.get('request_id') == old['session_id']):
            return old
        verified_sources, metadata = snapshot(root, catalog)
        if sources != verified_sources:
            raise ValueError('STALE_SOURCE')
        state = dict(binding, session_id=uuid.uuid4().hex, sources=sources, status='ANALYZING',
                     batches=[dict(b, status='PENDING') for b in metadata],
                     scope={'extensions': sorted(EXTENSIONS), 'excluded_directories': sorted(EXCLUDED),
                            'max_depth': 12, 'max_files_per_module': 5000,
                            'max_file_bytes': 1048576, 'packet_bytes': MAX_BYTES})
        outputs = {STATE: encoded(state), REQUEST: encoded({'schema_version': 2, 'request_id': state['session_id']})}
        apply_files(root, owned_changes(root, outputs), 'analysis-session')
        return state


def checked_session(root, session_id):
    state = read_json(root, STATE, {})
    if not session_id or state.get('session_id') != session_id or read_json(root, REQUEST, {}).get('request_id') != session_id:
        raise ValueError('STALE_REQUEST')
    if framework_digest(root) != state['framework_digest']:
        raise ValueError('STALE_FRAMEWORK')
    catalog = read_json(root, 'module-catalog.generated.json', {})
    if digest(catalog) != state['catalog_digest']:
        raise ValueError('STALE_CATALOG')
    if current_sources(root, catalog) != state['sources']:
        raise ValueError('STALE_SOURCE')
    return state, catalog


def selected_batch(state, batch_id):
    for batch in state['batches']:
        if batch['batch_id'] == batch_id:
            return batch
    raise ValueError('UNKNOWN_BATCH')


def read_batch(root, session_id, batch_id, grants):
    require(grants)
    with project_lock(root):
        state, catalog = checked_session(root, session_id)
        batch = selected_batch(state, batch_id)
        if batch['status'] == 'ACCEPTED':
            return {'session_id': session_id, 'batch_id': batch_id, 'status': 'ACCEPTED', 'result': batch['result']}
        parts = []
        for part in batch['slices']:
            body = safe_path(root, part['path']).read_bytes()
            if hashlib.sha256(body).hexdigest() != part['file_sha256']:
                raise ValueError('STALE_SOURCE')
            content = ''.join(body.decode('utf-8').splitlines(keepends=True)[part['start_line']-1:part['end_line']])
            restored = dict(part, content=content)
            if digest({k: v for k, v in restored.items() if k != 'slice_id'}) != part['slice_id']:
                raise ValueError('STALE_SOURCE')
            parts.append(restored)
        packet = {'schema_version': 2, 'session_id': session_id, 'batch_id': batch_id, 'slices': parts}
        if len(encoded(packet).encode()) > MAX_BYTES:
            raise ValueError('SOURCE_BUDGET_EXCEEDED')
        checked_session(root, session_id)
        return packet


def accept_batch(root, session_id, batch_id, result, grants):
    require(grants)
    with project_lock(root):
        state, catalog = checked_session(root, session_id)
        batch = selected_batch(state, batch_id)
        if (not isinstance(result, dict) or set(result) != {'summary', 'uncertainties', 'slice_ids'}
                or not isinstance(result['summary'], str) or not result['summary'].strip()
                or not isinstance(result['uncertainties'], list)
                or any(not isinstance(u, str) for u in result['uncertainties'])
                or result['slice_ids'] != [s['slice_id'] for s in batch['slices']]
                or len(encoded(result).encode()) > 100000):
            raise ValueError('INVALID_EVIDENCE: batch coverage/summary')
        if batch['status'] == 'ACCEPTED':
            if batch['result'] != result:
                raise ValueError('BATCH_CONFLICT')
        else:
            batch.update(status='ACCEPTED', result=result)
            checked_session(root, session_id)
            save_state(root, state)
        return {'status': 'ACCEPTED', 'session_id': session_id, 'batch_id': batch_id}


def finalize_analysis(root, session_id, result, grants):
    require(grants)
    with project_lock(root):
        state, catalog = checked_session(root, session_id)
        if any(b['status'] != 'ACCEPTED' for b in state['batches']):
            raise ValueError('INCOMPLETE_COVERAGE')
        if state['status'] == 'COMPLETE':
            if state.get('result_digest') != digest(result):
                raise ValueError('BATCH_CONFLICT')
            resume_run(root, 'analysis-final-'+session_id, grants)
            return {'status': 'ANALYZED', 'coverage': state['coverage'], 'runtime': 'NOT_RUN'}
        try:
            errors = validate_map(root, catalog, result)
        except (TypeError, KeyError, AttributeError, ValueError):
            errors = ['INVALID_SCHEMA']
        if errors:
            raise ValueError('INVALID_EVIDENCE: ' + ','.join(errors))
        coverage = {'status': 'COMPLETE', 'session_id': session_id, 'source_digest': state['source_digest'],
                    'catalog_digest': state['catalog_digest'], 'framework_digest': state['framework_digest'],
                    'files': len(state['sources']), 'batches': len(state['batches']), 'scope': state['scope']}
        observed = dict(result, schema_version=1, source_digest=state['source_digest'])
        state.update(status='COMPLETE', result_digest=digest(result), coverage=coverage)
        outputs = map_outputs(root, catalog, observed)
        outputs.update({STATE: encoded(state), '.framework/local-state/analysis-coverage.json': encoded(coverage),
            '.framework/local-state/agent-status.json': encoded({'status': 'ANALYZED', 'execution': 'current-session',
                'source_digest': state['source_digest'], 'analysis_revision': 'batches-v2', 'request_id': session_id})})
        checked_session(root, session_id)
        apply_files(root, owned_changes(root, outputs), 'analysis-final-'+session_id)
        checked_session(root, session_id)
        return {'status': 'ANALYZED', 'coverage': coverage, 'runtime': 'NOT_RUN'}
