import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


OPERATIONS = {
    'baseline': {'action': 'device', 'grant': 'device-observe', 'read_only': True,
                 'argv': ['baseline', '{device_id}'], 'timeout': 5},
    'read-state': {'action': 'device', 'grant': 'device-observe', 'read_only': True,
                   'argv': ['read', '{device_id}'], 'timeout': 5},
    'read-network': {'action': 'network', 'grant': 'network-capture', 'read_only': True,
                     'provider': 'network', 'timeout': 5}
}


class DynamicReverseTests(unittest.TestCase):
    def setUp(self):
        self.reverse = importlib.import_module('framework_core.reverse')
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def scope(self, action='device'):
        observation = {'id': 'observe-1', 'question': 'Read current state',
                       'action': action, 'operation': 'read-state' if action == 'device' else 'read-network'}
        if action == 'network':
            observation['endpoint'] = 'device.local:443'
        return {
            'schema': 'reverse-scope/v2', 'id': 'device-case', 'goal': 'Read without changing state',
            'target': {'kind': 'device', 'device_id': 'living-room', 'baseline_sha256': hashlib.sha256(b'baseline-v1').hexdigest(),
                       'baseline_operation': 'baseline', 'tools': []},
            'acceptance': ['State is observed without modification'], 'observations': [observation],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {'capabilities': [{'name': 'read-state', 'provenance': 'DYNAMIC_OBSERVED',
                                           'observations': ['observe-1']}],
                         'constraints': ['No writes'], 'inferences': []}
        }

    def runner(self, calls, result=None):
        def run(argv, cwd):
            calls.append(list(argv))
            if argv[0] == 'baseline':
                return {'exit_code': 0, 'stdout': 'baseline-v1', 'stderr': '', 'timed_out': False, 'output_limit': False}
            return result or {'exit_code': 0, 'stdout': 'state token=secret', 'stderr': '',
                              'timed_out': False, 'output_limit': False}
        return run

    def execute(self, scope, grants, calls, provider=None, result=None):
        with mock.patch('framework_core.reverse_v2.load_operations', return_value=OPERATIONS):
            return self.reverse.prepare_reverse(
                self.root, scope, grants, runner=self.runner(calls, result), platform='darwin', present=set(),
                device_executor=provider)

    def test_device_observation_checks_baseline_and_emits_dynamic_contract(self):
        calls = []
        report = self.execute(self.scope(), {'write', 'reverse', 'device-connect', 'device-observe'}, calls)
        self.assertEqual(report['observation_status'], 'RECORDED')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        self.assertEqual(report['device_change_status'], 'NOT_REQUESTED')
        self.assertEqual(calls, [['baseline', 'living-room'], ['read', 'living-room']])
        record = json.loads((self.root / '.framework/local-state/reverse/v2/device-case/observations/observe-1.json').read_text())
        self.assertEqual(record['provenance'], 'DYNAMIC_OBSERVED')
        self.assertNotIn('secret', json.dumps(record))
        contract = json.loads((self.root / '.framework/local-state/reverse/v2/device-case/behavior-contract.json').read_text())
        self.assertEqual(contract['capabilities'][0]['provenance'], 'DYNAMIC_OBSERVED')

    def test_missing_device_grants_or_unregistered_operation_never_executes(self):
        calls = []
        report = self.execute(self.scope(), {'write', 'reverse'}, calls)
        self.assertEqual(report['observation_status'], 'NOT_AUTHORIZED')
        self.assertEqual(calls, [])
        invalid = self.scope()
        invalid['observations'][0]['operation'] = 'arbitrary-shell'
        with self.assertRaisesRegex(ValueError, 'INVALID_OPERATION'):
            self.execute(invalid, {'write', 'reverse', 'device-connect', 'device-observe'}, calls)
        self.assertEqual(calls, [])

    def test_stale_device_baseline_stops_before_requested_observation(self):
        calls = []
        scope = self.scope()
        scope['target']['baseline_sha256'] = hashlib.sha256(b'other-baseline').hexdigest()
        report = self.execute(scope, {'write', 'reverse', 'device-connect', 'device-observe'}, calls)
        self.assertEqual(report['observation_status'], 'STALE')
        self.assertEqual(calls, [['baseline', 'living-room']])

    def test_network_requires_named_provider_and_separate_grant(self):
        calls = []
        report = self.execute(self.scope('network'), {'write', 'reverse', 'network-capture'}, calls)
        self.assertEqual(report['observation_status'], 'PROVIDER_MISSING')
        self.assertEqual(calls, [])
        provider_calls = []
        def provider(operation, target, endpoint):
            provider_calls.append((operation, target['device_id'], endpoint))
            return {'exit_code': 0, 'stdout': 'sanitized packet metadata', 'stderr': '',
                    'timed_out': False, 'output_limit': False}
        ready = self.scope('network')
        ready['id'] = 'network-ready'
        report = self.execute(ready, {'write', 'reverse', 'network-capture'}, calls, provider=provider)
        self.assertEqual(report['observation_status'], 'RECORDED')
        self.assertEqual(provider_calls[0][1:], ('living-room', 'device.local:443'))

    def test_reverse_report_detects_tampered_device_baseline_without_repair(self):
        calls = []
        self.execute(self.scope(), {'write', 'reverse', 'device-connect', 'device-observe'}, calls)
        baseline = self.root / '.framework/local-state/reverse/v2/device-case/baseline.txt'
        baseline.write_text('tampered')
        before_count = len(calls)
        report = self.reverse.reverse_report(self.root)
        self.assertEqual(report['status'], 'STALE')
        self.assertEqual(report['id'], 'device-case')
        self.assertEqual(baseline.read_text(), 'tampered')
        self.assertEqual(len(calls), before_count)

    def test_disconnect_is_not_a_dynamic_observation(self):
        calls = []
        disconnected = {'exit_code': 1, 'stdout': '', 'stderr': 'offline',
                        'timed_out': False, 'output_limit': False}
        report = self.execute(self.scope(), {'write', 'reverse', 'device-connect', 'device-observe'},
                              calls, result=disconnected)
        self.assertEqual(report['observation_status'], 'FAILED')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        self.assertFalse((self.root / '.framework/local-state/reverse/v2/device-case/behavior-contract.json').exists())

    def test_timeout_and_output_limit_are_not_success(self):
        for result, expected in [
                ({'exit_code': 0, 'stdout': '', 'stderr': '', 'timed_out': True, 'output_limit': False}, 'TIMEOUT'),
                ({'exit_code': 0, 'stdout': 'too much', 'stderr': '', 'timed_out': False, 'output_limit': True}, 'OUTPUT_LIMIT')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as separate:
                self.root = Path(separate)
                calls = []
                report = self.execute(self.scope(), {'write', 'reverse', 'device-connect', 'device-observe'}, calls, result=result)
                self.assertEqual(report['observation_status'], expected)
                self.assertEqual(report['runtime_validation'], 'NOT_RUN')


if __name__ == '__main__':
    unittest.main()
