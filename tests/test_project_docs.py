"""Complete module instructions must not erase the user's existing rules."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from framework_core.config import encoded
from framework_core.modules import catalog_update, discover
from framework_core.storage import atomic, fingerprint

PROJECT_FIELDS = ('goal', 'non_goals', 'architecture', 'interfaces', 'integration_order', 'constraints', 'resources')
MODULE_FIELDS = ('purpose', 'non_responsibilities', 'entrypoints', 'inputs', 'outputs', 'dependencies', 'internal_roles', 'commands', 'limitations', 'knowledge')


def dossier_fixture(root, catalog):
    def fact(value, path):
        return {'value': value, 'provenance': 'STATIC_SUPPORTED', 'status': 'KNOWN',
                'evidence': [{'path': path, 'anchor': 'def handle()', 'sha256': fingerprint(root/path)}]}
    path = next(iter(next(iter(catalog['modules'].values()))['sources']))
    project = {key: fact('Project '+key+' documented from fixtures', path) for key in PROJECT_FIELDS}
    modules = []
    for mid, module in catalog['modules'].items():
        path = next(iter(module['sources']))
        item = {key: fact(mid+' '+key+' uses handle', path) for key in MODULE_FIELDS}
        item['id'] = mid
        item['commands'] = fact([{'command': 'python3 -m unittest discover', 'cwd': module['path'],
                                 'prerequisites': 'Python 3; verify test availability', 'execution': 'NOT_RUN'}], path)
        item['commands']['status'] = 'NOT_VERIFIED'
        item['knowledge'] = {'value': 'No registered module knowledge base', 'status': 'NOT_CONFIGURED',
                             'provenance': 'DECLARED', 'evidence': [], 'reason': 'No explicit KB registration'}
        modules.append(item)
    return {'project': project, 'modules': modules, 'blockers': [], 'rule_conflicts': [], 'planning_refs': []}


class ProjectDocsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.project_docs'), 'Complete project docs missing')
        self.api = importlib.import_module('framework_core.project_docs')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        for name in ('human', 'readonly', 'writable'):
            (self.root/name).mkdir()
            (self.root/name/'code.py').write_text('def handle(): return 1\n')
        declarations = [{'id': n, 'path': n, 'writable': n != 'readonly'} for n in ('human', 'readonly', 'writable')]
        self.catalog = catalog_update({}, declarations, discover(self.root, [d['path'] for d in declarations]))
        atomic(self.root, 'module-catalog.generated.json', encoded(self.catalog))
        atomic(self.root, 'framework-project.json', encoded({'project_id': 'demo', 'modules': declarations}))
        self.original = b'# Human rules\r\nDo not run hardware.\r\n'
        (self.root/'human/AGENTS.md').write_bytes(self.original)
        self.dossier = dossier_fixture(self.root, self.catalog)
        self.grants = {'write', 'agent'}

    def test_incomplete_placeholder_and_stale_evidence_rejected(self):
        self.assertIn('INCOMPLETE_DOCUMENTATION', self.api.validate_project_docs(self.root, self.catalog, {'project': {}, 'modules': []}))
        for key in PROJECT_FIELDS:
            invalid = copy.deepcopy(self.dossier)
            invalid['project'][key]['value'] = 'TODO'
            self.assertTrue(self.api.validate_project_docs(self.root, self.catalog, invalid))
        invalid = copy.deepcopy(self.dossier)
        invalid['modules'][0]['purpose']['evidence'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'INVALID_EVIDENCE'):
            self.api.publish_project_docs(self.root, self.catalog, invalid, self.grants)
        self.assertEqual((self.root/'human/AGENTS.md').read_bytes(), self.original)

    def test_full_module_docs_preserve_human_and_readonly_files(self):
        report = self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        self.assertEqual(report['status'], 'COMPLETE')
        self.assertTrue((self.root/'human/AGENTS.md').read_bytes().startswith(self.original))
        self.assertFalse((self.root/'readonly/AGENTS.md').exists())
        text = (self.root/'writable/AGENTS.md').read_text()
        self.assertIn('writable purpose uses handle', text)
        self.assertIn('python3 -m unittest discover', text)
        self.assertIn('NOT_RUN', text)
        self.assertIn('readonly purpose uses handle', (self.root/'docs/project/modules/readonly.md').read_text())
        before = (self.root/'human/AGENTS.md').read_bytes()
        self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        self.assertEqual((self.root/'human/AGENTS.md').read_bytes(), before)

    def test_edited_generated_block_and_semantic_conflict_are_not_overwritten(self):
        self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        path = self.root/'writable/AGENTS.md'
        changed = path.read_bytes().replace(b'writable purpose', b'User changed purpose')
        path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, 'RULE_CONFLICT'):
            self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        self.assertEqual(path.read_bytes(), changed)
        self.dossier['rule_conflicts'] = [{'module_id': 'writable', 'description': 'User instruction differs; resolve before implementation'}]
        report = self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertEqual(path.read_bytes(), changed)
        self.assertIn('User instruction differs', (self.root/'docs/project/handoff.md').read_text())

    def test_no_permission_writes_nothing_and_unknown_module_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.api.publish_project_docs(self.root, self.catalog, self.dossier, set())
        self.assertFalse((self.root/'docs').exists())
        self.dossier['modules'][0]['id'] = 'not-selected'
        self.assertTrue(self.api.validate_project_docs(self.root, self.catalog, self.dossier))

    def test_map_refresh_does_not_replace_complete_module_docs_with_summary(self):
        from framework_core.maps import map_outputs
        self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        result = {'module_summaries': [{'id': m, 'summary': 'Short summary'} for m in self.catalog['modules']],
                  'relationships': [], 'uncertainties': []}
        outputs = map_outputs(self.root, self.catalog, result)
        self.assertNotIn('docs/project/modules/human.md', outputs)

    def test_cli_publishes_dossier_without_running_commands(self):
        from test_bootstrap_config import invoke
        path = self.root/'dossier.json'
        path.write_text(encoded(self.dossier))
        result = invoke('accept-docs', '--target', self.root, '--result', path, '--allow', 'write', '--allow', 'agent')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'COMPLETE')

    def test_generated_output_cannot_also_be_planning_evidence(self):
        path = self.root/'docs/project/overview.md'
        atomic(self.root, 'docs/project/overview.md', 'Existing approved intent\n')
        ref = {'path': 'docs/project/overview.md', 'anchor': 'Existing approved intent', 'sha256': fingerprint(path)}
        self.dossier['planning_refs'] = [ref]
        self.dossier['project']['goal'] = {'value': 'Existing approved intent', 'provenance': 'DECLARED',
                                          'status': 'KNOWN', 'evidence': [ref]}
        with self.assertRaisesRegex(ValueError, 'SELF_REFERENTIAL_EVIDENCE'):
            self.api.publish_project_docs(self.root, self.catalog, self.dossier, self.grants)
        self.assertEqual(path.read_text(), 'Existing approved intent\n')

    def test_optional_evidence_and_ids_are_validated_without_crashing(self):
        for evidence in (['malformed'], {}, [{'path': 'missing', 'anchor': 'x', 'sha256': '0'*64}]):
            invalid = copy.deepcopy(self.dossier)
            invalid['modules'][0]['knowledge']['evidence'] = evidence
            self.assertTrue(self.api.validate_project_docs(self.root, self.catalog, invalid))
        for key in ('modules', 'rule_conflicts'):
            invalid = copy.deepcopy(self.dossier)
            if key == 'modules':
                invalid['modules'][0]['id'] = []
            else:
                invalid[key] = [{'module_id': [], 'description': 'Invalid ID'}]
            self.assertTrue(self.api.validate_project_docs(self.root, self.catalog, invalid))
