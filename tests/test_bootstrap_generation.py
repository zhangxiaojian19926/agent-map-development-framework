from pathlib import Path
import hashlib
import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from test_bootstrap_config import invoke
from framework_core.generation import generation_changes


class GenerationTests(unittest.TestCase):
    def prepare(self, root):
        args = ('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
        result = invoke(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return args

    def inject_legacy(self, root, rel, content, owned):
        path = root / '.agent-framework' / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if owned:
            registry_rel = '.framework/local-state/owned.json'
            registry_path = root / registry_rel
            registry = json.loads(registry_path.read_text())
            registry['.agent-framework/' + rel] = hashlib.sha256(content.encode()).hexdigest()
            registry_path.write_text(json.dumps(registry))

    def test_prepare_removes_only_unchanged_owned_legacy_payload(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            args = self.prepare(root)
            outside = root / 'docs/acceptance.md'
            outside.parent.mkdir(parents=True, exist_ok=True)
            outside.write_text('outside\n')
            self.inject_legacy(root, 'docs/acceptance.md', 'legacy\n', owned=True)
            result = invoke(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / '.agent-framework/docs/acceptance.md').exists())
            self.assertEqual(outside.read_text(), 'outside\n')

    def test_prepare_preserves_edited_legacy_payload_as_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            args = self.prepare(root)
            self.inject_legacy(root, 'docs/acceptance.md', 'original\n', owned=True)
            edited = root / '.agent-framework/docs/acceptance.md'
            edited.write_text('human edit\n')
            result = invoke(*args)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn('CONFLICT: .agent-framework/docs/acceptance.md', result.stdout)
            self.assertEqual(edited.read_text(), 'human edit\n')

    def test_prepare_preserves_unowned_legacy_payload_as_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            args = self.prepare(root)
            self.inject_legacy(root, 'docs/maintainer/private.md', 'unknown owner\n', owned=False)
            result = invoke(*args)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn('CONFLICT: .agent-framework/docs/maintainer/private.md', result.stdout)
            self.assertEqual((root / '.agent-framework/docs/maintainer/private.md').read_text(), 'unknown owner\n')

    def test_prepare_upgrade_preserves_human_content_and_active_change(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'src/app.py'
            source.parent.mkdir()
            source.write_text('VALUE = 1\n')
            (root / 'AGENTS.md').write_text('# Human entry\n')
            args = self.prepare(root)
            protected = {
                'AGENTS.md': '# Human entry plus managed block\n',
                'docs/project/overview.md': '# Human project facts\n',
                'modules/api/AGENTS.md': '# Module-local rules\n',
                'src/app.py': 'VALUE = 1\n',
                'knowledge/project/purpose.md': '# Approved reusable knowledge\n',
                'openspec/changes/active-change/tasks.md': '- [ ] NOT_RUN\n',
            }
            for rel, content in protected.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                if rel == 'AGENTS.md':
                    content = path.read_text()
                path.write_text(content)
                protected[rel] = content
            before = {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in protected}
            result = invoke(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in protected}
            self.assertEqual(after, before)
            self.assertEqual(source.read_text(), 'VALUE = 1\n')

    def test_runtime_payload_missing_required_file_reports_path(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            distribution = base / 'distribution'
            distribution.mkdir()
            (distribution / 'framework-manifest.json').write_text('{"files": {}}')
            with self.assertRaisesRegex(ValueError, r'RUNTIME_PAYLOAD_INCOMPLETE: AGENTS\.md'):
                generation_changes(base / 'target', {'project_id': 'demo'}, distribution)

    def test_prepare_copies_only_runtime_payload(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'new'
            result = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            required = (
                'AGENTS.md', 'BOOTSTRAP.md',
                'docs/framework/development-workflow.md', 'docs/guide/project-layout.md',
                'docs/project-intake.md', 'docs/bootstrap.md', 'docs/integrations.md',
                'skill/llm-wiki/SKILL.md', 'templates/PROJECT-START.md',
                'tools/framework', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
            )
            forbidden = (
                'docs/maintainer/repository-layout.md', 'docs/archive/README.md',
                'docs/acceptance.md', 'docs/verification/bootstrap-0.2.0.md',
                'docs/superpowers/plans', 'tests', '.github', 'CHANGELOG.md',
            )
            for rel in required:
                self.assertTrue((root / '.agent-framework' / rel).is_file(), rel)
            for rel in forbidden:
                self.assertFalse((root / '.agent-framework' / rel).exists(), rel)

    def test_runtime_markdown_links_stay_inside_payload(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'new'
            self.prepare(root)
            package = root / '.agent-framework'
            checker_path = Path(__file__).resolve().parents[1] / 'tools/check-framework'
            loader = importlib.machinery.SourceFileLoader('runtime_checker', str(checker_path))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            checker = importlib.util.module_from_spec(spec)
            loader.exec_module(checker)
            for path in package.rglob('*.md'):
                with self.subTest(path=path.relative_to(package).as_posix()):
                    self.assertEqual(checker.link_errors(package, path), [])

    def test_prepare_without_approved_business_design_or_git(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'new'
            result = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['onboarding'], 'PREPARED')
            self.assertFalse((root/'.git').exists())
            self.assertFalse((root/'taskcli').exists())
            self.assertIn('No approved design', (root/'docs/project/architecture.md').read_text())
            self.assertTrue((root/'knowledge/project/.wiki-schema.md').is_file())
            self.assertTrue((root/'knowledge/project/wiki/topics/problems/.gitkeep').is_file())
            self.assertEqual(json.loads((root/'llm-wiki-aliases.json').read_text())['project'], 'knowledge/project')
            report = json.loads(result.stdout)
            self.assertEqual(report['knowledge']['status'], 'SCAFFOLDED')
            self.assertEqual(report['knowledge']['ingestion'], 'EMPTY')
            (root/'knowledge/project/purpose.md').write_text('KEEP\n')
            again = invoke('prepare', '--target', root, '--project-id', 'demo', '--agent', 'current', '--yes', '--allow', 'write')
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertEqual((root/'knowledge/project/purpose.md').read_text(), 'KEEP\n')

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
