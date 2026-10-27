import copy
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tar_bytes(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as packed:
        for name, content in entries:
            payload = content.encode() if isinstance(content, str) else content
            item = tarfile.TarInfo(name)
            item.size = len(payload)
            item.mode = 0o755
            packed.addfile(item, io.BytesIO(payload))
    return stream.getvalue()


class DownloadResponse:
    def __init__(self, payload):
        self.payload = payload
        self.offset = 0
        self.headers = {}

    def read(self, size=-1):
        if size < 0:
            size = len(self.payload) - self.offset
        result = self.payload[self.offset:self.offset + size]
        self.offset += len(result)
        return result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class HTTPResponse:
    def __init__(self, url, payload=b'', status=200, headers=None):
        self.url = url
        self.payload = payload
        self.status = status
        self.headers = headers or {'Content-Type': 'text/html'}
        self.offset = 0

    def geturl(self):
        return self.url

    def getcode(self):
        return self.status

    def read(self, size=-1):
        if size < 0:
            size = len(self.payload) - self.offset
        result = self.payload[self.offset:self.offset + size]
        self.offset += len(result)
        return result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class AutoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.auto = importlib.import_module('framework_core.reverse_auto')
        self.adapters = importlib.import_module('framework_core.reverse_adapters')
        self.planner = importlib.import_module('framework_core.reverse_planner')
        self.web = importlib.import_module('framework_core.reverse_web')

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, target, request_id='case'):
        if isinstance(target, Path):
            target = {'kind': 'file', 'path': str(target), 'sha256': digest(target)}
        elif isinstance(target, str):
            target = {'kind': 'url', 'url': target}
        return {'schema': 'reverse-request/v1', 'id': request_id, 'goal': 'inspect target',
                'target': target, 'intent': 'static', 'acceptance': ['observed'],
                'observations': [{'id': 'observe-1', 'question': 'inspect', 'action': 'static'}],
                'evidence': {'raw': 'retain', 'public': True},
                'behavior': {'capabilities': [], 'constraints': [], 'inferences': []}}

    def resolver(self, *args, **kwargs):
        return [(2, 1, 6, '', ('93.184.216.34', 443))]


class AdapterTests(AutoCase):
    def test_registered_placeholders_and_operation_boundaries(self):
        catalog = self.planner.load_catalog()
        spec = catalog['adapters']['wasm.static.wabt']
        argv = self.adapters.render_argv(spec, {'tool_path': '/tool', 'target_path': '/target',
                                                'output_path': '/output'})
        self.assertEqual(argv, ['/tool', '/target', '-o', '/output'])
        for invalid in ('{unknown}', '{target_path.__class__}', '{target_path!r}', '{target_path:>10}'):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, 'INVALID_PLACEHOLDER'):
                self.adapters.render_argv({'argv': [invalid]}, {})
        with self.assertRaisesRegex(ValueError, 'INVALID_PLACEHOLDER'):
            self.adapters.render_argv({'argv': ['--out={output_path}']}, {'output_path': '/tmp/x'})
        with self.assertRaisesRegex(ValueError, 'CAPABILITY_TARGET_MISMATCH'):
            self.adapters.adapter_for(catalog, 'wasm.static', 'native', 'static')

    def test_dynamic_authorization_and_provider_missing_are_not_execution(self):
        target = self.root / 'page.html'
        target.write_text('<html></html>')
        request = self.request(target)
        request['observations'] = [{'id': 'dynamic', 'question': 'dom', 'action': 'browser',
                                    'operation': 'observe-dom'}]
        plan = {'plan_sha256': 'a' * 64, 'target': {'kind': 'web_snapshot', 'target_sha256': 'b' * 64},
                'capabilities': ['web.dynamic.dom'], 'tools': []}
        calls = []
        provider = lambda context: calls.append(context) or {'status': 'RECORDED', 'stdout': 'secret'}
        record = self.adapters.execute_observation(self.root, request, plan, request['observations'][0],
                                                   set(), provider=provider, manifest={'snapshot_sha256': 'b' * 64})
        self.assertEqual(record['status'], 'NOT_AUTHORIZED')
        self.assertEqual(calls, [])
        request['id'] = 'second'
        record = self.adapters.execute_observation(self.root, request, plan, request['observations'][0],
                                                   {'browser-observe'}, provider=None,
                                                   manifest={'snapshot_sha256': 'b' * 64})
        self.assertEqual(record['status'], 'PROVIDER_MISSING')
        self.assertEqual(record['runtime_validation'], 'NOT_RUN')


class AutomaticBinaryTests(AutoCase):
    def test_dry_run_approval_install_observe_and_reuse(self):
        target = self.root / 'module.wasm'
        target.write_bytes(b'\x00asm\x01\x00\x00\x00')
        request = self.request(target)
        payload = tar_bytes([('wabt-1.0.42/bin/wasm2wat', '#!/bin/sh\n')])
        lock = self.planner.load_lock()
        lock['tools']['wabt']['artifacts']['darwin-arm64'] = {
            'url': 'https://tools.invalid/wabt.tar.gz', 'sha256': hashlib.sha256(payload).hexdigest(), 'kind': 'tar'}
        downloads, commands = [], []

        def opener(url, timeout=0):
            downloads.append(url)
            return DownloadResponse(payload)

        def runner(argv, cwd, *args):
            commands.append(list(argv))
            if argv[-1] == '--version':
                return {'exit_code': 0, 'stdout': '1.0.42', 'stderr': ''}
            return {'exit_code': 0, 'stdout': '{"wat":"fixture"}', 'stderr': '',
                    'timed_out': False, 'output_limit': False}

        with mock.patch.object(self.auto, 'load_lock', return_value=lock):
            preview = self.auto.execute_auto(self.root, request, set(), dry_run=True,
                                             opener=opener, runner=runner, platform='darwin', machine='arm64')
            self.assertEqual(preview['status'], 'DRY_RUN')
            self.assertEqual([item['tool_id'] for item in preview['plan']['tools']], ['wabt'])
            self.assertFalse((self.root / '.framework').exists())
            self.assertEqual(downloads, [])
            self.assertEqual(commands, [])
            grants = {'write', 'reverse', 'reverse-install'}
            pending = self.auto.execute_auto(self.root, request, grants, opener=opener, runner=runner,
                                             platform='darwin', machine='arm64')
            self.assertEqual(pending['status'], 'PLAN_APPROVAL_REQUIRED')
            self.assertEqual(downloads, [])
            conflict = self.auto.execute_auto(self.root, request, grants, {'toolchain': '0' * 64},
                                              opener=opener, runner=runner, platform='darwin', machine='arm64')
            self.assertEqual(conflict['status'], 'PLAN_CONFLICT')
            missing = self.auto.execute_auto(self.root, request, {'write', 'reverse'},
                                             {'toolchain': pending['plan_sha256']}, opener=opener, runner=runner,
                                             platform='darwin', machine='arm64')
            self.assertEqual(missing['status'], 'CONSENT_REQUIRED')
            self.assertEqual(downloads, [])
            result = self.auto.execute_auto(self.root, request, grants,
                                            {'toolchain': pending['plan_sha256']}, opener=opener, runner=runner,
                                            platform='darwin', machine='arm64')
            self.assertEqual(result['status'], 'READY')
            self.assertEqual(result['toolchain_status'], 'READY')
            self.assertEqual(result['observation_status'], 'RECORDED')
            self.assertEqual(result['runtime_validation'], 'NOT_RUN')
            self.assertEqual(len(downloads), 1)
            second = self.auto.execute_auto(self.root, request, {'write', 'reverse'}, opener=opener,
                                            runner=runner, platform='darwin', machine='arm64')
            self.assertEqual(second['status'], 'PLAN_APPROVAL_REQUIRED')
            self.assertTrue(all(item['action'] == 'REUSE' for item in second['plan']['tools']))
            self.assertNotEqual(second['plan_sha256'], pending['plan_sha256'])
            reused = self.auto.execute_auto(self.root, request, {'write', 'reverse'},
                                            {'toolchain': second['plan_sha256']}, opener=opener, runner=runner,
                                            platform='darwin', machine='arm64')
            self.assertEqual(reused['status'], 'READY')
            self.assertEqual(len(downloads), 1)
            self.assertEqual(reused['observation_status'], 'RECORDED')

    def test_ghidra_jdk_dependency_full_fake_install(self):
        target = self.root / 'program'
        target.write_bytes(b'\x7fELFfixture')
        request = self.request(target)
        request['intent'] = 'deep-static'
        jdk = tar_bytes([('jdk-21.0.13+9.jdk/Contents/Home/bin/java', '#!/bin/sh\n')])
        ghidra = tar_bytes([('ghidra_12.1.4_PUBLIC/support/analyzeHeadless', '#!/bin/sh\n')])
        lock = self.planner.load_lock()
        lock['tools']['temurin-jdk']['artifacts']['darwin-arm64'] = {
            'url': 'https://tools.invalid/jdk.tar.gz', 'sha256': hashlib.sha256(jdk).hexdigest(), 'kind': 'tar'}
        lock['tools']['ghidra']['artifacts'] = {'darwin-arm64': {
            'url': 'https://tools.invalid/ghidra.tar.gz', 'sha256': hashlib.sha256(ghidra).hexdigest(), 'kind': 'tar'}}
        payloads = {'https://tools.invalid/jdk.tar.gz': jdk, 'https://tools.invalid/ghidra.tar.gz': ghidra}
        commands = []
        def opener(url, timeout=0):
            return DownloadResponse(payloads[url])
        def runner(argv, cwd, *args):
            commands.append(list(argv))
            if argv[-1] == '--version':
                return {'exit_code': 0, 'stdout': '', 'stderr': 'openjdk 21.0.13 2026-10-01'}
            return {'exit_code': 0, 'stdout': '{"decompiled":"fixture"}', 'stderr': ''}
        with mock.patch.object(self.auto, 'load_lock', return_value=lock):
            grants = {'write', 'reverse', 'reverse-install'}
            pending = self.auto.execute_auto(self.root, request, grants, opener=opener, runner=runner,
                                             platform='darwin', machine='arm64')
            self.assertEqual([item['tool_id'] for item in pending['plan']['tools']], ['temurin-jdk', 'ghidra'])
            result = self.auto.execute_auto(self.root, request, grants,
                                            {'toolchain': pending['plan_sha256']}, opener=opener, runner=runner,
                                            platform='darwin', machine='arm64')
            self.assertEqual(result['status'], 'READY')
            self.assertEqual(result['observation_status'], 'RECORDED')
            ghidra_calls = [call for call in commands if 'analyzeHeadless' in call[0]]
            self.assertEqual(len(ghidra_calls), 1)
            self.assertIn('-import', ghidra_calls[0])
            receipt = json.loads((self.root / '.framework/tools/temurin-jdk/21.0.13+9/install-receipt.json').read_text())
            self.assertEqual(receipt['probe_expect'], '21.0.13')


class WebTests(AutoCase):
    def web_opener(self, pages, calls):
        def open_url(request, timeout=0):
            url = request.full_url if hasattr(request, 'full_url') else request
            calls.append(url)
            value = pages[url]
            if isinstance(value, HTTPResponse):
                return value
            return HTTPResponse(url, value, headers={'Content-Type': 'text/html' if url.endswith(('/', '.html'))
                                                    else 'application/octet-stream'})
        return open_url

    def test_snapshot_static_resources_and_out_of_scope_save_nothing(self):
        request = self.request('https://example.test/app')
        request['network'] = {'origins': ['https://example.test'], 'allow_private': False,
                              'allow_http': False, 'max_resources': 10, 'max_bytes': 10000, 'timeout': 5}
        pages = {'https://example.test/app': b'<html><script src="/app.js"></script><link href="/site.css"></html>',
                 'https://example.test/app.js': b'console.log("fixture")',
                 'https://example.test/site.css': b'body{}'}
        calls = []
        manifest = self.web.fetch_snapshot(self.root, request, {'web-fetch'},
                                           opener=self.web_opener(pages, calls), resolver=self.resolver,
                                           now='2026-01-01T00:00:00+00:00')
        self.assertEqual(len(manifest['resources']), 3)
        self.assertEqual(len({item['sha256'] for item in manifest['resources']}), 3)
        loaded = self.web.load_snapshot(self.root, 'case', manifest['snapshot_sha256'])
        profile = self.web.profile_snapshot(self.root, request, loaded)
        self.assertEqual(profile['capabilities'], ['web.static.resources'])
        resources = self.web.static_resources(self.root, loaded)
        self.assertEqual(resources['scripts'], ['https://example.test/app.js'])
        self.assertEqual(resources['styles'], ['https://example.test/site.css'])
        other = Path(self.tmp.name) / 'other'
        other.mkdir()
        pages['https://example.test/app'] = b'<script src="https://evil.invalid/x.js"></script>'
        with self.assertRaisesRegex(ValueError, 'ORIGIN_OUT_OF_SCOPE'):
            self.web.fetch_snapshot(other, request, {'web-fetch'}, opener=self.web_opener(pages, []),
                                    resolver=self.resolver)
        self.assertFalse((other / '.framework').exists())

    def test_redirect_timeout_and_resource_budgets(self):
        request = self.request('https://example.test/')
        request['network'] = {'origins': ['https://example.test'], 'allow_private': False,
                              'allow_http': False, 'max_resources': 1, 'max_bytes': 4, 'timeout': 5}
        response = HTTPResponse('https://example.test/', status=302,
                                headers={'Location': 'https://evil.invalid/'})
        with self.assertRaisesRegex(ValueError, 'ORIGIN_OUT_OF_SCOPE'):
            self.web.fetch_snapshot(self.root, request, {'web-fetch'}, opener=lambda *args, **kwargs: response,
                                    resolver=self.resolver)
        with self.assertRaisesRegex(ValueError, 'RESOURCE_LIMIT'):
            self.web.fetch_snapshot(self.root, request, {'web-fetch'},
                                    opener=lambda *args, **kwargs: HTTPResponse('https://example.test/', b'12345'),
                                    resolver=self.resolver)
        def timeout(*args, **kwargs):
            raise TimeoutError('fixture')
        with self.assertRaisesRegex(ValueError, 'NETWORK_TIMEOUT'):
            self.web.fetch_snapshot(self.root, request, {'web-fetch'}, opener=timeout, resolver=self.resolver)
        request['network']['max_bytes'] = 100
        pages = {'https://example.test/': b'<script src="/extra.js"></script>',
                 'https://example.test/extra.js': b'x'}
        calls = []
        with self.assertRaisesRegex(ValueError, 'RESOURCE_LIMIT'):
            self.web.fetch_snapshot(self.root, request, {'web-fetch'},
                                    opener=self.web_opener(pages, calls), resolver=self.resolver)
        self.assertEqual(calls, ['https://example.test/'])
        self.assertFalse((self.root / '.framework').exists())

    def test_url_auto_static_dynamic_provider_and_secret_summary(self):
        request = self.request('https://example.test/')
        request['intent'] = 'dynamic'
        request['observations'].extend([
            {'id': 'dom', 'question': 'dom', 'action': 'browser', 'operation': 'observe-dom'},
            {'id': 'har', 'question': 'network', 'action': 'network', 'operation': 'capture-har'}])
        pages = {'https://example.test/': b'<html><script src="/app.js"></script></html>',
                 'https://example.test/app.js': b'fixture'}
        calls = []
        opener = self.web_opener(pages, calls)
        offline = self.auto.execute_auto(self.root, request, set(), dry_run=True, opener=opener,
                                         resolver=self.resolver)
        self.assertEqual(offline['status'], 'SNAPSHOT_REQUIRED')
        self.assertEqual(calls, [])
        grants = {'write', 'reverse', 'web-fetch'}
        pending = self.auto.execute_auto(self.root, request, grants, opener=opener, resolver=self.resolver)
        self.assertEqual(pending['status'], 'PLAN_APPROVAL_REQUIRED')
        result = self.auto.execute_auto(self.root, request, grants, {'toolchain': pending['plan_sha256']},
                                        opener=opener, resolver=self.resolver)
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['toolchain_status'], 'READY')
        self.assertEqual([item['status'] for item in result['observations']],
                         ['RECORDED', 'NOT_AUTHORIZED', 'NOT_AUTHORIZED'])
        all_grants = grants | {'browser-observe', 'network-capture'}
        missing = self.auto.execute_auto(self.root, request, all_grants,
                                         {'toolchain': pending['plan_sha256']}, opener=opener,
                                         resolver=self.resolver)
        self.assertEqual([item['status'] for item in missing['observations']],
                         ['RECORDED', 'PROVIDER_MISSING', 'PROVIDER_MISSING'])
        secret = 'Cookie=very-secret-token'
        provider = lambda context: {'status': 'RECORDED', 'stdout': secret, 'browser_version': 'fake-1'}
        dynamic_request = copy.deepcopy(request)
        dynamic_request['id'] = 'dynamic-case'
        dynamic_pending = self.auto.execute_auto(self.root, dynamic_request, all_grants,
                                                 opener=opener, resolver=self.resolver)
        dynamic = self.auto.execute_auto(self.root, dynamic_request, all_grants,
                                         {'toolchain': dynamic_pending['plan_sha256']}, opener=opener,
                                         resolver=self.resolver, provider=provider)
        self.assertEqual(dynamic['observation_status'], 'RECORDED')
        self.assertEqual(dynamic['runtime_validation'], 'NOT_RUN')
        summary = (self.root / 'docs/project/reverse/dynamic-case.md').read_text()
        self.assertNotIn(secret, summary)
        raw = (self.root / '.framework/local-state/reverse/auto/dynamic-case/raw/dom.txt').read_text()
        self.assertIn(secret, raw)

    def test_remote_wasm_incremental_plan_and_static_adapters(self):
        request = self.request('https://example.test/')
        request['observations'].append({'id': 'wasm', 'question': 'wat', 'action': 'static',
                                        'capability': 'wasm.static'})
        pages = {'https://example.test/': b'<script src="/module.wasm"></script>',
                 'https://example.test/module.wasm': b'\x00asm\x01\x00\x00\x00'}
        payload = tar_bytes([('wabt-1.0.42/bin/wasm2wat', '#!/bin/sh\n')])
        artifact_url = 'https://tools.invalid/wabt.tar.gz'
        lock = self.planner.load_lock()
        lock['tools']['wabt']['artifacts']['darwin-arm64'] = {
            'url': artifact_url, 'sha256': hashlib.sha256(payload).hexdigest(), 'kind': 'tar'}
        downloads = []
        def opener(value, timeout=0):
            if isinstance(value, str):
                downloads.append(value)
                return DownloadResponse(payload)
            return HTTPResponse(value.full_url, pages[value.full_url],
                                headers={'Content-Type': 'application/octet-stream'})
        def runner(argv, cwd, *args):
            if argv[-1] == '--version':
                return {'exit_code': 0, 'stdout': '1.0.42', 'stderr': ''}
            return {'exit_code': 0, 'stdout': '(module)', 'stderr': ''}
        with mock.patch.object(self.auto, 'load_lock', return_value=lock):
            grants = {'write', 'reverse', 'reverse-install', 'web-fetch'}
            pending = self.auto.execute_auto(self.root, request, grants, opener=opener,
                                             resolver=self.resolver, runner=runner,
                                             platform='darwin', machine='arm64')
            self.assertEqual([item['tool_id'] for item in pending['plan']['tools']], ['wabt'])
            self.assertIn('wasm.static', pending['plan']['capabilities'])
            result = self.auto.execute_auto(self.root, request, grants,
                                            {'toolchain': pending['plan_sha256']}, opener=opener,
                                            resolver=self.resolver, runner=runner,
                                            platform='darwin', machine='arm64')
            self.assertEqual(result['observation_status'], 'RECORDED')
            self.assertEqual(result['observations'], [{'id': 'observe-1', 'status': 'RECORDED'},
                                                      {'id': 'wasm', 'status': 'RECORDED'}])
            self.assertEqual(downloads, [artifact_url])
            self.assertEqual(result['runtime_validation'], 'NOT_RUN')

    def test_snapshot_discovers_wasm_and_content_change_is_new_identity(self):
        request = self.request('https://example.test/')
        pages = {'https://example.test/': b'<script src="/module.wasm"></script>',
                 'https://example.test/module.wasm': b'\x00asm\x01\x00\x00\x00'}
        opener = self.web_opener(pages, [])
        manifest = self.web.fetch_snapshot(self.root, request, {'web-fetch'}, opener=opener,
                                           resolver=self.resolver)
        profile = self.web.profile_snapshot(self.root, request, manifest)
        self.assertIn('wasm.static', profile['capabilities'])
        first_identity = manifest['snapshot_sha256']
        pages['https://example.test/module.wasm'] = b'\x00asm\x01\x00\x00\x01'
        changed = self.web.fetch_snapshot(self.root, request, {'web-fetch'}, opener=opener,
                                          resolver=self.resolver)
        self.assertNotEqual(first_identity, changed['snapshot_sha256'])
        self.assertEqual(self.web.load_snapshot(self.root, 'case', first_identity)['snapshot_sha256'], first_identity)


if __name__ == '__main__':
    unittest.main()
