import contextlib
import hashlib
import importlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core import cli

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def snapshot(root):
    """Every file under root with its content hash."""
    items = {}
    for path in sorted(root.rglob('*')):
        if path.is_file():
            items[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return items


class WorkflowRouteCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = importlib.import_module('framework_core.workflows.catalog')
        write_json(self.root / 'framework-project.json', {'project_id': 'demo', 'agent': 'current'})
        self.request_path = self.root / 'workflow-request.json'
        self.request = {
            'schema': 'workflow-request/v1',
            'operation': 'route',
            'task_category': 'new_behavior',
            'intent': '给订单服务补一个退款接口',
        }
        self.save_request()

    def save_request(self):
        write_json(self.request_path, self.request)

    def route(self):
        return self.catalog.route(self.root, self.request)

    def ids(self, bucket):
        return [entry['id'] for entry in self.route()['classification'][bucket]]


class BusinessProjectRouteTest(WorkflowRouteCase):
    def test_ordinary_development_task_keeps_shell_flows_out(self):
        """WF-01-ROUTE：业务工程的普通开发任务不进入公共壳流程。"""
        before = snapshot(self.root)
        result = self.route()
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['project_role'], 'business')
        self.assertIn('flow-02', self.ids('main'))
        self.assertIn('flow-14', self.ids('not_applicable'))
        self.assertIn('flow-15', self.ids('not_applicable'))
        self.assertIn('flow-06', self.ids('not_applicable'))
        self.assertNotIn('flow-06', self.ids('main'))
        self.assertNotIn('flow-06', self.ids('conditional'))
        self.assertEqual(snapshot(self.root), before)


class ShellRepositoryRouteTest(WorkflowRouteCase):
    def setUp(self):
        super().setUp()
        (self.root / 'framework-project.json').unlink()
        write_json(self.root / 'framework-manifest.json', {'schema': 'framework-manifest/v1', 'files': {}})

    def test_shell_repository_runs_its_own_gates(self):
        """WF-01-SHELL：公共壳仓库自身进入壳验证与发布流程。"""
        result = self.route()
        self.assertEqual(result['project_role'], 'shell')
        self.assertEqual(result['project_role_source'], 'framework-manifest.json')
        self.assertIn('flow-14', self.ids('main'))
        self.assertIn('flow-15', self.ids('conditional'))
        self.assertIn('flow-01', self.ids('not_applicable'))


class InsufficientIntentRouteTest(WorkflowRouteCase):
    def setUp(self):
        super().setUp()
        del self.request['task_category']
        self.request['intent'] = '把那个地方弄好一点'
        self.save_request()

    def test_unknown_intent_asks_for_confirmation_with_read_only_steps(self):
        """WF-01-UNKNOWN：意图不足时报告待确认并给出可继续的只读步骤。"""
        before = snapshot(self.root)
        result = self.route()
        self.assertIsNone(result['task_category'])
        self.assertIn('flow-02', self.ids('needs_confirmation'))
        self.assertIn('flow-14', self.ids('not_applicable'))
        self.assertTrue([action for action in result['next_actions'] if '只读' in action])
        self.assertEqual(snapshot(self.root), before)


class RoleClaimRouteTest(WorkflowRouteCase):
    def test_request_cannot_claim_the_shell_role(self):
        """WF-01-UNKNOWN：声明与目标资料冲突时不得取得公共壳维护路由。"""
        self.request['project_role'] = 'shell'
        self.save_request()
        result = self.route()
        self.assertIsNotNone(result['role_conflict'])
        self.assertNotIn('flow-14', self.ids('main'))
        self.assertIn('flow-14', self.ids('needs_confirmation'))
        self.assertIn('flow-02', self.ids('main'))


class CatalogDriftTest(unittest.TestCase):
    """The catalog must stay the fifteen rows of the tutorial table."""

    def tutorial_rows(self):
        text = (ROOT / 'docs/guide/from-zero-to-one.md').read_text(encoding='utf-8')
        section = text.split('## 15 条一览', 1)[1].split('\n## ', 1)[0]
        rows = {}
        for line in section.splitlines():
            match = re.match(r'^\|\s*(\d+)\s*\|(.+)\|\s*$', line)
            if not match:
                continue
            cells = [cell.strip() for cell in match.group(2).split('|')]
            if len(cells) != 4:
                continue
            rows[int(match.group(1))] = [cell.replace('`', '') for cell in cells]
        return rows

    def test_catalog_matches_the_tutorial_table(self):
        catalog = importlib.import_module('framework_core.workflows.catalog')
        rows = self.tutorial_rows()
        self.assertEqual(sorted(rows), list(range(1, 16)))
        entries = catalog.entries()
        self.assertEqual(len(entries), 15)
        for entry in entries:
            row = rows[entry['row']]
            self.assertEqual(entry['id'], 'flow-%02d' % entry['row'])
            self.assertEqual(entry['name'], row[0])
            self.assertEqual(entry['scope'], row[1])
            self.assertEqual(entry['enters_when'], row[2])
            self.assertEqual(entry['outputs'], row[3])


class FlowCommandTest(WorkflowRouteCase):
    def run_cli(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = cli.main(args)
        return code, json.loads(stdout.getvalue())

    def test_cli_routes_a_request_file(self):
        code, report = self.run_cli(['flow', '--target', str(self.root), '--request', str(self.request_path)])
        self.assertEqual(code, 0)
        self.assertEqual(report['status'], 'READY')
        self.assertIn('flow-02', [entry['id'] for entry in report['classification']['main']])

    def test_cli_rejects_a_foreign_schema(self):
        self.request['schema'] = 'other-request/v1'
        self.save_request()
        code, report = self.run_cli(['flow', '--target', str(self.root), '--request', str(self.request_path)])
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'INVALID_INPUT')


class DevelopmentClassificationTest(WorkflowRouteCase):
    def classify(self, **overrides):
        request = {
            'task_category': 'new_behavior',
            'modifies_files': True,
            'acceptance_impact': 'none',
            'existing_scenario': None,
        }
        request.update(overrides)
        return self.catalog.classify_development(self.root, request)

    def test_link_only_change_stays_a_document_check(self):
        """WF-03-DOC：只改链接走文档验证。"""
        result = self.classify(task_category='pure_doc', acceptance_impact='none')
        self.assertEqual(result['route'], 'pure_doc')
        self.assertEqual(result['flows'], ['flow-02'])

    def test_document_change_to_acceptance_goes_to_spec(self):
        """WF-03-DOC：通过文档改变公开接口或验收进入规格流程。"""
        result = self.classify(task_category='pure_doc', acceptance_impact='acceptance')
        self.assertEqual(result['route'], 'new_behavior')

    def test_restoring_a_known_scenario_returns_the_fix_route(self):
        """WF-03-FIX：恢复已有明确场景返回复现与回归要求。"""
        result = self.classify(task_category='spec_fix', existing_scenario='WF-02-ALLOW')
        self.assertEqual(result['route'], 'spec_fix')
        self.assertTrue([action for action in result['next_actions'] if 'RED' in action or '复现' in action])

    def test_read_only_task_is_an_audit(self):
        """WF-03-DOC：不修改文件的请求归只读审计。"""
        result = self.classify(modifies_files=False)
        self.assertEqual(result['route'], 'read_only_audit')

    def test_knowledge_ingestion_is_left_to_the_catalog(self):
        """WF-03-SCOPE：知识摄入不由日常开发四类承接。"""
        result = self.classify(task_category='knowledge_ingestion')
        self.assertEqual(result['route'], 'catalog')
        self.assertEqual(result['flows'], ['flow-05'])

    def test_release_task_is_left_to_the_catalog(self):
        """WF-03-SCOPE：设备与发布不由日常开发四类承接。"""
        result = self.classify(task_category='device_release')
        self.assertEqual(result['route'], 'catalog')
        self.assertEqual(result['flows'], ['flow-13', 'flow-11', 'flow-12'])

    def test_unclear_facts_keep_read_only_exploration(self):
        """WF-03：意图不明时继续只读探索。"""
        result = self.classify(acceptance_impact=None)
        self.assertEqual(result['route'], 'needs_confirmation')
        self.assertTrue([action for action in result['next_actions'] if '只读' in action])

    def test_local_rules_of_the_target_directory_are_reported(self):
        """WF-03：读取目标目录适用的局部规则。"""
        module = self.root / 'module'
        module.mkdir()
        (self.root / 'AGENTS.md').write_text('# 根规则\n', encoding='utf-8')
        (module / 'AGENTS.md').write_text('# 模块规则\n', encoding='utf-8')
        result = self.classify(target='module')
        self.assertEqual(result['local_rules'], ['AGENTS.md', 'module/AGENTS.md'])

    def test_route_report_carries_the_development_route(self):
        """WF-03：路由输出同时给出日常开发四类的分流结果。"""
        self.request.update({'task_category': 'pure_doc', 'modifies_files': True,
                              'acceptance_impact': 'none'})
        self.save_request()
        result = self.route()
        self.assertEqual(result['development']['route'], 'pure_doc')
        self.assertEqual(result['development']['flows'], ['flow-02'])


class GuideConsistencyTest(unittest.TestCase):
    """The published guide must state the same routes the router returns."""

    def guide_rows(self):
        text = (ROOT / 'docs/guide/daily-development.md').read_text(encoding='utf-8')
        section = text.split('## 按任务分流', 1)[1].split('\n## ', 1)[0]
        rows = []
        for line in section.splitlines():
            match = re.match(r'^\|\s*([^|]+?)\s*\|(.+)\|\s*$', line)
            if not match:
                continue
            cells = [cell.strip() for cell in match.group(2).split('|')]
            if len(cells) != 3:
                continue
            if all(cell.startswith('-') for cell in cells):
                continue
            if match.group(1).strip() == '任务':
                continue
            rows.append((match.group(1).strip(), cells))
        return rows

    def test_guide_rows_match_the_catalog_routes(self):
        catalog = importlib.import_module('framework_core.workflows.catalog')
        routes = {route['route']: route for route in catalog.development_routes()}
        rows = self.guide_rows()
        self.assertEqual(len(rows), 5)
        for name, cells in rows[:4]:
            route_id = cells[0].strip('`')
            self.assertIn(route_id, routes)
            self.assertEqual(routes[route_id]['path'], cells[1])
            self.assertEqual(routes[route_id]['evidence'], cells[2])
        self.assertIn('flow-05', rows[4][1][0])
