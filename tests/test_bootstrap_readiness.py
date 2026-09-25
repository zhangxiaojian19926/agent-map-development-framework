import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from test_bootstrap_config import invoke


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class ReadinessTests(unittest.TestCase):
    def test_doctor_is_readonly_and_does_not_claim_agent_success(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            invoke('init', '--target', root, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            before = snapshot(root)
            result = invoke('doctor', '--target', root)
            self.assertEqual(result.returncode, 5, result.stdout)
            self.assertEqual(json.loads(result.stdout)['agent']['status'], 'WAITING_AGENT')
            self.assertEqual(snapshot(root), before)

    def test_deleted_index_is_not_reported_ready_from_cache(self):
        from framework_core.config import digest
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'framework-project.json').write_text(json.dumps({'project_id': 'demo', 'agent': 'manual', 'index': True}))
            (root / 'a.py').write_text('def a(): pass')
            sha = hashlib.sha256((root / 'a.py').read_bytes()).hexdigest()
            sources = {'a.py': sha}
            catalog = {'modules': {'a': {'path': '.', 'sources': sources}},
                       'indexes': {'i': {'root': '.', 'sources': sources}}}
            (root / 'module-catalog.generated.json').write_text(json.dumps(catalog))
            (root / '.framework/local-state').mkdir(parents=True)
            (root / '.framework/local-state/indexes.json').write_text(json.dumps({'i': {'status': 'READY', 'verified': True, 'source_digest': digest(sources)}}))
            report = json.loads(invoke('doctor', '--target', root).stdout)
            self.assertNotEqual(report['indexes']['i'], 'READY')

    def test_missing_installed_framework_blocks_scaffold(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            invoke('init', '--target', root, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            (root / '.agent-framework/tools/framework').unlink()
            report = json.loads(invoke('doctor', '--target', root).stdout)
            self.assertEqual(report['scaffold'], 'BLOCKED')
