import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_checker():
    loader = importlib.machinery.SourceFileLoader('checker', str(ROOT / 'tools/check-framework'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


checker = load_checker()


CONTRACT = """# 流程契约

## 8. IMPLEMENT — 实现与任务验证

**技能**:`matt-pocock:tdd`。
1. RED:写测试。
2. GREEN:最小实现。
3. REFACTOR:必要整理。
4. REGRESSION:跑回归。
5. TASK_VERIFIED:核对证据。

## 12. 交付与收尾

完整行为变更路线:
```text
DISCOVERY → SPEC_VALIDATED
→ (TASK_SELECTED → RED → GREEN → REFACTOR → REGRESSION → TASK_VERIFIED)*
→ REVIEWED → ARCHIVED
```
"""

CONTRACT_WITHOUT_REGRESSION = CONTRACT.replace(
    "→ REFACTOR → REGRESSION → TASK_VERIFIED)*",
    "→ REFACTOR → TASK_VERIFIED)*",
)

GUIDE = """# 指南

## 工作流 14：公共工程壳验证与 CI

### 流程

```text
公共壳变更 → python3 tools/check-framework → 全量 unittest
→ openspec validate --all --strict → openspec validate --archived
→ python3 tools/check-changes → git diff --check
```

## 工作流 15：公共工程壳版本发布

定时为每周一 02:17 UTC，即北京时间 10:17。
"""

GUIDE_WITHOUT_CHANGE_GATE = GUIDE.replace("→ python3 tools/check-changes → ", "")

VALIDATE = """name: Validate
on: [push]
jobs:
  validate:
    steps:
      - uses: actions/checkout@v7
      - name: Install pinned OpenSpec CLI
        run: npm install --global @fission-ai/openspec@1.13.2
      - run: python3 tools/check-framework
      - run: python3 -m unittest discover -s tests -v
      - name: Validate active changes and main specs
        run: openspec validate --all --strict --no-interactive
      - name: Validate archived changes have completed tasks
        run: openspec validate --archived --no-interactive
      - name: Report completed changes that were never archived
        run: python3 tools/check-changes
      - name: Check whitespace errors in this change
        run: |
          git diff --check "$BASE" HEAD
"""

RELEASE = """name: Release
on:
  schedule:
    # GitHub recommends avoiding the top of the hour.
    - cron: '17 2 * * 1'
"""

SCHEDULE_OK = "定时为每周一 02:17 UTC，即北京时间 10:17。"
SCHEDULE_STALE = "定时为每周一 02:00 UTC，即北京时间 10:00。"
UNRELATED_UTC = "构建在 03:00 UTC 开始，与发布调度无关。"


class DocContractTests(unittest.TestCase):
    def make_root(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        return root

    def test_current_repository_satisfies_the_document_contract(self):
        manifest = (ROOT / 'framework-manifest.json').read_text(encoding='utf-8')
        import json
        files = list(json.loads(manifest)['files'])
        self.assertEqual(checker.doc_contract_errors(ROOT, files), [])

    def test_summary_line_must_cover_the_implementation_steps(self):
        self.assertEqual(checker._summary_step_errors(CONTRACT), [])
        errors = checker._summary_step_errors(CONTRACT_WITHOUT_REGRESSION)
        self.assertEqual(len(errors), 1)
        self.assertIn('REGRESSION', errors[0])

    def test_guide_must_list_every_gate_ci_runs(self):
        self.assertEqual(checker._guide_gate_errors(GUIDE, VALIDATE), [])
        errors = checker._guide_gate_errors(GUIDE_WITHOUT_CHANGE_GATE, VALIDATE)
        self.assertEqual(len(errors), 1)
        self.assertIn('check-changes', errors[0])

    def test_a_live_document_must_state_the_scheduled_time(self):
        root = self.make_root({'docs/guide/from-zero-to-one.md': SCHEDULE_STALE})
        errors = checker._schedule_time_errors(root, ['docs/guide/from-zero-to-one.md'], RELEASE)
        self.assertEqual(len(errors), 2)
        self.assertIn('02:00', errors[0])
        self.assertIn('10:00', errors[1])

    def test_a_correct_schedule_passes(self):
        root = self.make_root({'docs/guide/from-zero-to-one.md': SCHEDULE_OK})
        errors = checker._schedule_time_errors(root, ['docs/guide/from-zero-to-one.md'], RELEASE)
        self.assertEqual(errors, [])

    def test_an_unrelated_utc_time_is_not_read_as_a_schedule(self):
        root = self.make_root({'docs/guide/other.md': UNRELATED_UTC})
        errors = checker._schedule_time_errors(root, ['docs/guide/other.md'], RELEASE)
        self.assertEqual(errors, [])

    def test_historical_documents_are_not_scanned(self):
        files = {
            'CHANGELOG.md': SCHEDULE_STALE,
            'docs/archive/plans/old.md': SCHEDULE_STALE,
            'openspec/changes/archive/old/spec.md': SCHEDULE_STALE,
            'openspec/changes/active/proposal.md': SCHEDULE_STALE,
        }
        root = self.make_root(files)
        errors = checker._schedule_time_errors(root, list(files), RELEASE)
        self.assertEqual(errors, [])

    def test_gates_are_derived_from_the_ci_workflow(self):
        gates, unknown = checker._ci_gates(VALIDATE)
        self.assertEqual(gates, [
            'check-framework',
            'unittest',
            'openspec validate --all',
            'openspec validate --archived',
            'check-changes',
            'git diff --check',
        ])
        self.assertEqual(unknown, [])

    def test_a_new_gate_is_picked_up_without_editing_the_checker(self):
        extended = VALIDATE.replace(
            '      - name: Report completed changes that were never archived\n',
            '      - run: python3 tools/check-manifest\n'
            '      - name: Report completed changes that were never archived\n',
        )
        gates, unknown = checker._ci_gates(extended)
        self.assertIn('check-manifest', gates)
        self.assertEqual(unknown, [])

    def test_an_unrecognised_ci_step_is_reported(self):
        extended = VALIDATE.replace(
            '      - run: python3 tools/check-framework\n',
            '      - run: python3 tools/check-framework\n      - run: echo something-new\n',
        )
        gates, unknown = checker._ci_gates(extended)
        self.assertNotIn('echo something-new', gates)
        self.assertEqual(len(unknown), 1)
        self.assertIn('echo something-new', unknown[0])

    def test_the_expected_time_follows_the_cron_expression(self):
        moved = RELEASE.replace("'17 2 * * 1'", "'42 9 * * 1'")
        root = self.make_root({'docs/guide/from-zero-to-one.md': SCHEDULE_OK})
        errors = checker._schedule_time_errors(root, ['docs/guide/from-zero-to-one.md'], moved)
        self.assertEqual(len(errors), 2)
        self.assertIn('09:42', errors[0])
        self.assertIn('17:42', errors[1])

    def test_a_missing_section_is_reported_instead_of_passing_silently(self):
        errors = checker._guide_gate_errors("# 指南\n\n没有工作流小节。\n", VALIDATE)
        self.assertEqual(len(errors), 1)
        self.assertIn('verification workflow section not found', errors[0])


class StatusVocabularyTests(unittest.TestCase):
    def make_root(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        return root

    def marked(self, body):
        return (checker.DICTIONARY_START + '\n' + body + '\n' + checker.DICTIONARY_END + '\n')

    def test_the_shipped_guides_state_only_real_status_codes(self):
        import json
        files = list(json.loads((ROOT / 'framework-manifest.json').read_text(encoding='utf-8'))['files'])
        self.assertEqual(checker.status_dictionary_errors(ROOT, files), [])

    def test_an_invented_status_code_is_reported(self):
        files = {
            'docs/guide/from-zero-to-one.md': self.marked('| `MADE_UP_STATE` | 编造的状态 |\n'),
            'docs/guide/framework-model.md': self.marked('| `READY` | 就绪 |\n'),
            'tools/framework_core/ready.py': "STATUS = 'READY'\n",
        }
        root = self.make_root(files)
        errors = checker.status_dictionary_errors(root, list(files))
        self.assertEqual(len(errors), 1)
        self.assertIn('MADE_UP_STATE', errors[0])

    def test_an_unmarked_status_table_is_reported(self):
        files = {
            'docs/guide/from-zero-to-one.md': '| `READY` | 就绪 |\n',
            'docs/guide/framework-model.md': self.marked('| `READY` | 就绪 |\n'),
            'tools/framework_core/ready.py': "STATUS = 'READY'\n",
        }
        root = self.make_root(files)
        errors = checker.status_dictionary_errors(root, list(files))
        self.assertEqual(len(errors), 1)
        self.assertIn('not marked for checking', errors[0])

    def test_a_missing_guide_is_reported(self):
        files = {'tools/framework_core/ready.py': "STATUS = 'READY'\n"}
        root = self.make_root(files)
        errors = checker.status_dictionary_errors(root, list(files))
        self.assertEqual(len(errors), 2)
        self.assertTrue(all('missing' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
