import contextlib
import hashlib
import importlib
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


class EvidenceCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.engine = importlib.import_module('framework_core.workflows.engine')
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
        self.make_key('approver')
        self.trust_dir = self.root / 'trust'
        self.trust_dir.mkdir()
        self.trust = self.trust_dir / 'allowed_signers'
        self.trust.write_text('approver-1 ' + (self.keys / 'approver.pub').read_text().strip() + '\n',
                               encoding='utf-8')
        os.chmod(self.trust, 0o444)
        os.chmod(self.trust_dir, 0o555)
        self.payload_path = self.keys / 'approval.json'
        self.signature_path = self.keys / 'approval.json.sig'

    def make_key(self, name):
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(self.keys / name)],
                       check=True, capture_output=True)

    def current_files(self):
        return {
            'specs/core/spec.md': digest(self.spec),
            'implementation-plan.md': digest(self.plan),
        }

    def payload(self, project='demo', change='demo-change', scope=('edit_source',), files=None):
        return {
            'schema': 'workflow-approval/v1',
            'project': project,
            'change': change,
            'files': self.current_files() if files is None else files,
            'scope': list(scope),
        }

    def sign(self, payload, key='approver'):
        self.payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
                                     encoding='utf-8')
        subprocess.run(['ssh-keygen', '-Y', 'sign', '-f', str(self.keys / key), '-n', NAMESPACE,
                        str(self.payload_path)], check=True, capture_output=True)
        return str(self.payload_path), str(self.signature_path)

    def approval(self, payload=None, key='approver'):
        payload_path, signature_path = self.sign(payload or self.payload(), key)
        return {'payload': payload_path, 'signature': signature_path}

    def check(self, **overrides):
        request = {
            'schema': 'workflow-request/v1',
            'operation': 'check',
            'change': 'demo-change',
            'action': 'edit_source',
        }
        request.update(overrides)
        return self.engine.check(self.root, request, trust_path=self.trust)


class ApprovalMissingTest(EvidenceCase):
    def test_source_edit_without_approval_is_rejected_with_missing_items(self):
        """WF-02-MISSING：缺少批准时拒绝并返回缺失项。"""
        result = self.check()
        self.assertEqual(result['status'], 'NEEDS_DESIGN_APPROVAL')
        self.assertIn('approval.payload', result['missing'])
        self.assertIn('approval.signature', result['missing'])
        self.assertTrue(result['next_actions'])

    def test_draft_edit_needs_no_approval(self):
        """WF-02-MISSING：已授权的规格或计划草稿编辑仍判定允许。"""
        result = self.check(action='edit_spec')
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['missing'], [])


class ApprovalAcceptedTest(EvidenceCase):
    def test_signed_approval_allows_the_source_edit(self):
        """WF-02-ALLOW：有效批准返回允许及依据。"""
        result = self.check(approval=self.approval())
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['axes']['flow']['status'], 'READY')
        self.assertTrue(result['facts']['files'])
        self.assertEqual(result['facts']['files'], self.current_files())

    def test_action_outside_the_approved_scope_is_not_authorized(self):
        """WF-02-ALLOW：动作不在批准范围内时不放行。"""
        result = self.check(approval=self.approval(self.payload(scope=('implement',))))
        self.assertEqual(result['status'], 'NOT_AUTHORIZED')


class ApprovalStaleTest(EvidenceCase):
    def test_changed_plan_invalidates_the_approval(self):
        """WF-02-STALE：已批准的内容改变后旧批准不再有效。"""
        approval = self.approval()
        self.plan.write_text('# 计划\n\n- 改过的步骤\n', encoding='utf-8')
        result = self.check(approval=approval)
        self.assertEqual(result['status'], 'STALE')

    def test_approval_from_another_project_is_stale(self):
        """WF-02-STALE：引用来自其他项目的批准无效。"""
        result = self.check(approval=self.approval(self.payload(project='other')))
        self.assertEqual(result['status'], 'STALE')

    def test_approval_for_another_change_is_stale(self):
        """WF-02-STALE：引用来自其他 change 的批准无效。"""
        result = self.check(approval=self.approval(self.payload(change='other-change')))
        self.assertEqual(result['status'], 'STALE')


class ApprovalUnverifiableTest(EvidenceCase):
    def test_signature_from_an_untrusted_key_is_not_accepted(self):
        """WF-02-MISSING：签名不在受信来源内不构成批准。"""
        self.make_key('stranger')
        result = self.check(approval=self.approval(key='stranger'))
        self.assertEqual(result['status'], 'NEEDS_DESIGN_APPROVAL')

    def test_missing_trust_source_is_not_verified(self):
        """WF-02-UNOBSERVED：没有受信来源时证据不足。"""
        missing_trust = self.root / 'no-trust'
        result = self.engine.check(self.root, {
            'schema': 'workflow-request/v1', 'operation': 'check',
            'change': 'demo-change', 'action': 'edit_source',
            'approval': self.approval(),
        }, trust_path=missing_trust)
        self.assertEqual(result['status'], 'NOT_VERIFIED')
        self.assertTrue(result['next_actions'])

    def test_request_cannot_smuggle_the_trust_source(self):
        """WF-02：请求无权指定或替换受信来源。"""
        request = {
            'schema': 'workflow-request/v1', 'operation': 'check',
            'change': 'demo-change', 'action': 'edit_source',
            'approval': self.approval(),
            'trust_path': str(self.trust),
        }
        result = self.engine.check(self.root, request, trust_path=self.root / 'no-trust')
        self.assertEqual(result['status'], 'NOT_VERIFIED')


class CheckCommandTest(EvidenceCase):
    def run_cli(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(args)
        return code, json.loads(stdout.getvalue())

    def test_cli_checks_a_change_request(self):
        request = {
            'schema': 'workflow-request/v1', 'operation': 'check',
            'change': 'demo-change', 'action': 'edit_source',
        }
        request_path = self.root / 'check-request.json'
        write_json(request_path, request)
        code, report = self.run_cli(['flow', '--target', str(self.root), '--request', str(request_path)])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'NEEDS_DESIGN_APPROVAL')
        self.assertEqual(report['facts']['change'], 'demo-change')
