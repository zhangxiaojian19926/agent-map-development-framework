import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class HookTests(unittest.TestCase):
    def test_user_hook_is_preserved(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.hooks'), 'hooks missing')
        hooks = importlib.import_module('framework_core.hooks')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            hook = root / '.git/hooks/post-commit'
            hook.write_text('#!/bin/sh\nexit 0\n')
            plan = hooks.hook_plan(root, root)
            self.assertEqual(plan['status'], 'HOOK_CONFLICT')
            self.assertEqual(hook.read_text(), '#!/bin/sh\nexit 0\n')

    def test_dirty_events_are_coalesced(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.hooks'), 'hooks missing')
        hooks = importlib.import_module('framework_core.hooks')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            hooks.mark_dirty(root, 'worktree', 'commit')
            hooks.mark_dirty(root, 'worktree', 'commit')
            hooks.mark_dirty(root, 'worktree', 'checkout')
            import json
            data = json.loads((root / '.framework/local-state/dirty.json').read_text())
            self.assertEqual(data['reasons'], ['checkout', 'commit'])
