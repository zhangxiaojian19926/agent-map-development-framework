"""Initialization is a verified handoff, not the existence of a skeleton."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_bootstrap_config import invoke
from test_project_docs import dossier_fixture, PROJECT_FIELDS
from framework_core.analysis_batches import begin_analysis, read_batch, accept_batch, finalize_analysis
from framework_core.config import encoded
from framework_core.project_docs import publish_project_docs
from framework_core.storage import fingerprint


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()/'project'
        self.grants = {'write', 'agent'}

    def prepare(self):
        result = invoke('prepare', '--target', self.root, '--project-id', 'demo', '--yes', '--allow', 'write')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def report(self):
        return json.loads(invoke('doctor', '--target', self.root).stdout)

    def complete_existing(self):
        for mid in ('api', 'client', 'store'):
            path = self.root/mid
            path.mkdir(parents=True)
            (path/'framework-module.json').write_text(encoded({'id': mid}))
            (path/'code.py').write_text('def handle(): return 1\n')
        self.prepare()
        catalog = json.loads((self.root/'module-catalog.generated.json').read_text())
        session = begin_analysis(self.root, catalog, self.grants)
        sid = session['session_id']
        for batch in session['batches']:
            packet = read_batch(self.root, sid, batch['batch_id'], self.grants)
            accept_batch(self.root, sid, batch['batch_id'], {'summary': 'Contains handle', 'uncertainties': [],
                'slice_ids': [s['slice_id'] for s in packet['slices']]}, self.grants)
        result = {'module_summaries': [{'id': m, 'summary': 'Exports handle'} for m in catalog['modules']],
                  'relationships': [], 'uncertainties': ['No static cross-module connection proved']}
        finalize_analysis(self.root, sid, result, self.grants)
        publish_project_docs(self.root, catalog, dossier_fixture(self.root, catalog), self.grants)
        return catalog

    def test_prepare_alone_needs_documentation_and_design_handoff(self):
        self.prepare()
        report = self.report()
        self.assertEqual(report['onboarding'], 'PREPARED')
        self.assertEqual(report.get('initialization'), 'PARTIAL')
        self.assertEqual(report['handoff']['status'], 'NEEDS_DESIGN_APPROVAL')

    def test_complete_requires_current_docs_coverage_and_saved_handoff(self):
        self.complete_existing()
        report = self.report()
        self.assertEqual(report.get('initialization'), 'COMPLETE')
        self.assertEqual(report['runtime'], 'NOT_RUN')
        self.assertEqual(report['handoff']['status'], 'READY_FOR_PLANNING')
        handoff = json.loads((self.root/'.framework/local-state/handoff.json').read_text())
        self.assertEqual(set(handoff['modules']), {'api', 'client', 'store'})
        path = self.root/'docs/project/modules/api.md'
        path.write_text(path.read_text()+'\nUser addition\n')
        self.assertEqual(self.report()['documentation']['status'], 'STALE')
        self.assertNotEqual(self.report()['initialization'], 'COMPLETE')

    def test_added_or_missing_module_invalidates_completion_without_deleting_docs(self):
        self.complete_existing()
        old = (self.root/'docs/project/modules/api.md').read_bytes()
        candidate = self.root/'fourth'
        candidate.mkdir()
        (candidate/'framework-module.json').write_text(encoded({'id': 'fourth'}))
        (candidate/'code.py').write_text('def handle(): return 4\n')
        self.assertNotEqual(self.report().get('initialization'), 'COMPLETE')
        result = invoke('module', 'add', '--target', self.root, '--id', 'fourth', '--path', 'fourth', '--yes', '--allow', 'write')
        self.assertEqual(result.returncode, 5, result.stdout)
        self.assertNotEqual(self.report()['initialization'], 'COMPLETE')
        (self.root/'api').rename(self.root.parent/'moved-api')
        self.assertNotEqual(self.report()['initialization'], 'COMPLETE')
        self.assertEqual((self.root/'docs/project/modules/api.md').read_bytes(), old)

    def test_missing_persisted_handoff_cannot_report_complete(self):
        self.complete_existing()
        path = self.root/'.framework/local-state/handoff.json'
        path.rename(self.root.parent/'saved-handoff.json')
        report = self.report()
        self.assertEqual(report['initialization'], 'PARTIAL')
        self.assertEqual(report['handoff']['status'], 'MISSING')

    def test_new_design_approval_is_explicit_and_does_not_create_code_or_git(self):
        self.prepare()
        brief = self.root/'docs/project/design-input.md'
        brief.write_text('Task manager: CLI calls domain; domain calls storage. No deployment.\n')
        ref = {'path': 'docs/project/design-input.md', 'anchor': 'Task manager', 'sha256': fingerprint(brief)}
        project = {k: {'value': 'Task manager '+k+'; CLI/domain/storage design, not implemented', 'status': 'KNOWN',
                       'provenance': 'DECLARED', 'evidence': [ref]} for k in PROJECT_FIELDS}
        dossier = {'project': project, 'modules': [], 'blockers': [], 'rule_conflicts': [], 'planning_refs': [ref]}
        payload = self.root.parent/'dossier.json'
        payload.write_text(encoded(dossier))
        args = ('accept-docs', '--target', self.root, '--result', payload, '--allow', 'write', '--allow', 'agent')
        result = invoke(*args)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.report().get('initialization'), 'PARTIAL')
        approved = invoke(*args, '--approve', 'design='+ref['sha256'])
        self.assertEqual(approved.returncode, 0, approved.stdout)
        self.assertEqual(self.report()['initialization'], 'COMPLETE')
        self.assertEqual(self.report()['coverage']['status'], 'NOT_APPLICABLE')
        self.assertFalse((self.root/'.git').exists())
        self.assertFalse((self.root/'modules').exists())
