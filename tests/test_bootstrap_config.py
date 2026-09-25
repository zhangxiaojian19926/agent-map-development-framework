import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'tools/framework'


def invoke(*args):
    return subprocess.run([sys.executable, '-B', str(CLI), *map(str, args)],
                          capture_output=True, text=True, timeout=30)


class ConfigurationTests(unittest.TestCase):
    def test_preview_has_no_filesystem_side_effects(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / '中文 project'
            result = invoke('init', '--target', root, '--project-id', 'demo',
                            '--agent', 'manual', '--dry-run')
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan['action'], 'init')
            self.assertIn('write', plan['required_capabilities'])
            self.assertFalse(root.exists())

    def test_yes_is_not_a_source_sending_grant(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'project'
            result = invoke('init', '--target', root, '--project-id', 'demo',
                            '--agent', 'codex', '--yes')
            self.assertEqual(result.returncode, 3, result.stdout)
            self.assertFalse(root.exists())

    def test_invalid_identity_and_root_rejected(self):
        for root, name in [('/', 'demo'), (str(Path.home()), 'demo'),
                           ('/tmp/not-created-framework-test', '../escape')]:
            result = invoke('init', '--target', root, '--project-id', name,
                            '--agent', 'manual', '--dry-run')
            self.assertEqual(result.returncode, 2)

    def test_new_requires_real_approved_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'new'
            result = invoke('new', '--target', root, '--project-id', 'demo',
                            '--agent', 'manual', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 3, result.stdout)
            self.assertEqual(json.loads(result.stdout)['status'], 'NEEDS_DESIGN_APPROVAL')
            self.assertFalse(root.exists())
