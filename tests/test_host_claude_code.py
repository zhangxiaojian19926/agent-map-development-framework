import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core import cli

NAMESPACE = 'framework-workflow-approval/v1'
CLAUDE_FILES = [
    '.claude/agents/uap-challenger.md',
    '.claude/agents/uap-investigator.md',
    '.claude/agents/uap-verifier.md',
    '.claude/settings.json',
]
WRITE_TOOLS = ('Write', 'Edit', 'MultiEdit')


def agent_tools(text):
    for line in text.splitlines():
        if line.startswith('tools:'):
            return [item.strip() for item in line.split(':', 1)[1].split(',')]
    return []


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class HostCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.records = __import__('framework_core.workflows.records', fromlist=['records'])
        write_json(self.root / 'framework-project.json', {'project_id': 'demo', 'agent': 'current'})
        self.change_dir = self.root / 'openspec/changes/demo-change'
        self.spec = self.change_dir / 'specs/core/spec.md'
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text(
            '## ADDED Requirements\n\n### Requirement: 核心\n\n'
            '#### Scenario: 正常\n- **WHEN** 有效\n- **THEN** 完成\n', encoding='utf-8')
        self.plan = self.change_dir / 'implementation-plan.md'
        self.plan.write_text('# 计划\n\n- 步骤\n', encoding='utf-8')
        self.keys = self.root / 'keys'
        self.keys.mkdir()
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(self.keys / 'approver')],
                       check=True, capture_output=True)
        self.trust_dir = self.root / 'trust'
        self.trust_dir.mkdir()
        self.trust = self.trust_dir / 'allowed_signers'
        self.trust.write_text('approver-1 ' + (self.keys / 'approver.pub').read_text().strip() + '\n',
                               encoding='utf-8')
        os.chmod(self.trust, 0o444)
        os.chmod(self.trust_dir, 0o555)

    def approval(self):
        payload = {
            'schema': 'workflow-approval/v1',
            'project': 'demo',
            'change': 'demo-change',
            'files': {
                'specs/core/spec.md': digest(self.spec),
                'implementation-plan.md': digest(self.plan),
            },
            'scope': ['edit_source', 'implement'],
        }
        payload_path = self.keys / 'approval.json'
        payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run(['ssh-keygen', '-Y', 'sign', '-f', str(self.keys / 'approver'), '-n', NAMESPACE,
                        str(payload_path)], check=True, capture_output=True)
        return {'payload': str(payload_path), 'signature': str(payload_path) + '.sig'}

    def record_task(self, approval=None):
        request = {
            'schema': 'workflow-request/v1',
            'operation': 'record',
            'task_id': 'demo-task',
            'request_id': 'req-1',
            'expected_version': 0,
            'change': 'demo-change',
            'action': 'edit_source',
        }
        if approval:
            request['approval'] = approval
        return self.records.commit(self.root, request, trust_path=self.trust)

    def run_cli(self, args, stdin=None):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            if stdin is not None:
                saved = sys.stdin
                sys.stdin = io.StringIO(stdin)
                try:
                    code = cli.main(args)
                finally:
                    sys.stdin = saved
            else:
                code = cli.main(args)
        return code, json.loads(stdout.getvalue())


class HostInstallTest(HostCase):
    def request_file(self, operation):
        path = self.root / ('host-%s.json' % operation)
        write_json(path, {'schema': 'host-request/v1', 'operation': operation, 'host': 'claude-code'})
        return path

    def test_preview_lists_the_project_level_hook(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('preview'))])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'READY')
        self.assertEqual(report['files'], CLAUDE_FILES)
        self.assertEqual(report['conflicts'], [])

    def test_apply_installs_the_hook_and_records_the_host(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('apply')), '--allow', 'write', '--allow', 'hooks'])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'UPDATED')
        self.assertTrue((self.root / '.claude/settings.json').is_file())
        for rel in CLAUDE_FILES:
            self.assertTrue((self.root / rel).is_file(), rel)
        self.assertFalse((self.root / 'CODEBUDDY.md').exists())
        for name in ('uap-challenger.md', 'uap-investigator.md', 'uap-verifier.md'):
            tools = agent_tools((self.root / '.claude/agents' / name).read_text(encoding='utf-8'))
            self.assertFalse(set(WRITE_TOOLS) & set(tools), name)
        state = json.loads((self.root / '.framework/local-state/hosts.json').read_text(encoding='utf-8'))
        self.assertEqual(state['host'], 'claude-code')

    def test_apply_without_the_write_grant_is_refused(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('apply'))])
        self.assertEqual(code, 3)
        self.assertEqual(report['status'], 'CONSENT_REQUIRED')
        self.assertFalse((self.root / '.claude/settings.json').exists())

    def test_verify_reports_the_installed_hook(self):
        self.run_cli(['host', '--target', str(self.root), '--request',
                      str(self.request_file('apply')), '--allow', 'write', '--allow', 'hooks'])
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('verify'))])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'VERIFIED')

    def test_apply_host_refuses_without_the_grant(self):
        """WF-05：安装宿主适配需要 write 与 hooks 两项能力。"""
        from framework_core.hosts.base import apply_host, load_adapter
        self.assertTrue(load_adapter('claude-code').requires_hooks)
        result = apply_host(self.root, 'claude-code', set())
        self.assertEqual(result['status'], 'CONSENT_REQUIRED')
        self.assertEqual(result['required'], ['write', 'hooks'])
        write_only = apply_host(self.root, 'claude-code', {'write'})
        self.assertEqual(write_only['status'], 'CONSENT_REQUIRED')
        self.assertEqual(write_only['required'], ['write', 'hooks'])
        self.assertFalse((self.root / '.claude/settings.json').exists())


class HostEventTest(HostCase):
    def install(self):
        request = {'schema': 'host-request/v1', 'operation': 'apply', 'host': 'claude-code'}
        path = self.root / 'host-apply.json'
        write_json(path, request)
        self.run_cli(['host', '--target', str(self.root), '--request', str(path),
                      '--allow', 'write', '--allow', 'hooks'])

    def send(self, tool, task_ref=None):
        event = {'hook_event_name': 'PreToolUse', 'tool_name': tool,
                 'tool_input': {'file_path': 'src/service.py'}}
        if task_ref:
            event['task_ref'] = task_ref
        code, report = self.run_cli(['host', '--target', str(self.root), '--event'],
                                    stdin=json.dumps(event))
        return code, report

    def decision(self, report):
        return report['hookSpecificOutput']['permissionDecision']

    def test_write_without_a_bound_task_is_denied(self):
        """WF-05-NATIVE：没有绑定任务时缺事实，不放行写入。"""
        self.install()
        code, report = self.send('Edit')
        self.assertEqual(code, 0)
        self.assertEqual(self.decision(report), 'deny')
        self.assertTrue(report['hookSpecificOutput']['permissionDecisionReason'])

    def test_write_without_a_valid_approval_is_denied(self):
        """WF-05-NATIVE：缺少批准时请求宿主阻断。"""
        self.install()
        self.record_task()
        code, report = self.send('Edit')
        self.assertEqual(self.decision(report), 'deny')

    def test_write_with_a_valid_approval_is_allowed(self):
        """WF-05-NATIVE：有效批准时放行（模块接缝；CLI 接缝需要系统级信任锚点）。"""
        from framework_core.hosts.base import judge_event
        from framework_core.hosts.claude_code import ClaudeCodeAdapter
        self.install()
        self.record_task(self.approval())
        verdict = judge_event(self.root, ClaudeCodeAdapter(), {'tool_name': 'Edit'},
                              trust_path=self.trust)
        self.assertEqual(verdict['status'], 'READY')
        payload, _ = ClaudeCodeAdapter().encode(verdict)
        self.assertEqual(payload['hookSpecificOutput']['permissionDecision'], 'allow')

    def test_cli_denies_when_no_protected_trust_source_exists(self):
        """WF-08-MUTABLE：没有受保护的信任来源时 CLI 也拒绝写入。"""
        self.install()
        self.record_task(self.approval())
        code, report = self.send('Edit')
        self.assertEqual(self.decision(report), 'deny')
        self.assertIn('信任来源', report['hookSpecificOutput']['permissionDecisionReason'])

    def test_unauthenticated_tool_is_reported_as_a_coverage_gap(self):
        """WF-06-FAIL：未命中已认证入口时不声称已阻断。"""
        self.install()
        self.record_task(self.approval())
        code, report = self.send('Bash')
        self.assertEqual(self.decision(report), 'allow')
        self.assertIn('不在已认证入口内', report['hookSpecificOutput']['permissionDecisionReason'])
