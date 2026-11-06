"""Shared host adapter contract.

An adapter normalises a native tool event into the shared judgement and
encodes the verdict back into the host's own decision. The gate only claims
control of authenticated entry points; every other tool is reported as a
coverage gap and left to the host's own permission model.
"""
from ..config import encoded
from ..storage import apply_files, fingerprint, owned_changes, safe_path
from ..workflows.engine import check
from ..workflows.records import find_task

ADAPTERS = {'claude-code': 'claude_code', 'qwen-code': 'qwen_code'}
FAULT_CLASSES = ('shell', 'unknown_tool', 'hook_timeout', 'hook_crash', 'hook_disabled')
HOST_STATE = '.framework/local-state/hosts.json'
HOST_REQUEST_SCHEMA = 'host-request/v1'


def load_adapter(host_id):
    """The adapter for an installed host id."""
    if host_id not in ADAPTERS:
        raise ValueError('UNKNOWN_HOST: ' + str(host_id))
    module = __import__('framework_core.hosts.' + ADAPTERS[host_id], fromlist=['ADAPTER'])
    return module.ADAPTER()


def installed_host(root):
    """Which host this project installed, from the private state."""
    from pathlib import Path
    path = Path(root) / HOST_STATE
    if not path.is_file():
        return None
    import json
    try:
        return json.loads(path.read_text(encoding='utf-8')).get('host')
    except ValueError:
        return None


def _axes(flow, host):
    return {
        'flow': {'status': flow},
        'host': {'status': host},
        'delivery': {'status': 'NOT_RUN'},
    }


class Adapter:
    """What every host adapter must provide."""

    host_id = ''
    label = ''
    write_tools = ()
    read_tools = ()

    def tool_action(self, tool):
        """The shared action for a native tool name, or None when not covered."""
        if tool in self.write_tools:
            return 'edit_source'
        if tool in self.read_tools:
            return 'read'
        return None

    def preview(self, root):
        """Project-level files this adapter would install."""
        return {}

    def encode(self, verdict):
        """Encode a shared verdict into this host's native decision."""
        raise NotImplementedError('host adapters must encode their own decision')

    def verify(self, root):
        """Check the installed files against the adapter's own content."""
        return {'status': 'NOT_VERIFIED', 'files': []}


def judge_event(root, adapter, event, trust_path=None):
    """Judge one native tool event with the shared engine."""
    event = event or {}
    tool = event.get('tool_name') or (event.get('tool') or {}).get('name')
    action = adapter.tool_action(tool)
    if action is None:
        return {
            'status': 'NOT_APPLICABLE',
            'reason': '工具 %s 不在已认证入口内，本门禁不声明覆盖' % (tool or '未知'),
            'axes': _axes('NOT_APPLICABLE', 'NOT_VERIFIED'),
            'covered': False,
            'tool': tool,
        }
    state = find_task(root, event.get('task_ref') or event.get('task_id'))
    if not state:
        return {
            'status': 'NOT_VERIFIED',
            'reason': '没有绑定任务，缺少 change 与批准事实',
            'axes': _axes('NOT_VERIFIED', 'NOT_VERIFIED'),
            'covered': False,
            'tool': tool,
        }
    request = {
        'schema': 'workflow-request/v1',
        'operation': 'check',
        'change': state.get('change'),
        'action': action,
        'approval': state.get('approval'),
    }
    verdict = check(root, request, trust_path=trust_path)
    verdict['covered'] = True
    verdict['tool'] = tool
    return verdict


def preview_host(root, host_id):
    """Read-only preview of the project-level files an adapter would install."""
    adapter = load_adapter(host_id)
    preview = adapter.preview(root)
    return {
        'schema': 'host-report/v1',
        'operation': 'preview',
        'status': 'READY',
        'host': host_id,
        'files': sorted(preview['files']),
        'conflicts': preview['conflicts'],
    }


def apply_host(root, host_id, grants):
    """Install the project-level files under the current write grant."""
    if not {'write', 'hooks'} <= set(grants):
        return {'status': 'CONSENT_REQUIRED', 'required': ['write', 'hooks']}
    adapter = load_adapter(host_id)
    preview = adapter.preview(root)
    if preview['conflicts']:
        return {'status': 'CONFLICT', 'host': host_id, 'conflicts': preview['conflicts'],
                'reason': '存在人工改动或归属不明的受管文件，保留现场'}
    changes = owned_changes(root, preview['files'])
    changes.append({
        'path': HOST_STATE,
        'before_sha256': fingerprint(safe_path(root, HOST_STATE)),
        'content': encoded({'host': host_id, 'label': adapter.label,
                            'files': sorted(preview['files'])}),
    })
    apply_files(root, changes, 'host-' + host_id)
    return {'status': 'UPDATED', 'host': host_id, 'files': sorted(preview['files'])}


def verify_host(root, host_id):
    """Check the installed files against the adapter's own content."""
    adapter = load_adapter(host_id)
    result = adapter.verify(root)
    return {'schema': 'host-report/v1', 'operation': 'verify', 'status': result['status'],
            'host': host_id, 'files': result['files']}


COVERAGE_STATUSES = ('VERIFIED', 'NOT_VERIFIED', 'NOT_RUN', 'INFRA_ERROR',
                      'NOT_APPLICABLE', 'CONFLICT', 'FAILED')


def record_coverage(root, host_id, classes, grants):
    """Record what a host was actually observed to do. Claims need evidence."""
    if not {'write', 'hooks'} <= set(grants):
        return {'status': 'CONSENT_REQUIRED', 'required': ['write', 'hooks']}
    rows = {}
    for item in classes or []:
        name = item.get('class')
        if name not in FAULT_CLASSES:
            raise ValueError('UNKNOWN_FAULT_CLASS: ' + str(name))
        status = item.get('status')
        if status not in COVERAGE_STATUSES:
            raise ValueError('INVALID_COVERAGE_STATUS: ' + str(status))
        if status == 'VERIFIED' and not item.get('evidence'):
            raise ValueError('MISSING_EVIDENCE: a verified class needs its evidence')
        rows[name] = {'status': status, 'evidence': item.get('evidence')}
    path = '.framework/local-state/hosts/%s-coverage.json' % host_id
    changes = [{
        'path': path,
        'before_sha256': fingerprint(safe_path(root, path)),
        'content': encoded(rows),
    }]
    apply_files(root, changes, 'host-coverage-' + host_id)
    return {'status': 'UPDATED', 'host': host_id, 'classes': sorted(rows)}


def coverage(root, host_id):
    """What this host has been observed to do. Nothing is claimed without evidence."""
    from pathlib import Path as _Path
    state = _Path(root) / ('.framework/local-state/hosts/%s-coverage.json' % host_id)
    observed = {}
    if state.is_file():
        import json
        try:
            observed = json.loads(state.read_text(encoding='utf-8'))
        except ValueError:
            observed = {}
    classes = []
    for name in FAULT_CLASSES:
        row = observed.get(name) or {}
        classes.append({'class': name, 'status': row.get('status', 'NOT_RUN'),
                        'evidence': row.get('evidence')})
    return {'schema': 'host-report/v1', 'operation': 'coverage', 'status': 'READY',
            'host': host_id, 'classes': classes}


def handle_event(root, event, trust_path=None):
    """Judge a native event and encode the host's own decision."""
    host_id = installed_host(root)
    if not host_id:
        return {'status': 'NOT_CONFIGURED', 'reason': '本工程没有安装宿主适配'}, 5
    adapter = load_adapter(host_id)
    verdict = judge_event(root, adapter, event, trust_path=trust_path)
    payload, code = adapter.encode(verdict)
    return payload, code
