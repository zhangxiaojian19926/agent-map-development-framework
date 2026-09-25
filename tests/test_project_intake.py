"""User input must not silently rename, truncate, or authorize modules."""
import importlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.intake'),
                             'Named project intake is not implemented')
        self.api = importlib.import_module('framework_core.intake')

    def test_pairs_preserve_names_and_whole_urls(self):
        request = self.api.parse_request('设备端 = https://example.com/a/same.git\n服务端: git@example.com:b/same.git\n项目：https://example.com/c.git', 'demo')
        self.assertEqual(request['mode'], 'remote-modules')
        self.assertEqual([m['path'] for m in request['modules']], ['modules/设备端', 'modules/服务端', 'modules/项目'])
        self.assertEqual(request['modules'][1]['source_url'], 'git@example.com:b/same.git')

    def test_markdown_and_new_requirements(self):
        request = self.api.parse_request('# 工程启动单\n项目：家务\n目标：本地任务管理\n仓库：暂无', 'demo')
        self.assertEqual(request['mode'], 'new')
        self.assertEqual(request['project'], {'name': '家务', 'goal': '本地任务管理'})
        request = self.api.parse_request('# 工程启动单\n项目：家务\n## 模块仓库\n服务端 = https://example.com/a.git\n## 来源版本\n服务端 = branch:release/2.x', 'demo')
        self.assertEqual(request['modules'][0]['requested_ref'], {'kind': 'branch', 'value': 'release/2.x'})

    def test_invalid_input_never_becomes_new_project(self):
        for text in ('', '# 工程启动单\n目标：x\n## 模块仓库\nbroken',
                     'api=', 'api=x', 'api=https://u:secret@example.com/a',
                     'api=https://token@example.com/a', 'api=https://example.com/a?token=secret',
                     '../outside=https://example.com/a', 'CON=https://example.com/a',
                     'a/b=https://example.com/a', 'a\\b=https://example.com/a',
                     'a.=https://example.com/a', 'a\x00=https://example.com/a'):
            with self.subTest(text=text), self.assertRaises(ValueError) as caught:
                self.api.parse_request(text, 'demo')
            self.assertNotIn('secret', str(caught.exception))

    def test_duplicates_case_unicode_and_id_collision(self):
        for names in [('api', 'api'), ('Api', 'api'), ('é', 'e\u0301')]:
            text = '\n'.join(n + '=https://example.com/a' for n in names)
            with self.subTest(names=names), self.assertRaisesRegex(ValueError, 'NAME_CONFLICT.*line'):
                self.api.parse_request(text, 'demo')
        with self.assertRaisesRegex(ValueError, 'lines 1,2'):
            self.api.parse_request('api=https://example.com/a\napi=https://example.com/b', 'demo')
        with patch.object(self.api.hashlib, 'sha256') as hashing:
            hashing.return_value.hexdigest.return_value = 'a' * 64
            with self.assertRaisesRegex(ValueError, 'NAME_CONFLICT'):
                self.api.parse_request('设备=https://example.com/a\n服务=https://example.com/b', 'demo')

    def test_reordering_and_same_source_do_not_change_identity(self):
        rows = ['设备=https://example.com/same', 'api=https://example.com/same']
        one = self.api.parse_request('\n'.join(rows), 'demo')['modules']
        two = self.api.parse_request('\n'.join(reversed(rows)), 'demo')['modules']
        self.assertEqual(one, list(reversed(two)))
        self.assertNotEqual(one[0]['id'], one[1]['id'])
        self.assertEqual(one[1]['id'], 'api')

    def test_local_sources_need_current_grant(self):
        with self.assertRaises(ValueError):
            self.api.parse_request('api=/tmp/source', 'demo')
        request = self.api.parse_request('api=/tmp/source', 'demo', {'local-clone'})
        self.assertEqual(request['modules'][0]['source_url'], '/tmp/source')

    def test_direct_identity_rejects_unsafe_names(self):
        for name in ('a ', ' ', '.', '..', 'nul.txt', 'LPT1', 'a:b', 'a\n', '/x'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.api.module_identity(name)

    def test_invalid_project_name_rejected_during_parse(self):
        with self.assertRaises(ValueError):
            self.api.parse_request('# 工程启动单\n项目：../oops\n## 模块仓库\napi=https://example.com/a', 'demo')

    def test_configured_target_rejected_during_plan_without_writes(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            target = base/'project'
            target.mkdir()
            request = self.api.parse_request('api=https://example.com/a', 'demo')
            for config in ({'project_id': 'old'}, {'project_id': 'old', 'intake_id': 'another-plan'}):
                with self.subTest(config=config):
                    path = target/'framework-project.json'
                    path.write_text(json.dumps(config))
                    before = path.read_bytes()
                    with self.assertRaisesRegex(ValueError, 'CONFLICT'):
                        self.api.plan_intake(request, target, base/'launch', base/'dist')
                    self.assertEqual(path.read_bytes(), before)
                    self.assertFalse((base/'launch').exists())
                    self.assertFalse((target/'modules').exists())

    def test_launch_plan_preview_permission_and_snapshot(self):
        self.assertTrue(hasattr(self.api, 'plan_intake'), 'Private intake planning missing')
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            text = 'api=https://example.com/a.git'
            request = self.api.parse_request(text, 'demo')
            plan = self.api.plan_intake(request, base / 'project', base / 'launch', base / 'distribution')
            self.assertEqual(list(base.iterdir()), [])
            with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
                self.api.save_intake(plan, text, set())
            self.assertEqual(list(base.iterdir()), [])
            self.api.save_intake(plan, text, {'write'})
            self.assertEqual((base / 'launch/PROJECT-START.md').read_text(), text)
            self.assertFalse((base / 'project').exists())
            self.api.save_intake(plan, text, {'write'})
            with self.assertRaisesRegex(ValueError, 'STALE_INPUT'):
                self.api.save_intake(plan, text + '\n', {'write'})

    def test_launch_conflicting_input_and_overlapping_roots(self):
        self.assertTrue(hasattr(self.api, 'plan_intake'), 'Private intake planning missing')
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            text = 'api=https://example.com/a'
            request = self.api.parse_request(text, 'demo')
            for target, staging, distribution in ((base/'p', base/'p/s', base/'dist'),
                    (base/'dist/p', base/'s', base/'dist'), (base/'p', base/'s', base/'p/dist')):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    self.api.plan_intake(request, target, staging, distribution)
            plan = self.api.plan_intake(request, base/'p', base/'s', base/'dist')
            self.api.save_intake(plan, text, {'write'})
            other = text.replace('/a', '/b')
            with self.assertRaisesRegex(ValueError, 'CONFLICT'):
                plan2 = self.api.plan_intake(self.api.parse_request(other, 'demo'), base/'p', base/'s', base/'dist')
                self.api.save_intake(plan2, other, {'write'})
            self.assertEqual((base/'s/PROJECT-START.md').read_text(), text)

    def test_static_target_conflicts_before_any_write(self):
        self.assertTrue(hasattr(self.api, 'plan_intake'), 'Private intake planning missing')
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            (base/'p/modules/api').mkdir(parents=True)
            request = self.api.parse_request('api=https://example.com/a', 'demo')
            with self.assertRaisesRegex(ValueError, 'CONFLICT'):
                self.api.plan_intake(request, base/'p', base/'s', base/'dist')
            self.assertFalse((base/'s').exists())

    def test_launch_rejects_tampered_plan_and_symlink_parent(self):
        self.assertTrue(hasattr(self.api, 'plan_intake'), 'Private intake planning missing')
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            (base/'real').mkdir()
            (base/'link').symlink_to(base/'real', target_is_directory=True)
            text = 'api=https://example.com/a'
            request = self.api.parse_request(text, 'demo')
            with self.assertRaises(ValueError):
                self.api.plan_intake(request, base/'link/p', base/'s', base/'dist')
            plan = self.api.plan_intake(request, base/'p', base/'s', base/'dist')
            plan['request']['modules'][0]['path'] = '../escape'
            with self.assertRaises(ValueError):
                self.api.save_intake(plan, text, {'write'})
            self.assertFalse((base/'s').exists())


if __name__ == '__main__':
    unittest.main()
