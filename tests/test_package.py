import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class PackageTests(unittest.TestCase):
    def test_package_hashes_dist_and_refuses_reverse_files(self):
        package = importlib.import_module('framework_core.package')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'dist').mkdir()
            (root / 'dist' / 'app.txt').write_text('build')
            with self.assertRaises(ValueError):
                package.package_project(root, {'write'})
            report = package.package_project(root, {'write', 'package'})
            self.assertEqual(report['status'], 'PACKAGED')
            self.assertEqual(report['runtime'], 'NOT_RUN')
            self.assertEqual(report['files'][0]['path'], 'dist/app.txt')
            saved = json.loads((root / '.framework/local-state/package-manifest.json').read_text())
            self.assertEqual(saved['files'][0]['sha256'], report['files'][0]['sha256'])
            nested = root / 'dist' / 'docs' / 'project' / 'reverse'
            nested.mkdir(parents=True)
            (nested / 'secret.md').write_text('nope')
            with self.assertRaises(ValueError):
                package.package_project(root, {'write', 'package'})

    def test_empty_project_has_nothing_to_package(self):
        package = importlib.import_module('framework_core.package')
        with tempfile.TemporaryDirectory() as tmp:
            report = package.package_project(Path(tmp), {'write', 'package'})
        self.assertEqual(report['status'], 'NOTHING_TO_PACKAGE')


if __name__ == '__main__':
    unittest.main()
