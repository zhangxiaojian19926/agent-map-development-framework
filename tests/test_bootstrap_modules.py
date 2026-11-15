import importlib
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class ModuleTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.modules'), 'module lifecycle missing')
        self.module = importlib.import_module('framework_core.modules')

    def test_identity_shared_repository_and_missing(self):
        decl = [{'id': k, 'path': k} for k in ('a', 'b', 'c')]
        obs = [{'path': k, 'git_root': '.' if k != 'c' else 'c', 'sources': {k + '/x.py': 'abc'}} for k in ('a', 'b', 'c')]
        result = self.module.catalog_update({}, decl, obs)
        self.assertEqual(len(result['modules']), 3)
        self.assertEqual(len(result['indexes']), 2)
        after = self.module.catalog_update(result, decl, [])
        self.assertTrue(all(m['presence'] == 'missing' for m in after['modules'].values()))

    def test_discovery_is_bounded_and_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'src').mkdir()
            (root / 'src/a.py').write_text('def alpha(): return 1')
            (root / 'outside').symlink_to(root.parent)
            obs = self.module.discover(root, ['src'], 2)
            self.assertEqual(obs[0]['path'], 'src')
            with self.assertRaises(ValueError):
                self.module.discover(root, ['outside'], 2)

    def test_discovery_finds_new_nested_repo_but_does_not_register_it(self):
        self.assertTrue(hasattr(self.module, 'find_candidates'), 'candidate finder missing')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'modules/new/.git').mkdir(parents=True)
            (root / 'modules/new/run.py').write_text('def run(): pass')
            found = self.module.find_candidates(root, ['.'], 3)
            self.assertEqual([c['path'] for c in found], ['modules/new'])
            self.assertFalse((root / 'module-catalog.generated.json').exists())

    def test_worktree_subtree_stays_out_of_module_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / '.git').mkdir()
            (root / 'app.py').write_text('def app(): return 1\n')
            worktree = root / '.worktrees' / 'feishu-preflight'
            (worktree / '.git').mkdir(parents=True)
            (worktree / 'snap.py').write_text('def snap(): return 1\n')
            (root / '.worktrees' / 'note.py').write_text('def note(): return 1\n')
            found = self.module.find_candidates(root, ['.'], 4)
            paths = [item['path'] for item in found]
            self.assertFalse(any(path == '.worktrees' or path.startswith('.worktrees/') for path in paths))
            sources = self.module.discover(root, ['.'])[0]['sources']
            self.assertFalse(any(path.startswith('.worktrees/') for path in sources))

    def test_gitignore_does_not_select_discovered_directories(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / '.git').mkdir()
            (root / '.gitignore').write_text('.worktrees/\nlocal-snapshots/\n')
            (root / 'app.py').write_text('def app(): return 1\n')
            worktree = root / '.worktrees' / 'feishu-preflight'
            (worktree / '.git').mkdir(parents=True)
            (worktree / 'snap.py').write_text('def snap(): return 1\n')
            kept = root / 'local-snapshots'
            (kept / '.git').mkdir(parents=True)
            (kept / 'keep.py').write_text('def keep(): return 1\n')
            found = self.module.find_candidates(root, ['.'], 4)
            paths = [item['path'] for item in found]
            self.assertFalse(any(path == '.worktrees' or path.startswith('.worktrees/') for path in paths))
            self.assertIn('local-snapshots', paths)
