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

    def test_legacy_clone_ignores_inherited_url_redirection(self):
        import os
        import subprocess
        from unittest.mock import patch
        adapter = importlib.import_module('framework_core.adapters')
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source, target = base/'redirected', base/'target'
            source.mkdir(); target.mkdir()
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source/'marker.txt').write_text('REDIRECTED\n')
            subprocess.run(['git', '-C', str(source), 'add', 'marker.txt'], check=True)
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture',
                            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture'], check=True)
            url = 'https://127.0.0.1:1/repo'
            env = {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'url.'+str(source)+'.insteadOf',
                   'GIT_CONFIG_VALUE_0': url}
            with patch.dict(os.environ, env):
                result = adapter.clone(target, url, 'modules/api', None,
                                       {'write', 'clone', 'local-clone'})
            self.assertNotEqual(result['exit_code'], 0)
            self.assertFalse((target/'modules/api/marker.txt').exists())

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

    def test_major_version_one_is_accepted_and_two_is_not(self):
        adapter = importlib.import_module('framework_core.adapters')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'a.py').write_text('def alpha(): pass')
            def runner(argv, *args):
                text = '1.6.2' if '--version' in argv else '{}'
                return {'exit_code': 0, 'stdout': text, 'stderr': '', 'timed_out': False}
            result = adapter.ensure_index(root, {'id': 'i', 'root': '.', 'sources': {'a.py': 'sha'}}, {'index'}, runner)
            self.assertEqual(result['version'], '1.6.2')
            self.assertTrue((root / 'codegraph.json').is_file())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'a.py').write_text('def alpha(): pass')
            calls = []
            def runner(argv, *args):
                calls.append(argv)
                return {'exit_code': 0, 'stdout': '2.0.0', 'stderr': '', 'timed_out': False}
            result = adapter.ensure_index(root, {'id': 'i', 'root': '.', 'sources': {'a.py': 'sha'}}, {'index'}, runner)
            self.assertEqual(result['status'], 'UNSUPPORTED_VERSION')
            self.assertFalse(result['verified'])
            self.assertFalse((root / 'codegraph.json').exists())
            self.assertFalse(any(argv[0] == 'npm' for argv in calls))

    def test_missing_cli_installs_only_into_the_project(self):
        adapter = importlib.import_module('framework_core.adapters')
        spec = adapter.codegraph_lock()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            calls = []
            def runner(argv, *args):
                calls.append(list(argv))
                if argv[0] in ('node', 'npm') and '--version' in argv:
                    return {'exit_code': 0, 'stdout': '1', 'stderr': '', 'timed_out': False}
                if argv[0] == 'npm' and 'install' in argv:
                    self.assertNotIn('-g', argv)
                    self.assertNotIn('--global', argv)
                    self.assertIn(spec['package'] + '@' + spec['version'], argv)
                    prefix = Path(argv[argv.index('--prefix') + 1])
                    self.assertEqual(prefix, root / '.framework/tools/codegraph')
                    package = prefix / 'node_modules' / spec['package']
                    package.mkdir(parents=True)
                    binary = prefix / 'node_modules/.bin'
                    binary.mkdir(parents=True)
                    (binary / 'codegraph').write_text('#!/bin/sh\n')
                    lock = {'packages': {'node_modules/' + spec['package']: {
                        'version': spec['version'], 'integrity': spec['integrity']}}}
                    (prefix / 'package-lock.json').write_text(__import__('json').dumps(lock))
                    return {'exit_code': 0, 'stdout': '', 'stderr': '', 'timed_out': False}
                if str(argv[0]).endswith('/codegraph') and '--version' in argv:
                    return {'exit_code': 0, 'stdout': spec['version'], 'stderr': '', 'timed_out': False}
                return {'exit_code': 127, 'stdout': '', 'stderr': 'missing', 'timed_out': False}
            refused = adapter.resolve_codegraph(root, {'index'}, runner)
            self.assertEqual(refused['status'], 'DEPENDENCY_MISSING')
            self.assertFalse(any(argv[0] == 'npm' for argv in calls))
            installed = adapter.resolve_codegraph(root, {'index', 'index-install'}, runner)
            self.assertEqual(installed['status'], 'READY')
            self.assertTrue(installed['installed'])
            self.assertTrue(str(installed['bin']).startswith(str(root)))

    def test_bad_integrity_and_missing_node_do_not_count_as_ready(self):
        adapter = importlib.import_module('framework_core.adapters')
        spec = adapter.codegraph_lock()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            def runner(argv, *args):
                if argv[:2] == ['node', '--version']:
                    return {'exit_code': 127, 'stdout': '', 'stderr': 'missing', 'timed_out': False}
                return {'exit_code': 0, 'stdout': '', 'stderr': '', 'timed_out': False}
            self.assertEqual(adapter.resolve_codegraph(root, {'index-install'}, runner)['status'], 'NODE_MISSING')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            def runner(argv, *args):
                if argv[0] in ('node', 'npm') and '--version' in argv:
                    return {'exit_code': 0, 'stdout': '1', 'stderr': '', 'timed_out': False}
                if argv[0] == 'npm':
                    prefix = Path(argv[argv.index('--prefix') + 1])
                    prefix.mkdir(parents=True, exist_ok=True)
                    (prefix / 'package-lock.json').write_text(__import__('json').dumps(
                        {'packages': {'node_modules/' + spec['package']: {
                            'version': spec['version'], 'integrity': 'sha512-nope'}}}))
                    return {'exit_code': 0, 'stdout': '', 'stderr': '', 'timed_out': False}
                return {'exit_code': 127, 'stdout': '', 'stderr': '', 'timed_out': False}
            result = adapter.resolve_codegraph(root, {'index-install'}, runner)
            self.assertEqual(result['status'], 'INTEGRITY_MISMATCH')
            self.assertFalse(result.get('installed'))
