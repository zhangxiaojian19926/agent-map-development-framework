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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core import cli

NAMESPACE = 'framework-workflow-approval/v1'


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RecordCase(unittest.TestCase):
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

    def commit_request(self, **overrides):
        request = {
            'schema': 'workflow-request/v1',
            'operation': 'record',
            'task_id': 'demo-task',
            'request_id': 'req-1',
            'expected_version': 0,
            'change': 'demo-change',
            'action': 'edit_source',
        }
        request.update(overrides)
        return request

    def commit(self, **overrides):
        return self.records.commit(self.root, self.commit_request(**overrides),
                                    trust_path=self.trust)


class RecordWriteTest(RecordCase):
    def test_commit_stores_a_private_record_and_the_three_axes(self):
        """WF-04-RETRY：首次提交写入私有记录并记下三轴。"""
        result = self.commit(approval=self.approval())
        self.assertEqual(result['status'], 'UPDATED')
        self.assertEqual(result['version'], 1)
        record = self.root / '.framework/local-state/workflows/demo-task.json'
        self.assertTrue(record.is_file())
        stored = json.loads(record.read_text(encoding='utf-8'))
        self.assertEqual(stored['version'], 1)
        report = json.loads((self.root / '.framework/local-state/workflows/report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['tasks']['demo-task']['flow'], 'READY')
        self.assertEqual(report['tasks']['demo-task']['delivery'], 'NOT_RUN')

    def test_same_request_returns_the_original_result(self):
        """WF-04-RETRY：同一请求重试返回原结果。"""
        first = self.commit(approval=self.approval())
        second = self.commit(approval=self.approval())
        self.assertEqual(second['status'], 'UNCHANGED')
        self.assertEqual(second['result'], first)
        record = json.loads((self.root / '.framework/local-state/workflows/demo-task.json')
                            .read_text(encoding='utf-8'))
        self.assertEqual(record['version'], 1)

    def test_a_second_session_on_the_same_version_conflicts(self):
        """WF-04-RETRY：同一版本的另一更新被拒绝，现场保留。"""
        first = self.commit(approval=self.approval())
        second = self.commit(request_id='req-2', action='implement', approval=self.approval())
        self.assertEqual(second['status'], 'CONFLICT')
        self.assertEqual(second['version'], first['version'])
        stored = json.loads((self.root / '.framework/local-state/workflows/demo-task.json')
                            .read_text(encoding='utf-8'))
        self.assertEqual(stored['version'], 1)
        self.assertIn('req-1', stored['requests'])


class RecordResumeTest(RecordCase):
    def test_resume_rejudges_the_current_facts(self):
        """WF-04-RESUME：恢复时按当前事实重新判定，不沿用旧结论。"""
        self.commit(approval=self.approval())
        self.plan.write_text('# 计划\n\n- 改过的步骤\n', encoding='utf-8')
        resumed = self.records.resume(self.root, 'demo-task', trust_path=self.trust)
        self.assertEqual(resumed['status'], 'STALE')
        self.assertEqual(resumed['version'], 1)
        stored = json.loads((self.root / '.framework/local-state/workflows/demo-task.json')
                            .read_text(encoding='utf-8'))
        self.assertEqual(stored['version'], 1)

    def test_resume_keeps_history_without_inheriting_the_grant(self):
        """WF-04-RESUME：保留历史记录，不继承上一会话操作授权。"""
        self.commit(approval=self.approval())
        resumed = self.records.resume(self.root, 'demo-task', trust_path=self.trust)
        self.assertEqual(resumed['status'], 'READY')
        self.assertNotIn('approval', resumed)
        self.assertTrue(resumed['next_actions'])


class RecordCommandTest(RecordCase):
    def run_cli(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(args)
        return code, json.loads(stdout.getvalue())

    def test_record_without_write_grant_is_refused(self):
        request = self.commit_request()
        request_path = self.root / 'record-request.json'
        write_json(request_path, request)
        code, report = self.run_cli(['flow', '--target', str(self.root), '--request', str(request_path)])
        self.assertEqual(code, 3)
        self.assertEqual(report['status'], 'CONSENT_REQUIRED')
        self.assertEqual(report['required'], ['write'])
        self.assertFalse((self.root / '.framework/local-state/workflows/demo-task.json').exists())

    def test_record_with_write_grant_writes_the_private_state(self):
        request = self.commit_request()
        request_path = self.root / 'record-request.json'
        write_json(request_path, request)
        code, report = self.run_cli(['flow', '--target', str(self.root), '--request', str(request_path),
                                     '--allow', 'write'])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'UPDATED')
        self.assertTrue((self.root / '.framework/local-state/workflows/demo-task.json').is_file())
