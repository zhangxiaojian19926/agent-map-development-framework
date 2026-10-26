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
    'apply': {'action': 'change', 'grant': 'device-change', 'read_only': False,
              'argv': ['apply', '{device_id}'], 'timeout': 5},
    'verify': {'action': 'verify', 'grant': 'device-observe', 'read_only': True,
               'argv': ['verify', '{device_id}'], 'timeout': 5},
    'restore': {'action': 'restore', 'grant': 'device-change', 'read_only': False,
                'argv': ['restore', '{device_id}'], 'timeout': 5}
}


class DevicePilotTests(unittest.TestCase):
    def setUp(self):
        self.reverse = importlib.import_module('framework_core.reverse')
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.backup = self.root / 'backup.json'
        self.backup.write_text('original-state')

    def tearDown(self):
        self.tmp.cleanup()

    def backup_evidence(self, path=None):
        path = path or self.backup
        return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def scope(self, action='pilot'):
        return {
            'schema': 'reverse-scope/v2', 'id': 'pilot-case', 'goal': 'Change one device safely',
            'target': {'kind': 'device', 'device_id': 'meeting-1',
                       'baseline_sha256': hashlib.sha256(b'baseline-v1').hexdigest(),
                       'baseline_operation': 'baseline', 'tools': []},
            'acceptance': ['New behavior passes verification'],
            'observations': [{'id': 'observe-1', 'question': 'Read before change',
                              'action': 'device', 'operation': 'read-state'}],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {'capabilities': [{'name': 'read-state', 'provenance': 'DYNAMIC_OBSERVED',
                                           'observations': ['observe-1']}],
                         'constraints': ['One device only'], 'inferences': []},
            'device_plan': {
                'action': action, 'backup': self.backup_evidence(),
                'operations': [{'id': 'apply-1', 'operation': 'apply'}],
                'verify': [{'id': 'verify-1', 'operation': 'verify'}],
                'restore': [{'id': 'restore-1', 'operation': 'restore'}],
                'rollout': []
            }
        }

    def runner(self, calls, failures=None):
        failures = failures or set()
        def run(argv, cwd):
            calls.append(list(argv))
            command, device = argv[0], argv[1]
            failed = (command, device) in failures or command in failures
            output = 'baseline-v1' if command == 'baseline' else command + '-ok'
            return {'exit_code': 1 if failed else 0, 'stdout': output, 'stderr': '',
                    'timed_out': False, 'output_limit': False}
        return run

    def execute(self, scope, calls, extra=(), failures=None):
        grants = {'write', 'reverse', 'device-connect', 'device-observe', *extra}
        with mock.patch('framework_core.reverse_v2.load_operations', return_value=OPERATIONS):
            return self.reverse.prepare_reverse(
                self.root, scope, grants, runner=self.runner(calls, failures), platform='darwin', present=set())

    def test_pilot_requires_backup_and_change_grant_before_apply(self):
        calls = []
        invalid = self.scope()
        invalid['device_plan']['backup']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'BACKUP_INVALID'):
            self.execute(invalid, calls, extra=('device-change',))
        self.assertNotIn(['apply', 'meeting-1'], calls)

        calls = []
        report = self.execute(self.scope(), calls)
        self.assertEqual(report['device_change_status'], 'NOT_AUTHORIZED')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        self.assertNotIn(['apply', 'meeting-1'], calls)

    def test_missing_restore_or_unregistered_operation_rejects_before_apply(self):
        for mutate in (lambda plan: plan.update(restore=[]),
                       lambda plan: plan['operations'][0].update(operation='unregistered')):
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as separate:
                self.root = Path(separate)
                calls = []
                scope = self.scope()
                mutate(scope['device_plan'])
                with self.assertRaisesRegex(ValueError, 'INVALID_DEVICE_PLAN|INVALID_OPERATION'):
                    self.execute(scope, calls, extra=('device-change',))
                self.assertNotIn(['apply', 'meeting-1'], calls)

    def test_stale_pilot_baseline_rejects_before_apply(self):
        calls = []
        scope = self.scope()
        scope['target']['baseline_sha256'] = hashlib.sha256(b'other').hexdigest()
        report = self.execute(scope, calls, extra=('device-change',))
        self.assertEqual(report['device_change_status'], 'STALE')
        self.assertNotIn(['apply', 'meeting-1'], calls)

    def test_successful_pilot_persists_recovery_ready_and_runtime_pass(self):
        calls = []
        report = self.execute(self.scope(), calls, extra=('device-change',))
        self.assertEqual(report['device_change_status'], 'ROLLBACK_READY')
        self.assertEqual(report['runtime_validation'], 'PASS')
        self.assertEqual(calls[-2:], [['apply', 'meeting-1'], ['verify', 'meeting-1']])
        state = json.loads((self.root / '.framework/local-state/reverse/v2/pilot-case/device-state.json').read_text())
        self.assertEqual(state['state'], 'ROLLBACK_READY')
        self.assertIn('PILOT_VERIFIED', state['history'])
        contract = json.loads((self.root / '.framework/local-state/reverse/v2/pilot-case/behavior-contract.json').read_text())
        self.assertEqual(contract['runtime_validation'], 'PASS')

    def test_apply_failure_stops_before_verify_and_does_not_auto_retry(self):
        calls = []
        report = self.execute(self.scope(), calls, extra=('device-change',), failures={'apply'})
        self.assertEqual(report['device_change_status'], 'FAILED')
        self.assertNotIn(['verify', 'meeting-1'], calls)
        count = len(calls)
        report = self.execute(self.scope(), calls, extra=('device-change',))
        self.assertEqual(report['device_change_status'], 'FAILED')
        self.assertEqual(len(calls), count)

    def test_rollback_is_separate_action_and_clears_runtime_pass(self):
        calls = []
        self.execute(self.scope(), calls, extra=('device-change',))
        report = self.execute(self.scope('rollback'), calls, extra=('device-change',))
        self.assertEqual(report['device_change_status'], 'ROLLED_BACK')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        self.assertEqual(calls[-1], ['restore', 'meeting-1'])

    def test_rollout_checks_each_baseline_and_preserves_partial_results(self):
        second_backup = self.root / 'backup-2.json'
        second_backup.write_text('original-2')
        scope = self.scope()
        scope['device_plan']['rollout'] = [
            {'device_id': 'meeting-2', 'baseline_sha256': hashlib.sha256(b'baseline-v1').hexdigest(),
             'backup': self.backup_evidence(second_backup)},
            {'device_id': 'meeting-3', 'baseline_sha256': hashlib.sha256(b'baseline-v1').hexdigest(),
             'backup': self.backup_evidence()}
        ]
        calls = []
        self.execute(scope, calls, extra=('device-change',))
        rollout = self.scope('rollout')
        rollout['device_plan']['rollout'] = scope['device_plan']['rollout']
        report = self.execute(rollout, calls, extra=('device-rollout',), failures={('apply', 'meeting-2')})
        self.assertEqual(report['device_change_status'], 'PARTIAL')
        self.assertNotIn(['verify', 'meeting-2'], calls)
        self.assertIn(['verify', 'meeting-3'], calls)
        state = json.loads((self.root / '.framework/local-state/reverse/v2/pilot-case/device-state.json').read_text())
        self.assertEqual(state['rollout']['meeting-2']['status'], 'FAILED')
        self.assertEqual(state['rollout']['meeting-3']['status'], 'COMPLETE')

    def test_rollout_does_not_implicitly_gain_observation_grants(self):
        calls = []
        scope = self.scope()
        scope['device_plan']['rollout'] = [
            {'device_id': 'meeting-2', 'baseline_sha256': hashlib.sha256(b'baseline-v1').hexdigest(),
             'backup': self.backup_evidence()}]
        self.execute(scope, calls, extra=('device-change',))
        rollout = self.scope('rollout')
        rollout['device_plan']['rollout'] = scope['device_plan']['rollout']
        with mock.patch('framework_core.reverse_v2.load_operations', return_value=OPERATIONS):
            report = self.reverse.prepare_reverse(
                self.root, rollout, {'write', 'reverse', 'device-rollout'},
                runner=self.runner(calls), platform='darwin', present=set())
        self.assertEqual(report['device_change_status'], 'NOT_AUTHORIZED')
        self.assertNotIn(['apply', 'meeting-2'], calls)

    def test_rollout_rejects_incompatible_baseline_without_touching_that_device(self):
        scope = self.scope()
        scope['device_plan']['rollout'] = [
            {'device_id': 'other-model', 'baseline_sha256': hashlib.sha256(b'different').hexdigest(),
             'backup': self.backup_evidence()}
        ]
        calls = []
        self.execute(scope, calls, extra=('device-change',))
        rollout = self.scope('rollout')
        rollout['device_plan']['rollout'] = scope['device_plan']['rollout']
        report = self.execute(rollout, calls, extra=('device-rollout',))
        self.assertEqual(report['device_change_status'], 'PARTIAL')
        self.assertNotIn(['apply', 'other-model'], calls)
        state = json.loads((self.root / '.framework/local-state/reverse/v2/pilot-case/device-state.json').read_text())
        self.assertEqual(state['rollout']['other-model']['status'], 'STALE')


if __name__ == '__main__':
    unittest.main()
