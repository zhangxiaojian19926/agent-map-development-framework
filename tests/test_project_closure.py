"""A project that adopted the shell must be able to find its own unfinished work."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_tool():
    loader = importlib.machinery.SourceFileLoader('checkp', str(ROOT / 'tools/check-project'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def make_change(root, name, done, todo, capability=None, synced=False, skip_specs=False):
    change = root / 'openspec' / 'changes' / name
    change.mkdir(parents=True)
    lines = ['## 1. Work', '']
    for index in range(done):
        lines.append('- [x] task %d' % (index + 1))
    for index in range(todo):
        lines.append('- [ ] task %d' % (index + 1))
    (change / 'tasks.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if capability:
        spec = change / 'specs' / capability / 'spec.md'
        write(spec, '## ADDED Requirements\n\n### Requirement: %s\n' % capability)
        if synced:
            write(root / 'openspec' / 'specs' / capability / 'spec.md', '## Requirements\n')
    if skip_specs:
        (change / '.openspec.yaml').write_text('schema: spec-driven\nskip_specs: true\n', encoding='utf-8')


class ProjectClosureTests(unittest.TestCase):
    def setUp(self):
        self.tool = load_tool()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_an_unsynced_change_is_reported(self):
        make_change(self.root, 'alpha', 2, 0, capability='alpha-cap')
        findings = self.tool.collect(self.root)['outstanding_changes']
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['change'], 'alpha')
        self.assertIn('not synced', findings[0]['problem'])

    def test_an_unarchived_change_is_reported(self):
        make_change(self.root, 'beta', 3, 0, capability='beta-cap', synced=True)
        from test_check_changes import install_receipt
        install_receipt(self.root, 'beta', 'beta-cap')
        findings = self.tool.collect(self.root)['outstanding_changes']
        self.assertEqual(len(findings), 1)
        self.assertIn('archived', findings[0]['problem'])

    def test_a_missing_knowledge_receipt_is_the_same_debt_in_both_modes(self):
        make_change(self.root, 'kappa', 2, 0, capability='kappa-cap', synced=True)
        script = ROOT / 'tools' / 'check-project'
        default = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--json'],
                                 capture_output=True, text=True)
        strict = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--strict', '--json'],
                                capture_output=True, text=True)
        self.assertEqual(default.returncode, 0)
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(json.loads(default.stdout)['outstanding_changes'],
                         json.loads(strict.stdout)['outstanding_changes'])
        self.assertIn('NOT_CONFIGURED', json.loads(strict.stdout)['outstanding_changes'][0]['detail'])
        self.assertFalse((self.root / 'knowledge').exists())

    def test_an_unfinished_change_is_not_debt(self):
        make_change(self.root, 'gamma', 1, 2, capability='gamma-cap')
        self.assertEqual(self.tool.collect(self.root)['outstanding_changes'], [])

    def test_stale_map_evidence_is_reported_with_its_reason(self):
        source = self.root / 'app.py'
        write(source, 'def greet():\n    return "hello"\n')
        anchor = 'def greet():'
        map_path = self.root / 'docs' / 'project' / 'relationships.generated.json'
        write(map_path, json.dumps({
            'schema_version': 1,
            'relationships': [{
                'id': 'e1', 'from': 'root', 'to': 'root', 'kind': 'call',
                'provenance': 'STATIC_SUPPORTED',
                'evidence': [{'path': 'app.py', 'sha256': '0' * 64, 'anchor': anchor}],
            }],
            'module_summaries': [{'id': 'root', 'summary': 'x'}],
        }, ensure_ascii=False))
        problems = self.tool.collect(self.root)['map_evidence_problems']
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0]['kind'], 'SOURCE_DRIFT')

    def test_a_lost_anchor_is_reported_apart_from_drift(self):
        source = self.root / 'app.py'
        write(source, 'def greet():\n    return "hello"\n')
        digest = __import__('hashlib').sha256(source.read_bytes()).hexdigest()
        map_path = self.root / 'docs' / 'project' / 'relationships.generated.json'
        write(map_path, json.dumps({
            'schema_version': 1,
            'relationships': [{
                'id': 'e1', 'from': 'root', 'to': 'root', 'kind': 'call',
                'provenance': 'STATIC_SUPPORTED',
                'evidence': [{'path': 'app.py', 'sha256': digest, 'anchor': 'a line that is gone'}],
            }],
            'module_summaries': [{'id': 'root', 'summary': 'x'}],
        }, ensure_ascii=False))
        problems = self.tool.collect(self.root)['map_evidence_problems']
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0]['kind'], 'LOST_ANCHOR')

    def test_the_check_never_writes_to_the_project(self):
        make_change(self.root, 'delta', 2, 0, capability='delta-cap')
        before = {p: p.read_bytes() for p in sorted(self.root.rglob('*')) if p.is_file()}
        self.tool.collect(self.root)
        after = {p: p.read_bytes() for p in sorted(self.root.rglob('*')) if p.is_file()}
        self.assertEqual(before, after)

    def test_the_default_run_reports_without_failing_and_strict_fails(self):
        make_change(self.root, 'epsilon', 2, 0, capability='epsilon-cap')
        script = ROOT / 'tools' / 'check-project'
        default = subprocess.run([sys.executable, str(script), '--root', str(self.root)],
                                 capture_output=True, text=True)
        self.assertEqual(default.returncode, 0)
        self.assertIn('DEBT', default.stdout)
        strict = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--strict'],
                                capture_output=True, text=True)
        self.assertEqual(strict.returncode, 1)
        self.assertIn('DEBT', strict.stdout)

    def test_both_modes_report_the_same_debt(self):
        make_change(self.root, 'zeta', 2, 0, capability='zeta-cap')
        script = ROOT / 'tools' / 'check-project'
        default = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--json'],
                                 capture_output=True, text=True)
        strict = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--strict', '--json'],
                                capture_output=True, text=True)
        self.assertEqual(json.loads(default.stdout)['outstanding_changes'],
                         json.loads(strict.stdout)['outstanding_changes'])

    def test_the_public_shell_and_the_project_reach_the_same_verdict(self):
        make_change(self.root, 'eta', 2, 0, capability='eta-cap')
        from framework_core import closure
        shell = json.loads(subprocess.run(
            [sys.executable, str(ROOT / 'tools/check-changes'), '--root', str(self.root), '--json'],
            capture_output=True, text=True).stdout)
        self.assertEqual(shell['outstanding'], closure.outstanding_changes(self.root))

    def test_the_check_and_the_template_reach_a_project(self):
        from test_bootstrap_config import invoke
        existing = self.root / '.github' / 'workflows' / 'ci.yml'
        write(existing, 'name: their own pipeline\n')
        before = existing.read_bytes()
        result = invoke('prepare', '--target', str(self.root), '--project-id', 'demo',
                        '--agent', 'current', '--yes', '--allow', 'write')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        package = self.root / '.agent-framework'
        self.assertTrue((package / 'tools' / 'check-project').is_file())
        self.assertTrue((package / 'templates' / 'project-ci.yml').is_file())
        # Their own pipeline is not ours to touch.
        self.assertEqual(existing.read_bytes(), before)
        self.assertFalse((package / '.github').exists())


if __name__ == '__main__':
    unittest.main()
