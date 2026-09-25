import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_bootstrap_config import invoke


class EndToEndTests(unittest.TestCase):
    def test_local_clone_registration_move_missing_and_hook_event(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source, target = base / 'source', base / 'project'
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source / 'code.py').write_text('def alpha(): return 1\n')
            subprocess.run(['git', '-C', str(source), 'add', 'code.py'], check=True)
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture'], check=True)
            first = invoke('init', '--target', target, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            self.assertEqual(first.returncode, 5, first.stdout)
            imported = invoke('module', 'clone', '--target', target, '--id', 'lib', '--path', 'modules/lib', '--url', source,
                              '--yes', '--allow', 'write', '--allow', 'clone', '--allow', 'local-clone', '--hooks', '--allow', 'hooks')
            self.assertEqual(imported.returncode, 5, imported.stdout)
            self.assertTrue((target / 'modules/lib/code.py').is_file())
            hook = target / 'modules/lib/.git/hooks/post-commit'
            self.assertTrue(hook.stat().st_mode & 0o111)
            subprocess.run([str(hook)], cwd=target / 'modules/lib', check=True)
            dirty = json.loads((target / '.framework/local-state/dirty.json').read_text())
            self.assertEqual(dirty['reasons'], ['post-commit'])
            (target / 'modules/lib').rename(target / 'modules/moved')
            moved = invoke('module', 'add', '--target', target, '--id', 'lib', '--path', 'modules/moved', '--yes', '--allow', 'write', '--allow', 'hooks')
            self.assertEqual(moved.returncode, 5, moved.stdout)
            catalog = json.loads((target / 'module-catalog.generated.json').read_text())
            self.assertEqual(catalog['modules']['lib']['history'], ['modules/lib'])
            (target / 'modules/moved').rename(base / 'retained')
            synced = invoke('module', 'sync', '--target', target, '--yes', '--allow', 'write')
            self.assertEqual(synced.returncode, 0, synced.stdout)
            catalog = json.loads((target / 'module-catalog.generated.json').read_text())
            self.assertEqual(catalog['modules']['lib']['presence'], 'missing')

    def test_live_verifier_needs_explicit_opt_in(self):
        cli = Path(__file__).resolve().parents[1] / 'tools/verify-live'
        import sys
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'not-created'
            result = subprocess.run([sys.executable, '-B', str(cli), '--target', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertFalse(target.exists())

    def test_live_probe_rejects_an_always_empty_fake_cli(self):
        import sys
        probe = Path(__file__).resolve().parent / 'integration/probe_task_cli.py'
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'taskcli').mkdir()
            (root / 'taskcli/__main__.py').write_text('print("[]")\n')
            result = subprocess.run([sys.executable, '-B', str(probe), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('CONTRACT_FAILED', result.stderr)
