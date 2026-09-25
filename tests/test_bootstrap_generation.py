from pathlib import Path
import json
import tempfile
import unittest
from test_bootstrap_config import invoke


class GenerationTests(unittest.TestCase):
    def test_init_generates_owned_project_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'demo'
            args = ('init', '--target', root, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            first = invoke(*args)
            self.assertEqual(first.returncode, 5, first.stdout + first.stderr)
            self.assertTrue((root / 'AGENTS.md').is_file())
            self.assertTrue((root / '.agent-framework/skill/llm-wiki/SKILL.md').is_file())
            self.assertFalse((root / '.git').exists())
            second = invoke(*args)
            self.assertEqual(second.returncode, 5, second.stdout)
            self.assertEqual(json.loads((root / 'framework-project.json').read_text())['project_id'], 'demo')

    def test_manual_agents_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'AGENTS.md').write_text('User rules')
            result = invoke('init', '--target', root, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 3, result.stdout)
            self.assertEqual((root / 'AGENTS.md').read_text(), 'User rules')
