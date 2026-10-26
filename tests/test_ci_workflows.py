from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CiWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validate = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
        cls.release = (ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')

    def test_validate_uses_supported_action_versions(self):
        self.assertIn('- uses: actions/checkout@v7\n', self.validate)
        self.assertIn('- uses: actions/setup-python@v7\n', self.validate)
        self.assertNotIn('actions/checkout@v4', self.validate)
        self.assertNotIn('actions/setup-python@v5', self.validate)

    def test_release_uses_supported_action_versions(self):
        self.assertIn('- uses: actions/checkout@v7\n', self.release)
        self.assertIn('- uses: actions/setup-python@v7\n', self.release)
        self.assertNotIn('actions/checkout@v4', self.release)
        self.assertNotIn('actions/setup-python@v5', self.release)

    def test_validate_triggers_permissions_and_concurrency(self):
        self.assertIn('on: [push, pull_request, workflow_dispatch]\n', self.validate)
        self.assertIn('permissions:\n  contents: read\n', self.validate)
        self.assertIn('group: validate-${{ github.workflow }}-${{ github.ref }}\n', self.validate)
        self.assertIn('cancel-in-progress: true\n', self.validate)

    def test_validate_matrix_and_python_contract(self):
        self.assertIn('os: [ubuntu-latest, macos-latest]\n', self.validate)
        self.assertIn('runs-on: ${{ matrix.os }}\n', self.validate)
        self.assertIn("python-version: '3.9'\n", self.validate)
        self.assertIn('timeout-minutes: 15\n', self.validate)

    def test_validate_commands_contract(self):
        self.assertIn('- run: python3 tools/check-framework\n', self.validate)
        self.assertIn('- run: python3 -m unittest discover -s tests -v\n', self.validate)
        self.assertIn("PYTHONDONTWRITEBYTECODE: '1'\n", self.validate)

    def test_release_triggers_permissions_and_concurrency(self):
        self.assertIn("cron: '0 2 * * 1'\n", self.release)
        self.assertIn('workflow_dispatch:\n    inputs:\n      bump:\n', self.release)
        self.assertIn('options: [patch, minor, major]\n', self.release)
        self.assertIn('default: patch\n', self.release)
        self.assertIn('permissions:\n  contents: write\n', self.release)
        self.assertIn('group: framework-release\n', self.release)
        self.assertIn('cancel-in-progress: false\n', self.release)

    def test_release_runner_checkout_and_python_contract(self):
        self.assertIn('runs-on: ubuntu-latest\n', self.release)
        self.assertIn('timeout-minutes: 20\n', self.release)
        self.assertIn('fetch-depth: 0\n', self.release)
        self.assertIn('persist-credentials: true\n', self.release)
        self.assertIn("python-version: '3.9'\n", self.release)

    def test_release_validates_before_preparing_and_publishing(self):
        self.assertIn(
            'run: |\n'
            '          python3 tools/check-framework\n'
            '          PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q\n',
            self.release,
        )
        validate = self.release.index('- name: Validate before publishing\n')
        prepare = self.release.index('- name: Prepare version, changelog, and manifest\n')
        publish = self.release.index('- name: Tag and publish the GitHub release\n')
        self.assertLess(validate, prepare)
        self.assertLess(prepare, publish)

    def test_release_prepare_status_and_bump_contract(self):
        self.assertIn(
            "BUMP: ${{ github.event_name == 'workflow_dispatch' && inputs.bump || 'patch' }}\n",
            self.release,
        )
        self.assertIn('python3 tools/prepare-release --bump "$BUMP"', self.release)
        self.assertIn('if meta["status"] not in ("READY", "SKIP"):\n', self.release)
        self.assertIn('fh.write("status=%s\\n" % meta["status"])\n', self.release)
        self.assertIn('fh.write("version=%s\\n" % meta.get("version", ""))\n', self.release)
        self.assertIn('fh.write("tag=%s\\n" % meta.get("tag", ""))\n', self.release)

    def test_release_publish_condition_and_commands_contract(self):
        self.assertIn("if: steps.prep.outputs.status == 'READY'\n", self.release)
        self.assertIn('GH_TOKEN: ${{ github.token }}\n', self.release)
        for command in (
            'git config user.name "github-actions[bot]"',
            'git config user.email "41898282+github-actions[bot]@users.noreply.github.com"',
            'git add CHANGELOG.md framework-manifest.json',
            'git commit -m "release: ${TAG}"',
            'git tag "${TAG}"',
            'git push origin HEAD:main',
            'git push origin "${TAG}"',
            'gh release create "${TAG}" --title "${TAG}" --notes-file "$RUNNER_TEMP/notes.md"',
        ):
            with self.subTest(command=command):
                self.assertIn(command, self.release)


if __name__ == '__main__':
    unittest.main()
