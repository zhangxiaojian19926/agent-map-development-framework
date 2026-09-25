"""Real local Git fixtures prove named acquisition, ref selection and recovery."""
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import os
import socket
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from framework_core.intake import parse_request, plan_intake, save_intake
from framework_core.process import run

GRANTS = {'write', 'clone', 'local-clone'}


def git(root, *args):
    result = subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                             '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('framework_core.acquisition'), 'Named acquisition missing')
        self.api = importlib.import_module('framework_core.acquisition')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.source = self.base/'source'
        self.source.mkdir()
        git(self.source, 'init', '-b', 'develop')
        (self.source/'app.py').write_text('def greet(): return "hi"\n')
        git(self.source, 'add', 'app.py')
        git(self.source, 'commit', '-m', 'initial')
        self.first = git(self.source, 'rev-parse', 'HEAD')
        git(self.source, 'tag', 'v1')
        (self.source/'app.py').write_text('def greet(): return "hello"\n')
        git(self.source, 'commit', '-am', 'second')
        self.latest = git(self.source, 'rev-parse', 'HEAD')

    def plan(self, text):
        plan = plan_intake(parse_request(text, 'demo', GRANTS), self.base/'project', self.base/'launch', self.base/'dist')
        save_intake(plan, text, GRANTS)
        return plan

    def test_named_same_source_default_ref_and_resume_no_clone(self):
        plan = self.plan('设备端=' + str(self.source) + '\n服务端=' + str(self.source))
        report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['status'], 'COMPLETE', report)
        for name in ('设备端', '服务端'):
            target = self.base/'project/modules'/name
            self.assertEqual(git(target, 'rev-parse', 'HEAD'), self.latest)
            self.assertEqual(git(target, 'remote', 'get-url', 'origin'), str(self.source))
        def no_clone(argv, *args):
            self.assertNotIn('clone', argv)
            return run(argv, *args)
        self.assertEqual(self.api.acquire_modules(plan, GRANTS, no_clone)['status'], 'COMPLETE')

    def test_branch_tag_and_commit_selection(self):
        for kind, ref, expected in [('branch', 'develop', self.latest), ('tag', 'v1', self.first), ('commit', self.first, self.first)]:
            module = {'source_url': str(self.source), 'requested_ref': {'kind': kind, 'value': ref}}
            result = self.api.resolve_source(module, GRANTS)
            self.assertEqual(result['resolved_commit'], expected)
        plan = self.plan('# 工程启动单\n## 模块仓库\napi=' + str(self.source) + '\n## 来源版本\napi=commit:' + self.first)
        report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['status'], 'COMPLETE', report)
        self.assertEqual(git(self.base/'project/modules/api', 'rev-parse', 'HEAD'), self.first)

    def test_missing_ref_empty_and_unavailable_are_distinct(self):
        result = self.api.resolve_source({'source_url': str(self.source), 'requested_ref': {'kind': 'branch', 'value': 'absent'}}, GRANTS)
        self.assertEqual(result['error_code'], 'REF_NOT_FOUND')
        empty = self.base/'empty'
        empty.mkdir()
        git(empty, 'init', '--bare')
        self.assertEqual(self.api.resolve_source({'source_url': str(empty)}, GRANTS)['state'], 'EMPTY')
        failed = self.api.resolve_source({'source_url': str(self.base/'absent')}, GRANTS)
        self.assertEqual(failed['state'], 'FAILED')
        self.assertNotEqual(failed.get('error_code'), 'EMPTY')

    def test_partial_failure_then_retry_preserves_success(self):
        missing = self.base/'missing'
        plan = self.plan('one=' + str(self.source) + '\ntwo=' + str(missing) + '\nthree=' + str(self.source))
        report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertEqual([report['modules'][k]['state'] for k in ('one', 'two', 'three')], ['REGISTERED', 'FAILED', 'REGISTERED'])
        git(self.base, 'clone', str(self.source), str(missing))
        def spy(argv, *args):
            if 'clone' in argv:
                self.assertTrue(argv[-1].endswith('/two'))
            return run(argv, *args)
        self.assertEqual(self.api.acquire_modules(plan, GRANTS, spy)['status'], 'COMPLETE')

    def test_user_changes_and_lost_permission_are_preserved(self):
        plan = self.plan('api=' + str(self.source))
        self.api.acquire_modules(plan, GRANTS)
        file = self.base/'project/modules/api/app.py'
        file.write_text('user work\n')
        report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['modules']['api']['state'], 'CONFLICT')
        self.assertEqual(file.read_text(), 'user work\n')
        with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
            self.api.acquire_modules(plan, set())

    def test_auth_failure_is_redacted_and_no_submodule_execution(self):
        def rejected(argv, *args):
            return {'exit_code': 128, 'stdout': '', 'stderr': 'Authentication failed SECRET', 'timed_out': False}
        result = self.api.resolve_source({'source_url': 'https://example.com/private'}, {'clone', 'write'}, rejected)
        self.assertEqual(result['error_code'], 'AUTH_REQUIRED')
        self.assertNotIn('SECRET', json.dumps(result))
        (self.source/'install.sh').write_text('touch OWNED\n')
        (self.source/'.gitmodules').write_text('[submodule "trap"]\npath=trap\nurl=https://example.invalid/trap\n')
        git(self.source, 'add', '.')
        git(self.source, 'commit', '-m', 'untrusted input')
        plan = self.plan('api=' + str(self.source))
        report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['status'], 'COMPLETE', report)
        self.assertFalse((self.base/'project/modules/api/OWNED').exists())
        self.assertFalse((self.base/'project/modules/api/trap').exists())

    def test_remote_moves_between_query_and_clone(self):
        plan = self.plan('api=' + str(self.source))
        def moving(argv, *args):
            if 'clone' in argv:
                (self.source/'app.py').write_text('moved\n')
                git(self.source, 'commit', '-am', 'move')
            return run(argv, *args)
        report = self.api.acquire_modules(plan, GRANTS, moving)
        self.assertEqual(report['modules']['api']['error_code'], 'SOURCE_MOVED')
        self.assertEqual(report['status'], 'PARTIAL')

    def test_inherited_git_configuration_cannot_redirect_clone(self):
        plan = self.plan('api=' + str(self.source))
        with patch.dict(os.environ, {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'core.bare', 'GIT_CONFIG_VALUE_0': 'true',
                                     'GIT_DIR': '/nonexistent/evil', 'GIT_SSH_COMMAND': 'false'}):
            report = self.api.acquire_modules(plan, GRANTS)
        self.assertEqual(report['status'], 'COMPLETE', report)
        self.assertTrue((self.base/'project/modules/api/app.py').exists())

    def test_auth_adapter_requires_explicit_grant_and_safe_socket(self):
        sockpath = str(self.base/'agent.sock')
        with socket.socket(socket.AF_UNIX) as sock:
            sock.bind(sockpath)
            with self.assertRaisesRegex(ValueError, 'CONSENT_REQUIRED'):
                self.api.git_call(['--version'], self.base, GRANTS, auth={'ssh_agent': sockpath})
            calls = []
            def spy(argv, *args):
                calls.append(argv)
                return run(argv, *args)
            result = self.api.git_call(['--version'], self.base, GRANTS | {'auth'}, spy, {'ssh_agent': sockpath})
            self.assertEqual(result['exit_code'], 0)
            self.assertIn('SSH_AUTH_SOCK=' + sockpath, calls[0])
            self.assertIn('GIT_CONFIG_GLOBAL=/dev/null', calls[0])

    def test_new_target_conflict_after_preview_keeps_all_files(self):
        plan = self.plan('api=' + str(self.source))
        target = self.base/'project/modules/api'
        target.mkdir(parents=True)
        (target/'human.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'CONFLICT'):
            self.api.acquire_modules(plan, GRANTS)
        self.assertEqual((target/'human.txt').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
