import importlib.machinery
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
