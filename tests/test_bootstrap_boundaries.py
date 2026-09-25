import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
from unittest.mock import patch
from test_bootstrap_config import invoke
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from framework_core.storage import apply_files, resume_run, safe_path
from framework_core.hooks import hook_plan
from framework_core.modules import discover


class BoundaryTests(unittest.TestCase):
    def test_preview_reports_existing_agents_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'AGENTS.md').write_text('human rules')
            result = invoke('init', '--target', root, '--project-id', 'demo', '--agent', 'manual', '--dry-run')
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('AGENTS.md', ' '.join(json.loads(result.stdout)['conflicts']))
            self.assertEqual(list(root.iterdir()), [root / 'AGENTS.md'])

    def test_interruption_resume_preserves_manual_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'manual').write_text('keep')
            changes = [{'path': p, 'before_sha256': None, 'content': p} for p in ('one', 'two')]
            from framework_core import storage
            original = storage.atomic
            def interrupted(root, rel, content):
                if rel == 'two':
                    raise OSError('injected interruption')
                original(root, rel, content)
            with patch.object(storage, 'atomic', interrupted):
                with self.assertRaises(OSError):
                    apply_files(root, changes, 'recover')
            resume_run(root, 'recover', {'write'})
            self.assertEqual((root / 'two').read_text(), 'two')
            self.assertEqual((root / 'manual').read_text(), 'keep')

    def test_main_checkout_with_linked_worktree_refuses_shared_hooks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'main'
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'base'], check=True)
            subprocess.run(['git', '-C', str(root), 'worktree', 'add', '-q', '--detach', str(Path(d) / 'linked')], check=True)
            self.assertEqual(hook_plan(root, root)['status'], 'HOOK_CONFLICT')

    def test_source_scan_reports_depth_truncation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a/b/c').mkdir(parents=True)
            (root / 'a/b/c/mod.py').write_text('def deep(): pass')
            with self.assertRaises(ValueError):
                discover(root, ['a'], 1)

    def test_download_config_cannot_silently_request_external_action(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            config = root / 'download.json'
            config.write_text(json.dumps({'project_id': 'demo', 'agent': 'codex', 'authorized': True}))
            result = invoke('init', '--target', root / 'target', '--config', config, '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 3)
            self.assertFalse((root / 'target').exists())
