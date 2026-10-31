"""A completed change must reach the spec store and the archive."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_tool():
    loader = importlib.machinery.SourceFileLoader('checkt', str(ROOT / 'tools/check-changes'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def make_change(root, name, done, todo, capability=None, synced=False, skip_specs=False):
    change = root / 'openspec' / 'changes' / name
    change.mkdir(parents=True)
    lines = ['## 1. Work', '']
    lines += ['- [x] %d.1 step' % i for i in range(1, done + 1)]
    lines += ['- [ ] %d.1 step' % i for i in range(1, todo + 1)]
    (change / 'tasks.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    meta = 'schema: spec-driven\ncreated: 2026-11-01\n'
    if skip_specs:
        meta += 'skip_specs: true\n'
    (change / '.openspec.yaml').write_text(meta, encoding='utf-8')
    if capability:
        spec = change / 'specs' / capability
        spec.mkdir(parents=True)
        (spec / 'spec.md').write_text(
            '## Purpose\n\nx\n\n## ADDED Requirements\n\n### Requirement: R\ntext\n', encoding='utf-8')
    if synced and capability:
        target = root / 'openspec' / 'specs' / capability
        target.mkdir(parents=True)
        (target / 'spec.md').write_text(
            '# %s Specification\n\n## Purpose\n\nx\n\n## Requirements\n\n### Requirement: R\ntext\n' % capability,
            encoding='utf-8')


class OutstandingChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()

    def test_incomplete_change_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'wip', done=2, todo=3, capability='demo')
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_change_without_tasks_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            change = root / 'openspec' / 'changes' / 'no-tasks'
            change.mkdir(parents=True)
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_completed_change_with_unsynced_capability_is_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('not synced', findings[0]['problem'])
            self.assertIn('demo-cap', findings[0]['detail'])

    def test_completed_and_synced_change_must_be_archived(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_archived_change_is_never_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap')
            archive = root / 'openspec' / 'changes' / 'archive'
            archive.mkdir(parents=True)
            (root / 'openspec' / 'changes' / 'done').rename(archive / 'done')
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_skip_specs_change_must_still_be_archived(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, skip_specs=True)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_tool_exits_non_zero_on_findings(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, capability='demo-cap')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools/check-changes'), '--root', str(root)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('FAIL', result.stdout)

    def test_tool_reports_json_when_asked(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, capability='demo-cap')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools/check-changes'), '--root', str(root), '--json'],
                capture_output=True, text=True)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['status'], 'FAIL')
            self.assertEqual(payload['outstanding'][0]['change'], 'done')

    def test_this_repository_has_no_outstanding_change(self):
        self.assertEqual(self.tool.find_outstanding(ROOT), [])


if __name__ == '__main__':
    unittest.main()
