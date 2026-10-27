import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import threading
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class Response:
    def __init__(self, payload, headers=None):
        self.payload = payload
        self.headers = headers or {}
        self.offset = 0

    def read(self, size=-1):
        if self.offset >= len(self.payload):
            return b''
        if size < 0:
            size = len(self.payload) - self.offset
        chunk = self.payload[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class BoundedDownloadTests(unittest.TestCase):
    def setUp(self):
        self.downloads = importlib.import_module('framework_core.reverse_downloads')

    def test_declared_and_actual_download_limits_remove_partial(self):
        for headers, payload in [({'Content-Length': '9'}, b'1234'), ({}, b'123456789')]:
            with self.subTest(headers=headers), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / 'artifact'
                opener = lambda *args, **kwargs: Response(payload, headers)
                with self.assertRaisesRegex(ValueError, 'DOWNLOAD_LIMIT'):
                    self.downloads.fetch_verified('https://example.test/tool', dest, '0' * 64,
                                                  opener, max_bytes=8)
                self.assertFalse(dest.exists())
                self.assertFalse(dest.with_name(dest.name + '.partial').exists())

    def test_integrity_failure_leaves_no_artifact_or_ready_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = {'version': '1', 'artifacts': {'darwin-arm64': {
                'url': 'https://example.test/tool', 'sha256': '0' * 64, 'kind': 'file'}}}
            opener = lambda *args, **kwargs: Response(b'actual')
            with self.assertRaises(self.downloads.IntegrityError):
                self.downloads.install_archive(root, 'wabt', spec, 'darwin', 'arm64', opener)
            self.assertFalse((root / '.framework/tools/wabt/1/.sha256').exists())
            self.assertFalse((root / '.framework/tools/wabt/1/install-receipt.json').exists())


def zip_bytes(names):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as packed:
        for name, content in names:
            packed.writestr(name, content)
    return stream.getvalue()


def tar_link_bytes():
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as packed:
        item = tarfile.TarInfo('tool/link')
        item.type = tarfile.SYMTYPE
        item.linkname = '../../outside'
        packed.addfile(item)
    return stream.getvalue()


class TransactionInstallTests(unittest.TestCase):
    def setUp(self):
        self.downloads = importlib.import_module('framework_core.reverse_downloads')
        self.install = importlib.import_module('framework_core.reverse_install')

    def spec(self, payload, kind='zip', entrypoint='tool/bin/tool'):
        return {'version': '1', 'entrypoint': entrypoint, 'artifacts': {'darwin-arm64': {
            'url': 'https://example.test/tool', 'sha256': hashlib.sha256(payload).hexdigest(),
            'kind': kind}}}

    def runner(self, calls, version='1'):
        def run(argv, cwd):
            calls.append(list(argv))
            return {'exit_code': 0, 'stdout': version, 'stderr': '', 'timed_out': False,
                    'output_limit': False}
        return run

    def test_safe_archive_atomic_receipt_and_health_reuse(self):
        payload = zip_bytes([('tool/bin/tool', '#!/bin/sh\n')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls = []
            opener_calls = []
            def opener(*args, **kwargs):
                opener_calls.append(args[0])
                return Response(payload)
            result = self.install.install_archive(root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                                                  opener, runner=self.runner(calls))
            self.assertEqual(result['action'], 'INSTALL')
            receipt = root / '.framework/tools/wabt/1/install-receipt.json'
            self.assertTrue(receipt.is_file())
            self.assertTrue(json.loads(receipt.read_text())['status'] == 'READY')
            again = self.install.install_archive(root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                                                 opener, runner=self.runner(calls))
            self.assertEqual(again['action'], 'REUSE')
            self.assertEqual(opener_calls, ['https://example.test/tool'])
            healthy = self.install.inspect_installed(root, 'wabt', '1', runner=self.runner(calls), probe=True)
            self.assertEqual(healthy['status'], 'READY')

    def test_tar_extract_supports_python39_signature(self):
        from unittest import mock
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as packed:
            item = tarfile.TarInfo('tool/bin/tool')
            item.size = 1
            packed.addfile(item, io.BytesIO(b'x'))
        original = self.downloads.tarfile.TarFile.extractall
        def python39_extractall(packed, path, members=None, *, numeric_owner=False):
            return original(packed, path, members=members, numeric_owner=numeric_owner, filter='data')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / 'tool.tar'
            archive.write_bytes(stream.getvalue())
            staging = root / 'staging'
            staging.mkdir()
            with mock.patch.object(self.downloads.tarfile.TarFile, 'extractall',
                                   new=python39_extractall):
                self.downloads.extract_archive(archive, 'tar', staging)
            self.assertEqual((staging / 'tool/bin/tool').read_text(), 'x')

    def test_malicious_archives_and_expand_limits_are_rejected(self):
        cases = [zip_bytes([('../escape', 'bad')]), tar_link_bytes(), zip_bytes([('a', '1'), ('b', '2')])]
        for index, payload in enumerate(cases):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as tmp:
                kind = 'tar' if index == 1 else 'zip'
                spec = self.spec(payload, kind=kind, entrypoint=None)
                opener = lambda *args, **kwargs: Response(payload)
                with self.assertRaisesRegex(ValueError, 'ARCHIVE_UNSAFE|ARCHIVE_LIMIT'):
                    self.downloads.install_archive(Path(tmp), 'wabt', spec, 'darwin', 'arm64', opener,
                                                   max_files=1)
                self.assertFalse((Path(tmp) / '.framework/tools/wabt/1').exists())

    def test_missing_entrypoint_unknown_final_and_approved_repair(self):
        payload = zip_bytes([('tool/bin/other', 'x')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            opener = lambda *args, **kwargs: Response(payload)
            result = self.install.install_archive(root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                                                  opener, runner=self.runner([]))
            self.assertEqual(result['status'], 'INSTALL_FAILED')
            self.assertFalse((root / '.framework/tools/wabt/1').exists())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / '.framework/tools/wabt/1'
            final.mkdir(parents=True)
            (final / 'human.txt').write_text('keep')
            opener = lambda *args, **kwargs: Response(payload)
            conflict = self.install.install_archive(root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                                                    opener, runner=self.runner([]))
            self.assertEqual(conflict['status'], 'CONFLICT')
            self.assertEqual((final / 'human.txt').read_text(), 'keep')
            good = zip_bytes([('tool/bin/tool', 'x')])
            repaired = self.install.install_archive(
                root, 'wabt', self.spec(good), 'darwin', 'arm64',
                lambda *args, **kwargs: Response(good), runner=self.runner([]), repair=True)
            self.assertEqual(repaired['action'], 'REPAIR')
            self.assertFalse((final / 'human.txt').exists())

    def test_per_tool_lock_blocks_without_touching_final(self):
        payload = zip_bytes([('tool/bin/tool', 'x')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.install.tool_lock(root, 'wabt'):
                result = self.install.install_archive(
                    root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                    lambda *args, **kwargs: Response(payload), runner=self.runner([]))
            self.assertEqual(result['status'], 'LOCKED')
            self.assertFalse((root / '.framework/tools/wabt/1').exists())

    def test_concurrent_install_has_one_final_receipt(self):
        payload = zip_bytes([('tool/bin/tool', 'x')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = []
            errors = []
            def worker():
                try:
                    results.append(self.install.install_archive(
                        root, 'wabt', self.spec(payload), 'darwin', 'arm64',
                        lambda *args, **kwargs: Response(payload), runner=self.runner([])))
                except Exception as exc:
                    errors.append(exc)
            threads = [threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(errors, [])
            self.assertEqual(len(results), 2)
            self.assertTrue(all(item['status'] in ('INSTALLED', 'LOCKED') for item in results))
            self.assertTrue((root / '.framework/tools/wabt/1/install-receipt.json').is_file())

    def test_interrupted_repair_restores_previous_version(self):
        from unittest import mock
        old = zip_bytes([('tool/bin/tool', 'old')])
        new = zip_bytes([('tool/bin/tool', 'new')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.install.install_archive(root, 'wabt', self.spec(old), 'darwin', 'arm64',
                                         lambda *args, **kwargs: Response(old), runner=self.runner([]))
            with mock.patch('framework_core.reverse_install.atomic', side_effect=OSError('interrupted')):
                with self.assertRaisesRegex(OSError, 'interrupted'):
                    self.install.install_archive(
                        root, 'wabt', self.spec(new), 'darwin', 'arm64',
                        lambda *args, **kwargs: Response(new), runner=self.runner([]), repair=True)
            self.assertEqual((root / '.framework/tools/wabt/1/tool/bin/tool').read_text(), 'old')

    def test_npm_health_reuse_corruption_version_and_node_missing(self):
        spec = {'package': 'rea-agents', 'version': '6.7.0', 'integrity': 'sha512-pinned'}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls = []
            version = {'value': spec['version']}
            def runner(argv, cwd):
                calls.append(list(argv))
                if argv[:2] in (['node', '--version'], ['npm', '--version']):
                    return {'exit_code': 0, 'stdout': 'runtime', 'stderr': ''}
                if argv[0] == 'npm':
                    self.assertIn('--ignore-scripts', argv)
                    self.assertIn('--cache', argv)
                    prefix = Path(argv[argv.index('--prefix') + 1])
                    package = prefix / 'node_modules/rea-agents'
                    package.mkdir(parents=True)
                    (package / 'cli.js').write_text('#!/bin/sh\n')
                    binary = prefix / 'node_modules/.bin'
                    binary.mkdir(parents=True)
                    (binary / 'rea').symlink_to('../rea-agents/cli.js')
                    (prefix / 'package-lock.json').write_text(json.dumps({'packages': {
                        'node_modules/rea-agents': {'version': spec['version'], 'integrity': spec['integrity']}}}))
                    return {'exit_code': 0, 'stdout': '', 'stderr': ''}
                return {'exit_code': 0, 'stdout': version['value'], 'stderr': ''}
            result = self.install.install_npm(root, 'rea-agents', spec, runner)
            self.assertEqual(result['action'], 'INSTALL')
            again = self.install.install_npm(root, 'rea-agents', spec, runner)
            self.assertEqual(again['action'], 'REUSE')
            self.assertEqual(sum(argv[0] == 'npm' and 'install' in argv for argv in calls), 1)
            binary = root / '.framework/tools/rea-agents/6.7.0/node_modules/.bin/rea'
            binary.unlink()
            self.assertEqual(self.install.inspect_installed(
                root, 'rea-agents', spec['version'], runner=runner, probe=True)['status'], 'CORRUPT')
            repaired = self.install.install_npm(root, 'rea-agents', spec, runner, repair=True)
            self.assertEqual(repaired['action'], 'REPAIR')
            version['value'] = '9.0.0'
            self.assertEqual(self.install.inspect_installed(
                root, 'rea-agents', spec['version'], runner=runner, probe=True)['status'], 'UNSUPPORTED_VERSION')
        with tempfile.TemporaryDirectory() as tmp:
            missing = lambda argv, cwd: {'exit_code': 127, 'stdout': '', 'stderr': 'missing'}
            self.assertEqual(self.install.install_npm(Path(tmp), 'rea-agents', spec, missing)['status'],
                             'NODE_MISSING')


if __name__ == '__main__':
    unittest.main()
