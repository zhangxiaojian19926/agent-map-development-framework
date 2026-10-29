import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from test_bootstrap_config import invoke
from test_project_docs import PROJECT_FIELDS, dossier_fixture
from framework_core.analysis_batches import accept_batch, begin_analysis, finalize_analysis, read_batch
from framework_core.config import encoded
from framework_core.project_docs import publish_project_docs
from framework_core.storage import fingerprint


SECTIONS = ('一、结果', '二、当前流程产物', '三、条件性未生成',
            '四、未执行与限制', '五、提交与本机状态', '六、下一步')


def prepare(root):
    result = invoke('prepare', '--target', root, '--project-id', 'demo', '--yes', '--allow', 'write')
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def complete_new(root):
    prepare(root)
    brief = root / 'docs/project/design-input.md'
    brief.write_text('Task manager: CLI calls domain; domain calls storage. No deployment.\n')
    ref = {'path': 'docs/project/design-input.md', 'anchor': 'Task manager', 'sha256': fingerprint(brief)}
    project = {key: {'value': 'Task manager ' + key + '; declared design', 'status': 'KNOWN',
                     'provenance': 'DECLARED', 'evidence': [ref]} for key in PROJECT_FIELDS}
    dossier = {'project': project, 'modules': [], 'blockers': [], 'rule_conflicts': [], 'planning_refs': [ref]}
    payload = root.parent / 'new-dossier.json'
    payload.write_text(encoded(dossier))
    result = invoke('accept-docs', '--target', root, '--result', payload,
                    '--allow', 'write', '--allow', 'agent', '--approve', 'design=' + ref['sha256'])
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def complete_existing(root):
    for module_id in ('api', 'client'):
        path = root / module_id
        path.mkdir(parents=True)
        (path / 'framework-module.json').write_text(encoded({'id': module_id}))
        (path / 'code.py').write_text('def handle(): return 1\n')
    prepare(root)
    catalog = json.loads((root / 'module-catalog.generated.json').read_text())
    session = begin_analysis(root, catalog, {'write', 'agent'})
    session_id = session['session_id']
    for batch in session['batches']:
        packet = read_batch(root, session_id, batch['batch_id'], {'write', 'agent'})
        accept_batch(root, session_id, batch['batch_id'], {
            'summary': 'Contains handle', 'uncertainties': [],
            'slice_ids': [item['slice_id'] for item in packet['slices']]}, {'write', 'agent'})
    result = {'module_summaries': [{'id': item, 'summary': 'Exports handle'} for item in catalog['modules']],
              'relationships': [], 'uncertainties': ['No static cross-module connection proved']}
    finalize_analysis(root, session_id, result, {'write', 'agent'})
    publish_project_docs(root, catalog, dossier_fixture(root, catalog), {'write', 'agent'})


def request_for(path, request_id='case'):
    return {'schema': 'reverse-request/v1', 'id': request_id, 'goal': 'inspect target',
            'target': {'kind': 'file', 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
            'intent': 'static', 'acceptance': ['observed'],
            'observations': [{'id': 'observe', 'question': 'inspect', 'action': 'static'}],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {'capabilities': [], 'constraints': [], 'inferences': []}}


def tree_hash(root):
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / 'project'

    def assert_sections(self, text):
        for section in SECTIONS:
            self.assertIn(section, text)
        self.assertNotIn('本次新建', text)
        self.assertEqual(text.count('六、下一步'), 1)

    def test_default_json_summary_exit_and_unsupported_scope(self):
        complete_new(self.root)
        plain = invoke('doctor', '--target', self.root)
        self.assertEqual(plain.returncode, 0, plain.stdout)
        report = json.loads(plain.stdout)
        self.assertEqual(report['initialization'], 'COMPLETE')
        self.assertNotIn('summary', report)
        summary = invoke('doctor', '--target', self.root, '--summary')
        self.assertEqual(summary.returncode, plain.returncode, summary.stdout)
        self.assert_sections(summary.stdout)
        unsupported = invoke('reverse', '--target', self.root, '--scope', 'missing.json', '--summary')
        self.assertEqual(unsupported.returncode, 2)
        self.assertIn('SUMMARY_NOT_SUPPORTED', unsupported.stdout)

    def test_new_complete_and_existing_source_artifacts(self):
        complete_new(self.root)
        summary = invoke('doctor', '--target', self.root, '--summary').stdout
        self.assertIn('initialization=COMPLETE', summary)
        self.assertIn('runtime=NOT_RUN', summary)
        self.assertIn('knowledge/project/', summary)
        self.assertIn('module-catalog.generated.json', summary)
        self.assertIn('首个', summary)
        missing = summary.split('三、条件性未生成', 1)[1].split('四、未执行与限制', 1)[0]
        self.assertNotIn('docs/project/design-input.md', missing)

        other = self.root.parent / 'existing'
        complete_existing(other)
        existing = invoke('doctor', '--target', other, '--summary')
        self.assertEqual(existing.returncode, 0, existing.stdout)
        self.assertIn('docs/project/module-map.generated.md', existing.stdout)
        self.assertIn('docs/project/modules/api.md', existing.stdout)
        self.assertIn('静态地图不证明业务运行成功', existing.stdout)
        existing_missing = existing.stdout.split('三、条件性未生成', 1)[1].split('四、未执行与限制', 1)[0]
        self.assertNotIn('docs/project/module-map.generated.md', existing_missing)

    def test_partial_next_step_and_repeated_doctor_are_read_only(self):
        prepare(self.root)
        before = tree_hash(self.root)
        first = invoke('doctor', '--target', self.root, '--summary')
        second = invoke('doctor', '--target', self.root, '--summary')
        self.assertEqual(first.returncode, 5)
        self.assertEqual(second.returncode, 5)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(tree_hash(self.root), before)
        self.assert_sections(first.stdout)
        self.assertIn('initialization=PARTIAL', first.stdout)
        self.assertIn('NEEDS_DESIGN_APPROVAL', first.stdout)
        self.assertIn('确认 docs/project/design-input.md', first.stdout)

    def test_reverse_pending_default_json_and_recorded_secret_boundary(self):
        self.root.mkdir()
        target = self.root / 'page.html'
        target.write_text('<html><script src="app.js"></script></html>')
        request_path = self.root / 'request.json'
        request_path.write_text(json.dumps(request_for(target)))
        pending = invoke('reverse', '--target', self.root, '--request', request_path,
                         '--allow', 'write', '--allow', 'reverse', '--summary')
        self.assertEqual(pending.returncode, 5, pending.stdout)
        self.assert_sections(pending.stdout)
        self.assertIn('PLAN_APPROVAL_REQUIRED', pending.stdout)
        self.assertIn('批准当前计划', pending.stdout)
        self.assertIn('行为契约：未生成', pending.stdout)

        pending_json = invoke('reverse', '--target', self.root, '--request', request_path,
                              '--allow', 'write', '--allow', 'reverse')
        self.assertEqual(pending_json.returncode, 5)
        plan_hash = json.loads(pending_json.stdout)['plan_sha256']
        approved = invoke('reverse', '--target', self.root, '--request', request_path,
                          '--allow', 'write', '--allow', 'reverse', '--approve', 'toolchain=' + plan_hash)
        self.assertEqual(approved.returncode, 0, approved.stdout)
        self.assertEqual(json.loads(approved.stdout)['observation_status'], 'RECORDED')
        raw = self.root / '.framework/local-state/reverse/auto/case/raw/observe.txt'
        secret = 'Cookie=completion-summary-secret'
        raw.write_text(secret)
        public = self.root / 'docs/project/reverse/case.md'
        public_before = public.read_bytes()
        summary = invoke('reverse', '--target', self.root, '--request', request_path,
                         '--allow', 'write', '--allow', 'reverse', '--approve', 'toolchain=' + plan_hash,
                         '--summary')
        self.assertEqual(summary.returncode, 0, summary.stdout)
        self.assert_sections(summary.stdout)
        self.assertIn('observation_status=RECORDED', summary.stdout)
        self.assertIn('runtime_validation=NOT_RUN', summary.stdout)
        self.assertIn('behavior-contract.json', summary.stdout)
        self.assertNotIn(secret, summary.stdout)
        self.assertEqual(public.read_bytes(), public_before)

    def test_reverse_dynamic_missing_grant_and_provider(self):
        self.root.mkdir()
        target = self.root / 'page.html'
        target.write_text('<html></html>')
        request = request_for(target, 'dynamic')
        request['intent'] = 'dynamic'
        request['observations'] += [
            {'id': 'dom', 'question': 'dom', 'action': 'browser', 'operation': 'observe-dom'},
            {'id': 'har', 'question': 'network', 'action': 'network', 'operation': 'capture-har'}]
        request_path = self.root / 'dynamic.json'
        request_path.write_text(json.dumps(request))
        pending = invoke('reverse', '--target', self.root, '--request', request_path,
                         '--allow', 'write', '--allow', 'reverse')
        plan_hash = json.loads(pending.stdout)['plan_sha256']
        denied = invoke('reverse', '--target', self.root, '--request', request_path,
                        '--allow', 'write', '--allow', 'reverse', '--approve', 'toolchain=' + plan_hash,
                        '--summary')
        self.assertEqual(denied.returncode, 5, denied.stdout)
        self.assertIn('dom：NOT_AUTHORIZED', denied.stdout)
        self.assertIn('har：NOT_AUTHORIZED', denied.stdout)
        self.assertIn('行为契约：未生成', denied.stdout)

        missing = invoke('reverse', '--target', self.root, '--request', request_path,
                         '--allow', 'write', '--allow', 'reverse', '--allow', 'browser-observe',
                         '--allow', 'network-capture', '--approve', 'toolchain=' + plan_hash, '--summary')
        self.assertEqual(missing.returncode, 5, missing.stdout)
        self.assertIn('dom：PROVIDER_MISSING', missing.stdout)
        self.assertIn('har：PROVIDER_MISSING', missing.stdout)
        self.assertIn('接入真实浏览器 provider', missing.stdout)

    def test_reverse_tool_failure_selects_toolchain_recovery(self):
        from framework_core.completion_summary import render_reverse

        self.root.mkdir()
        request = {'id': 'case', 'observations': [], 'evidence': {'raw': 'discard'}}
        for status in ('INSTALL_FAILED', 'HEALTH_FAILED'):
            with self.subTest(status=status):
                report = {'status': status, 'observation_status': 'NOT_RUN',
                          'runtime_validation': 'NOT_RUN', 'observations': [],
                          'actions': [{'tool_id': 'demo-tool', 'action': 'INSTALL',
                                       'status': 'HASH_MISMATCH'}]}
                summary = render_reverse(self.root, request, report)
                next_step = summary.split('六、下一步', 1)[1]
                self.assertIn('处理当前工具或平台缺口', next_step)
                self.assertNotIn('处理未完成的观察项', next_step)
                self.assertIn('demo-tool', summary)
                self.assertIn('HASH_MISMATCH', summary)


if __name__ == '__main__':
    unittest.main()
