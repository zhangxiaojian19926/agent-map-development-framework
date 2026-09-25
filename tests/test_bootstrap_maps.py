import importlib
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class MapTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.maps'), 'map validation missing')
        self.maps = importlib.import_module('framework_core.maps')

    def test_static_analysis_cannot_claim_runtime_success(self):
        with tempfile.TemporaryDirectory() as d:
            errors = self.maps.validate_map(Path(d), {'modules': {'a': {}, 'b': {}}}, {
                'module_summaries': [], 'uncertainties': [], 'relationships': [
                    {'from': 'a', 'to': 'b', 'kind': 'runtime-call', 'interface': 'POST /task',
                     'provenance': 'STATIC_SUPPORTED', 'runtime_validation': 'VERIFIED', 'evidence': []}]})
            self.assertTrue(errors)

    def test_deleted_or_changed_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.py').write_text('def alpha(): pass\n')
            sha = hashlib.sha256((root / 'a.py').read_bytes()).hexdigest()
            evidence = {'path': 'a.py', 'anchor': 'def alpha', 'sha256': sha}
            result = {'module_summaries': [{'id': 'a', 'summary': 'a'}, {'id': 'b', 'summary': 'b'}], 'uncertainties': [], 'relationships': [
                {'id': 'a-b', 'from': 'a', 'to': 'b', 'kind': 'build-dependency',
                 'interface': 'alpha', 'provenance': 'INFERRED', 'runtime_validation': 'NOT_RUN',
                 'evidence': [evidence]}]}
            catalog = {'modules': {'a': {'sources': {'a.py': sha}}, 'b': {'sources': {}}}}
            self.assertEqual(self.maps.validate_map(root, catalog, result), [])
            (root / 'a.py').write_text('changed')
            self.assertTrue(self.maps.validate_map(root, catalog, result))

    def test_empty_agent_result_does_not_cover_declared_modules(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(self.maps.validate_map(Path(d), {'modules': {'a': {}}},
                {'module_summaries': [], 'relationships': [], 'uncertainties': []}))
