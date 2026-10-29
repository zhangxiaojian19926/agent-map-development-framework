import contextlib
import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class ResearchCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.module = importlib.import_module('framework_core.market_research_handoff')
        self.request_path = self.root / 'research-request.json'
        self.request = {
            'schema': 'market-research-request/v1',
            'id': 'market-demo',
            'question': '公开竞品如何组织项目初始化？',
            'sources': [{
                'id': 'source-a',
                'url': 'https://example.com/public-report',
                'accessed_at': '2026-10-29',
                'content_sha256': 'a' * 64,
            }],
            'facts': [{
                'id': 'fact-a',
                'statement': '公开报告描述了分阶段初始化。',
                'source_ids': ['source-a'],
            }],
            'inferences': [{
                'id': 'inference-a',
                'statement': '分阶段入口可能降低首次使用成本。',
                'fact_ids': ['fact-a'],
                'confidence': 'MEDIUM',
            }],
            'limitations': ['仅整理一份公开资料，未验证其外部真实性。'],
            'design': {
                'summary': '待确认的分阶段初始化草案。',
                'opportunities': ['减少首次配置项。'],
                'constraints': ['不得改变既有普通初始化。'],
            },
        }
        self.save_request()
        self.report = self.root / 'docs/project/market-research/market-demo.md'
        self.receipt = self.root / '.framework/local-state/market-research/market-demo.json'

    def tearDown(self):
        self.temp.cleanup()

    def save_request(self):
        write_json(self.request_path, self.request)

    def research(self, dry_run=False):
        return self.module.generate(self.root, self.request_path, dry_run=dry_run)

    def assert_rejected(self, error='RESEARCH_INPUT'):
        self.save_request()
        with self.assertRaisesRegex(ValueError, error):
            self.research()
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())


class ResearchContractTests(ResearchCase):
    def test_valid_handoff_separates_facts_inferences_and_pending_design(self):
        design_input = self.root / 'docs/project/design-input.md'
        design_input.parent.mkdir(parents=True)
        design_input.write_text('人工设计资料，不得覆盖。\n', encoding='utf-8')
        before = digest(design_input)
        result = self.research()
        self.assertEqual(result['status'], 'RECORDED')
        self.assertEqual(result['design_status'], 'NEEDS_DESIGN_APPROVAL')
        self.assertEqual(result['source_verification'], 'NOT_RUN')
        self.assertEqual(result['execution'], 'NOT_RUN')
        text = self.report.read_text(encoding='utf-8')
        for expected in (
            '公开竞品如何组织项目初始化？', 'https://example.com/public-report',
            '公开报告描述了分阶段初始化。', '分阶段入口可能降低首次使用成本。',
            '仅整理一份公开资料，未验证其外部真实性。', '待确认的分阶段初始化草案。',
            'design_status=NEEDS_DESIGN_APPROVAL', 'source_verification=NOT_RUN',
            'execution=NOT_RUN', '## 来源事实', '## Agent 推断', '## 待确认设计草案',
        ):
            self.assertIn(expected, text)
        self.assertLess(text.index('## 来源事实'), text.index('## Agent 推断'))
        self.assertLess(text.index('## Agent 推断'), text.index('## 待确认设计草案'))
        saved = json.loads(self.receipt.read_text(encoding='utf-8'))
        self.assertEqual(saved['schema'], 'market-research-receipt/v1')
        self.assertEqual(saved['report_sha256'], digest(self.report))
        self.assertEqual(saved['design_status'], 'NEEDS_DESIGN_APPROVAL')
        self.assertEqual(saved['source_verification'], 'NOT_RUN')
        self.assertEqual(saved['execution'], 'NOT_RUN')
        self.assertEqual(digest(design_input), before)

    def test_source_url_date_hash_and_duplicate_ids_are_strict(self):
        variants = [
            ('url', 'file:///tmp/private.txt'),
            ('url', 'https://user:password@example.com/report'),
            ('url', 'https:///missing-host'),
            ('url', 'https://example.com/\nprivate'),
            ('accessed_at', '2026-02-30'),
            ('accessed_at', '29-10-2026'),
            ('content_sha256', 'A' * 64),
            ('content_sha256', 'a' * 63),
        ]
        for field, value in variants:
            with self.subTest(field=field, value=value):
                self.request['sources'][0][field] = value
                self.assert_rejected()
                self.request['sources'][0][field] = {
                    'url': 'https://example.com/public-report',
                    'accessed_at': '2026-10-29',
                    'content_sha256': 'a' * 64,
                }[field]
        self.request['sources'].append(copy.deepcopy(self.request['sources'][0]))
        self.assert_rejected()

    def test_references_confidence_and_duplicate_record_ids_are_strict(self):
        variants = [
            ('fact-source', 'missing-source'),
            ('inference-fact', 'missing-fact'),
        ]
        for kind, missing in variants:
            with self.subTest(kind=kind):
                if kind == 'fact-source':
                    self.request['facts'][0]['source_ids'] = [missing]
                else:
                    self.request['inferences'][0]['fact_ids'] = [missing]
                self.assert_rejected()
                self.request = json.loads(self.request_path.read_text(encoding='utf-8'))
                self.request['facts'][0]['source_ids'] = ['source-a']
                self.request['inferences'][0]['fact_ids'] = ['fact-a']
        self.request['inferences'][0]['confidence'] = 'CERTAIN'
        self.assert_rejected()
        self.request['inferences'][0]['confidence'] = 'MEDIUM'
        self.request['facts'].append(copy.deepcopy(self.request['facts'][0]))
        self.assert_rejected()
        self.request['facts'].pop()
        self.request['inferences'].append(copy.deepcopy(self.request['inferences'][0]))
        self.assert_rejected()

    def test_unknown_fields_attachments_and_private_path_references_are_rejected(self):
        variants = [
            ('request', 'attachment', '.framework/local-state/private.json'),
            ('source', 'path', 'docs/project/reverse/raw/private.txt'),
            ('fact', 'evidence_path', 'docs/project/reverse/output/private.txt'),
            ('design', 'summary', '见 .framework/local-state/private.json'),
        ]
        for kind, field, value in variants:
            with self.subTest(kind=kind, field=field):
                target = self.request if kind == 'request' else self.request[kind + 's'][0] if kind in ('source', 'fact') else self.request[kind]
                original = target.get(field, None)
                target[field] = value
                self.assert_rejected()
                if kind == 'design':
                    target[field] = original
                else:
                    target.pop(field, None)

    def test_dry_run_idempotence_update_and_manual_conflicts(self):
        result = self.research(dry_run=True)
        self.assertEqual(result['status'], 'DRY_RUN')
        self.assertIn('report_sha256', result)
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())
        self.research()
        self.assertEqual(self.research()['status'], 'UNCHANGED')
        self.request['design']['opportunities'] = ['更新后的公开机会。']
        self.save_request()
        self.assertEqual(self.research()['status'], 'UPDATED')
        self.report.write_text(self.report.read_text(encoding='utf-8') + '人工补充\n', encoding='utf-8')
        before = digest(self.report)
        self.request['design']['summary'] = '不得覆盖人工内容。'
        self.save_request()
        with self.assertRaisesRegex(ValueError, 'RESEARCH_CONFLICT'):
            self.research()
        self.assertEqual(digest(self.report), before)

    def test_receipt_tampering_and_missing_artifact_are_conflicts(self):
        self.research()
        receipt = json.loads(self.receipt.read_text(encoding='utf-8'))
        receipt['execution'] = 'RUN'
        write_json(self.receipt, receipt)
        with self.assertRaisesRegex(ValueError, 'RESEARCH_CONFLICT'):
            self.research()
        self.receipt.unlink()
        with self.assertRaisesRegex(ValueError, 'RESEARCH_CONFLICT'):
            self.research()

    def test_second_write_failure_restores_previous_report_and_receipt(self):
        self.research()
        old_report = self.report.read_bytes()
        old_receipt = self.receipt.read_bytes()
        self.request['question'] = '合法更新后的研究问题？'
        self.save_request()
        original = self.module.atomic
        calls = []

        def fail_second(root, rel, content):
            calls.append(rel)
            if len(calls) == 2:
                raise OSError('controlled write failure')
            return original(root, rel, content)

        with mock.patch.object(self.module, 'atomic', side_effect=fail_second):
            with self.assertRaises(OSError):
                self.research()
        self.assertEqual(self.report.read_bytes(), old_report)
        self.assertEqual(self.receipt.read_bytes(), old_receipt)


class ResearchCliTests(ResearchCase):
    def invoke(self, *args):
        cli = importlib.import_module('framework_core.cli')
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(list(args))
        return code, json.loads(stdout.getvalue())

    def test_cli_consent_dry_run_write_and_unsupported_combinations(self):
        base = ['research', '--target', str(self.root), '--request', str(self.request_path)]
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (3, 'CONSENT_REQUIRED'))
        code, result = self.invoke(*base, '--dry-run')
        self.assertEqual((code, result['status']), (0, 'DRY_RUN'))
        self.assertFalse(self.report.exists())
        code, result = self.invoke(*base, '--allow', 'write')
        self.assertEqual((code, result['status']), (0, 'RECORDED'))
        for extra in (['--summary'], ['--allow', 'agent'], ['--allow', 'write', '--scope', '{}']):
            with self.subTest(extra=extra):
                code, result = self.invoke(*base, *extra)
                self.assertEqual((code, result['status']), (2, 'INVALID_INPUT'))
                self.assertIn('RESEARCH_NOT_SUPPORTED', result['error'])

    def test_cli_invalid_request_exits_without_partial_output(self):
        self.request['facts'][0]['source_ids'] = ['unknown']
        self.save_request()
        base = ['research', '--target', str(self.root), '--request', str(self.request_path), '--allow', 'write']
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (2, 'INVALID_INPUT'))
        self.assertIn('RESEARCH_INPUT', result['error'])
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())


if __name__ == '__main__':
    unittest.main()
