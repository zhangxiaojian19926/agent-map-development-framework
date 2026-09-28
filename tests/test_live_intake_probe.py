"""Live acceptance must inspect artifacts, not trust a host's success message."""
import runpy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from test_bootstrap_config import CLI
sys.path.insert(0, str(CLI.parent))


class LiveProbeTests(unittest.TestCase):
    def test_expected_relation_needs_correct_endpoints_and_caller_evidence(self):
        probe = runpy.run_path(str(CLI.parent/'verify-live')).get('verify_fixture_relationships')
        self.assertIsNotNone(probe, 'Independent fixture relationship probe missing')
        from framework_core.config import encoded
        from framework_core.modules import catalog_update, discover
        from framework_core.storage import atomic, fingerprint
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for mid, content in {'client': 'from service_api import receive\ndef send(): return receive("message")\n',
                                 'service': 'def receive(value): return value\n',
                                 'other': 'def receive(value): return "unrelated"\n'}.items():
                atomic(root, mid+'/app.py', content)
            catalog = catalog_update({}, [{'id': m, 'path': m} for m in ('client', 'service', 'other')],
                                     discover(root, ['client', 'service', 'other']))
            result = {'module_summaries': [{'id': m, 'summary': 'Fixture '+m} for m in catalog['modules']],
                      'relationships': [], 'uncertainties': []}
            def save():
                atomic(root, 'docs/project/relationships.generated.json', encoded(result))
            save()
            with self.assertRaisesRegex(ValueError, 'WRONG_FIXTURE_RELATIONSHIP'):
                probe(root, catalog, 'client', 'service', 'other')
            edge = {'id': 'call', 'from': 'client', 'to': 'service', 'kind': 'runtime-call',
                    'interface': 'receive', 'provenance': 'STATIC_SUPPORTED', 'runtime_validation': 'NOT_RUN',
                    'evidence': [{'path': mid+'/app.py', 'sha256': fingerprint(root/(mid+'/app.py')), 'anchor': anchor}
                                 for mid, anchor in [('client', 'receive("message")'), ('service', 'def receive(value)')]]}
            result['relationships'] = [edge]
            save()
            probe(root, catalog, 'client', 'service', 'other')
            edge['evidence'] = edge['evidence'][1:]
            save()
            with self.assertRaisesRegex(ValueError, 'WRONG_FIXTURE_RELATIONSHIP'):
                probe(root, catalog, 'client', 'service', 'other')
            edge.update(to='other', provenance='INFERRED')
            save()
            with self.assertRaisesRegex(ValueError, 'WRONG_FIXTURE_RELATIONSHIP'):
                probe(root, catalog, 'client', 'service', 'other')

    def test_remote_alone_does_not_prove_head_or_content(self):
        probe = runpy.run_path(str(CLI.parent/'verify-live')).get('verify_checkout')
        self.assertIsNotNone(probe, 'Independent checkout probe missing')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            source, target = root/'source', root/'target'
            source.mkdir()
            def git(*args):
                return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@example.invalid', *map(str, args)], check=True, capture_output=True)
            git('init', '-b', 'develop', source)
            (source/'app.py').write_text('value = 1\n')
            git('-C', source, 'add', '.')
            git('-C', source, 'commit', '-m', 'first')
            git('clone', source, target)
            probe(source, target)
            (target/'app.py').write_text('value = 2\n')
            with self.assertRaisesRegex(ValueError, 'CONTENT'):
                probe(source, target)
            git('-C', target, 'add', '.')
            git('-C', target, 'commit', '-m', 'wrong head')
            with self.assertRaisesRegex(ValueError, 'HEAD'):
                probe(source, target)

    def test_prepared_with_placeholder_docs_is_not_complete(self):
        probe = runpy.run_path(str(CLI.parent/'verify-live')).get('verify_intake_readiness')
        self.assertIsNotNone(probe, 'Independent completeness probe missing')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'INCOMPLETE'):
                probe(Path(tmp), {'onboarding': 'PREPARED', 'runtime': 'NOT_RUN',
                      'initialization': 'PARTIAL', 'maps': {'status': 'READY'}}, 'existing')
