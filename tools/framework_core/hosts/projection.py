"""Project workflow routers and recorded hook carriers onto a target project."""
import hashlib
import json
from pathlib import Path

from ..storage import fingerprint, safe_path
from .base import Adapter

DISTRIBUTION = Path(__file__).resolve().parents[3]
ROSTER_PATH = Path(__file__).with_name('roster.json')
FLOW_IDS = tuple('flow-%02d' % number for number in range(1, 16))
MEMBER_PREFIXES = ('openspec/', 'superpowers/', 'matt-pocock/', 'llm-wiki/', 'project-bootstrap/', 'reverse-engineer/')


def load_roster():
    return json.loads(ROSTER_PATH.read_text(encoding='utf-8'))


def host_record(host_id):
    for item in load_roster()['hosts']:
        if item['id'] == host_id:
            return item
    return None


def git_root(start):
    current = Path(start).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / '.git').exists():
            return candidate
    return None


def execution_axis(host_id, evidence=None):
    """Host execution stays NOT_RUN until a real session records a denial.

    File install is not interception. An unmounted DeepSeek bridge is not blocked.
    """
    evidence = evidence or {}
    if host_id == 'deepseek-harness' and not evidence.get('config_path_mounted'):
        return 'NOT_RUN'
    if not evidence.get('session'):
        return 'NOT_RUN'
    if evidence.get('exit_code') == 2 and evidence.get('bytes_unchanged'):
        return 'INTERCEPTED'
    if evidence.get('denied') and evidence.get('bytes_unchanged'):
        return 'INTERCEPTED'
    if evidence.get('infra_error'):
        return 'INFRA_ERROR'
    return 'NOT_RUN'


def _router_files():
    files = {}
    for flow_id in FLOW_IDS:
        path = DISTRIBUTION / 'skill/flows' / flow_id / 'SKILL.md'
        files[flow_id] = path.read_text(encoding='utf-8')
    return files


def _hook_command(root):
    if (Path(root) / 'tools/framework').is_file() and not (Path(root) / '.agent-framework/tools/framework').is_file():
        return 'python3 tools/framework host --event --target .'
    return 'python3 .agent-framework/tools/framework host --event --target .'


def _cursor_hook(root):
    return json.dumps({
        'version': 1,
        'hooks': {
            'preToolUse': [
                {
                    'command': _hook_command(root),
                    'failClosed': True,
                }
            ]
        },
    }, ensure_ascii=False, indent=2) + '\n'


def _claude_shaped_hook(root):
    return json.dumps({
        'hooks': {
            'PreToolUse': [
                {
                    'hooks': [
                        {
                            'type': 'command',
                            'command': _hook_command(root),
                        }
                    ]
                }
            ]
        }
    }, ensure_ascii=False, indent=2) + '\n'


def _gemini_hook(root):
    return json.dumps({
        'hooks': {
            'BeforeTool': [
                {
                    'hooks': [
                        {
                            'type': 'command',
                            'command': _hook_command(root),
                        }
                    ]
                }
            ]
        }
    }, ensure_ascii=False, indent=2) + '\n'


def _write(root, relative, content):
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return relative


def project_routers(root, host_id):
    """Copy the fifteen routers into a documented project discovery directory."""
    root = Path(root)
    before = _snapshot(root)
    record = host_record(host_id)
    if record is None:
        return _unchanged(root, before, {
            'status': 'FAILED',
            'reason': '宿主不在名册中：' + str(host_id),
            'files': [],
        })
    if record['discovery_evidence'] == 'CARRIER_UNKNOWN' or not record.get('discovery_dir'):
        return _unchanged(root, before, {
            'status': 'GAP',
            'host': host_id,
            'reason': 'CARRIER_UNKNOWN',
            'files': [],
        })
    target_root = root
    if host_id == 'deepseek-harness':
        target_root = git_root(root)
        if target_root is None:
            return _unchanged(root, before, {
                'status': 'FAILED',
                'host': host_id,
                'reason': '找不到 Git 根，不写入技能目录',
                'files': [],
            })
    files = []
    for flow_id, content in _router_files().items():
        relative = record['discovery_dir'] + '/' + flow_id + '/SKILL.md'
        files.append(_write(target_root, relative, content))
    report = {
        'status': 'UPDATED',
        'host': host_id,
        'files': files,
        'execution': execution_axis(host_id),
    }
    leaked = [item for item in report['files'] if not _inside(target_root, item)]
    if leaked:
        raise ValueError('install path escaped the project: ' + ','.join(leaked))
    return report


def install_gate(root, host_id):
    """Write a recorded project hook carrier. Unknown carriers write nothing."""
    root = Path(root)
    before = _snapshot(root)
    record = host_record(host_id)
    if record is None:
        return _unchanged(root, before, {
            'status': 'FAILED',
            'reason': '宿主不在名册中：' + str(host_id),
            'files': [],
        })
    if host_id == 'codebuddy':
        return _unchanged(root, before, {
            'status': 'UNCHANGED',
            'host': host_id,
            'reason': 'CodeBuddy 不获得钩子或 CODEBUDDY.md',
            'files': [],
        })
    if record['hook_evidence'] == 'CARRIER_UNKNOWN' or not record.get('hook_path'):
        return _unchanged(root, before, {
            'status': 'GAP',
            'host': host_id,
            'reason': 'CARRIER_UNKNOWN',
            'files': [],
        })
    if host_id in ('claude-code', 'qwen-code'):
        return {
            'status': 'UNCHANGED',
            'host': host_id,
            'reason': '沿用既有钩子载体，拒绝理由由适配器编码',
            'files': [],
            'execution': execution_axis(host_id),
        }
    target_root = root
    if host_id == 'deepseek-harness':
        target_root = git_root(root)
        if target_root is None:
            return _unchanged(root, before, {
                'status': 'FAILED',
                'host': host_id,
                'reason': '找不到 Git 根，不写入钩子',
                'files': [],
            })
    content = {
        'cursor': _cursor_hook,
        'deepseek-harness': _claude_shaped_hook,
        'codex': _claude_shaped_hook,
        'gemini-cli': _gemini_hook,
    }[host_id](target_root)
    relative = _write(target_root, record['hook_path'], content)
    return {
        'status': 'UPDATED',
        'host': host_id,
        'files': [relative],
        'execution': execution_axis(host_id),
        'blocked': False,
    }


def _snapshot(root):
    paths = []
    if Path(root).exists():
        for path in Path(root).rglob('*'):
            if path.is_file():
                paths.append(str(path.relative_to(root)))
    return sorted(paths)


def _unchanged(root, before, report):
    after = _snapshot(root)
    if after != before:
        raise ValueError('refusing host wrote files: ' + ','.join(sorted(set(after) - set(before))))
    return report


def _inside(root, relative):
    try:
        safe_path(root, relative)
    except ValueError:
        return False
    return True


class CursorAdapter(Adapter):
    """Cursor project skills plus a fail-closed preToolUse hook.

    Only Write is an authenticated write tool. Other write tool names stay
    uncovered until a real preToolUse event records them. Read is allowed.
    """

    host_id = 'cursor'
    label = 'Cursor'
    write_tools = ('Write',)
    read_tools = ('Read',)

    def preview(self, root):
        files = {}
        for flow_id, content in _router_files().items():
            files['.cursor/skills/%s/SKILL.md' % flow_id] = content
        files['.cursor/hooks.json'] = _cursor_hook(root)
        return _preview(root, files)

    def verify(self, root):
        return _verify(root, self.preview(root)['files'])

    def encode(self, verdict):
        if verdict.get('status') in ('READY', 'NOT_APPLICABLE') or not verdict.get('covered'):
            return {'permission': 'allow'}, 0
        reason = verdict.get('reason') or ''
        return {'permission': 'deny', 'agent_message': reason, 'user_message': reason}, 0


class DeepSeekAdapter(Adapter):
    """Flat project skills under the Git root. The hook file does not block
    until a profile mounts it, and unconfirmed tool names stay uncovered.
    """

    host_id = 'deepseek-harness'
    label = 'DeepSeek harness'
    write_tools = ()
    read_tools = ()

    def preview(self, root):
        files = {}
        for flow_id, content in _router_files().items():
            files['.dsh/skills/%s/SKILL.md' % flow_id] = content
        files['.dsh/hooks.json'] = _claude_shaped_hook(root)
        return _preview(root, files)

    def verify(self, root):
        return _verify(root, self.preview(root)['files'])

    def encode(self, verdict):
        blocked = verdict['status'] not in ('READY', 'NOT_APPLICABLE') and verdict.get('covered')
        decision = 'deny' if blocked else 'allow'
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': decision,
                'permissionDecisionReason': verdict.get('reason') or '',
            }
        }, 2 if blocked else 0


class CodexAdapter(Adapter):
    """Recorded project hook carrier. Tool names stay uncovered."""

    host_id = 'codex'
    label = 'Codex'
    write_tools = ()
    read_tools = ()

    def preview(self, root):
        return _preview(root, {'.codex/hooks.json': _claude_shaped_hook(root)})

    def verify(self, root):
        return _verify(root, self.preview(root)['files'])

    def encode(self, verdict):
        return {'status': verdict['status'], 'covered': False, 'reason': verdict.get('reason')}, 0


class GeminiAdapter(Adapter):
    """Recorded BeforeTool carrier. Tool names stay uncovered."""

    host_id = 'gemini-cli'
    label = 'Gemini CLI'
    write_tools = ()
    read_tools = ()

    def preview(self, root):
        return _preview(root, {'.gemini/settings.json': _gemini_hook(root)})

    def verify(self, root):
        return _verify(root, self.preview(root)['files'])

    def encode(self, verdict):
        return {'status': verdict['status'], 'covered': False, 'reason': verdict.get('reason')}, 0


def _preview(root, files):
    conflicts = []
    for rel, content in files.items():
        actual = fingerprint(safe_path(root, rel))
        if actual is not None and actual != hashlib.sha256(content.encode()).hexdigest():
            conflicts.append(rel)
    return {'files': files, 'conflicts': conflicts}


def _verify(root, files):
    results = []
    for rel, content in files.items():
        actual = fingerprint(safe_path(root, rel))
        expected = hashlib.sha256(content.encode()).hexdigest()
        results.append({'path': rel, 'installed': actual == expected})
    status = 'VERIFIED' if results and all(item['installed'] for item in results) else 'NOT_VERIFIED'
    return {'status': status, 'files': results, 'execution': 'NOT_RUN'}
