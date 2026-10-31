"""A skill must declare the same invocation form to every host."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_checker():
    loader = importlib.machinery.SourceFileLoader('checker', str(ROOT / 'tools/check-framework'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class InvocationFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.manifest = json.loads((ROOT / 'framework-manifest.json').read_text(encoding='utf-8'))

    def test_every_skill_declares_one_consistent_form(self):
        errors = self.checker.invocation_errors(ROOT, self.manifest['files'])
        self.assertEqual(errors, [], 'invocation forms disagree: ' + '; '.join(errors))

    def test_user_invoked_skills_carry_both_declarations(self):
        user_invoked = []
        for rel in sorted(self.manifest['files']):
            if not rel.endswith('/SKILL.md'):
                continue
            front = (ROOT / rel).read_text(encoding='utf-8')[:800]
            if 'disable-model-invocation: true' in front:
                user_invoked.append(rel)
                yaml = (ROOT / rel).parent / 'agents/openai.yaml'
                self.assertTrue(yaml.is_file(), rel + ' must also declare its form for Codex')
                self.assertIn('allow_implicit_invocation: false', yaml.read_text(encoding='utf-8'))
        self.assertTrue(user_invoked, 'the distribution is expected to carry at least one user-invoked skill')

    def test_checker_reports_a_form_declared_for_one_host_only(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            skill = root / 'skill' / 'group' / 'demo'
            (skill / 'agents').mkdir(parents=True)
            (skill / 'SKILL.md').write_text(
                '---\nname: demo\ndescription: demo\ndisable-model-invocation: true\n---\n',
                encoding='utf-8')
            (skill / 'agents' / 'openai.yaml').write_text(
                'interface:\n  display_name: "Demo"\n', encoding='utf-8')
            errors = self.checker.invocation_errors(root, {'skill/group/demo/SKILL.md': 'x'})
            self.assertEqual(len(errors), 1)
            self.assertIn('one host only', errors[0])

    def test_checker_accepts_a_consistent_user_invoked_pair(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            skill = root / 'skill' / 'group' / 'demo'
            (skill / 'agents').mkdir(parents=True)
            (skill / 'SKILL.md').write_text(
                '---\nname: demo\ndescription: demo\ndisable-model-invocation: true\n---\n',
                encoding='utf-8')
            (skill / 'agents' / 'openai.yaml').write_text(
                'policy:\n  allow_implicit_invocation: false\n', encoding='utf-8')
            errors = self.checker.invocation_errors(root, {'skill/group/demo/SKILL.md': 'x'})
            self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
