import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core import cli

CODEBUDDY_FILES = [
    '.codebuddy/agents/uap-challenger.md',
    '.codebuddy/agents/uap-investigator.md',
    '.codebuddy/agents/uap-verifier.md',
]
WRITE_TOOLS = ('Write', 'Edit', 'MultiEdit')


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def agent_tools(text):
    for line in text.splitlines():
        if line.startswith('tools:'):
            return [item.strip() for item in line.split(':', 1)[1].split(',')]
    return []


class CodeBuddyHostTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def request_file(self, operation):
        path = self.root / ('host-%s.json' % operation)
        write_json(path, {'schema': 'host-request/v1', 'operation': operation, 'host': 'codebuddy'})
        return path

    def run_cli(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(args)
        return code, json.loads(stdout.getvalue())

    def test_preview_lists_only_the_shared_agents(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('preview'))])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'READY')
        self.assertEqual(report['files'], CODEBUDDY_FILES)
        self.assertEqual(report['conflicts'], [])
        self.assertNotIn('CODEBUDDY.md', report['files'])
        self.assertFalse(any(path.endswith('settings.json') for path in report['files']))

    def test_apply_installs_agents_with_write_only(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('apply')), '--allow', 'write'])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'UPDATED')
        self.assertEqual(report['files'], CODEBUDDY_FILES)
        for rel in CODEBUDDY_FILES:
            self.assertTrue((self.root / rel).is_file(), rel)
        self.assertFalse((self.root / 'CODEBUDDY.md').exists())
        self.assertFalse((self.root / '.codebuddy/settings.json').exists())
        self.assertFalse((self.root / '.claude/settings.json').exists())
        state = json.loads((self.root / '.framework/local-state/hosts.json').read_text(encoding='utf-8'))
        self.assertEqual(state['host'], 'codebuddy')
        for name in ('uap-challenger.md', 'uap-investigator.md', 'uap-verifier.md'):
            tools = agent_tools((self.root / '.codebuddy/agents' / name).read_text(encoding='utf-8'))
            self.assertFalse(set(WRITE_TOOLS) & set(tools), name)

    def test_apply_without_write_is_refused(self):
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('apply'))])
        self.assertEqual(code, 3)
        self.assertEqual(report['status'], 'CONSENT_REQUIRED')
        self.assertEqual(report['required'], ['write'])
        self.assertFalse((self.root / '.codebuddy').exists())
        self.assertFalse((self.root / 'CODEBUDDY.md').exists())

    def test_apply_host_accepts_write_and_rejects_hooks_requirement(self):
        from framework_core.hosts.base import apply_host, load_adapter
        adapter = load_adapter('codebuddy')
        self.assertFalse(adapter.requires_hooks)
        refused = apply_host(self.root, 'codebuddy', set())
        self.assertEqual(refused['status'], 'CONSENT_REQUIRED')
        self.assertEqual(refused['required'], ['write'])
        result = apply_host(self.root, 'codebuddy', {'write'})
        self.assertEqual(result['status'], 'UPDATED')
        self.assertEqual(result['files'], CODEBUDDY_FILES)
        self.assertFalse((self.root / 'CODEBUDDY.md').exists())

    def test_verify_reports_the_installed_agents(self):
        self.run_cli(['host', '--target', str(self.root), '--request',
                      str(self.request_file('apply')), '--allow', 'write'])
        code, report = self.run_cli(['host', '--target', str(self.root), '--request',
                                     str(self.request_file('verify'))])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'VERIFIED')
        self.assertEqual([item['path'] for item in report['files']], CODEBUDDY_FILES)
