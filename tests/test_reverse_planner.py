import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apk_bytes():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as packed:
        packed.writestr('AndroidManifest.xml', 'manifest')
        packed.writestr('classes.dex', 'dex\n')
    return stream.getvalue()


class RequestProfileTests(unittest.TestCase):
    def setUp(self):
        self.requests = importlib.import_module('framework_core.reverse_request')
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, path, intent='static'):
        return {'schema': 'reverse-request/v1', 'id': 'case', 'goal': 'inspect target',
                'target': {'kind': 'file', 'path': str(path), 'sha256': digest(path)},
                'intent': intent, 'acceptance': ['observed'],
                'observations': [{'id': 'observe-1', 'question': 'inspect', 'action': 'static'}],
                'evidence': {'raw': 'retain', 'public': True},
                'behavior': {'capabilities': [], 'constraints': [], 'inferences': []}}

    def test_strict_request_rejects_unknown_shell_and_symlink(self):
        target = self.root / 'sample.bin'
        target.write_bytes(b'program')
        request = self.request(target)
        request['argv'] = ['sh', '-c', 'bad']
        with self.assertRaisesRegex(ValueError, 'INVALID_REQUEST'):
            self.requests.validate_request(request)
        request = self.request(target)
        request['target']['download_url'] = 'https://evil.invalid'
        with self.assertRaisesRegex(ValueError, 'INVALID_TARGET'):
            self.requests.validate_request(request)
        link = self.root / 'link'
        link.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'INVALID_TARGET'):
            self.requests.validate_request(self.request(link))

    def test_magic_profiles_and_stale_target(self):
        cases = [
            ('elf', b'\x7fELFrest', 'native', 'binary.static.generic'),
            ('pe', b'MZrest', 'native', 'binary.static.generic'),
            ('macho', b'\xcf\xfa\xed\xferest', 'native', 'binary.static.generic'),
            ('wasm', b'\x00asm\x01\x00\x00\x00', 'wasm', 'wasm.static'),
            ('apk', apk_bytes(), 'android', 'android.static.bytecode'),
            ('html', b'<html><script src="app.js"></script></html>', 'web_snapshot', 'web.static.resources')]
        for name, payload, kind, capability in cases:
            with self.subTest(name=name):
                path = self.root / (name + '.bin')
                path.write_bytes(payload)
                profile = self.requests.profile_request(self.request(path))
                self.assertEqual(profile['kind'], kind)
                self.assertIn(capability, profile['capabilities'])
                self.assertEqual(profile['target_sha256'], digest(path))
        deep = self.root / 'deep'
        deep.write_bytes(b'\x7fELFrest')
        profile = self.requests.profile_request(self.request(deep, intent='deep-static'))
        self.assertIn('binary.static.native', profile['capabilities'])
        unknown = self.root / 'unknown'
        unknown.write_bytes(b'plain text')
        self.assertEqual(self.requests.profile_request(self.request(unknown))['status'], 'PROFILE_UNKNOWN')
        stale = self.request(unknown)
        unknown.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'STALE_TARGET'):
            self.requests.profile_request(stale)

    def test_url_preprofile_is_offline_and_checks_boundaries(self):
        placeholder = self.root / 'unused'
        placeholder.write_bytes(b'placeholder')
        request = self.request(placeholder)
        request['target'] = {'kind': 'url', 'url': 'https://example.test/app'}
        request['network'] = {'origins': ['https://example.test'], 'allow_private': False,
                              'allow_http': False, 'max_resources': 10, 'max_bytes': 1000, 'timeout': 5}
        calls = []
        profile = self.requests.preprofile_url(request, grants=set(), opener=lambda *args: calls.append(args))
        self.assertEqual(profile['status'], 'SNAPSHOT_REQUIRED')
        self.assertIn('web-fetch', profile['required_grants'])
        self.assertEqual(calls, [])
        for url in ('https://user:pass@example.test/', 'file:///tmp/a', 'http://example.test/'):
            request['target']['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.requests.preprofile_url(request, grants=set())
        request['target']['url'] = 'http://localhost:8000/'
        request['network']['origins'] = ['http://localhost:8000']
        request['network']['allow_http'] = True
        with self.assertRaisesRegex(ValueError, 'PRIVATE_NETWORK'):
            self.requests.preprofile_url(request, grants=set())
        request['network']['allow_private'] = True
        self.assertEqual(self.requests.preprofile_url(request, grants=set())['status'], 'SNAPSHOT_REQUIRED')


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner = importlib.import_module('framework_core.reverse_planner')
        self.catalog = self.planner.load_catalog()
        self.lock = importlib.import_module('framework_core.reverse').load_lock()

    def request(self, capability=None):
        request = {'schema': 'reverse-request/v1', 'id': 'case', 'goal': 'inspect',
                   'target': {'kind': 'file', 'path': '/tmp/target', 'sha256': '0' * 64},
                   'intent': 'static', 'acceptance': ['observed'],
                   'observations': [{'id': 'observe-1', 'question': 'inspect', 'action': 'static'}],
                   'evidence': {'raw': 'retain', 'public': True},
                   'behavior': {'capabilities': [], 'constraints': [], 'inferences': []}}
        if capability:
            request['capabilities'] = [capability]
        return request

    def profile(self, kind, capabilities):
        return {'status': 'PROFILED', 'kind': kind, 'format': kind,
                'target_sha256': '0' * 64, 'capabilities': capabilities, 'facts': ['fixture']}

    def test_minimal_capability_dependency_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            generic = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'native', ['binary.static.generic']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual([item['tool_id'] for item in generic['tools']], ['rea-agents'])
            deep = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'native', ['binary.static.native']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual({item['tool_id'] for item in deep['tools']}, {'ghidra', 'temurin-jdk'})
            self.assertNotIn('wabt', {item['tool_id'] for item in deep['tools']})
            wasm = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'wasm', ['wasm.static']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual([item['tool_id'] for item in wasm['tools']], ['wabt'])
            web = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'web_snapshot', ['web.static.resources']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual(web['tools'], [])
            self.assertEqual(web['status'], 'READY')

    def test_unpinned_host_unknown_dependency_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'android', ['android.static.bytecode']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual(apk['status'], 'INTEGRITY_UNPINNED')
            deep = self.planner.build_plan(Path(tmp), self.request(), self.profile(
                'native', ['binary.static.native']), self.catalog, self.lock, 'linux', 'x64')
            self.assertEqual(deep['status'], 'HOST_UNSUPPORTED')
        invalid = copy.deepcopy(self.catalog)
        invalid['tools']['ghidra']['requires'] = ['unknown']
        with self.assertRaisesRegex(ValueError, 'INVALID_TOOLCHAIN'):
            self.planner.validate_catalog(invalid, self.lock)
        unregistered = copy.deepcopy(self.catalog)
        unregistered['capabilities']['wasm.static']['tools'] = ['not-registered']
        with self.assertRaisesRegex(ValueError, 'INVALID_TOOLCHAIN'):
            self.planner.validate_catalog(unregistered, self.lock)
        with self.assertRaisesRegex(ValueError, 'INVALID_CATALOG'):
            self.planner.loads_catalog('{"tools": {}, "tools": {}}')

    def test_explicit_capability_stays_in_registered_target_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = self.request('wasm.static')
            plan = self.planner.build_plan(Path(tmp), request, self.profile(
                'wasm', ['wasm.static']), self.catalog, self.lock, 'darwin', 'arm64')
            self.assertEqual([item['tool_id'] for item in plan['tools']], ['wabt'])
            request['target']['tools'] = ['ghidra']
            with self.assertRaisesRegex(ValueError, 'INVALID_TARGET'):
                importlib.import_module('framework_core.reverse_request').validate_request(request)
            mismatch = self.request('wasm.static')
            with self.assertRaisesRegex(ValueError, 'CAPABILITY_TARGET_MISMATCH'):
                self.planner.build_plan(Path(tmp), mismatch, self.profile(
                    'native', ['binary.static.generic']), self.catalog, self.lock, 'darwin', 'arm64')

    def test_plan_hash_is_stable_and_binds_lock_and_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = self.profile('wasm', ['wasm.static'])
            first = self.planner.build_plan(Path(tmp), self.request(), profile, self.catalog, self.lock,
                                            'darwin', 'arm64')
            second = self.planner.build_plan(Path(tmp), self.request(), profile, self.catalog, self.lock,
                                             'darwin', 'arm64')
            self.assertEqual(first['plan_sha256'], second['plan_sha256'])
            changed = copy.deepcopy(self.lock)
            changed['tools']['wabt']['artifacts']['darwin-arm64']['sha256'] = 'f' * 64
            third = self.planner.build_plan(Path(tmp), self.request(), profile, self.catalog, changed,
                                            'darwin', 'arm64')
            self.assertNotEqual(first['plan_sha256'], third['plan_sha256'])
            networked = self.request()
            networked['network'] = {'origins': ['https://example.test'], 'allow_private': False,
                                    'allow_http': False, 'max_resources': 10, 'max_bytes': 1000, 'timeout': 5}
            fourth = self.planner.build_plan(Path(tmp), networked, profile, self.catalog, self.lock,
                                             'darwin', 'arm64')
            self.assertNotEqual(first['plan_sha256'], fourth['plan_sha256'])


if __name__ == '__main__':
    unittest.main()
