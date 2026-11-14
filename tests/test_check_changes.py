"""A completed change must reach the spec store, the knowledge receipt, and the archive."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def load_tool():
    loader = importlib.machinery.SourceFileLoader('checkt', str(ROOT / 'tools/check-changes'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def make_change(root, name, done, todo, capability=None, synced=False, skip_specs=False):
    change = root / 'openspec' / 'changes' / name
    change.mkdir(parents=True)
    lines = ['## 1. Work', '']
    lines += ['- [x] %d.1 step' % i for i in range(1, done + 1)]
    lines += ['- [ ] %d.1 step' % i for i in range(1, todo + 1)]
    (change / 'tasks.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    meta = 'schema: spec-driven\ncreated: 2026-11-01\n'
    if skip_specs:
        meta += 'skip_specs: true\n'
    (change / '.openspec.yaml').write_text(meta, encoding='utf-8')
    if capability:
        spec = change / 'specs' / capability
        spec.mkdir(parents=True)
        (spec / 'spec.md').write_text(
            '## Purpose\n\nx\n\n## ADDED Requirements\n\n### Requirement: R\ntext\n', encoding='utf-8')
    if synced and capability:
        target = root / 'openspec' / 'specs' / capability
        target.mkdir(parents=True)
        (target / 'spec.md').write_text(
            '# %s Specification\n\n## Purpose\n\nx\n\n## Requirements\n\n### Requirement: R\ntext\n' % capability,
            encoding='utf-8')


PAGE_DIRS = {'requirement': 'requirements', 'problem': 'problems', 'concept': 'concepts'}


def page_body(digest, kind='requirement', applies=None, not_applies=None, extra=None, status='approved'):
    """A knowledge page whose frontmatter records the digest and, where the
    kind demands it, the conditions the conclusion holds under."""
    fields = ['type: %s' % kind, 'artifact_kind: %s' % kind, 'created: 2026-11-01',
              'confidence: EXTRACTED', 'status: %s' % status, 'source_sha256: %s' % digest]
    if applies is not None:
        fields.append('applies_when: %s' % applies)
    if not_applies is not None:
        fields.append('not_applicable_when: %s' % not_applies)
    fields.extend(extra or [])
    return '---\n' + '\n'.join(fields) + '\n---\n\n正文\n'


def install_receipt(root, name, capability, digest=None, page_kind='requirement',
                     source_rel=None, problem=None, schema=None, influenced=None):
    """Put a project alias, one page, and a receipt into a fixture repository."""
    source_rel = source_rel or ('openspec/specs/%s/spec.md' % capability)
    source = root / source_rel
    if digest is None:
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
    (root / 'llm-wiki-aliases.json').write_text(
        json.dumps({'project': 'knowledge/project'}) + '\n', encoding='utf-8')
    page_rel = 'knowledge/project/wiki/topics/%s/%s.md' % (
        PAGE_DIRS.get(page_kind, 'problems'), capability)
    page = root / page_rel
    page.parent.mkdir(parents=True, exist_ok=True)
    applies = 'X 分支' if page_kind in ('problem', 'concept') else None
    not_applies = 'Y 非空' if page_kind == 'problem' else None
    page.write_text(page_body(digest, page_kind, applies, not_applies), encoding='utf-8')
    if problem is None:
        problem = {'status': 'not_applicable', 'reason': 'no verified problem'}
    receipt = {
        'change': name,
        'alias': 'project',
        'pages': [{
            'path': page_rel,
            'artifact_kind': page_kind,
            'source_path': source_rel,
            'source_sha256': digest,
        }],
        'problem': problem,
    }
    if schema is not None:
        receipt['schema'] = schema
    if influenced is not None:
        receipt['influenced'] = influenced
    change = root / 'openspec' / 'changes' / name
    (change / 'knowledge-receipt.json').write_text(
        json.dumps(receipt, ensure_ascii=False) + '\n', encoding='utf-8')
    return receipt


class OutstandingChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()

    def test_incomplete_change_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'wip', done=2, todo=3, capability='demo')
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_change_without_tasks_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            change = root / 'openspec' / 'changes' / 'no-tasks'
            change.mkdir(parents=True)
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_completed_change_with_unsynced_capability_is_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('not synced', findings[0]['problem'])
            self.assertIn('demo-cap', findings[0]['detail'])

    def test_completed_and_synced_change_without_a_knowledge_base_is_not_configured(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('NOT_CONFIGURED', findings[0]['detail'])
            self.assertFalse((root / 'knowledge').exists())
            self.assertFalse((root / 'llm-wiki-aliases.json').exists())

    def test_completed_synced_change_with_a_receipt_must_be_archived(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_missing_receipt_is_outstanding_when_the_knowledge_base_exists(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            (root / 'llm-wiki-aliases.json').write_text(
                '{"project": "knowledge/project"}\n', encoding='utf-8')
            (root / 'knowledge' / 'project').mkdir(parents=True)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('knowledge-receipt.json', findings[0]['detail'])

    def test_a_source_hash_mismatch_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap', digest='0' * 64)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('source_sha256', findings[0]['detail'])

    def test_a_verified_problem_requires_a_problem_page(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap')
            record = {'id': 'p-1', 'conclusion': 'pass', 'evidence': 'unit', 'limits': 'none'}
            change = root / 'openspec' / 'changes' / 'done'
            (change / 'verified-problem.json').write_text(json.dumps(record) + '\n', encoding='utf-8')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('problem page', findings[0]['detail'])

    def test_a_verified_problem_page_lets_the_change_wait_for_archive(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap')
            change = root / 'openspec' / 'changes' / 'done'
            record = {'id': 'p-1', 'conclusion': 'pass', 'evidence': 'unit', 'limits': 'root cause remains'}
            (change / 'verified-problem.json').write_text(json.dumps(record) + '\n', encoding='utf-8')
            source_rel = 'openspec/changes/done/verified-problem.json'
            digest = hashlib.sha256((change / 'verified-problem.json').read_bytes()).hexdigest()
            page_rel = 'knowledge/project/wiki/topics/problems/p-1.md'
            page = root / page_rel
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(page_body(digest, 'problem', 'X 分支', 'Y 非空'), encoding='utf-8')
            receipt = json.loads((change / 'knowledge-receipt.json').read_text(encoding='utf-8'))
            receipt['pages'].append({
                'path': page_rel,
                'artifact_kind': 'problem',
                'source_path': source_rel,
                'source_sha256': digest,
            })
            receipt['problem'] = {'status': 'recorded', 'reason': 'verified problem'}
            (change / 'knowledge-receipt.json').write_text(json.dumps(receipt) + '\n', encoding='utf-8')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_without_a_verified_problem_not_applicable_is_accepted(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, skip_specs=True)
            (root / 'llm-wiki-aliases.json').write_text(
                '{"project": "knowledge/project"}\n', encoding='utf-8')
            (root / 'knowledge' / 'project').mkdir(parents=True)
            receipt = {
                'change': 'done',
                'alias': 'project',
                'pages': [],
                'problem': {'status': 'not_applicable', 'reason': 'no verified problem'},
            }
            change = root / 'openspec' / 'changes' / 'done'
            (change / 'knowledge-receipt.json').write_text(json.dumps(receipt) + '\n', encoding='utf-8')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def add_receipt_page(self, root, name, page_rel, kind, source_rel, digest, body):
        """Attach one more page to the receipt of a fixture change."""
        page = root / page_rel
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(body, encoding='utf-8')
        change = root / 'openspec' / 'changes' / name
        receipt = json.loads((change / 'knowledge-receipt.json').read_text(encoding='utf-8'))
        receipt['pages'].append({
            'path': page_rel,
            'artifact_kind': kind,
            'source_path': source_rel,
            'source_sha256': digest,
        })
        (change / 'knowledge-receipt.json').write_text(
            json.dumps(receipt, ensure_ascii=False) + '\n', encoding='utf-8')

    def glossary(self, root):
        path = root / 'docs/project/GLOSSARY.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# 术语表\n\n- 任务：本工程内的任务\n', encoding='utf-8')
        return path

    def test_a_problem_page_without_applicability_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            change = root / 'openspec' / 'changes' / 'done'
            record = {'id': 'p-1', 'conclusion': 'pass', 'evidence': 'unit', 'limits': 'none'}
            (change / 'verified-problem.json').write_text(json.dumps(record) + '\n', encoding='utf-8')
            source_rel = 'openspec/changes/done/verified-problem.json'
            digest = hashlib.sha256((change / 'verified-problem.json').read_bytes()).hexdigest()
            install_receipt(root, 'done', 'demo-cap')
            self.add_receipt_page(root, 'done', 'knowledge/project/wiki/topics/problems/p-1.md',
                                  'problem', source_rel, digest,
                                  page_body(digest, 'problem', None, 'Y 非空'))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('applies_when', findings[0]['detail'])

    def test_a_concept_page_from_the_glossary_is_accepted(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            glossary = self.glossary(root)
            digest = hashlib.sha256(glossary.read_bytes()).hexdigest()
            install_receipt(root, 'done', 'demo-cap')
            self.add_receipt_page(root, 'done', 'knowledge/project/wiki/topics/concepts/task.md',
                                  'concept', 'docs/project/GLOSSARY.md', digest,
                                  page_body(digest, 'concept', '本工程内指该术语时', None))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_a_concept_page_from_an_unverifiable_source_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            other = root / 'notes/arbitrary.md'
            other.parent.mkdir(parents=True, exist_ok=True)
            other.write_text('随手写的\n', encoding='utf-8')
            digest = hashlib.sha256(other.read_bytes()).hexdigest()
            install_receipt(root, 'done', 'demo-cap')
            self.add_receipt_page(root, 'done', 'knowledge/project/wiki/topics/concepts/task.md',
                                  'concept', 'notes/arbitrary.md', digest,
                                  page_body(digest, 'concept', '本工程内指该术语时', None))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('concept source', findings[0]['detail'])

    def test_a_concept_page_without_applicability_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            glossary = self.glossary(root)
            digest = hashlib.sha256(glossary.read_bytes()).hexdigest()
            install_receipt(root, 'done', 'demo-cap')
            self.add_receipt_page(root, 'done', 'knowledge/project/wiki/topics/concepts/task.md',
                                  'concept', 'docs/project/GLOSSARY.md', digest,
                                  page_body(digest, 'concept', None, None))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('applies_when', findings[0]['detail'])

    def test_a_requirement_page_needs_no_applicability(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def rewrite_page(self, root, receipt, index, body):
        path = root / receipt['pages'][index]['path']
        path.write_text(body, encoding='utf-8')

    def test_a_superseded_page_without_a_successor_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='superseded'))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('superseded', findings[0]['detail'])

    def test_a_superseded_page_pointing_at_a_missing_page_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='superseded',
                                        extra=['superseded_by: wiki/topics/problems/nowhere.md']))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('superseded', findings[0]['detail'])

    def test_a_superseded_page_with_a_real_successor_is_accepted(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            successor = 'knowledge/project/wiki/topics/problems/newer.md'
            (root / successor).parent.mkdir(parents=True, exist_ok=True)
            (root / successor).write_text(page_body(digest, 'problem', 'X 分支', 'Y 非空'), encoding='utf-8')
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='superseded',
                                        extra=['superseded_by: wiki/topics/problems/newer.md']))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_a_retracted_page_without_a_reason_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='retracted'))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('retraction reason', findings[0]['detail'])

    def test_a_retracted_page_with_a_reason_is_accepted(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='retracted',
                                        extra=['retraction_reason: 根因被证伪']))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_a_live_page_may_not_quote_a_voided_page(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            digest = receipt['pages'][0]['source_sha256']
            voided = 'knowledge/project/wiki/topics/problems/old.md'
            (root / voided).parent.mkdir(parents=True, exist_ok=True)
            (root / voided).write_text(
                page_body(digest, 'problem', 'X 分支', 'Y 非空', status='retracted',
                          extra=['retraction_reason: 根因被证伪']), encoding='utf-8')
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement',
                                        applies='见 wiki/topics/problems/old.md'))
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('voided', findings[0]['detail'])

    def test_a_v2_receipt_without_influence_is_outstanding(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('took effect', findings[0]['detail'])

    def test_a_v2_receipt_may_declare_influence_not_applicable_with_a_reason(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2',
                            influenced={'status': 'not_applicable', 'reason': 'the change touched no code'})
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_a_v2_receipt_influence_must_point_at_a_page_in_the_receipt(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2',
                            influenced=[{'page': 'knowledge/project/wiki/topics/problems/elsewhere.md',
                                         'task_id': '1.1', 'file': 'src/a.py', 'assertion': 'test_a'}])
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('not in the receipt', findings[0]['detail'])

    def test_a_v2_receipt_influence_must_point_at_a_task_that_exists(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2')
            install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2',
                            influenced=[{'page': receipt['pages'][0]['path'], 'task_id': '9.9',
                                         'file': 'src/a.py', 'assertion': 'test_a'}])
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('task that does not exist', findings[0]['detail'])

    def test_a_v2_receipt_with_matching_influence_is_accepted(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            install_receipt(root, 'done', 'demo-cap', schema='knowledge-receipt/v2',
                            influenced=[{'page': receipt['pages'][0]['path'], 'task_id': '1.1',
                                         'file': 'src/a.py', 'assertion': 'test_a'}])
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_a_v1_receipt_is_not_retroactively_required_to_record_influence(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            install_receipt(root, 'done', 'demo-cap')
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('still active', findings[0]['problem'])

    def test_the_doctor_reports_knowledge_references(self):
        from framework_core.readiness import knowledge_status
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            orphan = 'knowledge/project/wiki/topics/problems/orphan.md'
            (root / orphan).parent.mkdir(parents=True, exist_ok=True)
            (root / orphan).write_text(page_body('0' * 64, 'problem', 'X', 'Y'), encoding='utf-8')
            (root / 'knowledge/project/.wiki-schema.md').write_text(
                'Topic: synthetic\nLanguage: en\n', encoding='utf-8')
            knowledge = knowledge_status(root)
            self.assertEqual(knowledge['status'], 'SCAFFOLDED')
            self.assertEqual(knowledge['references']['wiki/topics/requirements/demo-cap.md'], 1)
            self.assertEqual(knowledge['references']['wiki/topics/problems/orphan.md'], 0)
            self.assertIn('wiki/topics/problems/orphan.md', knowledge['never_referenced'])

    def test_the_doctor_lists_the_downstream_of_a_page_under_review(self):
        from framework_core.readiness import knowledge_status
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap', synced=True)
            receipt = install_receipt(root, 'done', 'demo-cap')
            (root / 'knowledge/project/.wiki-schema.md').write_text(
                'Topic: synthetic\nLanguage: en\n', encoding='utf-8')
            digest = receipt['pages'][0]['source_sha256']
            quoted = 'knowledge/project/wiki/topics/problems/quoted.md'
            (root / quoted).parent.mkdir(parents=True, exist_ok=True)
            (root / quoted).write_text(
                page_body(digest, 'problem', '见 wiki/topics/requirements/demo-cap.md', 'Y 非空'),
                encoding='utf-8')
            self.rewrite_page(root, receipt, 0,
                              page_body(digest, 'requirement', status='needs-review'))
            knowledge = knowledge_status(root)
            self.assertIn('wiki/topics/requirements/demo-cap.md', knowledge['under_review'])
            self.assertIn('wiki/topics/problems/quoted.md', knowledge['under_review']['wiki/topics/requirements/demo-cap.md'])

    def test_archived_change_is_never_flagged(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=2, todo=0, capability='demo-cap')
            archive = root / 'openspec' / 'changes' / 'archive'
            archive.mkdir(parents=True)
            (root / 'openspec' / 'changes' / 'done').rename(archive / 'done')
            self.assertEqual(self.tool.find_outstanding(root), [])

    def test_skip_specs_change_without_a_knowledge_base_is_not_configured(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, skip_specs=True)
            findings = self.tool.find_outstanding(root)
            self.assertEqual(len(findings), 1)
            self.assertIn('NOT_CONFIGURED', findings[0]['detail'])
            self.assertFalse((root / 'knowledge').exists())

    def test_tool_exits_non_zero_on_findings(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, capability='demo-cap')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools/check-changes'), '--root', str(root)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('FAIL', result.stdout)

    def test_tool_reports_json_when_asked(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / 'repo'
            make_change(root, 'done', done=1, todo=0, capability='demo-cap')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools/check-changes'), '--root', str(root), '--json'],
                capture_output=True, text=True)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['status'], 'FAIL')
            self.assertEqual(payload['outstanding'][0]['change'], 'done')

    def test_this_repository_has_no_outstanding_change(self):
        self.assertEqual(self.tool.find_outstanding(ROOT), [])


if __name__ == '__main__':
    unittest.main()
