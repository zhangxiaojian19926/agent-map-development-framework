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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def evidence(provenance='STATIC_SUPPORTED', observations=None, confidence='HIGH'):
    if observations is None:
        observations = ['observe'] if provenance != 'INFERRED' else []
    return {'provenance': provenance, 'observations': observations, 'confidence': confidence}


class HandoffCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / 'page.html'
        self.target.write_text('<html>private target</html>')
        target_sha = digest(self.target)
        self.request = {
            'schema': 'reverse-request/v1', 'id': 'case', 'goal': 'private request goal',
            'target': {'kind': 'file', 'path': str(self.target), 'sha256': target_sha},
            'intent': 'static', 'acceptance': ['observed'],
            'observations': [{'id': 'observe', 'question': 'inspect', 'action': 'static'}],
            'evidence': {'raw': 'retain', 'public': True},
            'behavior': {'capabilities': [], 'constraints': [], 'inferences': []},
        }
        self.plan = {
            'schema': 'toolchain-plan/v1', 'status': 'READY',
            'target': {'kind': 'web_snapshot', 'target_sha256': target_sha},
            'capabilities': ['web.static.resources'], 'tools': [],
        }
        from framework_core.reverse_request import canonical
        from framework_core.reverse_v2 import sha_text
        self.plan_sha = sha_text(canonical(self.plan))
        self.plan['plan_sha256'] = self.plan_sha
        self.record = {
            'schema': 'reverse-observation/v1', 'id': 'observe', 'status': 'RECORDED',
            'provenance': 'STATIC_SUPPORTED', 'plan_sha256': self.plan_sha,
            'target_sha256': target_sha, 'raw_status': 'RAW_RETAINED',
            'raw_path': '.framework/local-state/reverse/auto/case/raw/observe.txt',
            'raw_sha256': hashlib.sha256(b'private raw evidence').hexdigest(),
        }
        from framework_core.reverse_adapters import behavior_contract, observation_request_sha256
        self.record['request_sha256'] = observation_request_sha256(
            self.request, self.plan, self.request['observations'][0])
        self.contract = behavior_contract(self.request, self.plan, [self.record])
        self.auto = self.root / '.framework/local-state/reverse/auto/case'
        write_json(self.auto / 'request.json', self.request)
        write_json(self.auto / 'plans' / (self.plan_sha + '.json'), self.plan)
        write_json(self.auto / 'observations/observe.json', self.record)
        write_json(self.auto / 'behavior-contract.json', self.contract)
        raw = self.auto / 'raw/observe.txt'
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text('private raw evidence')
        self.product_module = importlib.import_module('framework_core.product_recon')
        self.module = importlib.import_module('framework_core.product_design_handoff')
        self.product = self.generate()['product']
        self.design = self.root / 'docs/project/design-input.md'
        self.receipt = self.auto / 'design-handoff.json'

    def tearDown(self):
        self.tmp.cleanup()

    def draft(self):
        return {
            'schema': 'product-recon-draft/v1', 'id': 'case', 'plan_sha256': self.plan_sha,
            'screens': [{
                'id': 'S01', 'name': 'private-screen-name', 'purpose': 'Cookie=private-purpose',
                'component_ids': ['C01'], 'states_observed': ['filled'],
                'states_unobserved': ['error', 'mobile'], 'evidence': evidence(),
            }],
            'flows': [{
                'id': 'F01', 'name': 'private-flow-name', 'goal': 'Authorization: private-goal',
                'screen_ids': ['S01'], 'steps': ['https://private.invalid/?token=secret'],
                'evidence': evidence(),
            }],
            'components': [{
                'id': 'C01', 'name': 'private-component-name', 'kind': 'private-kind',
                'states_observed': ['default'], 'states_unobserved': ['disabled'],
                'evidence': evidence(),
            }],
            'entities': [{
                'id': 'E01', 'name': 'private-entity-name', 'fields': ['private_token'],
                'relationships': ['private-relationship'],
                'evidence': evidence('INFERRED', [], 'MEDIUM'),
            }],
            'exclusions': [{
                'kind': 'PRIVATE_DATA', 'reason': 'private-exclusion-reason',
                'related_ids': ['S01', 'E01'],
            }],
        }

    def generate(self, draft=None):
        return self.product_module.generate_product_recon(
            self.root, self.request, self.plan, self.contract, [self.record], draft or self.draft())

    def handoff(self, dry_run=False):
        return self.module.handoff(self.root, 'case', dry_run=dry_run)

    def assert_private_text_absent(self, text):
        for secret in (
                'private-screen-name', 'private-purpose', 'private-flow-name', 'private-goal',
                'private.invalid', 'private-component-name', 'private-kind', 'private-entity-name',
                'private_token', 'private-relationship', 'private-exclusion-reason',
                'private request goal', 'private raw evidence', 'Cookie', 'Authorization'):
            self.assertNotIn(secret, text)


class SourceValidationTests(HandoffCase):
    def test_valid_chain_and_sensitive_public_handoff(self):
        result = self.handoff()
        self.assertEqual(result['status'], 'RECORDED')
        self.assertEqual(result['design_approval'], 'NEEDS_DESIGN_APPROVAL')
        self.assertEqual(result['runtime_validation'], 'NOT_RUN')
        self.assertFalse(result['source_map_evidence'])
        self.assertFalse(result['implementation_approved'])
        self.assertEqual(result['product_sha256'], digest(self.auto / 'product-recon.json'))
        text = self.design.read_text()
        self.assert_private_text_absent(text)
        for expected in ('S01', 'F01', 'C01', 'E01', 'STATIC_SUPPORTED', 'DYNAMIC_OBSERVED' if False else 'INFERRED',
                         'MEDIUM', 'error', 'mobile', 'disabled', 'PRIVATE_DATA', 'NEEDS_DESIGN_APPROVAL'):
            self.assertIn(expected, text)
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt['schema'], 'product-design-handoff/v1')
        self.assertEqual(receipt['design_input_sha256'], digest(self.design))
        self.assertEqual(receipt['product_sha256'], result['product_sha256'])

    def test_tampered_product_contract_and_plan_are_rejected_without_writes(self):
        cases = []
        product_path = self.auto / 'product-recon.json'
        product = json.loads(product_path.read_text())
        product['screens'][0]['name'] = 'tampered'
        cases.append((product_path, product, 'PRODUCT_HANDOFF_INTEGRITY'))
        contract = copy.deepcopy(self.contract)
        contract['observations'] = []
        cases.append((self.auto / 'behavior-contract.json', contract, 'PRODUCT_HANDOFF_INTEGRITY'))
        plan = copy.deepcopy(self.plan)
        plan['capabilities'] = []
        cases.append((self.auto / 'plans' / (self.plan_sha + '.json'), plan, 'PRODUCT_HANDOFF_INTEGRITY'))
        for path, value, error in cases:
            original = path.read_bytes()
            with self.subTest(path=path.name):
                write_json(path, value)
                with self.assertRaisesRegex(ValueError, error):
                    self.handoff()
                self.assertFalse(self.design.exists())
                self.assertFalse(self.receipt.exists())
                path.write_bytes(original)

    def test_stale_target_invalid_observation_and_cross_plan_record_are_rejected(self):
        record_path = self.auto / 'observations/observe.json'
        original_record = record_path.read_bytes()
        for record in (
                dict(self.record, status='FAILED'),
                dict(self.record, plan_sha256='b' * 64),
                dict(self.record, provenance='DYNAMIC_OBSERVED')):
            with self.subTest(status=record['status'], plan=record['plan_sha256']):
                write_json(record_path, record)
                with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_(STALE|INTEGRITY)'):
                    self.handoff()
                self.assertFalse(self.design.exists())
                record_path.write_bytes(original_record)
        self.target.write_text('changed target')
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_STALE'):
            self.handoff()
        self.assertFalse(self.design.exists())

    def test_missing_raw_evidence_preserves_previous_handoff(self):
        first = self.handoff()
        before_design = digest(self.design)
        before_receipt = digest(self.receipt)
        (self.auto / 'raw/observe.txt').unlink()
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_STALE'):
            self.handoff()
        self.assertEqual(digest(self.design), before_design)
        self.assertEqual(digest(self.receipt), before_receipt)
        self.assertEqual(json.loads(self.receipt.read_text())['product_sha256'], first['product_sha256'])


class LifecycleAndBoundaryTests(HandoffCase):
    def test_dry_run_repeat_update_and_private_observation_hashes(self):
        before_observation = digest(self.auto / 'observations/observe.json')
        preview = self.handoff(dry_run=True)
        self.assertEqual(preview['status'], 'DRY_RUN')
        self.assertEqual(preview['write'], 'NOT_RUN')
        self.assertFalse(self.design.exists())
        self.assertFalse(self.receipt.exists())
        first = self.handoff()
        self.assertEqual(first['design_input_sha256'], preview['design_input_sha256'])
        first_design = digest(self.design)
        first_receipt = digest(self.receipt)
        repeated = self.handoff()
        self.assertEqual(repeated['status'], 'UNCHANGED')
        self.assertEqual(digest(self.design), first_design)
        self.assertEqual(digest(self.receipt), first_receipt)
        updated = self.draft()
        updated['screens'][0]['states_unobserved'].append('permission-denied')
        self.generate(updated)
        changed = self.handoff()
        self.assertEqual(changed['status'], 'UPDATED')
        self.assertNotEqual(digest(self.design), first_design)
        self.assertIn('permission-denied', self.design.read_text())
        self.assertEqual(digest(self.auto / 'observations/observe.json'), before_observation)

    def test_manual_document_and_source_conflicts_preserve_content(self):
        self.design.parent.mkdir(parents=True)
        self.design.write_text('manual design')
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_CONFLICT'):
            self.handoff()
        self.assertEqual(self.design.read_text(), 'manual design')
        self.design.unlink()
        self.handoff()
        self.design.write_text(self.design.read_text() + '\nmanual edit\n')
        edited = digest(self.design)
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_CONFLICT'):
            self.handoff()
        self.assertEqual(digest(self.design), edited)

    def test_malformed_limits_depth_and_symlink_are_controlled(self):
        product = self.auto / 'product-recon.json'
        original = product.read_bytes()
        cases = [b'{', b' ' * (1024 * 1024 + 1), ('[' * 100 + '0' + ']' * 100).encode()]
        for content in cases:
            with self.subTest(size=len(content)):
                product.write_bytes(content)
                with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_(LIMIT|INTEGRITY)'):
                    self.handoff()
                self.assertFalse(self.design.exists())
                product.write_bytes(original)
        outside = self.root / 'outside.json'
        outside.write_bytes(original)
        product.unlink()
        product.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            self.handoff()
        self.assertFalse(self.design.exists())

    def test_tampered_receipt_and_noncanonical_product_are_not_self_healed(self):
        self.handoff()
        before_design = digest(self.design)
        receipt = json.loads(self.receipt.read_text())
        receipt['runtime_validation'] = 'PASS'
        write_json(self.receipt, receipt)
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_CONFLICT'):
            self.handoff()
        self.assertEqual(digest(self.design), before_design)
        self.receipt.unlink()
        self.design.unlink()
        product_path = self.auto / 'product-recon.json'
        product_path.write_text(json.dumps(self.product, ensure_ascii=False, sort_keys=True, indent=4) + '\n')
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_INTEGRITY'):
            self.handoff()
        self.assertFalse(self.design.exists())
        self.assertFalse(self.receipt.exists())

    def test_public_state_tokens_cannot_leak_private_text(self):
        draft = self.draft()
        draft['screens'][0]['states_unobserved'].append('https://private.invalid/state')
        self.generate(draft)
        with self.assertRaisesRegex(ValueError, 'PRODUCT_HANDOFF_INTEGRITY'):
            self.handoff()
        self.assertFalse(self.design.exists())

    def test_second_write_failure_restores_previous_public_design(self):
        self.handoff()
        before_design = digest(self.design)
        before_receipt = digest(self.receipt)
        updated = self.draft()
        updated['screens'][0]['states_unobserved'].append('offline')
        self.generate(updated)
        real_atomic = self.module.atomic
        calls = []

        def fail_receipt(root, rel, content):
            calls.append(rel)
            if rel.endswith('design-handoff.json') and len(calls) == 2:
                raise OSError('injected receipt failure')
            return real_atomic(root, rel, content)

        with mock.patch.object(self.module, 'atomic', side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, 'injected receipt failure'):
                self.handoff()
        self.assertEqual(digest(self.design), before_design)
        self.assertEqual(digest(self.receipt), before_receipt)


class CliTests(HandoffCase):
    def invoke(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(argv)
        return code, json.loads(stdout.getvalue())

    def setUp(self):
        super().setUp()
        self.cli = importlib.import_module('framework_core.cli')

    def test_preview_permission_generation_and_default_compatibility(self):
        base = ['reverse', '--target', str(self.root), '--design-handoff', 'case']
        code, preview = self.invoke(base + ['--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(preview['status'], 'DRY_RUN')
        self.assertFalse(self.design.exists())
        code, consent = self.invoke(base)
        self.assertEqual(code, 3)
        self.assertEqual(consent['status'], 'CONSENT_REQUIRED')
        self.assertFalse(self.design.exists())
        code, result = self.invoke(base + ['--allow', 'write'])
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'RECORDED')
        self.assertTrue(self.design.is_file())
        code, default = self.invoke(['reverse', '--target', str(self.root), '--dry-run'])
        self.assertEqual(code, 0)
        self.assertNotIn('design_handoff', default)

    def test_unsupported_combinations_fail_before_execution(self):
        for argv in (
                ['reverse', '--target', str(self.root), '--design-handoff', 'case', '--request', 'missing.json'],
                ['reverse', '--target', str(self.root), '--design-handoff', 'case', '--scope', 'missing.json'],
                ['reverse', '--target', str(self.root), '--design-handoff', 'case', '--product-recon', 'missing.json'],
                ['doctor', '--target', str(self.root), '--design-handoff', 'case']):
            with self.subTest(argv=argv):
                code, result = self.invoke(argv + ['--allow', 'write'])
                self.assertEqual(code, 2)
                self.assertEqual(result['status'], 'INVALID_INPUT')
                self.assertIn('DESIGN_HANDOFF_NOT_SUPPORTED', result['error'])
        self.assertFalse(self.design.exists())


if __name__ == '__main__':
    unittest.main()
