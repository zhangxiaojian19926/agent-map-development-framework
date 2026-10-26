import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


class ReverseV2Tests(unittest.TestCase):
    def setUp(self):
        self.reverse = importlib.import_module('framework_core.reverse')
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / 'sample.bin'
        self.target.write_bytes(b'program')
        self.present = {'rea-agents'}

    def tearDown(self):
        self.tmp.cleanup()

    def observation(self, ident='observe-1'):
        return {'id': ident, 'question': 'What is the entry point?', 'action': 'static'}

    def scope(self, ident='case', observations=None):
        return {
            'schema': 'reverse-scope/v2',
            'id': ident,
            'goal': 'Preserve the entry point behavior',
            'target': {'kind': 'file', 'path': str(self.target),
                       'sha256': hashlib.sha256(self.target.read_bytes()).hexdigest(),
                       'tools': ['rea-agents']},
            'acceptance': ['Entry point is identified'],
            'observations': observations or [self.observation()],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {
                'capabilities': [{'name': 'entry-point', 'provenance': 'STATIC_SUPPORTED',
                                  'observations': ['observe-1']}],
                'constraints': ['Do not execute the target'],
                'inferences': ['The entry point may be stable']
            }
        }

    def runner(self, calls, outputs=None):
        def run(argv, cwd):
            calls.append(list(argv))
            index = len(calls) - 1
            output = (outputs or ['decompiler dump secret-token'])[min(index, len(outputs or ['']) - 1)]
            return {'exit_code': 0, 'stdout': output, 'stderr': '', 'timed_out': False, 'output_limit': False}
        return run

    def execute(self, scope, calls=None, grants=None, outputs=None):
        calls = calls if calls is not None else []
        report = self.reverse.prepare_reverse(
            self.root, scope, grants or {'write', 'reverse'}, runner=self.runner(calls, outputs),
            platform='darwin', present=self.present)
        return report, calls

    def test_v2_file_scope_selects_only_rea_and_emits_separate_states(self):
        report, calls = self.execute(self.scope())
        self.assertEqual(report['toolchain_status'], 'READY')
        self.assertEqual(report['observation_status'], 'RECORDED')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        self.assertEqual(report['device_change_status'], 'NOT_REQUESTED')
        self.assertEqual(report['bundle'], ['rea-agents'])
        self.assertEqual(len(calls), 1)
        self.assertIn('analyze', calls[0])

    def test_v2_missing_required_rea_without_install_grant_has_zero_downloads(self):
        calls = []
        self.present = set()
        report, _ = self.execute(self.scope(), calls, grants={'write', 'reverse'})
        self.assertEqual(report['status'], 'DEPENDENCY_MISSING')
        self.assertEqual(report['toolchain_status'], 'DEPENDENCY_MISSING')
        self.assertEqual(report['missing'], ['rea-agents'])
        self.assertEqual(calls, [])
        self.assertFalse((self.root / '.framework/local-state/reverse/v2/case/scope.json').exists())

    def test_v2_rejects_unknown_fields_and_stale_target_before_running(self):
        calls = []
        unknown = self.scope()
        unknown['unexpected'] = True
        with self.assertRaisesRegex(ValueError, 'INVALID_SCOPE'):
            self.execute(unknown, calls)
        stale = self.scope()
        stale['target']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'STALE_TARGET'):
            self.execute(stale, calls)
        self.assertEqual(calls, [])

    def test_v2_without_reverse_or_write_has_no_side_effects(self):
        calls = []
        report, _ = self.execute(self.scope(), calls, grants={'write'})
        self.assertEqual(report['status'], 'NOT_CONFIGURED')
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.execute(self.scope(), calls, grants={'reverse'})
        self.assertEqual(calls, [])
        self.assertFalse((self.root / '.framework').exists())

    def test_v2_appends_new_observation_without_replaying_accepted_one(self):
        first = self.scope()
        self.execute(first)
        calls = []
        second = self.scope(observations=[self.observation(), self.observation('observe-2')])
        report, _ = self.execute(second, calls)
        self.assertEqual(report['observation_status'], 'RECORDED')
        self.assertEqual(len(calls), 1)
        folder = self.root / '.framework/local-state/reverse/v2/case/observations'
        self.assertEqual(len(list(folder.glob('*.json'))), 2)
        first_record = json.loads((folder / 'observe-1.json').read_text())
        self.assertEqual(first_record['status'], 'RECORDED')

    def test_v2_same_observation_id_with_different_request_conflicts_without_replay(self):
        self.execute(self.scope())
        changed = self.scope()
        changed['observations'][0]['question'] = 'A different question'
        calls = []
        with self.assertRaisesRegex(ValueError, 'OBSERVATION_CONFLICT'):
            self.execute(changed, calls)
        self.assertEqual(calls, [])
        record = json.loads((self.root / '.framework/local-state/reverse/v2/case/observations/observe-1.json').read_text())
        self.assertEqual(record['question'], 'What is the entry point?')

    def test_v2_raw_retention_and_discard_are_truthful_and_public_is_redacted(self):
        self.execute(self.scope())
        raw = self.root / '.framework/local-state/reverse/v2/case/raw/observe-1.txt'
        self.assertEqual(raw.read_text(), 'decompiler dump secret-token')
        record = json.loads((self.root / '.framework/local-state/reverse/v2/case/observations/observe-1.json').read_text())
        self.assertEqual(record['raw_sha256'], digest('decompiler dump secret-token'))
        public = (self.root / 'docs/project/reverse/case.md').read_text()
        self.assertNotIn('decompiler dump', public)
        self.assertNotIn('secret-token', public)

        discarded = self.scope('discarded')
        discarded['evidence']['raw'] = 'discard'
        self.execute(discarded)
        self.assertFalse((self.root / '.framework/local-state/reverse/v2/discarded/raw/observe-1.txt').exists())
        record = json.loads((self.root / '.framework/local-state/reverse/v2/discarded/observations/observe-1.json').read_text())
        self.assertEqual(record['raw_status'], 'RAW_DISCARDED')
        public = (self.root / 'docs/project/reverse/discarded.md').read_text()
        self.assertIn('RAW_DISCARDED', public)
        self.assertNotIn('stays in local-state', public)

    def test_v1_raw_output_is_actually_retained_without_public_decompiler_text(self):
        calls = []
        legacy = {'id': 'legacy', 'target': str(self.target),
                  'sha256': hashlib.sha256(self.target.read_bytes()).hexdigest(),
                  'question': 'inspect', 'action': 'static'}
        report = self.reverse.prepare_reverse(
            self.root, legacy, {'write', 'reverse'}, runner=self.runner(calls),
            platform='darwin', present=set(self.reverse.bundle_for('darwin')))
        self.assertEqual(report['observation']['status'], 'RECORDED')
        raw = self.root / '.framework/local-state/rea/legacy.raw'
        self.assertEqual(raw.read_text(), 'decompiler dump secret-token')
        public = (self.root / 'docs/project/reverse/legacy.md').read_text()
        self.assertNotIn('decompiler dump', public)
        self.assertNotIn('secret-token', public)

    def test_reverse_report_detects_tampered_v2_raw_without_repairing_it(self):
        self.execute(self.scope())
        raw = self.root / '.framework/local-state/reverse/v2/case/raw/observe-1.txt'
        raw.write_text('tampered')
        before = raw.read_text()
        report = self.reverse.reverse_report(self.root)
        self.assertEqual(report['status'], 'STALE')
        self.assertEqual(raw.read_text(), before)

    def test_behavior_contract_separates_inference_and_rejects_missing_evidence(self):
        self.execute(self.scope())
        contract = json.loads((self.root / '.framework/local-state/reverse/v2/case/behavior-contract.json').read_text())
        self.assertEqual(contract['schema'], 'device-behavior/v1')
        self.assertEqual(contract['runtime_validation'], 'NOT_RUN')
        self.assertEqual(contract['capabilities'][0]['provenance'], 'STATIC_SUPPORTED')
        self.assertEqual(contract['inferences'][0]['provenance'], 'INFERRED')

        invalid = self.scope('invalid-contract')
        invalid['behavior']['capabilities'][0]['observations'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'INVALID_BEHAVIOR'):
            self.execute(invalid)
        self.assertFalse((self.root / '.framework/local-state/reverse/v2/invalid-contract/behavior-contract.json').exists())

    def test_behavior_contract_rejects_provenance_mismatch(self):
        invalid = self.scope('wrong-provenance')
        invalid['behavior']['capabilities'][0]['provenance'] = 'DYNAMIC_OBSERVED'
        with self.assertRaisesRegex(ValueError, 'INVALID_BEHAVIOR'):
            self.execute(invalid)

    def test_invalid_behavior_does_not_overwrite_existing_contract(self):
        self.execute(self.scope())
        path = self.root / '.framework/local-state/reverse/v2/case/behavior-contract.json'
        before = path.read_bytes()
        invalid = self.scope(observations=[self.observation(), self.observation('observe-2')])
        invalid['behavior']['capabilities'][0]['observations'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'INVALID_BEHAVIOR'):
            self.execute(invalid)
        self.assertEqual(path.read_bytes(), before)

    def test_partial_observation_failure_is_not_complete_validation(self):
        scope = self.scope(observations=[self.observation(), self.observation('observe-2')])
        calls = []
        def failing(argv, cwd):
            calls.append(list(argv))
            return {'exit_code': 1 if len(calls) == 2 else 0, 'stdout': 'partial', 'stderr': 'failed',
                    'timed_out': False, 'output_limit': False}
        report = self.reverse.prepare_reverse(
            self.root, scope, {'write', 'reverse'}, runner=failing, platform='darwin', present=self.present)
        self.assertEqual(report['observation_status'], 'PARTIAL')
        self.assertEqual(report['runtime_validation'], 'NOT_RUN')
        records = [json.loads(path.read_text()) for path in sorted((self.root / '.framework/local-state/reverse/v2/case/observations').glob('*.json'))]
        self.assertEqual([item['status'] for item in records], ['RECORDED', 'FAILED'])


if __name__ == '__main__':
    unittest.main()
