"""Batch acceptance never turns incomplete or mixed-version observations into maps."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from framework_core.config import encoded
from framework_core.modules import catalog_update, discover
from framework_core.storage import atomic


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.analysis_batches'), 'Batch protocol missing')
        self.api = importlib.import_module('framework_core.analysis_batches')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        for name in ('api', 'client', 'other'):
            (self.root/name).mkdir()
            (self.root/name/'code.py').write_text('def ' + name + '(): return 1\n' + '# 注释\n'*45000)
        self.catalog = catalog_update({}, [{'id': n, 'path': n} for n in ('api', 'client', 'other')], discover(self.root, ['api', 'client', 'other']))
        atomic(self.root, 'module-catalog.generated.json', encoded(self.catalog))
        self.grants = {'write', 'agent'}

    def batch_result(self, packet):
        return {'summary': 'Checked the declared file range', 'uncertainties': [],
                'slice_ids': [s['slice_id'] for s in packet['slices']]}

    def final_result(self):
        evidence = [{'path': n+'/code.py', 'sha256': self.catalog['modules'][n]['sources'][n+'/code.py'],
                     'anchor': 'def '+n+'()'} for n in ('api', 'client')]
        return {'module_summaries': [{'id': n, 'summary': 'Exports '+n} for n in ('api', 'client', 'other')],
                'relationships': [{'id': 'shared', 'from': 'api', 'to': 'client', 'kind': 'data-exchange',
                    'interface': 'Synthetic inferred interface', 'provenance': 'INFERRED',
                    'runtime_validation': 'NOT_RUN', 'evidence': evidence}], 'uncertainties': ['Runtime untested']}

    def test_split_covers_large_unicode_files_with_bounded_serialized_packets(self):
        source = {'path': 'a/code.py', 'sha256': 'a'*64, 'content': '值 = "\\"\n'*60000}
        batches = self.api.split_sources([source])
        self.assertGreater(len(batches), 3)
        slices = [s for b in batches for s in b['slices']]
        self.assertEqual(''.join(s['content'] for s in slices), source['content'])
        line = 1
        for batch in batches:
            self.assertLessEqual(len(encoded(batch).encode()), 200000)
            for part in batch['slices']:
                self.assertEqual(part['start_line'], line)
                line = part['end_line'] + 1
        with self.assertRaisesRegex(ValueError, 'FILE_SLICE_TOO_LARGE'):
            self.api.split_sources([dict(source, content='x'*200000)])

    def test_resume_accepts_identical_replay_and_publishes_only_complete_map(self):
        session = self.api.begin_analysis(self.root, self.catalog, self.grants)
        sid = session['session_id']
        first = session['batches'][0]['batch_id']
        packet = self.api.read_batch(self.root, sid, first, self.grants)
        result = self.batch_result(packet)
        self.api.accept_batch(self.root, sid, first, result, self.grants)
        self.api.accept_batch(self.root, sid, first, result, self.grants)
        with self.assertRaisesRegex(ValueError, 'BATCH_CONFLICT'):
            self.api.accept_batch(self.root, sid, first, dict(result, summary='different'), self.grants)
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_COVERAGE'):
            self.api.finalize_analysis(self.root, sid, self.final_result(), self.grants)
        self.assertFalse((self.root/'docs/project/relationships.generated.json').exists())
        resumed = self.api.begin_analysis(self.root, self.catalog, self.grants)
        self.assertEqual(resumed['session_id'], sid)
        self.assertEqual(resumed['batches'][0]['status'], 'ACCEPTED')
        for batch in resumed['batches'][1:]:
            packet = self.api.read_batch(self.root, sid, batch['batch_id'], self.grants)
            self.api.accept_batch(self.root, sid, batch['batch_id'], self.batch_result(packet), self.grants)
        done = self.api.finalize_analysis(self.root, sid, self.final_result(), self.grants)
        self.assertEqual(done['coverage']['status'], 'COMPLETE')
        self.assertEqual(done['runtime'], 'NOT_RUN')
        saved = json.loads((self.root/'docs/project/relationships.generated.json').read_text())
        self.assertEqual(saved['relationships'][0]['to'], 'client')

    def test_source_drift_new_file_and_framework_drift_reject_old_session(self):
        session = self.api.begin_analysis(self.root, self.catalog, self.grants)
        sid, bid = session['session_id'], session['batches'][0]['batch_id']
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.api.read_batch(self.root, sid, bid, set())
        (self.root/'api/new.py').write_text('new = 1\n')
        with self.assertRaisesRegex(ValueError, 'STALE_SOURCE'):
            self.api.read_batch(self.root, sid, bid, self.grants)
        (self.root/'api/new.py').rename(self.root/'outside.py')
        atomic(self.root, '.agent-framework/framework-manifest.json', '{"version":"changed"}')
        with self.assertRaisesRegex(ValueError, 'STALE_FRAMEWORK'):
            self.api.read_batch(self.root, sid, bid, self.grants)

    def test_unknown_or_missing_slice_cannot_mark_batch_accepted(self):
        session = self.api.begin_analysis(self.root, self.catalog, self.grants)
        sid, bid = session['session_id'], session['batches'][0]['batch_id']
        for ids in ([], ['unknown']):
            with self.assertRaisesRegex(ValueError, 'INVALID_EVIDENCE'):
                self.api.accept_batch(self.root, sid, bid, {'summary': 'x', 'uncertainties': [], 'slice_ids': ids}, self.grants)
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_BATCH'):
            self.api.read_batch(self.root, sid, '../outside', self.grants)

    def test_private_state_does_not_duplicate_source_body(self):
        self.api.begin_analysis(self.root, self.catalog, self.grants)
        for path in (self.root/'.framework').rglob('*.json'):
            self.assertNotIn('def api()', path.read_text())

    def test_snapshot_splits_one_file_at_a_time_and_resume_does_not_resplit(self):
        from unittest.mock import patch
        original = self.api.split_sources
        seen = []
        def split(items, *args, **kwargs):
            seen.append(len(items))
            return original(items, *args, **kwargs)
        with patch.object(self.api, 'split_sources', split):
            initial = self.api.begin_analysis(self.root, self.catalog, self.grants)
        self.assertEqual(seen, [1, 1, 1])
        with patch.object(self.api, 'snapshot', side_effect=AssertionError('Unchanged source should not be resliced')):
            resumed = self.api.begin_analysis(self.root, self.catalog, self.grants)
        self.assertEqual(initial['session_id'], resumed['session_id'])

    def test_cli_v2_can_list_read_and_accept_a_batch(self):
        from test_bootstrap_config import invoke
        result = invoke('analyze-request', '--protocol', 'v2', '--target', self.root, '--allow', 'write', '--allow', 'agent')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads(result.stdout)
        args = ('--target', self.root, '--session-id', state['session_id'], '--batch-id', state['batches'][0]['batch_id'], '--allow', 'write', '--allow', 'agent')
        read = invoke('analysis-batch', *args)
        self.assertEqual(read.returncode, 0, read.stdout)
        response = self.root/'batch-result.json'
        response.write_text(json.dumps(self.batch_result(json.loads(read.stdout))))
        accepted = invoke('accept-batch', *args, '--result', response)
        self.assertEqual(accepted.returncode, 0, accepted.stdout)

    def test_bad_final_result_and_interrupted_publish_preserve_recovery_state(self):
        from unittest.mock import patch
        from framework_core.storage import read_json, resume_run
        session = self.api.begin_analysis(self.root, self.catalog, self.grants)
        sid = session['session_id']
        for batch in session['batches']:
            packet = self.api.read_batch(self.root, sid, batch['batch_id'], self.grants)
            self.api.accept_batch(self.root, sid, batch['batch_id'], self.batch_result(packet), self.grants)
        invalid = self.final_result()
        invalid['relationships'][0]['runtime_validation'] = 'VERIFIED'
        with self.assertRaisesRegex(ValueError, 'INVALID_EVIDENCE'):
            self.api.finalize_analysis(self.root, sid, invalid, self.grants)
        import framework_core.storage as storage
        original = storage.atomic
        def interrupted(root, rel, content):
            if rel == 'docs/project/relationships.generated.json':
                raise OSError('simulated storage interruption')
            return original(root, rel, content)
        with patch.object(storage, 'atomic', interrupted), self.assertRaises(OSError):
            self.api.finalize_analysis(self.root, sid, self.final_result(), self.grants)
        journal = read_json(self.root, '.framework/local-state/runs/analysis-final-'+sid+'.json')
        self.assertEqual(journal['status'], 'APPLYING')
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            resume_run(self.root, 'analysis-final-'+sid, {'write'})
        (self.root/'api/new.py').write_text('new = 1\n')
        with self.assertRaisesRegex(ValueError, 'STALE_SOURCE'):
            resume_run(self.root, 'analysis-final-'+sid, self.grants)
        (self.root/'api/new.py').rename(self.root/'outside.py')
        self.api.finalize_analysis(self.root, sid, self.final_result(), self.grants)
        resumed = read_json(self.root, '.framework/local-state/runs/analysis-final-'+sid+'.json')
        self.assertEqual(resumed['status'], 'COMPLETE')
        self.assertTrue((self.root/'docs/project/relationships.generated.json').exists())
