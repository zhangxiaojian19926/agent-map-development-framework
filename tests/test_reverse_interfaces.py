import contextlib
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_for(path, request_id='case'):
    return {'schema': 'reverse-request/v1', 'id': request_id, 'goal': 'inspect',
            'target': {'kind': 'file', 'path': str(path), 'sha256': digest(path)},
            'intent': 'static', 'acceptance': ['observed'],
            'observations': [{'id': 'observe', 'question': 'inspect', 'action': 'static'}],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {'capabilities': [], 'constraints': [], 'inferences': ['possible parser']}}


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cli = importlib.import_module('framework_core.cli')
        self.adapters = importlib.import_module('framework_core.reverse_adapters')
        self.reverse = importlib.import_module('framework_core.reverse')

    def tearDown(self):
        self.tmp.cleanup()

    def invoke_cli(self, argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = self.cli.main(argv)
        return code, json.loads(output.getvalue())

    def test_cli_real_preview_approval_and_legacy_dry_run(self):
        target = self.root / 'page.html'
        target.write_text('<html><script src="app.js"></script></html>')
        request_path = self.root / 'request.json'
        request_path.write_text(json.dumps(request_for(target)))
        code, legacy = self.invoke_cli(['reverse', '--target', str(self.root), '--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(legacy, {'action': 'reverse', 'required_capabilities': ['write', 'reverse'],
                                  'target': str(self.root.resolve())})
        code, preview = self.invoke_cli(['reverse', '--target', str(self.root), '--request', str(request_path),
                                         '--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(preview['status'], 'DRY_RUN')
        self.assertEqual(preview['plan']['tools'], [])
        self.assertFalse((self.root / '.framework').exists())
        code, pending = self.invoke_cli(['reverse', '--target', str(self.root), '--request', str(request_path),
                                         '--allow', 'write', '--allow', 'reverse'])
        self.assertEqual(code, 5)
        self.assertEqual(pending['status'], 'PLAN_APPROVAL_REQUIRED')
        code, result = self.invoke_cli(['reverse', '--target', str(self.root), '--request', str(request_path),
                                        '--allow', 'write', '--allow', 'reverse',
                                        '--approve', 'toolchain=' + pending['plan_sha256']])
        self.assertEqual(code, 0)
        self.assertEqual(result['observation_status'], 'RECORDED')
        invalid = self.root / 'invalid.json'
        invalid.write_text('{"schema":"reverse-request/v1"}')
        code, rejected = self.invoke_cli(['reverse', '--target', str(self.root), '--request', str(invalid),
                                          '--dry-run'])
        self.assertEqual(code, 2)
        self.assertEqual(rejected['status'], 'INVALID_INPUT')

    def test_rea_ghidra_wabt_fixed_argv_timeout_and_output_limit(self):
        target = self.root / 'sample'
        target.write_bytes(b'\x7fELFfixture')
        cases = [
            ('binary.static.generic', 'rea-agents', '/rea', '6.7.0', {}),
            ('binary.static.native', 'ghidra', '/ghidra/support/analyzeHeadless', '12.1.4',
             {'temurin-jdk': {'bin': '/jdk/bin/java', 'version': '21.0.13+9'}}),
            ('wasm.static', 'wabt', '/wasm2wat', '1.0.42', {})]
        for index, (capability, name, binary, version, extra) in enumerate(cases):
            with self.subTest(capability=capability):
                request = request_for(target, 'adapter-' + str(index))
                request['observations'][0]['capability'] = capability
                plan = {'plan_sha256': str(index) * 64,
                        'target': {'kind': 'native' if capability.startswith('binary') else 'wasm',
                                   'target_sha256': digest(target)},
                        'capabilities': [capability],
                        'tools': [{'tool_id': name, 'version': version}] + [
                            {'tool_id': key, 'version': value['version']} for key, value in extra.items()],
                        'network_origins': []}
                tools = {name: {'bin': binary, 'version': version}, **extra}
                calls = []
                def runner(argv, cwd, timeout, env):
                    calls.append((list(argv), timeout, env))
                    return {'exit_code': 0, 'stdout': 'raw-fixture', 'timed_out': False}
                record = self.adapters.execute_observation(self.root, request, plan, request['observations'][0],
                                                           {'reverse'}, tools=tools, runner=runner)
                self.assertEqual(record['status'], 'RECORDED')
                self.assertEqual(record['tool_versions'][name], version)
                argv, timeout, env = calls[0]
                self.assertEqual(argv[0], binary)
                self.assertIn(str(target), argv)
                self.assertGreater(timeout, 0)
                if capability == 'binary.static.native':
                    self.assertIn('analyzeHeadless', argv[0])
                    self.assertEqual(env['JAVA_HOME'], '/jdk')
                    self.assertTrue(any('/.framework/local-state/reverse/auto/' in part for part in argv))
        for index, failure in enumerate(({'exit_code': None, 'stdout': '', 'timed_out': True},
                                         {'exit_code': None, 'stdout': '', 'output_limit': True})):
            request = request_for(target, 'failure-' + str(index))
            request['evidence']['raw'] = 'discard'
            plan = {'plan_sha256': 'f' * 64, 'target': {'kind': 'native', 'target_sha256': digest(target)},
                    'capabilities': ['binary.static.generic'],
                    'tools': [{'tool_id': 'rea-agents', 'version': '6.7.0'}], 'network_origins': []}
            record = self.adapters.execute_observation(
                self.root, request, plan, request['observations'][0], {'reverse'},
                tools={'rea-agents': {'bin': '/rea', 'version': '6.7.0'}}, runner=lambda *args: failure)
            self.assertEqual(record['status'], 'TIMEOUT' if index == 0 else 'OUTPUT_LIMIT')
            self.assertEqual(record['raw_status'], 'NO_OUTPUT')
            self.assertEqual(record['runtime_validation'], 'NOT_RUN')

    def test_discard_idempotency_conflict_behavior_and_web_auth(self):
        target = self.root / 'sample'
        target.write_bytes(b'\x7fELFfixture')
        request = request_for(target)
        request['evidence']['raw'] = 'discard'
        request['behavior']['capabilities'] = [
            {'name': 'static-format', 'provenance': 'STATIC_SUPPORTED', 'observations': ['observe']}]
        plan = {'plan_sha256': 'a' * 64, 'target': {'kind': 'native', 'target_sha256': digest(target)},
                'capabilities': ['binary.static.generic'], 'tools': [{'tool_id': 'rea-agents', 'version': '6.7.0'}],
                'network_origins': []}
        tools = {'rea-agents': {'bin': '/rea', 'version': '6.7.0'}}
        runner = lambda *args: {'exit_code': 0, 'stdout': 'secret-decompiler-output'}
        first = self.adapters.execute_observation(self.root, request, plan, request['observations'][0],
                                                  {'reverse'}, tools=tools, runner=runner)
        second = self.adapters.execute_observation(self.root, request, plan, request['observations'][0],
                                                   {'reverse'}, tools=tools, runner=runner)
        self.assertEqual(first, second)
        self.assertEqual(first['raw_status'], 'RAW_DISCARDED')
        self.assertNotIn('raw_path', first)
        contract = self.adapters.behavior_contract(request, plan, [first])
        self.assertEqual(contract['capabilities'][0]['provenance'], 'STATIC_SUPPORTED')
        self.assertEqual(contract['inferences'][0]['provenance'], 'INFERRED')
        self.assertFalse(contract['source_map_evidence'])
        changed = dict(plan, plan_sha256='b' * 64,
                       tools=[{'tool_id': 'rea-agents', 'version': '6.7.1'}])
        with self.assertRaisesRegex(ValueError, 'OBSERVATION_CONFLICT'):
            self.adapters.execute_observation(self.root, request, changed, request['observations'][0],
                                              {'reverse'}, tools=tools, runner=runner)
        dynamic = request_for(target, 'auth-case')
        dynamic['auth'] = {'use_session': True}
        dynamic['observations'] = [{'id': 'dom', 'question': 'dom', 'action': 'browser',
                                    'operation': 'observe-dom'}]
        dynamic_plan = {'plan_sha256': 'c' * 64,
                        'target': {'kind': 'web_snapshot', 'target_sha256': 'd' * 64},
                        'capabilities': ['web.dynamic.dom'], 'tools': [], 'network_origins': []}
        calls = []
        record = self.adapters.execute_observation(
            self.root, dynamic, dynamic_plan, dynamic['observations'][0], {'browser-observe'},
            provider=lambda context: calls.append(context), manifest={'snapshot_sha256': 'd' * 64})
        self.assertEqual(record['status'], 'NOT_AUTHORIZED')
        self.assertIn('web-auth', record['required_grants'])
        self.assertEqual(calls, [])

    def test_target_change_after_preview_cannot_use_old_approval(self):
        target = self.root / 'page.html'
        target.write_text('<html>before</html>')
        request = request_for(target)
        from framework_core.reverse_auto import execute_auto
        pending = execute_auto(self.root, request, {'write', 'reverse'}, platform='darwin', machine='arm64')
        target.write_text('<html>after</html>')
        with self.assertRaisesRegex(ValueError, 'STALE_TARGET'):
            execute_auto(self.root, request, {'write', 'reverse'},
                         {'toolchain': pending['plan_sha256']}, platform='darwin', machine='arm64')
        self.assertFalse((self.root / '.framework/local-state/reverse/auto/case/observations').exists())

    def test_read_only_reverse_report_detects_tampering_without_repair(self):
        target = self.root / 'page.html'
        target.write_text('<html></html>')
        request = request_for(target)
        from framework_core.reverse_auto import execute_auto
        pending = execute_auto(self.root, request, {'write', 'reverse'}, platform='darwin', machine='arm64')
        result = execute_auto(self.root, request, {'write', 'reverse'},
                              {'toolchain': pending['plan_sha256']}, platform='darwin', machine='arm64')
        self.assertEqual(result['status'], 'READY')
        def tree_hash():
            return {path.relative_to(self.root).as_posix(): digest(path)
                    for path in self.root.rglob('*') if path.is_file()}
        before = tree_hash()
        with mock.patch('framework_core.process.run', side_effect=AssertionError('tool executed')), \
                mock.patch('framework_core.reverse_web.default_opener', side_effect=AssertionError('network')):
            report = self.reverse.reverse_report(self.root)
        self.assertEqual(report['status'], 'READY')  # No legacy bundle is needed when automatic state is present.
        self.assertEqual(report['automatic']['status'], 'PRESENT')
        self.assertEqual(tree_hash(), before)
        raw = self.root / '.framework/local-state/reverse/auto/case/raw/observe.txt'
        raw.write_text('tampered')
        after_tamper = tree_hash()
        report = self.reverse.reverse_report(self.root)
        self.assertEqual(report['status'], 'STALE')
        self.assertEqual(report['automatic']['status'], 'STALE')
        self.assertEqual(tree_hash(), after_tamper)


if __name__ == '__main__':
    unittest.main()
