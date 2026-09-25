from pathlib import Path
import json
import tempfile
import unittest
from test_bootstrap_config import invoke


class GenerationTests(unittest.TestCase):
    def test_prepare_without_approved_business_design_or_git(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'new'
            result = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['onboarding'], 'PREPARED')
            self.assertFalse((root/'.git').exists())
            self.assertFalse((root/'taskcli').exists())
            self.assertIn('No approved design', (root/'docs/project/architecture.md').read_text())

    def test_prepare_preserves_human_rules_and_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            original = b'# Human rules\r\nDo not deploy.\r\n'
            (root/'AGENTS.md').write_bytes(original)
            (root/'app.py').write_text('user code\n')
            args = ('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            result = invoke(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root/'AGENTS.md').read_bytes().startswith(original))
            first = (root/'AGENTS.md').read_bytes()
            self.assertEqual(invoke(*args).returncode, 0)
            self.assertEqual((root/'AGENTS.md').read_bytes(), first)
            self.assertEqual((root/'app.py').read_text(), 'user code\n')
            self.assertIn('docs/project/overview.md', first.decode())

    def test_prepare_rule_conflict_has_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            original = '<!-- FRAMEWORK_ENTRY_START -->\nuser edited incomplete block'
            (root/'AGENTS.md').write_text(original)
            result = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertEqual((root/'AGENTS.md').read_text(), original)

    def test_prepare_existing_loose_sources_are_not_treated_as_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root/'main.py').write_text('def main(): return 1\n')
            result = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 0, result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report['maps']['status'], 'NOT_RUN')
            catalog = json.loads((root/'module-catalog.generated.json').read_text())
            self.assertEqual(catalog['modules']['root']['path'], '.')
            self.assertIn('main.py', catalog['modules']['root']['sources'])
            self.assertFalse((root/'.git').exists())

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
