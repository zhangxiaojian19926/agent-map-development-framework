import importlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class AdapterTests(unittest.TestCase):
    def test_process_timeout_is_not_success(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.process'), 'executor missing')
        run = importlib.import_module('framework_core.process').run
        with tempfile.TemporaryDirectory() as d:
            result = run([sys.executable, '-c', 'import time; time.sleep(5)'], Path(d), 0.1, {})
        self.assertTrue(result['timed_out'])
        self.assertNotEqual(result['exit_code'], 0)

    def test_missing_index_tool_is_not_ready(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.adapters'), 'adapter missing')
        adapter = importlib.import_module('framework_core.adapters')
        def missing(*args, **kwargs):
            return {'exit_code': 127, 'stdout': '', 'stderr': 'missing', 'timed_out': False}
        with tempfile.TemporaryDirectory() as d:
            result = adapter.ensure_index(Path(d), {'id': 'i', 'root': '.', 'sources': {'a.py': 'abc'}}, {'index'}, missing)
        self.assertFalse(result['verified'])

    def test_clone_rejects_credentials_and_ext_protocol(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.adapters'), 'adapter missing')
        adapter = importlib.import_module('framework_core.adapters')
        for url in ('ext::evil', 'https://user:password@example.com/repo', '--upload-pack=evil'):
            with self.assertRaises(ValueError):
                adapter.validate_clone_url(url, set())

    def test_openspec_refuses_ancestor_root(self):
        adapter = importlib.import_module('framework_core.adapters')
        self.assertTrue(hasattr(adapter, 'ensure_openspec'), 'OpenSpec root adapter missing')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'openspec').mkdir()
            (root / 'openspec/config.yaml').write_text('schema: spec-driven\n')
            def wrong_root(*args, **kwargs):
                return {'exit_code': 0, 'stdout': '{"root":{"path":"/another-project"}}', 'stderr': '', 'timed_out': False}
            with self.assertRaises(ValueError):
                adapter.ensure_openspec(root, {'openspec'}, wrong_root)

    def test_query_echo_without_nodes_is_not_index_proof(self):
        adapter = importlib.import_module('framework_core.adapters')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'a.py').write_text('def alpha(): pass')
            def runner(argv, *args):
                body = '1.6.0' if '--version' in argv else ('{"query":"alpha","results":[]}' if 'query' in argv else '{}')
                return {'exit_code': 0, 'stdout': body, 'stderr': '', 'timed_out': False}
            result = adapter.ensure_index(root, {'id': 'i', 'root': '.', 'sources': {'a.py': 'hash'}}, {'index'}, runner)
            self.assertFalse(result['verified'])

    def test_index_excludes_unselected_sibling_and_nested_repo(self):
        adapter = importlib.import_module('framework_core.adapters')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            for name in ('app', 'sibling', 'nested'):
                (root / name).mkdir()
                (root / name / 'a.py').write_text('def alpha(): pass')
            (root / 'nested/.git').mkdir()
            def runner(argv, *args):
                return {'exit_code': 0, 'stdout': '1.6.0' if '--version' in argv else '{}', 'stderr': '', 'timed_out': False}
            adapter.ensure_index(root, {'id': 'i', 'root': '.', 'sources': {'app/a.py': 'sha'}}, {'index'}, runner)
            import json
            excludes = json.loads((root / 'codegraph.json').read_text())['exclude']
            self.assertEqual(excludes, ['**', '!/app/', '!/app/a.py'])
            (root / 'future-unapproved').mkdir()
            (root / 'future-unapproved/secret.py').write_text('def private(): pass')
            self.assertEqual(json.loads((root / 'codegraph.json').read_text())['exclude'], ['**', '!/app/', '!/app/a.py'])
