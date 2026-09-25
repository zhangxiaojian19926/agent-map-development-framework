"""Current-session analysis binds input and never spawns another coding agent."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from framework_core.modules import discover, catalog_update
from framework_core.storage import atomic
from framework_core.config import encoded


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.handoff'), 'Current-session handoff missing')
        self.api = importlib.import_module('framework_core.handoff')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root/'api').mkdir()
        (self.root/'api/app.py').write_text('def hello(): return 1\n')
        self.catalog = catalog_update({}, [{'id': 'api', 'path': 'api'}], discover(self.root, ['api']))
        atomic(self.root, 'module-catalog.generated.json', encoded(self.catalog))
        self.grants = {'write', 'agent'}

    def envelope(self, packet):
        return {'request_id': packet['request_id'], 'source_digest': packet['source_digest'],
                'result': {'module_summaries': [{'id': 'api', 'summary': 'Exports hello'}],
                           'relationships': [], 'uncertainties': ['No cross-module call proved']}}

    def test_current_session_no_codex_and_static_only(self):
        packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
        with patch('subprocess.Popen', side_effect=AssertionError('Must not run Codex')):
            report = self.api.accept_analysis(self.root, self.envelope(packet), self.grants)
        self.assertEqual(report['agent']['execution'], 'current-session')
        self.assertEqual(report['runtime'], 'NOT_RUN')
        self.assertTrue((self.root/'docs/project/module-map.generated.md').exists())

    def test_rejected_results_preserve_prior_map(self):
        packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
        valid = self.envelope(packet)
        self.api.accept_analysis(self.root, valid, self.grants)
        before = (self.root/'docs/project/relationships.generated.json').read_bytes()
        for changes in ({'module_summaries': []}, {'approved': True}, {'runtime': 'VERIFIED'},
                        {'module_summaries': [{'id': 'unknown', 'summary': 'x'}]}):
            packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
            invalid = self.envelope(packet)
            invalid['result'].update(changes)
            with self.assertRaisesRegex(ValueError, 'INVALID_EVIDENCE'):
                self.api.accept_analysis(self.root, invalid, self.grants)
            self.assertEqual((self.root/'docs/project/relationships.generated.json').read_bytes(), before)

    def test_stale_source_and_old_request_rejected(self):
        packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
        old = self.envelope(packet)
        self.api.make_analysis_request(self.root, self.catalog, self.grants)
        with self.assertRaisesRegex(ValueError, 'STALE_REQUEST'):
            self.api.accept_analysis(self.root, old, self.grants)
        packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
        (self.root/'api/app.py').write_text('changed\n')
        with self.assertRaisesRegex(ValueError, 'STALE_SOURCE'):
            self.api.accept_analysis(self.root, self.envelope(packet), self.grants)

    def test_permission_budget_and_catalog_recheck(self):
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.api.make_analysis_request(self.root, self.catalog, set())
        self.assertFalse((self.root/'.framework').exists())
        packet = self.api.make_analysis_request(self.root, self.catalog, self.grants)
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.api.accept_analysis(self.root, self.envelope(packet), {'write'})
        changed = copy.deepcopy(self.catalog)
        changed['modules']['api']['path'] = 'elsewhere'
        atomic(self.root, 'module-catalog.generated.json', encoded(changed))
        with self.assertRaisesRegex(ValueError, 'STALE'):
            self.api.accept_analysis(self.root, self.envelope(packet), self.grants)


if __name__ == '__main__':
    unittest.main()
