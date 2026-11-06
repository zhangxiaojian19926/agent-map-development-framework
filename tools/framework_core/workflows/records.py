"""Private task records: idempotent commits, conflict reporting and resume.

A record is private state under `.framework/local-state/workflows/`. The
project lock serialises writers; the existing file transaction keeps the
write owned and journalled. A retry of the same request returns the original
result; a competing update on the same version is refused, never merged.
"""
import hashlib
import json
from pathlib import Path

from ..config import encoded, identity
from ..storage import apply_files, fingerprint, project_lock, read_json, safe_path
from .engine import check

RECORD_SCHEMA = 'workflow-record/v1'
REPORT_SCHEMA = 'workflow-report/v1'
RECORD_DIR = '.framework/local-state/workflows'
PAYLOAD_FIELDS = ('change', 'action', 'approval', 'state')


def record_rel(task_id):
    identity(task_id)
    return RECORD_DIR + '/' + task_id + '.json'


def report_rel():
    return RECORD_DIR + '/report.json'


def load(root, task_id):
    return read_json(root, record_rel(task_id), {}) or {}


def find_task(root, task_ref=None):
    """The state of one recorded task. Without a reference, only a single task counts."""
    if task_ref:
        record = load(root, task_ref)
        return record.get('state') if record else None
    directory = Path(root) / RECORD_DIR
    if not directory.is_dir():
        return None
    records = sorted(path for path in directory.glob('*.json') if path.name != 'report.json')
    if len(records) != 1:
        return None
    record = json.loads(records[0].read_text(encoding='utf-8'))
    return record.get('state')


def payload_digest(request):
    """Digest of what a request wants recorded; the request id binds to it."""
    material = {key: request.get(key) for key in PAYLOAD_FIELDS}
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _judge(root, request, trust_path):
    return check(root, {
        'schema': 'workflow-request/v1',
        'operation': 'check',
        'change': request.get('change'),
        'action': request.get('action'),
        'approval': request.get('approval'),
    }, trust_path=trust_path)


def commit(root, request, trust_path=None, dry_run=False):
    """Record one task update. Writes only under the private state directory."""
    if not isinstance(request, dict) or request.get('schema') != 'workflow-request/v1':
        raise ValueError('INVALID_REQUEST: schema must be workflow-request/v1')
    if request.get('operation') != 'record':
        raise ValueError('INVALID_REQUEST: operation must be record')
    task_id = request.get('task_id')
    request_id = request.get('request_id')
    identity(task_id)
    identity(request_id)
    expected = request.get('expected_version')
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 0:
        raise ValueError('INVALID_REQUEST: expected_version must be a non-negative integer')
    digest = payload_digest(request)
    rel = record_rel(task_id)
    if dry_run:
        verdict = _judge(root, request, trust_path)
        return {'status': 'DRY_RUN', 'task_id': task_id, 'required_capabilities': ['write'],
                'files': [rel, report_rel()], 'verdict': verdict['status'],
                'reason': verdict['reason'], 'missing': verdict['missing']}
    with project_lock(root):
        current = load(root, task_id)
        version = current.get('version', 0)
        seen = (current.get('requests') or {}).get(request_id)
        if seen is not None:
            if seen.get('payload_digest') == digest:
                return {'status': 'UNCHANGED', 'version': version, 'result': seen.get('result'),
                        'task_id': task_id}
            return {'status': 'CONFLICT', 'version': version, 'task_id': task_id,
                    'reason': '同一请求标识绑定了不同载荷，保留现场', 'expected_version': expected}
        if expected != version:
            return {'status': 'CONFLICT', 'version': version, 'task_id': task_id,
                    'reason': '记录版本已变化，当前为 %d，期望 %d' % (version, expected),
                    'expected_version': expected}
        verdict = _judge(root, request, trust_path)
        result = {'status': 'UPDATED', 'version': version + 1, 'task_id': task_id,
                  'verdict': verdict['status'], 'reason': verdict['reason'],
                  'missing': verdict['missing']}
        record = {
            'schema': RECORD_SCHEMA,
            'task_id': task_id,
            'version': version + 1,
            'requests': dict(current.get('requests') or {}, **{request_id: {
                'payload_digest': digest, 'result': result}}),
            'state': {key: request.get(key) for key in PAYLOAD_FIELDS},
        }
        report = read_json(root, report_rel(), {}) or {}
        tasks = dict(report.get('tasks') or {})
        tasks[task_id] = {
            'flow': verdict['axes']['flow']['status'],
            'host': verdict['axes']['host']['status'],
            'delivery': verdict['axes']['delivery']['status'],
            'reason': verdict['reason'],
            'version': version + 1,
        }
        aggregate = {'schema': REPORT_SCHEMA, 'tasks': tasks}
        changes = [
            {'path': rel, 'before_sha256': fingerprint(safe_path(root, rel)),
             'content': encoded(record)},
            {'path': report_rel(), 'before_sha256': fingerprint(safe_path(root, report_rel())),
             'content': encoded(aggregate)},
        ]
        apply_files(root, changes, 'workflow-' + task_id)
        return result


def resume(root, task_id, trust_path=None):
    """Re-judge a recorded task against current facts. Reads and writes nothing."""
    identity(task_id)
    record = load(root, task_id)
    if not record:
        raise ValueError('INVALID_REQUEST: unknown task ' + task_id)
    state = record.get('state') or {}
    verdict = _judge(root, state, trust_path)
    return {
        'status': verdict['status'],
        'version': record.get('version', 0),
        'task_id': task_id,
        'reason': verdict['reason'],
        'missing': verdict['missing'],
        'facts': verdict['facts'],
        'next_actions': verdict['next_actions'] + ['本次恢复不继承上一会话的操作授权，请按当前请求重新取得授权'],
    }


def report(root, request=None):
    """Read the recorded three-axis report. Writes nothing."""
    data = read_json(root, report_rel(), {}) or {}
    return {
        'schema': REPORT_SCHEMA,
        'operation': 'report',
        'status': 'READY',
        'read_only': True,
        'tasks': data.get('tasks') or {},
    }
