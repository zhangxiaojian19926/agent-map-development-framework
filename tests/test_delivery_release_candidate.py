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


class CandidateCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.module = importlib.import_module('framework_core.delivery_release_candidate')
        self.dist = self.root / 'dist'
        self.dist.mkdir()
        self.app = self.dist / 'app.txt'
        self.app.write_text('controlled candidate\n', encoding='utf-8')
        self.evidence_dir = self.root / 'docs/verification/delivery'
        self.evidence_dir.mkdir(parents=True)
        self.evidence_paths = []
        self.evidence_data = []
        for category, name in [('BUILD', 'build'), ('FUNCTION', 'function')]:
            attachment = self.evidence_dir / (name + '.txt')
            attachment.write_text(name + ' controlled result\nSECRET-ATTACHMENT\n', encoding='utf-8')
            evidence = {
                'schema': 'delivery-evidence/v1', 'source_revision': 'abc123',
                'records': [{
                    'id': name.upper(), 'category': category, 'result': 'PASS',
                    'test': name + ' contract', 'environment': 'Host',
                    'artifact': {'path': 'docs/verification/delivery/' + name + '.txt',
                                 'sha256': digest(attachment)},
                    'reason': None,
                }],
            }
            path = self.evidence_dir / (name + '.json')
            write_json(path, evidence)
            self.evidence_paths.append(path)
            self.evidence_data.append(evidence)
        self.request_path = self.root / 'candidate-request.json'
        self.request = {
            'schema': 'release-candidate-request/v1', 'id': 'demo', 'version': '1.2.3',
            'source_revision': 'abc123',
            'evidence': [{'path': 'docs/verification/delivery/' + path.stem + '.json', 'sha256': digest(path)}
                         for path in self.evidence_paths],
            'artifacts': [{'path': 'dist/app.txt', 'sha256': digest(self.app)}],
            'notes': {'summary': '公开候选摘要', 'changes': ['公开变化'], 'known_limits': ['未做设备验收']},
        }
        self.save_request()
        self.report = self.root / 'docs/delivery/demo-candidate.md'
        self.receipt = self.root / '.framework/local-state/delivery/demo.json'

    def tearDown(self):
        self.temp.cleanup()

    def save_request(self):
        for index, ref in enumerate(self.request['evidence']):
            write_json(self.evidence_paths[index], self.evidence_data[index])
            ref['sha256'] = digest(self.evidence_paths[index])
        for ref in self.request['artifacts']:
            path = self.root / ref['path']
            if path.is_file() and not path.is_symlink():
                ref['sha256'] = digest(path)
        write_json(self.request_path, self.request)

    def candidate(self, dry_run=False):
        return self.module.generate(self.root, self.request_path, dry_run=dry_run)


class CandidateContractTests(CandidateCase):
    def test_ready_binds_sources_renders_public_notes_and_never_releases(self):
        result = self.candidate()
        self.assertEqual(result['status'], 'RECORDED')
        self.assertEqual(result['overall'], 'READY')
        self.assertEqual(result['release'], 'NOT_RUN')
        self.assertEqual(result['artifacts'], [{'path': 'dist/app.txt', 'sha256': digest(self.app),
                                               'size': len(self.app.read_bytes())}])
        text = self.report.read_text(encoding='utf-8')
        self.assertIn('1.2.3', text)
        self.assertIn('公开候选摘要', text)
        self.assertIn('未做设备验收', text)
        self.assertIn('release=NOT_RUN', text)
        self.assertNotIn('SECRET-ATTACHMENT', text)
        saved = json.loads(self.receipt.read_text(encoding='utf-8'))
        self.assertEqual(saved['execution'], 'NOT_RUN')
        self.assertEqual(saved['report_sha256'], digest(self.report))

    def test_missing_required_pass_and_nonpass_records_are_gaps(self):
        self.evidence_data = [self.evidence_data[1]]
        self.evidence_paths = [self.evidence_paths[1]]
        self.request['evidence'] = [self.request['evidence'][1]]
        self.save_request()
        result = self.candidate()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('MISSING_BUILD_PASS', {gap['code'] for gap in result['gaps']})
        self.evidence_data[0]['records'][0]['result'] = 'NOT_RUN'
        self.save_request()
        result = self.candidate()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('NOT_RUN', {gap['code'] for gap in result['gaps']})
        self.evidence_data[0]['records'][0]['result'] = 'INFRA_ERROR'
        self.evidence_data[0]['records'][0]['reason'] = 'RUNNER_UNAVAILABLE'
        self.save_request()
        result = self.candidate()
        self.assertEqual(result['overall'], 'GAPS_OPEN')
        self.assertIn('INFRA_ERROR', {gap['code'] for gap in result['gaps']})

    def test_failure_has_priority_over_other_gaps_and_passes(self):
        self.evidence_data[0]['records'][0]['result'] = 'FAIL'
        self.evidence_data[1]['records'][0]['result'] = 'NOT_RUN'
        self.save_request()
        result = self.candidate()
        self.assertEqual(result['overall'], 'FAILED')
        self.assertIn('BUILD_FAILED', {gap['code'] for gap in result['gaps']})
        self.assertIn('NOT_RUN', {gap['code'] for gap in result['gaps']})

    def test_stale_source_and_invalid_pass_attachment_are_rejected_before_write(self):
        self.evidence_data[0]['source_revision'] = 'other'
        self.save_request()
        with self.assertRaisesRegex(ValueError, 'CANDIDATE_EVIDENCE'):
            self.candidate()
        self.assertFalse(self.report.exists())
        self.evidence_data[0]['source_revision'] = 'abc123'
        self.evidence_data[0]['records'][0]['artifact'] = None
        self.save_request()
        with self.assertRaisesRegex(ValueError, 'CANDIDATE_EVIDENCE'):
            self.candidate()
        self.evidence_data[0]['records'][0]['artifact'] = {
            'path': 'docs/verification/delivery/build.txt', 'sha256': '0' * 64}
        self.save_request()
        with self.assertRaisesRegex(ValueError, 'CANDIDATE_STALE'):
            self.candidate()
        self.assertFalse(self.report.exists())

    def test_artifact_whitelist_rejects_duplicates_private_files_escape_and_symlink(self):
        variants = [
            [{'path': 'dist/app.txt', 'sha256': ''}] * 2,
            [{'path': '../outside.txt', 'sha256': '0' * 64}],
            [{'path': 'dist/.env', 'sha256': '0' * 64}],
            [{'path': 'docs/verification/delivery/build.txt', 'sha256': '0' * 64}],
        ]
        for artifacts in variants:
            with self.subTest(artifacts=artifacts):
                self.request['artifacts'] = copy.deepcopy(artifacts)
                write_json(self.request_path, self.request)
                with self.assertRaises(ValueError):
                    self.candidate()
                self.assertFalse(self.report.exists())
        self.request['artifacts'] = [{'path': 'dist/link', 'sha256': '0' * 64}]
        (self.dist / 'link').symlink_to(self.app)
        write_json(self.request_path, self.request)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            self.candidate()

    def test_dry_run_idempotence_update_and_manual_conflict(self):
        result = self.candidate(dry_run=True)
        self.assertEqual(result['status'], 'DRY_RUN')
        self.assertFalse(self.report.exists())
        self.candidate()
        self.assertEqual(self.candidate()['status'], 'UNCHANGED')
        self.request['notes']['changes'] = ['更新后的公开变化']
        self.save_request()
        self.assertEqual(self.candidate()['status'], 'UPDATED')
        self.report.write_text(self.report.read_text(encoding='utf-8') + '人工内容\n', encoding='utf-8')
        before = digest(self.report)
        self.request['notes']['changes'] = ['不能覆盖人工内容']
        self.save_request()
        with self.assertRaisesRegex(ValueError, 'CANDIDATE_CONFLICT'):
            self.candidate()
        self.assertEqual(digest(self.report), before)

    def test_second_write_failure_restores_previous_report_and_receipt(self):
        self.candidate()
        old_report = self.report.read_bytes()
        old_receipt = self.receipt.read_bytes()
        self.request['version'] = '1.2.4'
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
                self.candidate()
        self.assertEqual(self.report.read_bytes(), old_report)
        self.assertEqual(self.receipt.read_bytes(), old_receipt)


class CandidateCliTests(CandidateCase):
    def invoke(self, *args):
        cli = importlib.import_module('framework_core.cli')
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(list(args))
        return code, json.loads(stdout.getvalue())

    def test_cli_consent_dry_run_exit_codes_and_unsupported_combinations(self):
        base = ['candidate', '--target', str(self.root), '--request', str(self.request_path)]
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (3, 'CONSENT_REQUIRED'))
        code, result = self.invoke(*base, '--dry-run')
        self.assertEqual((code, result['overall']), (0, 'READY'))
        self.assertFalse(self.report.exists())
        self.evidence_data[0]['records'][0]['result'] = 'FAIL'
        self.save_request()
        code, result = self.invoke(*base, '--allow', 'write')
        self.assertEqual((code, result['overall']), (5, 'FAILED'))
        code, result = self.invoke(*base, '--summary')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'INVALID_INPUT')
        self.assertIn('CANDIDATE_NOT_SUPPORTED', result['error'])


if __name__ == '__main__':
    unittest.main()
