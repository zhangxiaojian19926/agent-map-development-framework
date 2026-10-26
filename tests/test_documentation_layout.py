from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationLayoutTests(unittest.TestCase):
    def test_readme_separates_user_and_maintainer_paths(self):
        text = (ROOT / 'README.md').read_text()
        self.assertIn('## 使用工程壳开发软件', text)
        self.assertIn('## 开发公共工程壳', text)
        for rel in (
            'BOOTSTRAP.md', 'templates/PROJECT-START.md',
            'docs/guide/project-layout.md', 'docs/guide/daily-development.md',
            'docs/maintainer/repository-layout.md', 'docs/maintainer/verification.md',
            'docs/maintainer/release.md', 'docs/archive/README.md',
        ):
            self.assertIn('(' + rel + ')', text)
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_development_guides_have_complete_flow_cards(self):
        for name in ('daily-development', 'module-lifecycle', 'testing-and-delivery', 'framework-upgrade'):
            with self.subTest(guide=name):
                text = (ROOT / 'docs/guide' / (name + '.md')).read_text()
                self.assertIn('## 流程卡', text)
                for field in ('输入', '写入范围', '授权', '验证证据', '完成状态'):
                    self.assertIn('| ' + field + ' |', text)
        daily = (ROOT / 'docs/guide/daily-development.md').read_text()
        for route in ('查询、解释、审计', '纯文档', '既有规格缺陷', '新行为或接口'):
            self.assertIn(route, daily)

    def test_archive_is_linked_and_every_document_is_marked_historical(self):
        archive = ROOT / 'docs/archive'
        index = (archive / 'README.md').read_text()
        self.assertIn('不是当前操作说明、活跃任务状态或发布结论', index)
        documents = sorted(path for path in archive.rglob('*.md') if path.name != 'README.md')
        self.assertGreaterEqual(len(documents), 4)
        for path in documents:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                relative = path.relative_to(archive).as_posix()
                self.assertIn('](' + relative + ')', index)
                heading = path.read_text().splitlines()[:5]
                self.assertTrue(any('历史' in line and '不是现行操作说明' in line for line in heading))

    def test_legacy_reconciliation_preserves_not_run_boundaries(self):
        text = (ROOT / 'docs/maintainer/legacy-change-status.md').read_text()
        for change in ('add-project-bootstrap-and-maps', 'agent-led-project-intake'):
            self.assertIn(change, text)
        self.assertIn('NOT_RUN', text)
        self.assertIn('没有勾选旧任务，没有执行规格同步或归档', text)
        self.assertIn('84a5caae73e4cb60f773245127e0d1a37693bda6', text)
        self.assertIn('40249970950', text)


if __name__ == '__main__':
    unittest.main()
