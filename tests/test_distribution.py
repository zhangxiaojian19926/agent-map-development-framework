import importlib.machinery
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest


class DistributionTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'tools/check-framework'
        loader = importlib.machinery.SourceFileLoader('checker', str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.checker = importlib.util.module_from_spec(spec)
        loader.exec_module(self.checker)

    def test_link_relative_to_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'docs').mkdir()
            (root / 'README.md').write_text('hello')
            page = root / 'docs/page.md'
            page.write_text('[home](../README.md)\n')
            self.assertEqual(self.checker.link_errors(root, page), [])
            page.write_text('[missing](missing.md)\n')
            self.assertEqual(len(self.checker.link_errors(root, page)), 1)

    def test_link_components_match_actual_case_on_every_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'docs/archive/plans/page.md'
            page.parent.mkdir(parents=True)
            (root / 'docs/bootstrap.md').write_text('lower-case guide')
            page.write_text('[guide](../../BOOTSTRAP.md)\n')
            self.assertEqual(len(self.checker.link_errors(root, page)), 1)

    def test_inventory_rejects_tamper_and_extras(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'README.md').write_text('hello')
            entries = self.checker.inventory(root)
            self.assertEqual(self.checker.inventory_errors(root, entries), [])
            (root / 'README.md').write_text('changed')
            (root / 'extra.txt').write_text('private')
            errors = self.checker.inventory_errors(root, entries)
            self.assertTrue(any('fingerprint' in e for e in errors))
            self.assertTrue(any('unexpected' in e for e in errors))

    def test_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'link').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                self.checker.inventory(root)

    def test_unbalanced_bold_markers_are_reported(self):
        balanced = (
            '# Title\n\n'
            '- **WHEN** something happens\n'
            '- **THEN** it works\n\n'
            'Text with **bold** and `code`.\n\n'
            '**bold text that\n'
            'continues on the next line.**\n\n'
            '```\n'
            '**not markdown**\n'
            '```\n'
        )
        unbalanced = '# Title\n\n- **THEN] it breaks\n'
        self.assertEqual(self.checker.emphasis_errors(Path('.'), 'ok.md', balanced), [])
        errors = self.checker.emphasis_errors(Path('.'), 'bad.md', unbalanced)
        self.assertEqual(len(errors), 1)
        self.assertIn('unbalanced bold marker', errors[0])

    def test_every_distribution_markdown_file_has_balanced_markers(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / 'framework-manifest.json').read_text(encoding='utf-8'))
        problems = []
        for rel in sorted(manifest['files']):
            if not rel.endswith('.md'):
                continue
            problems.extend(self.checker.emphasis_errors(root, rel, (root / rel).read_text(encoding='utf-8')))
        self.assertEqual(problems, [], 'unbalanced bold markers: ' + '; '.join(problems))
