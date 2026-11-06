import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

NAMESPACE = 'framework-workflow-approval/v1'


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TrustCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = importlib.import_module('framework_core.workflows.evidence')
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
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(self.keys / 'approver')],
                       check=True, capture_output=True)
        self.mutable_anchor = self.keys / 'allowed_signers'
        self.mutable_anchor.write_text(
            'approver-1 ' + (self.keys / 'approver.pub').read_text().strip() + '\n', encoding='utf-8')
        self.protected_dir = self.root / 'protected'
        self.protected_dir.mkdir()
        self.protected_anchor = self.protected_dir / 'allowed_signers'
        self.protected_anchor.write_text(self.mutable_anchor.read_text(encoding='utf-8'), encoding='utf-8')
        self.payload_path = self.keys / 'approval.json'
        self.payload = {
            'schema': 'workflow-approval/v1',
            'project': 'demo',
            'change': 'demo-change',
            'files': {
                'specs/core/spec.md': digest(self.spec),
                'implementation-plan.md': digest(self.plan),
            },
            'scope': ['edit_source', 'implement'],
        }
        self.payload_path.write_text(json.dumps(self.payload, ensure_ascii=False, indent=2) + '\n',
                                     encoding='utf-8')
        subprocess.run(['ssh-keygen', '-Y', 'sign', '-f', str(self.keys / 'approver'), '-n', NAMESPACE,
                        str(self.payload_path)], check=True, capture_output=True)
        self.approval = {'payload': str(self.payload_path),
                         'signature': str(self.payload_path) + '.sig'}

    def protect(self):
        """Make the anchor unreadable-for-write by this user, the way a system anchor sits."""
        os.chmod(self.protected_anchor, 0o444)
        os.chmod(self.protected_dir, 0o555)

    def check(self, trust_path, **extra):
        request = {
            'schema': 'workflow-request/v1', 'operation': 'check',
            'change': 'demo-change', 'action': 'edit_source', 'approval': self.approval,
        }
        request.update(extra)
        return self.engine.check(self.root, request, trust_path=trust_path)


class TrustSourceTest(TrustCase):
    def test_mutable_trust_source_is_not_verified(self):
        """WF-08-MUTABLE：可被改写的信任来源不构成可核验授权。"""
        result = self.check(self.mutable_anchor)
        self.assertEqual(result['status'], 'NOT_VERIFIED')
        self.assertIn('改写', result['reason'])
        self.assertTrue(result['next_actions'])

    def test_protected_trust_source_allows_the_approval(self):
        """WF-08-PROTECTED：受保护且签名有效时按批准范围判定。"""
        self.protect()
        result = self.check(self.protected_anchor)
        self.assertEqual(result['status'], 'READY')
        self.assertTrue([item for item in result['next_actions'] if '私钥' in item])

    def test_request_cannot_redirect_the_trust_source(self):
        """WF-08-REDIRECT：请求无权把信任来源指到代理可写的位置。"""
        result = self.check(self.mutable_anchor, trust_source=str(self.mutable_anchor))
        self.assertEqual(result['status'], 'NOT_VERIFIED')

    def test_trust_source_path_does_not_follow_the_environment(self):
        """WF-08-REDIRECT：信任来源路径不由环境变量决定。"""
        home = self.root / 'fake-home'
        (home / '.config/framework').mkdir(parents=True)
        (home / '.config/framework/workflow-trust.allowed_signers').write_text(
            self.mutable_anchor.read_text(encoding='utf-8'), encoding='utf-8')
        saved = os.environ.get('HOME')
        os.environ['HOME'] = str(home)
        try:
            self.assertEqual(str(self.evidence.trust_anchor()), '/etc/framework/workflow-trust.allowed_signers')
        finally:
            if saved is None:
                os.environ.pop('HOME', None)
            else:
                os.environ['HOME'] = saved


class AnchorProtectionTest(TrustCase):
    def test_writable_anchor_is_not_protected(self):
        """WF-08-MUTABLE：文件可写即视为可改写。"""
        self.assertFalse(self.evidence.anchor_protected(self.mutable_anchor))

    def test_writable_directory_is_not_protected(self):
        """WF-08-MUTABLE：目录可写即可替换其中的文件。"""
        self.protect()
        self.assertTrue(self.evidence.anchor_protected(self.protected_anchor))
        os.chmod(self.protected_dir, 0o755)
        self.assertFalse(self.evidence.anchor_protected(self.protected_anchor))
