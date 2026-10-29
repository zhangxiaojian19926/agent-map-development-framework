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


def tree_digest(root):
    root = Path(root)
    if not root.exists():
        return None
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob('*')) if path.is_file()
    }


class ChannelCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.module = importlib.import_module('framework_core.release_channel_adapter')
        self.candidate_module = importlib.import_module('framework_core.delivery_release_candidate')
        self.hashes = importlib.import_module('framework_core.reverse_v2')
        self.dist = self.root / 'dist'
        self.dist.mkdir()
        self.app = self.dist / 'app.txt'
        self.app.write_bytes(b'controlled channel asset\n')
        self.evidence_dir = self.root / 'docs/verification/delivery'
        self.evidence_dir.mkdir(parents=True)
        self.evidence_paths = []
        self.evidence_data = []
        for category, name in [('BUILD', 'build'), ('FUNCTION', 'function')]:
            attachment = self.evidence_dir / (name + '.txt')
            attachment.write_text(name + ' result\nSECRET-ATTACHMENT\n', encoding='utf-8')
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
        self.candidate_request_path = self.root / 'candidate-request.json'
        self.candidate_request = {
            'schema': 'release-candidate-request/v1', 'id': 'demo', 'version': '1.2.3',
            'source_revision': 'abc123',
            'evidence': [{'path': 'docs/verification/delivery/' + path.stem + '.json',
                          'sha256': digest(path)} for path in self.evidence_paths],
            'artifacts': [{'path': 'dist/app.txt', 'sha256': digest(self.app)}],
            'notes': {'summary': '公开候选摘要', 'changes': ['公开变化'], 'known_limits': ['未做设备验收']},
        }
        write_json(self.candidate_request_path, self.candidate_request)
        self.candidate_result = self.candidate_module.generate(self.root, self.candidate_request_path)
        self.candidate_report = self.root / 'docs/delivery/demo-candidate.md'
        self.request_path = self.root / 'channel-request.json'
        self.request = {
            'schema': 'release-channel-request/v1', 'id': 'github-demo',
            'candidate': {
                'id': 'demo', 'request': 'candidate-request.json',
                'request_sha256': self.hashes.sha_text(self.hashes.canonical(self.candidate_request)),
                'report_sha256': digest(self.candidate_report),
            },
            'channel': {
                'type': 'github-release', 'repository': 'owner/repo', 'tag': 'v1.2.3',
                'title': '1.2.3 公开版本', 'draft': False, 'prerelease': True,
            },
            'assets': [{'path': 'dist/app.txt', 'name': 'app.txt'}],
        }
        self.save_request()
        self.output = self.root / 'dist/delivery/github-demo'
        self.report = self.root / 'docs/delivery/github-demo-channel.md'
        self.receipt = self.root / '.framework/local-state/delivery/github-demo-channel.json'

    def tearDown(self):
        self.temp.cleanup()

    def save_request(self):
        write_json(self.request_path, self.request)

    def channel(self, dry_run=False):
        return self.module.generate(self.root, self.request_path, dry_run=dry_run)

    def rebind_candidate(self):
        self.request['candidate']['request_sha256'] = self.hashes.sha_text(
            self.hashes.canonical(self.candidate_request))
        self.request['candidate']['report_sha256'] = digest(self.candidate_report)
        self.save_request()

    def regenerate_candidate(self):
        for index, ref in enumerate(self.candidate_request['evidence']):
            write_json(self.evidence_paths[index], self.evidence_data[index])
            ref['sha256'] = digest(self.evidence_paths[index])
        for ref in self.candidate_request['artifacts']:
            ref['sha256'] = digest(self.root / ref['path'])
        write_json(self.candidate_request_path, self.candidate_request)
        self.candidate_result = self.candidate_module.generate(self.root, self.candidate_request_path)
        self.rebind_candidate()

    def snapshot(self):
        return tree_digest(self.output), digest(self.report), digest(self.receipt)

    def assert_snapshot(self, snapshot):
        current = (tree_digest(self.output), digest(self.report), digest(self.receipt))
        self.assertEqual(current, snapshot)

    def assert_rejected(self, error='CHANNEL_INPUT'):
        self.save_request()
        with self.assertRaisesRegex(ValueError, error):
            self.channel()
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())


class ChannelContractTests(ChannelCase):
    def test_valid_github_adaptation_is_deterministic_public_and_not_published(self):
        result = self.channel()
        self.assertEqual(result['status'], 'RECORDED')
        self.assertEqual(result['publish'], 'NOT_RUN')
        self.assertEqual(result['execution'], 'NOT_RUN')
        self.assertEqual({path.name for path in self.output.iterdir()},
                         {'app.txt', 'release-notes.md', 'channel-manifest.json'})
        self.assertEqual((self.output / 'app.txt').read_bytes(), self.app.read_bytes())
        notes = (self.output / 'release-notes.md').read_text(encoding='utf-8')
        self.assertIn('公开候选摘要', notes)
        self.assertIn('公开变化', notes)
        self.assertIn('未做设备验收', notes)
        self.assertNotIn('SECRET-ATTACHMENT', notes)
        manifest = json.loads((self.output / 'channel-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['schema'], 'release-channel-manifest/v1')
        self.assertEqual(manifest['candidate']['id'], 'demo')
        self.assertEqual(manifest['channel']['repository'], 'owner/repo')
        self.assertEqual(manifest['assets'], [{
            'path': 'dist/app.txt', 'name': 'app.txt',
            'size': len(self.app.read_bytes()), 'sha256': digest(self.app),
        }])
        self.assertEqual(manifest['publish'], 'NOT_RUN')
        self.assertEqual(manifest['execution'], 'NOT_RUN')
        text = self.report.read_text(encoding='utf-8')
        for expected in ('owner/repo', 'v1.2.3', 'publish=NOT_RUN', 'execution=NOT_RUN',
                         result['request_sha256'], digest(self.candidate_report), digest(self.app)):
            self.assertIn(expected, text)
        saved = json.loads(self.receipt.read_text(encoding='utf-8'))
        self.assertEqual(saved['schema'], 'release-channel-receipt/v1')
        self.assertEqual(saved['report_sha256'], digest(self.report))
        self.assertEqual(saved['files']['app.txt'], digest(self.output / 'app.txt'))
        self.assertEqual(saved['publish'], 'NOT_RUN')

    def test_channel_target_and_asset_names_are_strict(self):
        variants = [
            ('type', 'dynamic-plugin', 'CHANNEL_UNSUPPORTED'),
            ('repository', 'https://github.com/owner/repo', 'CHANNEL_INPUT'),
            ('repository', 'owner/repo@secret', 'CHANNEL_INPUT'),
            ('tag', 'v1/2/3', 'CHANNEL_INPUT'),
            ('tag', '.hidden', 'CHANNEL_INPUT'),
            ('title', '见 .framework/local-state/secret', 'CHANNEL_INPUT'),
            ('draft', 'false', 'CHANNEL_INPUT'),
            ('prerelease', 1, 'CHANNEL_INPUT'),
        ]
        original = copy.deepcopy(self.request['channel'])
        for field, value, error in variants:
            with self.subTest(field=field, value=value):
                self.request['channel'][field] = value
                self.assert_rejected(error)
                self.request['channel'] = copy.deepcopy(original)
        self.request['assets'] = [{'path': 'dist/app.txt', 'name': 'App.txt'},
                                  {'path': 'dist/app.txt', 'name': 'app.txt'}]
        self.assert_rejected()
        self.request['assets'] = [{'path': 'dist/app.txt', 'name': '../escape'}]
        self.assert_rejected()
        self.request['assets'] = [{'path': '.framework/local-state/secret', 'name': 'app.txt'}]
        self.assert_rejected()

    def test_non_ready_candidate_cannot_be_adapted(self):
        for result in ('NOT_RUN', 'FAIL'):
            with self.subTest(result=result):
                self.evidence_data[0]['records'][0]['result'] = result
                self.evidence_data[0]['records'][0]['reason'] = None
                self.regenerate_candidate()
                with self.assertRaisesRegex(ValueError, 'CHANNEL_NOT_READY'):
                    self.channel()
                self.assertFalse(self.output.exists())
                self.evidence_data[0]['records'][0]['result'] = 'PASS'
                self.regenerate_candidate()

    def test_candidate_binding_tampering_and_stale_assets_are_rejected(self):
        self.request['candidate']['report_sha256'] = '0' * 64
        self.assert_rejected('CHANNEL_STALE')
        self.rebind_candidate()
        original_report = self.candidate_report.read_bytes()
        self.candidate_report.write_bytes(original_report + b'tamper\n')
        with self.assertRaisesRegex(ValueError, 'CHANNEL_STALE'):
            self.channel()
        self.candidate_report.write_bytes(original_report)
        self.evidence_paths[0].write_text('stale evidence\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'CHANNEL_STALE'):
            self.channel()
        self.regenerate_candidate()
        self.app.write_bytes(b'changed after candidate\n')
        with self.assertRaisesRegex(ValueError, 'CHANNEL_STALE'):
            self.channel()
        self.assertFalse(self.output.exists())

    def test_budget_is_controlled(self):
        with mock.patch.object(self.module, 'MAX_TOTAL_BYTES', 1):
            with self.assertRaisesRegex(ValueError, 'CHANNEL_LIMIT'):
                self.channel()
        self.assertFalse(self.output.exists())

    def test_dry_run_idempotence_update_and_manual_conflicts(self):
        result = self.channel(dry_run=True)
        self.assertEqual(result['status'], 'DRY_RUN')
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())
        self.channel()
        self.assertEqual(self.channel()['status'], 'UNCHANGED')
        self.request['channel']['title'] = '合法更新标题'
        self.save_request()
        self.assertEqual(self.channel()['status'], 'UPDATED')
        (self.output / 'manual.txt').write_text('keep\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'CHANNEL_CONFLICT'):
            self.channel()
        self.assertEqual((self.output / 'manual.txt').read_text(encoding='utf-8'), 'keep\n')
        (self.output / 'manual.txt').unlink()
        self.report.write_text(self.report.read_text(encoding='utf-8') + '人工内容\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'CHANNEL_CONFLICT'):
            self.channel()

    def test_missing_artifact_and_tampered_receipt_are_conflicts(self):
        self.channel()
        (self.output / 'app.txt').unlink()
        with self.assertRaisesRegex(ValueError, 'CHANNEL_CONFLICT'):
            self.channel()
        (self.output / 'app.txt').write_bytes(self.app.read_bytes())
        saved = json.loads(self.receipt.read_text(encoding='utf-8'))
        saved['execution'] = 'RUN'
        write_json(self.receipt, saved)
        with self.assertRaisesRegex(ValueError, 'CHANNEL_CONFLICT'):
            self.channel()

    def test_directory_report_and_receipt_failures_restore_complete_state(self):
        with mock.patch.object(self.module, 'replace', side_effect=OSError('directory failure')):
            with self.assertRaises(OSError):
                self.channel()
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())
        self.assertFalse(self.receipt.exists())
        self.channel()
        self.request['channel']['title'] = '更新后需要恢复'
        self.save_request()
        for fail_at in (1, 2):
            with self.subTest(fail_at=fail_at):
                snapshot = self.snapshot()
                original = self.module.atomic
                calls = []

                def fail_atomic(root, rel, content):
                    calls.append(rel)
                    if len(calls) == fail_at:
                        raise OSError('controlled commit failure')
                    return original(root, rel, content)

                with mock.patch.object(self.module, 'atomic', side_effect=fail_atomic):
                    with self.assertRaises(OSError):
                        self.channel()
                self.assert_snapshot(snapshot)


class ChannelCliTests(ChannelCase):
    def invoke(self, *args):
        cli = importlib.import_module('framework_core.cli')
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(list(args))
        return code, json.loads(stdout.getvalue())

    def test_cli_consent_dry_run_write_and_unsupported_combinations(self):
        base = ['channel', '--target', str(self.root), '--request', str(self.request_path)]
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (3, 'CONSENT_REQUIRED'))
        code, result = self.invoke(*base, '--dry-run')
        self.assertEqual((code, result['status']), (0, 'DRY_RUN'))
        self.assertFalse(self.output.exists())
        code, result = self.invoke(*base, '--allow', 'write')
        self.assertEqual((code, result['status']), (0, 'RECORDED'))
        for extra in (['--summary'], ['--allow', 'agent'], ['--allow', 'write', '--scope', '{}']):
            with self.subTest(extra=extra):
                code, result = self.invoke(*base, *extra)
                self.assertEqual((code, result['status']), (2, 'INVALID_INPUT'))
                self.assertIn('CHANNEL_NOT_SUPPORTED', result['error'])

    def test_cli_not_ready_and_invalid_input_exit_without_output(self):
        self.evidence_data[0]['records'][0]['result'] = 'FAIL'
        self.regenerate_candidate()
        base = ['channel', '--target', str(self.root), '--request', str(self.request_path), '--allow', 'write']
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (5, 'CHANNEL_NOT_READY'))
        self.assertFalse(self.output.exists())
        self.request['channel']['repository'] = 'bad repository'
        self.save_request()
        code, result = self.invoke(*base)
        self.assertEqual((code, result['status']), (2, 'INVALID_INPUT'))
        self.assertIn('CHANNEL_INPUT', result['error'])


if __name__ == '__main__':
    unittest.main()
