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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_for(path):
    return {
        'schema': 'reverse-request/v1', 'id': 'case', 'goal': 'inspect product',
        'target': {'kind': 'file', 'path': str(path), 'sha256': digest(path)},
        'intent': 'static', 'acceptance': ['observed'],
        'observations': [{'id': 'observe', 'question': 'inspect', 'action': 'static'}],
        'evidence': {'raw': 'retain', 'public': True},
        'behavior': {'capabilities': [], 'constraints': [], 'inferences': []},
    }


def evidence(provenance='STATIC_SUPPORTED', observations=None, confidence='HIGH'):
    if observations is None:
        observations = ['observe'] if provenance != 'INFERRED' else []
    return {'provenance': provenance, 'observations': observations, 'confidence': confidence}


def draft_for(plan_sha256):
    return {
        'schema': 'product-recon-draft/v1', 'id': 'case', 'plan_sha256': plan_sha256,
        'screens': [{
            'id': 'S01', 'name': 'private-account-screen', 'purpose': 'Cookie=private-screen-purpose',
            'component_ids': ['C01'], 'states_observed': ['filled'],
            'states_unobserved': ['error', 'mobile'], 'evidence': evidence(),
        }],
        'flows': [{
            'id': 'F01', 'name': 'private-flow', 'goal': 'Authorization: private-flow-goal',
            'screen_ids': ['S01'], 'steps': ['https://private.invalid/accounts?token=secret'],
            'evidence': evidence(),
        }],
        'components': [{
            'id': 'C01', 'name': 'private-component', 'kind': 'form',
            'states_observed': ['default'], 'states_unobserved': ['disabled'],
            'evidence': evidence(),
        }],
        'entities': [{
            'id': 'E01', 'name': 'private-entity', 'fields': ['private_token'],
            'relationships': ['private-account-relationship'], 'evidence': evidence('INFERRED', [], 'MEDIUM'),
        }],
        'exclusions': [{
            'kind': 'PRIVATE_DATA', 'reason': 'private-exclusion-reason',
            'related_ids': ['S01', 'E01'],
        }],
    }


class ProductReconCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / 'page.html'
        self.target.write_text('<html>private source</html>')
        self.request = request_for(self.target)
        self.plan = {
            'plan_sha256': 'a' * 64,
            'target': {'kind': 'web_snapshot', 'target_sha256': digest(self.target)},
            'capabilities': ['web.static.resources'], 'tools': [],
        }
        self.record = {
            'id': 'observe', 'status': 'RECORDED', 'provenance': 'STATIC_SUPPORTED',
            'plan_sha256': self.plan['plan_sha256'], 'raw_status': 'RAW_RETAINED',
        }
        self.contract = {
            'schema': 'behavior-contract/v1', 'id': 'case', 'plan_sha256': self.plan['plan_sha256'],
            'observations': ['observe'], 'runtime_validation': 'NOT_RUN',
            'source_map_evidence': False, 'implementation_approved': False,
        }
        self.draft = draft_for(self.plan['plan_sha256'])
        self.module = importlib.import_module('framework_core.product_recon')

    def tearDown(self):
        self.tmp.cleanup()

    def generate(self, draft=None):
        return self.module.generate_product_recon(
            self.root, self.request, self.plan, self.contract, [self.record], draft or self.draft)


class DraftValidationTests(ProductReconCase):
    def test_valid_structure_preview_and_cross_references(self):
        preview = self.module.preview_product_recon(self.draft, self.request, self.plan)
        self.assertEqual(preview['status'], 'READY')
        self.assertEqual(preview['counts'], {'screens': 1, 'flows': 1, 'components': 1, 'entities': 1})
        self.assertEqual(len(preview['draft_sha256']), 64)
        normalized = self.module.validate_product_draft(self.draft, self.request, self.plan)
        self.assertEqual(normalized['screens'][0]['component_ids'], ['C01'])
        self.assertEqual(normalized['flows'][0]['screen_ids'], ['S01'])
        self.assertEqual(normalized['entities'][0]['evidence']['provenance'], 'INFERRED')

    def test_invalid_schema_ids_references_and_states_are_rejected(self):
        cases = []
        unknown = copy.deepcopy(self.draft)
        unknown['unexpected'] = True
        cases.append(unknown)
        duplicate = copy.deepcopy(self.draft)
        duplicate['screens'].append(copy.deepcopy(duplicate['screens'][0]))
        cases.append(duplicate)
        bad_id = copy.deepcopy(self.draft)
        bad_id['screens'][0]['id'] = 'screen-1'
        cases.append(bad_id)
        bad_provenance = copy.deepcopy(self.draft)
        bad_provenance['screens'][0]['evidence']['provenance'] = 'GUESSED'
        cases.append(bad_provenance)
        dangling = copy.deepcopy(self.draft)
        dangling['flows'][0]['screen_ids'] = ['S99']
        cases.append(dangling)
        overlap = copy.deepcopy(self.draft)
        overlap['screens'][0]['states_unobserved'].append('filled')
        cases.append(overlap)
        inferred_observation = copy.deepcopy(self.draft)
        inferred_observation['entities'][0]['evidence']['observations'] = ['observe']
        cases.append(inferred_observation)
        for index, draft in enumerate(cases):
            with self.subTest(case=index), self.assertRaisesRegex(ValueError, 'INVALID_PRODUCT_RECON'):
                self.module.validate_product_draft(draft, self.request, self.plan)

    def test_plan_and_request_binding_are_rejected(self):
        for key, value in (('id', 'other'), ('plan_sha256', 'b' * 64), ('schema', 'product-recon/v1')):
            with self.subTest(key=key):
                draft = copy.deepcopy(self.draft)
                draft[key] = value
                with self.assertRaisesRegex(ValueError, 'INVALID_PRODUCT_RECON'):
                    self.module.validate_product_draft(draft, self.request, self.plan)


class EvidenceAndOutputTests(ProductReconCase):
    def test_unavailable_unknown_and_cross_plan_observations_cannot_support_facts(self):
        records = []
        for status in ('NOT_AUTHORIZED', 'PROVIDER_MISSING', 'FAILED'):
            records.append(dict(self.record, status=status))
        records.append(dict(self.record, plan_sha256='b' * 64))
        records.append(dict(self.record, provenance='DYNAMIC_OBSERVED'))
        for record in records:
            with self.subTest(status=record['status'], plan=record['plan_sha256'],
                              provenance=record['provenance']):
                with self.assertRaisesRegex(ValueError, 'PRODUCT_RECON_EVIDENCE'):
                    self.module.generate_product_recon(
                        self.root, self.request, self.plan, self.contract, [record], self.draft)
        self.assertFalse((self.root / '.framework/local-state/reverse/auto/case/product-recon.json').exists())

    def test_generation_is_deterministic_private_and_preserves_handoff_boundaries(self):
        result = self.generate()
        product_path = self.root / result['path']
        self.assertEqual(result['status'], 'RECORDED')
        first_hash = digest(product_path)
        product = result['product']
        self.assertEqual(product['schema'], 'product-recon/v1')
        self.assertEqual(product['runtime_validation'], 'NOT_RUN')
        self.assertFalse(product['source_map_evidence'])
        self.assertFalse(product['implementation_approved'])
        self.assertIn('private-account-screen', product_path.read_text())
        repeated = self.generate()
        self.assertEqual(repeated['status'], 'UNCHANGED')
        self.assertEqual(digest(product_path), first_hash)

    def test_recorded_dynamic_evidence_supports_observed_product_items(self):
        self.request['observations'].append({
            'id': 'dynamic', 'question': 'observe the page', 'action': 'browser',
            'operation': 'observe-dom',
        })
        dynamic = dict(self.record, id='dynamic', provenance='DYNAMIC_OBSERVED')
        draft = copy.deepcopy(self.draft)
        draft['screens'][0]['evidence'] = evidence('DYNAMIC_OBSERVED', ['dynamic'])
        draft['flows'][0]['evidence'] = evidence('DYNAMIC_OBSERVED', ['dynamic'])
        product = self.module.generate_product_recon(
            self.root, self.request, self.plan, self.contract,
            [self.record, dynamic], draft)['product']
        self.assertEqual(product['screens'][0]['evidence']['observations'], ['dynamic'])
        self.assertEqual(product['screens'][0]['evidence']['provenance'], 'DYNAMIC_OBSERVED')
        self.assertEqual(product['flows'][0]['evidence']['observations'], ['dynamic'])
        self.assertEqual(product['components'][0]['evidence']['provenance'], 'STATIC_SUPPORTED')

    def test_public_summary_has_no_draft_free_text_and_never_duplicates_block(self):
        product = self.generate()['product']
        from framework_core.reverse_adapters import public_summary
        text = public_summary(self.request, self.plan, [self.record], 'READY', product=product)
        for secret in ('private-account-screen', 'private-screen-purpose', 'private-flow-goal',
                       'private.invalid', 'private-component', 'private_token',
                       'private-account-relationship', 'private-exclusion-reason'):
            self.assertNotIn(secret, text)
        self.assertIn('S01', text)
        self.assertIn('INFERRED', text)
        self.assertIn('PRIVATE_DATA', text)
        self.assertIn('NOT_RUN', text)
        self.assertEqual(text.count('<!-- product-recon:start -->'), 1)
        repeated = public_summary(self.request, self.plan, [self.record], 'READY', product=product)
        self.assertEqual(text, repeated)

    def test_valid_update_is_atomic_and_invalid_update_preserves_previous_output(self):
        auto = self.root / '.framework/local-state/reverse/auto/case'
        observations = auto / 'observations/observe.json'
        observations.parent.mkdir(parents=True)
        observations.write_text(json.dumps(self.record))
        contract_path = auto / 'behavior-contract.json'
        contract_path.write_text(json.dumps(self.contract))
        before_contract = digest(contract_path)
        before_observation = digest(observations)
        result = self.generate()
        product_path = self.root / result['path']
        first_hash = digest(product_path)
        updated = copy.deepcopy(self.draft)
        updated['screens'][0]['name'] = 'updated-private-screen'
        changed = self.generate(updated)
        self.assertEqual(changed['status'], 'UPDATED')
        self.assertNotEqual(digest(product_path), first_hash)
        updated_hash = digest(product_path)
        invalid = copy.deepcopy(updated)
        invalid['flows'][0]['screen_ids'] = ['S99']
        with self.assertRaisesRegex(ValueError, 'INVALID_PRODUCT_RECON'):
            self.generate(invalid)
        self.assertEqual(digest(product_path), updated_hash)
        self.assertEqual(digest(contract_path), before_contract)
        self.assertEqual(digest(observations), before_observation)
        self.assertFalse(list(auto.glob('*.tmp')))
        self.assertFalse(list(auto.glob('.framework-tmp-*')))


class InputBudgetTests(ProductReconCase):
    def test_malformed_oversized_deep_and_symlink_inputs_are_controlled(self):
        malformed = self.root / 'malformed.json'
        malformed.write_text('{')
        with self.assertRaisesRegex(ValueError, 'INVALID_PRODUCT_RECON'):
            self.module.read_product_draft(malformed)
        oversized = self.root / 'oversized.json'
        oversized.write_bytes(b' ' * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, 'PRODUCT_RECON_LIMIT'):
            self.module.read_product_draft(oversized)
        deep = self.root / 'deep.json'
        deep.write_text('[' * 100 + '0' + ']' * 100)
        with self.assertRaisesRegex(ValueError, 'PRODUCT_RECON_LIMIT'):
            self.module.read_product_draft(deep)
        linked = self.root / 'linked.json'
        linked.symlink_to(malformed)
        with self.assertRaisesRegex(ValueError, 'INVALID_PRODUCT_RECON'):
            self.module.read_product_draft(linked)

    def test_collection_item_count_limit_is_controlled(self):
        draft = copy.deepcopy(self.draft)
        draft['components'] = [dict(copy.deepcopy(self.draft['components'][0]),
                                    id='C{:03d}'.format(index)) for index in range(251)]
        draft['screens'][0]['component_ids'] = []
        with self.assertRaisesRegex(ValueError, 'PRODUCT_RECON_LIMIT'):
            self.module.validate_product_draft(draft, self.request, self.plan)


class CliIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cli = importlib.import_module('framework_core.cli')
        self.auto = importlib.import_module('framework_core.reverse_auto')
        self.target = self.root / 'page.html'
        self.target.write_text('<html></html>')
        self.request = request_for(self.target)
        self.request_path = self.root / 'request.json'
        self.request_path.write_text(json.dumps(self.request))

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(argv)
        return code, json.loads(stdout.getvalue())

    def test_cli_dry_run_generation_summary_and_default_compatibility(self):
        base_args = ['reverse', '--target', str(self.root), '--request', str(self.request_path)]
        code, baseline = self.invoke(base_args + ['--dry-run'])
        self.assertEqual(code, 0)
        draft_path = self.root / 'product.json'
        draft_path.write_text(json.dumps(draft_for(baseline['plan_sha256'])))
        code, preview = self.invoke(base_args + ['--dry-run', '--product-recon', str(draft_path)])
        self.assertEqual(code, 0)
        self.assertEqual(preview['plan_sha256'], baseline['plan_sha256'])
        self.assertEqual(preview['product_recon']['status'], 'READY')
        self.assertFalse((self.root / '.framework').exists())
        code, pending = self.invoke(base_args + ['--allow', 'write', '--allow', 'reverse',
                                                  '--product-recon', str(draft_path)])
        self.assertEqual(code, 5)
        code, result = self.invoke(base_args + ['--allow', 'write', '--allow', 'reverse',
                                                '--approve', 'toolchain=' + pending['plan_sha256'],
                                                '--product-recon', str(draft_path)])
        self.assertEqual(code, 0)
        self.assertEqual(result['product_recon']['status'], 'RECORDED')
        product_path = self.root / result['product_recon']['path']
        self.assertTrue(product_path.is_file())
        summary_path = self.root / 'docs/project/reverse/case.md'
        self.assertNotIn('private-account-screen', summary_path.read_text())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(base_args + ['--allow', 'write', '--allow', 'reverse',
                                              '--approve', 'toolchain=' + pending['plan_sha256'],
                                              '--product-recon', str(draft_path), '--summary'])
        self.assertEqual(code, 0)
        self.assertIn('product-recon.json', stdout.getvalue())
        code, default_result = self.invoke(base_args + ['--allow', 'write', '--allow', 'reverse',
                                                        '--approve', 'toolchain=' + pending['plan_sha256']])
        self.assertEqual(code, 0)
        self.assertNotIn('product_recon', default_result)

    def test_non_automatic_actions_reject_product_option_before_writes(self):
        draft_path = self.root / 'product.json'
        draft_path.write_text(json.dumps(draft_for('a' * 64)))
        for argv in (
                ['reverse', '--target', str(self.root), '--dry-run'],
                ['doctor', '--target', str(self.root), '--dry-run']):
            with self.subTest(action=argv[0]):
                code, result = self.invoke(argv + ['--product-recon', str(draft_path)])
                self.assertEqual(code, 2)
                self.assertEqual(result['status'], 'INVALID_INPUT')
                self.assertIn('PRODUCT_RECON_NOT_SUPPORTED', result['error'])
        self.assertFalse((self.root / '.framework').exists())


if __name__ == '__main__':
    unittest.main()
