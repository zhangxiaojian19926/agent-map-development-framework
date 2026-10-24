import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class ReverseTests(unittest.TestCase):
    def setUp(self):
        self.reverse = importlib.import_module('framework_core.reverse')
        self.maps = importlib.import_module('framework_core.maps')

    def test_bundles_are_open_source_and_split_by_host(self):
        darwin = self.reverse.bundle_for('darwin')
        linux = self.reverse.bundle_for('linux')
        for banned in ('hopper', 'ida', 'jeb'):
            self.assertNotIn(banned, darwin + linux)
        for linux_only in ('pwntools', 'unblob', 'tshark', 'sigrok-cli'):
            self.assertNotIn(linux_only, darwin)
            self.assertIn(linux_only, linux)
        self.assertIn('ghidra', darwin)
        self.assertIn('rea-agents', darwin)

    def test_without_reverse_nothing_is_installed(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self.reverse.prepare_reverse(root, None, {'write'}, runner=lambda *args: calls.append(args), platform='darwin', present=set())
        self.assertEqual(report['status'], 'NOT_CONFIGURED')
        self.assertEqual(calls, [])

    def test_missing_tools_do_not_install_without_reverse_install(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            report = self.reverse.prepare_reverse(Path(tmp), None, {'write', 'reverse'}, runner=lambda *args: calls.append(args), platform='darwin', present=set())
        self.assertEqual(report['status'], 'DEPENDENCY_MISSING')
        self.assertIn('ghidra', report['missing'])
        self.assertEqual(calls, [])

    def test_concentrated_install_skips_unpinned_and_checks_rea(self):
        spec = self.reverse.load_lock()['rea-agents']
        calls = []
        def runner(argv, cwd):
            calls.append(list(argv))
            if argv[0] == 'npm':
                self.assertNotIn('-g', argv)
                prefix = Path(argv[argv.index('--prefix') + 1])
                package = prefix / 'node_modules' / spec['package']
                package.mkdir(parents=True)
                lock = {'packages': {'node_modules/' + spec['package']: {'version': spec['version'], 'integrity': spec['integrity']}}}
                (prefix / 'package-lock.json').write_text(json.dumps(lock))
                return {'exit_code': 0}
            raise AssertionError(argv)
        present = set(self.reverse.bundle_for('darwin')) - {'rea-agents', 'temurin-jdk'}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self.reverse.prepare_reverse(root, None, {'write', 'reverse', 'reverse-install'}, runner=runner, platform='darwin', present=present)
        self.assertEqual(report['install'], ['rea-agents'])
        self.assertEqual(report['status'], 'PROVIDER_MISSING')
        self.assertIn('temurin-jdk', report['skipped'])
        self.assertTrue(any(argv[0] == 'npm' for argv in calls))

    def test_scope_records_summary_without_decompiler_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'sample.bin'
            target.write_bytes(b'not a program')
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            present = set(self.reverse.bundle_for('darwin'))
            scope = {'id': 'sample', 'target': str(target), 'sha256': digest, 'question': 'what does it print', 'action': 'static'}
            report = self.reverse.prepare_reverse(root, scope, {'write', 'reverse'}, runner=lambda *a: {'exit_code': 0}, platform='darwin', present=present)
            self.assertEqual(report['status'], 'READY')
            text = (root / 'docs/project/reverse/sample.md').read_text()
            self.assertIn(digest, text)
            self.assertNotIn('not a program', text)
            self.assertEqual(self.reverse.reverse_report(root)['status'], 'READY')
            target.write_bytes(b'changed')
            self.assertEqual(self.reverse.reverse_report(root)['status'], 'STALE')

    def test_reverse_path_cannot_be_a_map_edge(self):
        errors = self.maps.validate_map(Path('/tmp'), {'modules': {'api': {'path': 'api', 'sources': {'docs/project/reverse/sample.md': 'abc'}}}}, {
            'module_summaries': [{'id': 'api', 'summary': 'Api'}],
            'relationships': [{'id': 'edge', 'from': 'api', 'to': 'api', 'kind': 'contains', 'interface': 'entry',
                               'provenance': 'STATIC_SUPPORTED', 'runtime_validation': 'NOT_RUN',
                               'evidence': [{'path': 'docs/project/reverse/sample.md', 'sha256': 'abc', 'anchor': 'def api()'}]}],
            'uncertainties': []})
        self.assertIn('REVERSE_NOT_SOURCE', errors)


if __name__ == '__main__':
    unittest.main()
