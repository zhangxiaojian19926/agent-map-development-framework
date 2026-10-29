import contextlib
import copy
import importlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

from test_product_design_handoff import HandoffCase, digest, write_json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class ParityCase(HandoffCase):
    def setUp(self):
        super().setUp()
        self.change_root = self.root / 'openspec/changes/demo'
        self.spec_one = self.change_root / 'specs/core/spec.md'
        self.spec_two = self.change_root / 'specs/extra/spec.md'
        self.tasks_path = self.change_root / 'tasks.md'
        self.spec_one.parent.mkdir(parents=True, exist_ok=True)
        self.spec_two.parent.mkdir(parents=True, exist_ok=True)
        self.spec_one.write_text(
            '## ADDED Requirements\n\n'
            '### Requirement: 核心流程\n\n#### Scenario: 正常完成\n- **WHEN** 输入有效\n- **THEN** 完成\n\n'
            '### Requirement: 推断实体\n\n#### Scenario: 实体边界\n- **WHEN** 数据缺失\n- **THEN** 保留边界\n')
        self.spec_two.write_text(
            '## ADDED Requirements\n\n### Requirement: 声明目标\n\n'
            '#### Scenario: 新目标\n- **WHEN** 设计获批\n- **THEN** 跟踪目标\n')
        self.tasks_path.write_text(
            '## 1. 核心\n\n- [x] 1.1 核心实现\n- [ ] 1.2 后续增强\n\n'
            '## 2. 数据\n\n- [x] 2.1 实体实现\n')
        self.verification = self.root / 'docs/verification/demo'
        self.verification.mkdir(parents=True)
        self.artifact = self.verification / 'core-test.txt'
        self.artifact.write_text('controlled host test output\n')
        self.evidence_path = self.verification / 'evidence.json'
        self.evidence_data = {
            'schema': 'verification-evidence/v1', 'change': 'demo',
            'records': [{
                'id': 'R01', 'requirement': '核心流程', 'scenario': '正常完成',
                'task': '1.1', 'test': 'host contract test', 'environment': 'Host',
                'result': 'PASS', 'category': 'FUNCTION',
                'artifact': {'path': 'docs/verification/demo/core-test.txt', 'sha256': digest(self.artifact)},
                'reason': None,
            }],
            'findings': [],
        }
        write_json(self.evidence_path, self.evidence_data)
        self.request_path = self.root / 'parity-request.json'
        self.request = {
            'schema': 'feature-parity-request/v1', 'id': 'case', 'change': 'demo',
            'product_collections': ['flows', 'entities'],
            'specs': [
                {'path': 'openspec/changes/demo/specs/core/spec.md', 'sha256': digest(self.spec_one)},
                {'path': 'openspec/changes/demo/specs/extra/spec.md', 'sha256': digest(self.spec_two)},
            ],
            'tasks': {'path': 'openspec/changes/demo/tasks.md', 'sha256': digest(self.tasks_path)},
            'evidence': [{'path': 'docs/verification/demo/evidence.json', 'sha256': digest(self.evidence_path)}],
            'items': [
                {'id': 'P01', 'product_id': 'F01', 'priority': 'MUST', 'requirement': '核心流程',
                 'scenarios': ['正常完成'], 'tasks': ['1.1']},
                {'id': 'P02', 'product_id': 'E01', 'priority': 'SHOULD', 'requirement': '推断实体',
                 'scenarios': ['实体边界'], 'tasks': ['2.1']},
                {'id': 'P03', 'product_id': None, 'priority': 'COULD', 'requirement': '声明目标',
                 'scenarios': ['新目标'], 'tasks': []},
            ],
            'product_exclusions': [],
            'scenario_exclusions': [],
            'severity_policy': {'S1': 'BLOCK', 'S2': 'BLOCK', 'S3': 'REPORT', 'S4': 'REPORT'},
        }
        self.save_request()
        self.module = importlib.import_module('framework_core.verified_feature_parity')
        self.report = self.root / 'docs/verification/demo-parity.md'
        self.receipt = self.root / '.framework/local-state/parity/demo.json'

    def save_request(self):
        for source in self.request['specs']:
            source['sha256'] = digest(self.root / source['path'])
        self.request['tasks']['sha256'] = digest(self.root / self.request['tasks']['path'])
        for source in self.request['evidence']:
            source['sha256'] = digest(self.root / source['path'])
        write_json(self.request_path, self.request)

    def save_evidence(self):
        write_json(self.evidence_path, self.evidence_data)
        self.save_request()

    def generate(self):
        return super().generate()

    def parity(self, dry_run=False):
        return self.module.generate(self.root, self.request_path, dry_run=dry_run)

    def item(self, result, identifier):
        return next(item for item in result['items'] if item['id'] == identifier)

    def assert_sources_unchanged(self, sources):
        for path, expected in sources.items():
            self.assertEqual(digest(path), expected)


class SourceAndTraceTests(ParityCase):
    def test_valid_chain_public_report_and_privacy(self):
        result = self.parity()
        self.assertEqual(result['status'], 'RECORDED')
        self.assertEqual(result['overall'], 'PASS')
        self.assertEqual(self.item(result, 'P01')['target_evidence'], 'OBSERVED')
        self.assertEqual(self.item(result, 'P01')['implementation'], 'IMPLEMENTED')
        self.assertEqual(self.item(result, 'P01')['verification'], 'VERIFIED')
        self.assertEqual(self.item(result, 'P02')['target_evidence'], 'INFERRED')
        self.assertEqual(self.item(result, 'P02')['verification'], 'NOT_RUN')
        self.assertEqual(self.item(result, 'P03')['target_evidence'], 'NOT_OBSERVED')
        self.assertEqual(self.item(result, 'P03')['implementation'], 'DECLARED')
        text = self.report.read_text()
        self.assert_private_text_absent(text)
        self.assertNotIn('overall_score', text)
        self.assertNotIn('completion_percentage', text)
        self.assertIn('R01', text)
        self.assertIn('PASS', text)

    def test_source_tampering_and_cross_change_evidence_preserve_old_report(self):
        self.parity()
        before_report = digest(self.report)
        before_receipt = digest(self.receipt)
        self.spec_one.write_text(self.spec_one.read_text() + '\n未经绑定的修改\n')
        with self.assertRaisesRegex(ValueError, 'PARITY_STALE'):
            self.parity()
        self.assertEqual(digest(self.report), before_report)
        self.assertEqual(digest(self.receipt), before_receipt)
        self.spec_one.write_text(self.spec_one.read_text().replace('\n未经绑定的修改\n', ''))
        self.evidence_data['change'] = 'other'
        self.save_evidence()
        with self.assertRaisesRegex(ValueError, 'PARITY_EVIDENCE'):
            self.parity()
        self.assertEqual(digest(self.report), before_report)

    def test_task_and_evidence_hash_tampering_preserve_old_report(self):
        self.parity()
        before_report = digest(self.report)
        for path in (self.tasks_path, self.evidence_path):
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(original + b'\n')
                with self.assertRaisesRegex(ValueError, 'PARITY_(STALE|EVIDENCE)'):
                    self.parity()
                self.assertEqual(digest(self.report), before_report)
                path.write_bytes(original)

    def test_missing_scenario_and_unmapped_product_target_are_gaps(self):
        self.spec_one.write_text(self.spec_one.read_text() +
            '\n### Requirement: 遗漏流程\n\n#### Scenario: 必须覆盖\n- **WHEN** 遗漏\n- **THEN** 报告差距\n')
        self.save_request()
        result = self.parity()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('MISSING_SCENARIO', {gap['code'] for gap in result['gaps']})
        self.spec_one.write_text(self.spec_one.read_text().split('\n### Requirement: 遗漏流程')[0] + '\n')
        self.request['items'] = [item for item in self.request['items'] if item['id'] != 'P02']
        self.save_request()
        result = self.parity()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('UNMAPPED_TARGET', {gap['code'] for gap in result['gaps']})

    def test_unknown_duplicate_and_invalid_exclusion_are_rejected(self):
        variants = []
        unknown = copy.deepcopy(self.request)
        unknown['items'][0]['tasks'] = ['9.9']
        variants.append(unknown)
        duplicate = copy.deepcopy(self.request)
        duplicate['items'][1]['scenarios'] = ['正常完成']
        variants.append(duplicate)
        invalid_exclusion = copy.deepcopy(self.request)
        invalid_exclusion['scenario_exclusions'] = [{
            'requirement': '核心流程', 'scenario': '正常完成', 'priority': 'MUST', 'kind': 'OUT_OF_SCOPE'}]
        variants.append(invalid_exclusion)
        for variant in variants:
            with self.subTest(variant=variant['items'][0]['tasks']):
                self.request = variant
                self.save_request()
                with self.assertRaisesRegex(ValueError, 'PARITY_INPUT'):
                    self.parity()
                self.assertFalse(self.report.exists())


class StateAndGateTests(ParityCase):
    def test_partial_tasks_and_missing_evidence_never_verify(self):
        self.request['items'][0]['tasks'] = ['1.1', '1.2']
        self.save_request()
        result = self.parity()
        self.assertEqual(self.item(result, 'P01')['implementation'], 'PARTIAL')
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.tasks_path.write_text(self.tasks_path.read_text().replace('- [x] 1.1', '- [ ] 1.1'))
        self.save_request()
        result = self.parity()
        self.assertEqual(self.item(result, 'P01')['implementation'], 'DECLARED')
        self.assertEqual(self.item(result, 'P01')['verification'], 'NOT_RUN')

    def test_pass_without_artifact_and_tampered_artifact_are_rejected(self):
        self.evidence_data['records'][0]['artifact'] = None
        self.save_evidence()
        with self.assertRaisesRegex(ValueError, 'PARITY_EVIDENCE'):
            self.parity()
        self.assertFalse(self.report.exists())
        self.evidence_data['records'][0]['artifact'] = {
            'path': 'docs/verification/demo/core-test.txt', 'sha256': digest(self.artifact)}
        self.save_evidence()
        self.artifact.write_text('changed output')
        with self.assertRaisesRegex(ValueError, 'PARITY_STALE'):
            self.parity()
        self.assertFalse(self.report.exists())

    def test_failure_not_run_infra_na_and_severity_policy(self):
        self.evidence_data['records'][0]['result'] = 'FAIL'
        self.save_evidence()
        result = self.parity()
        self.assertEqual(result['overall'], 'FAILED')
        self.assertEqual(self.item(result, 'P01')['verification'], 'FAILED')
        self.evidence_data['records'][0]['result'] = 'INFRA_ERROR'
        self.evidence_data['records'][0]['reason'] = 'RUNNER_UNAVAILABLE'
        self.evidence_data['findings'] = [{
            'id': 'X01', 'severity': 'S1', 'status': 'OPEN',
            'category': 'FUNCTION', 'evidence_id': 'R01'}]
        self.save_evidence()
        result = self.parity()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('OPEN_S1', {gap['code'] for gap in result['gaps']})
        self.request['severity_policy']['S1'] = 'REPORT'
        self.evidence_data['records'][0]['result'] = 'PASS'
        self.evidence_data['records'][0]['reason'] = None
        self.save_request()
        self.save_evidence()
        result = self.parity()
        self.assertEqual(result['overall'], 'PASS')
        self.assertIn('REPORT_S1', {gap['code'] for gap in result['gaps']})
        self.evidence_data['findings'][0]['status'] = 'CLOSED'
        self.save_evidence()
        self.assertEqual(self.parity()['overall'], 'PASS')
        self.evidence_data['records'][0]['result'] = 'N/A'
        self.evidence_data['records'][0]['reason'] = 'NOT_APPLICABLE'
        self.save_evidence()
        result = self.parity()
        self.assertEqual(self.item(result, 'P01')['verification'], 'NOT_RUN')
        self.assertEqual(result['overall'], 'GAPS_OPEN')

    def test_visual_accessibility_and_brand_diagnostics_do_not_verify(self):
        self.evidence_data['records'][0]['category'] = 'VISUAL'
        self.save_evidence()
        result = self.parity()
        self.assertEqual(self.item(result, 'P01')['verification'], 'NOT_RUN')
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertEqual(result['diagnostics'][0]['category'], 'VISUAL')

    def test_legal_product_exclusion_is_skip_not_unmapped(self):
        self.request['items'] = [item for item in self.request['items'] if item['id'] != 'P02']
        self.request['product_exclusions'] = [{'product_id': 'E01', 'kind': 'OUT_OF_SCOPE'}]
        self.save_request()
        result = self.parity()
        self.assertEqual(self.item(result, 'X01')['target_evidence'], 'SKIP')
        self.assertNotIn('UNMAPPED_TARGET', {gap['code'] for gap in result['gaps']})


class LifecycleAndBoundaryTests(ParityCase):
    def test_dry_run_repeat_update_and_sources_unchanged(self):
        sources = {path: digest(path) for path in (
            self.spec_one, self.spec_two, self.tasks_path, self.evidence_path,
            self.auto / 'product-recon.json', self.auto / 'observations/observe.json')}
        preview = self.parity(dry_run=True)
        self.assertEqual(preview['status'], 'DRY_RUN')
        self.assertEqual(preview['write'], 'NOT_RUN')
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())
        first = self.parity()
        self.assertEqual(first['report_sha256'], preview['report_sha256'])
        self.assertEqual(self.parity()['status'], 'UNCHANGED')
        self.tasks_path.write_text(self.tasks_path.read_text().replace('- [x] 2.1', '- [ ] 2.1'))
        self.save_request()
        self.assertEqual(self.parity()['status'], 'UPDATED')
        self.assert_sources_unchanged(sources | {self.tasks_path: digest(self.tasks_path)})

    def test_manual_report_and_receipt_conflicts_preserve_content(self):
        self.report.parent.mkdir(parents=True, exist_ok=True)
        self.report.write_text('manual report')
        with self.assertRaisesRegex(ValueError, 'PARITY_CONFLICT'):
            self.parity()
        self.assertEqual(self.report.read_text(), 'manual report')
        self.report.unlink()
        self.parity()
        self.report.write_text(self.report.read_text() + '\nmanual edit\n')
        edited = digest(self.report)
        with self.assertRaisesRegex(ValueError, 'PARITY_CONFLICT'):
            self.parity()
        self.assertEqual(digest(self.report), edited)
        self.report.write_text(self.report.read_text().replace('\nmanual edit\n', ''))
        receipt = json.loads(self.receipt.read_text())
        receipt['execution'] = 'PASS'
        write_json(self.receipt, receipt)
        with self.assertRaisesRegex(ValueError, 'PARITY_CONFLICT'):
            self.parity()

    def test_cross_source_receipt_is_a_conflict(self):
        self.parity()
        receipt = json.loads(self.receipt.read_text())
        receipt['id'] = 'another-product-source'
        write_json(self.receipt, receipt)
        before_report = digest(self.report)
        with self.assertRaisesRegex(ValueError, 'PARITY_CONFLICT'):
            self.parity()
        self.assertEqual(digest(self.report), before_report)

    def test_malformed_limits_depth_and_symlink_are_controlled(self):
        original = self.request_path.read_bytes()
        for content in (b'{', b' ' * (1024 * 1024 + 1), ('[' * 100 + '0' + ']' * 100).encode()):
            with self.subTest(size=len(content)):
                self.request_path.write_bytes(content)
                with self.assertRaisesRegex(ValueError, 'PARITY_(LIMIT|INPUT)'):
                    self.parity()
                self.assertFalse(self.report.exists())
                self.request_path.write_bytes(original)
        outside = self.root / 'outside.json'
        outside.write_bytes(original)
        self.request_path.unlink()
        self.request_path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'SYMLINK|PARITY_INPUT'):
            self.parity()
        self.assertFalse(self.report.exists())

    def test_second_write_failure_restores_previous_report(self):
        self.parity()
        before_report = digest(self.report)
        before_receipt = digest(self.receipt)
        self.tasks_path.write_text(self.tasks_path.read_text().replace('- [x] 2.1', '- [ ] 2.1'))
        self.save_request()
        real_atomic = self.module.atomic
        calls = []

        def fail_receipt(root, rel, content):
            calls.append(rel)
            if rel == '.framework/local-state/parity/demo.json' and len(calls) == 2:
                raise OSError('injected parity receipt failure')
            return real_atomic(root, rel, content)

        with mock.patch.object(self.module, 'atomic', side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, 'injected parity receipt failure'):
                self.parity()
        self.assertEqual(digest(self.report), before_report)
        self.assertEqual(digest(self.receipt), before_receipt)


class CliTests(ParityCase):
    def setUp(self):
        super().setUp()
        self.cli = importlib.import_module('framework_core.cli')

    def invoke(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(argv)
        return code, json.loads(stdout.getvalue())

    def test_parity_action_preview_permission_generation_and_exit_codes(self):
        action = next(value for value in self.cli.parser()._actions if value.dest == 'action')
        self.assertIn('parity', action.choices)
        base = ['parity', '--target', str(self.root), '--request', str(self.request_path)]
        code, preview = self.invoke(base + ['--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(preview['status'], 'DRY_RUN')
        code, consent = self.invoke(base)
        self.assertEqual(code, 3)
        self.assertEqual(consent['status'], 'CONSENT_REQUIRED')
        code, result = self.invoke(base + ['--allow', 'write'])
        self.assertEqual(code, 0)
        self.assertEqual(result['overall'], 'PASS')
        self.evidence_data['records'][0]['result'] = 'FAIL'
        self.save_evidence()
        code, result = self.invoke(base + ['--allow', 'write'])
        self.assertEqual(code, 5)
        self.assertEqual(result['overall'], 'FAILED')

    def test_unsupported_combinations_fail_before_execution(self):
        base = ['parity', '--target', str(self.root), '--request', str(self.request_path)]
        for extra in (['--design-handoff', 'case'], ['--product-recon', 'missing.json'],
                      ['--scope', 'missing.json'], ['--approve', 'toolchain=' + 'a' * 64]):
            with self.subTest(extra=extra):
                code, result = self.invoke(base + extra + ['--allow', 'write'])
                self.assertEqual(code, 2)
                self.assertEqual(result['status'], 'INVALID_INPUT')
        self.assertFalse(self.report.exists())


if __name__ == '__main__':
    unittest.main()
