import importlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.storage'), 'storage capability missing')
        self.storage = importlib.import_module('framework_core.storage')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_changed_input_is_preserved(self):
        p = self.root / 'AGENTS.md'
        p.write_text('before')
        change = {'path': 'AGENTS.md', 'before_sha256': self.storage.fingerprint(p), 'content': 'generated'}
        p.write_text('user edit')
        with self.assertRaises(ValueError):
            self.storage.apply_files(self.root, [change], 'run-1')
        self.assertEqual(p.read_text(), 'user edit')

    def test_escape_and_symlink_rejected(self):
        (self.root / 'link').symlink_to(self.root.parent, target_is_directory=True)
        for path in ('../x', '/tmp/x', 'link/x'):
            with self.assertRaises(ValueError):
                self.storage.safe_path(self.root, path)

    def test_idempotent_apply_and_resume_detect_user_edit(self):
        changes = [{'path': 'a/b.txt', 'before_sha256': None, 'content': 'owned'}]
        self.storage.apply_files(self.root, changes, 'run-1')
        self.storage.apply_files(self.root, changes, 'run-1')
        self.assertEqual((self.root / 'a/b.txt').read_text(), 'owned')
        (self.root / 'a/b.txt').write_text('manual')
        with self.assertRaises(ValueError):
            self.storage.resume_run(self.root, 'run-1', {'write'})
        self.assertEqual((self.root / 'a/b.txt').read_text(), 'manual')

    def test_lock_owner_is_not_removed(self):
        with self.storage.project_lock(self.root):
            with self.assertRaises(ValueError):
                with self.storage.project_lock(self.root):
                    pass
            self.assertTrue((self.root / '.framework/local-state/lock').exists())

    def test_resume_rechecks_hook_capability(self):
        import json
        state = self.root / '.framework/local-state/runs'
        state.mkdir(parents=True)
        (state / 'hooks.json').write_text(json.dumps({'schema_version': 1, 'run_id': 'hooks', 'completed': [],
            'changes': [{'path': '.git/hooks/post-commit', 'before_sha256': None, 'content': '#!/bin/sh\n'}]}))
        with self.assertRaises(ValueError):
            self.storage.resume_run(self.root, 'hooks', {'write'})
        self.assertFalse((self.root / '.git/hooks/post-commit').exists())
