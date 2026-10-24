import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'tools/prepare-release'


def write_repo(root, version, changelog):
    manifest = {'schema': 'agent-map-framework/v1', 'version': version,
                'files': {'CHANGELOG.md': hashlib.sha256(changelog.encode()).hexdigest()}}
    (root / 'framework-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (root / 'CHANGELOG.md').write_text(changelog)


def run_release(root, *args):
    return subprocess.run([sys.executable, str(CLI), '--root', str(root), '--date', '2026-10-24', *args],
                          capture_output=True, text=True, timeout=30)


class ReleaseTests(unittest.TestCase):
    def test_empty_unreleased_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_repo(root, '0.2.0', '# Changelog\n\n## Unreleased\n\n## 0.2.0 — 2026-09-25\n\n- previous\n')
            result = run_release(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'SKIP')
            self.assertIn('## Unreleased\n', (root / 'CHANGELOG.md').read_text())
            self.assertNotIn('0.2.1', (root / 'CHANGELOG.md').read_text())

    def test_patch_release_updates_changelog_and_manifest_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            notes = Path(d) / 'notes.md'
            write_repo(root, '0.2.0', '# Changelog\n\n## Unreleased — 索引与任意 Agent\n\n- 当前会话建图。\n\n## 0.2.0 — 2026-09-25\n\n- 旧版本\n')
            result = run_release(root, '--bump', 'patch', '--notes-out', str(notes))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            published = json.loads(result.stdout)
            self.assertEqual(published['tag'], 'v0.2.1')
            self.assertEqual(published['title'], '索引与任意 Agent')
            text = (root / 'CHANGELOG.md').read_text()
            self.assertIn('## Unreleased\n', text)
            self.assertIn('## 0.2.1 — 2026-10-24\n', text)
            self.assertIn('- 当前会话建图。', text)
            self.assertIn('- 旧版本', text)
            self.assertEqual(notes.read_text(), '- 当前会话建图。\n')
            manifest = json.loads((root / 'framework-manifest.json').read_text())
            self.assertEqual(manifest['version'], '0.2.1')
            self.assertEqual(manifest['files']['CHANGELOG.md'], hashlib.sha256((root / 'CHANGELOG.md').read_bytes()).hexdigest())
            again = run_release(root)
            self.assertEqual(json.loads(again.stdout)['status'], 'SKIP')

    def test_minor_and_major_bumps(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_repo(root, '0.2.3', '# Changelog\n\n## Unreleased\n\n- 功能\n')
            minor = run_release(root, '--bump', 'minor', '--dry-run')
            self.assertEqual(json.loads(minor.stdout)['version'], '0.3.0')
            self.assertEqual(json.loads((root / 'framework-manifest.json').read_text())['version'], '0.2.3')
            major = run_release(root, '--bump', 'major')
            self.assertEqual(json.loads(major.stdout)['version'], '1.0.0')

    def test_invalid_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_repo(root, 'v0.2', '# Changelog\n\n## Unreleased\n\n- 功能\n')
            result = run_release(root)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['error'], 'INVALID_VERSION')


if __name__ == '__main__':
    unittest.main()
