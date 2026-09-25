import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_bootstrap_config import invoke


class EndToEndTests(unittest.TestCase):
    def test_prepared_new_project_keeps_new_candidate_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()/'project'
            prepared = invoke('prepare', '--target', root, '--project-id', 'demo', '--yes', '--allow', 'write')
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            candidate = root/'later'
            subprocess.run(['git', 'init', '-q', str(candidate)], check=True)
            (candidate/'code.py').write_text('def later(): return 1\n')
            doctor = invoke('doctor', '--target', root)
            report = json.loads(doctor.stdout)
            self.assertEqual(report['status'], 'PARTIAL')
            self.assertTrue(report['candidates'])
            self.assertTrue(any('module add' in action for action in report['next_actions']))

    def test_intake_new_from_one_input_and_preview_zero_write(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            request = base/'start.md'
            request.write_text('# 工程启动单\n项目：家庭任务助手\n目标：本地新增任务\n仓库：暂无')
            args = ('intake', '--target', base/'project', '--staging', base/'launch', '--request', request)
            preview = invoke(*args, '--dry-run')
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertFalse((base/'launch').exists())
            self.assertFalse((base/'project').exists())
            result = invoke(*args, '--yes', '--allow', 'write')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['onboarding'], 'PREPARED')
            config = json.loads((base/'project/framework-project.json').read_text())
            self.assertEqual(config['agent'], 'current')
            self.assertEqual(config['project_name'], '家庭任务助手')
            self.assertFalse((base/'project/.git').exists())
            self.assertFalse((base/'project/PROJECT-START.md').exists())
            resumed = invoke('intake', '--target', base/'project', '--yes', '--allow', 'write')
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            module = base/'project/later'
            module.mkdir()
            (module/'code.py').write_text('def later(): return 1\n')
            added = invoke('module', 'add', '--target', base/'project', '--id', 'later', '--path', 'later', '--yes', '--allow', 'write')
            self.assertEqual(added.returncode, 5, added.stdout)
            before = (base/'project/framework-project.json').read_bytes()
            resumed = invoke('intake', '--target', base/'project', '--yes', '--allow', 'write')
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            self.assertEqual((base/'project/framework-project.json').read_bytes(), before)

    def test_named_intake_current_agent_end_to_end(self):
        import sys
        from test_module_acquisition import git
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source = base/'source'
            source.mkdir()
            git(source, 'init', '-b', 'develop')
            (source/'code.py').write_text('def hello(): return 1\n')
            git(source, 'add', '.')
            git(source, 'commit', '-m', 'fixture')
            request = base/'start.md'
            request.write_text('设备端=' + str(source) + '\n服务端=' + str(source))
            root = base/'project'
            result = invoke('intake', '--target', root, '--staging', base/'launch', '--request', request,
                            '--yes', '--allow', 'write', '--allow', 'clone', '--allow', 'local-clone')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            catalog = json.loads((root/'module-catalog.generated.json').read_text())
            self.assertEqual({m['path'] for m in catalog['modules'].values()}, {'modules/设备端', 'modules/服务端'})
            self.assertNotIn(str(source), (root/'framework-project.json').read_text())
            packet_result = invoke('analyze-request', '--target', root, '--yes', '--allow', 'write', '--allow', 'agent')
            self.assertEqual(packet_result.returncode, 0, packet_result.stdout + packet_result.stderr)
            packet = json.loads(packet_result.stdout)
            envelope = {'request_id': packet['request_id'], 'source_digest': packet['source_digest'],
                        'result': {'module_summaries': [{'id': m['id'], 'summary': 'Contains hello'} for m in packet['modules']],
                                   'relationships': [], 'uncertainties': ['No proven relationship']}}
            (base/'response.json').write_text(json.dumps(envelope))
            accepted = invoke('accept-analysis', '--target', root, '--result', base/'response.json',
                              '--yes', '--allow', 'write', '--allow', 'agent')
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            doctor = invoke('doctor', '--target', root)
            self.assertEqual(doctor.returncode, 0, doctor.stdout)
            self.assertEqual(json.loads(doctor.stdout)['runtime'], 'NOT_RUN')

    def test_local_clone_registration_move_missing_and_hook_event(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d).resolve()
            source, target = base / 'source', base / 'project'
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source / 'code.py').write_text('def alpha(): return 1\n')
            subprocess.run(['git', '-C', str(source), 'add', 'code.py'], check=True)
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture'], check=True)
            first = invoke('init', '--target', target, '--project-id', 'demo', '--agent', 'manual', '--yes', '--allow', 'write')
            self.assertEqual(first.returncode, 5, first.stdout)
            imported = invoke('module', 'clone', '--target', target, '--id', 'lib', '--path', 'modules/lib', '--url', source,
                              '--yes', '--allow', 'write', '--allow', 'clone', '--allow', 'local-clone', '--hooks', '--allow', 'hooks')
            self.assertEqual(imported.returncode, 5, imported.stdout)
            self.assertTrue((target / 'modules/lib/code.py').is_file())
            hook = target / 'modules/lib/.git/hooks/post-commit'
            self.assertTrue(hook.stat().st_mode & 0o111)
            subprocess.run([str(hook)], cwd=target / 'modules/lib', check=True)
            dirty = json.loads((target / '.framework/local-state/dirty.json').read_text())
            self.assertEqual(dirty['reasons'], ['post-commit'])
            (target / 'modules/lib').rename(target / 'modules/moved')
            moved = invoke('module', 'add', '--target', target, '--id', 'lib', '--path', 'modules/moved', '--yes', '--allow', 'write', '--allow', 'hooks')
            self.assertEqual(moved.returncode, 5, moved.stdout)
            catalog = json.loads((target / 'module-catalog.generated.json').read_text())
            self.assertEqual(catalog['modules']['lib']['history'], ['modules/lib'])
            (target / 'modules/moved').rename(base / 'retained')
            synced = invoke('module', 'sync', '--target', target, '--yes', '--allow', 'write')
            self.assertEqual(synced.returncode, 0, synced.stdout)
            catalog = json.loads((target / 'module-catalog.generated.json').read_text())
            self.assertEqual(catalog['modules']['lib']['presence'], 'missing')

    def test_live_verifier_needs_explicit_opt_in(self):
        cli = Path(__file__).resolve().parents[1] / 'tools/verify-live'
        import sys
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'not-created'
            result = subprocess.run([sys.executable, '-B', str(cli), '--target', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertFalse(target.exists())

    def test_intake_live_verifier_requires_opt_in(self):
        import sys
        cli = Path(__file__).resolve().parents[1]/'tools/verify-live'
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/'not-created'
            result = subprocess.run([sys.executable, '-B', str(cli), '--target', str(target),
                                     '--scenario', 'intake', '--host', 'claude'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertFalse(target.exists())

    def test_live_probe_rejects_an_always_empty_fake_cli(self):
        import sys
        probe = Path(__file__).resolve().parent / 'integration/probe_task_cli.py'
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'taskcli').mkdir()
            (root / 'taskcli/__main__.py').write_text('print("[]")\n')
            result = subprocess.run([sys.executable, '-B', str(probe), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('CONTRACT_FAILED', result.stderr)
