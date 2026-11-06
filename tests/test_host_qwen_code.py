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


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CrossHostCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = __import__('framework_core.hosts.base', fromlist=['base'])
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


class SameFactsSameVerdictTest(CrossHostCase):
    """WF-06-SAME：两个原生宿主为相同项目和动作提供等价事实。"""

    def test_both_hosts_judge_the_same_facts_the_same_way(self):
        self.record_task(self.approval())
        claude = self.base.load_adapter('claude-code')
        qwen = self.base.load_adapter('qwen-code')
        claude_verdict = self.base.judge_event(self.root, claude, {'tool_name': 'Edit'},
                                                trust_path=self.trust)
        qwen_verdict = self.base.judge_event(self.root, qwen, {'tool_name': 'write_file'},
                                             trust_path=self.trust)
        self.assertEqual(claude_verdict['status'], qwen_verdict['status'])
        self.assertEqual(claude_verdict['reason'], qwen_verdict['reason'])

    def test_native_decisions_are_reported_per_host(self):
        self.record_task()
        claude = self.base.load_adapter('claude-code')
        qwen = self.base.load_adapter('qwen-code')
        claude_verdict = self.base.judge_event(self.root, claude, {'tool_name': 'Edit'},
                                                trust_path=self.trust)
        qwen_verdict = self.base.judge_event(self.root, qwen, {'tool_name': 'write_file'},
                                             trust_path=self.trust)
        claude_decision, _ = claude.encode(claude_verdict)
        qwen_decision, _ = qwen.encode(qwen_verdict)
        self.assertEqual(claude_decision['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(qwen_decision['hookSpecificOutput']['permissionDecision'], 'deny')


class CoverageGapTest(CrossHostCase):
    """WF-06-FAIL：覆盖缺口如实报告，不冒充已阻断。"""

    def test_shell_is_not_claimed_as_covered(self):
        self.record_task(self.approval())
        qwen = self.base.load_adapter('qwen-code')
        verdict = self.base.judge_event(self.root, qwen, {'tool_name': 'run_shell_command'},
                                        trust_path=self.trust)
        self.assertFalse(verdict['covered'])
        self.assertEqual(verdict['status'], 'NOT_APPLICABLE')
        self.assertEqual(verdict['axes']['host']['status'], 'NOT_VERIFIED')

    def test_unknown_tool_is_not_claimed_as_covered(self):
        self.record_task(self.approval())
        claude = self.base.load_adapter('claude-code')
        verdict = self.base.judge_event(self.root, claude, {'tool_name': 'NoSuchTool'},
                                        trust_path=self.trust)
        self.assertFalse(verdict['covered'])
        self.assertEqual(verdict['axes']['host']['status'], 'NOT_VERIFIED')

    def test_fault_matrix_claims_nothing_before_a_real_session(self):
        report = self.base.coverage(self.root, 'qwen-code')
        classes = {row['class']: row for row in report['classes']}
        self.assertEqual(sorted(classes), ['hook_crash', 'hook_disabled', 'hook_timeout',
                                            'shell', 'unknown_tool'])
        for row in classes.values():
            self.assertEqual(row['status'], 'NOT_RUN')
            self.assertIsNone(row['evidence'])


class CoverageRecordTest(CrossHostCase):
    def request_file(self, operation, **extra):
        payload = {'schema': 'host-request/v1', 'operation': operation, 'host': 'qwen-code'}
        payload.update(extra)
        path = self.root / ('host-%s.json' % operation)
        write_json(path, payload)
        return path

    def test_a_verified_class_needs_its_evidence(self):
        path = self.request_file('record', classes=[{'class': 'shell', 'status': 'VERIFIED'}])
        code, report = self.run_cli(['host', '--target', str(self.root), '--request', str(path),
                                     '--allow', 'write', '--allow', 'hooks'])
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'INVALID_INPUT')

    def test_an_observed_fault_is_reported_as_infrastructure_error(self):
        path = self.request_file('record', classes=[
            {'class': 'hook_timeout', 'status': 'INFRA_ERROR', 'evidence': '原生会话超时日志'}])
        code, report = self.run_cli(['host', '--target', str(self.root), '--request', str(path),
                                     '--allow', 'write', '--allow', 'hooks'])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'UPDATED')
        coverage = self.base.coverage(self.root, 'qwen-code')
        rows = {row['class']: row for row in coverage['classes']}
        self.assertEqual(rows['hook_timeout']['status'], 'INFRA_ERROR')
        self.assertEqual(rows['hook_timeout']['evidence'], '原生会话超时日志')
        self.assertEqual(rows['shell']['status'], 'NOT_RUN')
