"""The local pre-commit check must stay aligned with what CI actually runs."""
import json
import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/pre-commit-check'


class PreCommitCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding='utf-8')
        cls.manifest = json.loads((ROOT / 'framework-manifest.json').read_text(encoding='utf-8'))

    def test_script_exists_is_executable_and_registered(self):
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(os.access(SCRIPT, os.X_OK), 'the check script must be executable')
        self.assertIn('tools/pre-commit-check', self.manifest['files'])

    def test_script_runs_the_same_gates_as_ci(self):
        for gate in ('tools/check-framework', 'tools/update-manifest',
                     'unittest', 'diff', '--check'):
            with self.subTest(gate=gate):
                self.assertIn(gate, self.text)

    def test_committed_mode_checks_the_range_ci_inspects(self):
        self.assertIn("'HEAD^'", self.text)
        self.assertIn("'HEAD'", self.text)
        self.assertIn('committed_range', self.text)

    def test_script_never_rewrites_the_manifest_in_read_only_mode(self):
        self.assertIn('--read-only', self.text)
        self.assertIn('if not args.read_only:', self.text)
