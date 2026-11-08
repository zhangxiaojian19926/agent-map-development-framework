"""Host roster projection and write gates for the workflow routers."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core.hosts.base import judge_event, load_adapter
from framework_core.hosts.claude_code import ClaudeCodeAdapter
from framework_core.hosts.codebuddy import CodeBuddyAdapter
from framework_core.hosts.projection import (execution_axis, install_gate, load_roster,
                                             project_routers)
from framework_core.hosts.qwen_code import QwenCodeAdapter

ROOT = Path(__file__).resolve().parents[1]
UNKNOWN_DISCOVERY = (
    'trae', 'lingma', 'github-copilot', 'windsurf', 'grok', 'copilot-cli',
    'codebuddy', 'claude-code', 'codex', 'gemini-cli', 'qwen-code',
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RosterTests(unittest.TestCase):
    def test_thirteen_hosts_use_only_the_three_evidence_grades(self):
        hosts = load_roster()['hosts']
        self.assertEqual(len(hosts), 13)
        self.assertEqual(sum(item['region'] == 'international' for item in hosts), 8)
        self.assertEqual(sum(item['region'] == 'domestic' for item in hosts), 5)
        allowed = {'DOCUMENTED', 'RECORDED', 'CARRIER_UNKNOWN'}
        for item in hosts:
            self.assertIn(item['discovery_evidence'], allowed)
            self.assertIn(item['hook_evidence'], allowed)

    def test_a_host_outside_the_roster_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = project_routers(root, 'vscode')
            self.assertEqual(report['status'], 'FAILED')
            self.assertEqual(list(root.rglob('*')), [])
            gate = install_gate(root, 'vscode')
            self.assertEqual(gate['status'], 'FAILED')
            self.assertEqual(list(root.rglob('*')), [])


class ProjectionTests(unittest.TestCase):
    def test_cursor_projection_matches_the_canonical_routers(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            root = Path(tmp)
            report = project_routers(root, 'cursor')
            self.assertEqual(report['status'], 'UPDATED')
            self.assertEqual(len(report['files']), 15)
            names = sorted(path.parent.name for path in (root / '.cursor/skills').glob('*/SKILL.md'))
            self.assertEqual(names, ['flow-%02d' % n for n in range(1, 16)])
            for flow_id in names:
                projected = (root / '.cursor/skills' / flow_id / 'SKILL.md').read_text(encoding='utf-8')
                canonical = (ROOT / 'skill/flows' / flow_id / 'SKILL.md').read_text(encoding='utf-8')
                self.assertEqual(projected, canonical)
            for relative in report['files']:
                self.assertFalse(Path(relative).is_absolute())
                self.assertTrue((root / relative).is_file())
            self.assertEqual(list(Path(home).iterdir()), [])

    def test_deepseek_projection_is_flat_and_not_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.git').mkdir()
            nested = root / 'nested'
            nested.mkdir()
            report = project_routers(nested, 'deepseek-harness')
            self.assertEqual(report['status'], 'UPDATED')
            for flow_id in ['flow-%02d' % n for n in range(1, 16)]:
                path = root / '.dsh/skills' / flow_id / 'SKILL.md'
                self.assertTrue(path.is_file())
                self.assertEqual(path.read_text(encoding='utf-8'),
                                 (ROOT / 'skill/flows' / flow_id / 'SKILL.md').read_text(encoding='utf-8'))
            self.assertFalse((root / '.agents').exists())
            self.assertFalse((nested / '.dsh').exists())
            gate = install_gate(nested, 'deepseek-harness')
            self.assertTrue((root / '.dsh/hooks.json').is_file())
            self.assertEqual(gate['execution'], 'NOT_RUN')
            self.assertFalse(gate['blocked'])
            self.assertEqual(execution_axis('deepseek-harness'), 'NOT_RUN')
            self.assertNotEqual(execution_axis('deepseek-harness'), 'INTERCEPTED')

    def test_unknown_discovery_directories_are_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for host_id in UNKNOWN_DISCOVERY:
                report = project_routers(root, host_id)
                self.assertEqual(report['status'], 'GAP', host_id)
                self.assertEqual(report['reason'], 'CARRIER_UNKNOWN')
            self.assertEqual(list(root.rglob('*')), [])


class GateTests(unittest.TestCase):
    def test_cursor_denies_an_unapproved_write_without_changing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'src/app.py'
            target.parent.mkdir()
            target.write_text('original\n', encoding='utf-8')
            before = digest(target)
            install_gate(root, 'cursor')
            hook = json.loads((root / '.cursor/hooks.json').read_text(encoding='utf-8'))
            self.assertTrue(hook['hooks']['preToolUse'][0]['failClosed'])
            adapter = load_adapter('cursor')
            verdict = judge_event(root, adapter, {'tool_name': 'Write'})
            decision, _ = adapter.encode(verdict)
            self.assertEqual(decision['permission'], 'deny')
            self.assertIn('skill/flows/flow-02/SKILL.md', decision['agent_message'])
            self.assertIn('tdd', decision['agent_message'])
            self.assertEqual(digest(target), before)
            reading = judge_event(root, adapter, {'tool_name': 'Read'})
            allowed, _ = adapter.encode(reading)
            self.assertEqual(allowed['permission'], 'allow')
            unknown = judge_event(root, adapter, {'tool_name': 'StrReplace'})
            self.assertFalse(unknown['covered'])
            self.assertEqual(unknown['status'], 'NOT_APPLICABLE')
            self.assertEqual(execution_axis('cursor'), 'NOT_RUN')

    def test_claude_and_qwen_keep_their_tool_names_and_name_the_router(self):
        self.assertEqual(ClaudeCodeAdapter.write_tools, ('Edit', 'MultiEdit', 'Write', 'NotebookEdit'))
        self.assertEqual(QwenCodeAdapter.write_tools, ('write_file', 'replace', 'edit'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = judge_event(root, ClaudeCodeAdapter(), {'tool_name': 'Edit'})
            qwen = judge_event(root, QwenCodeAdapter(), {'tool_name': 'write_file'})
            self.assertEqual(claude['reason'], qwen['reason'])
            self.assertIn('skill/flows/flow-02/SKILL.md', claude['reason'])
            self.assertIn('缺失步骤：tdd', claude['reason'])

    def test_recorded_carriers_without_a_session_stay_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.git').mkdir()
            for host_id, relative in (('codex', '.codex/hooks.json'), ('gemini-cli', '.gemini/settings.json')):
                report = install_gate(root, host_id)
                self.assertTrue((root / relative).is_file(), host_id)
                self.assertEqual(report['execution'], 'NOT_RUN')
                self.assertEqual(execution_axis(host_id), 'NOT_RUN')
                self.assertNotEqual(report['execution'], 'INTERCEPTED')

    def test_codebuddy_gains_neither_memory_nor_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = CodeBuddyAdapter().preview(root)['files']
            self.assertTrue(files)
            self.assertFalse(any(path.endswith('CODEBUDDY.md') or 'hooks' in path for path in files))
            report = install_gate(root, 'codebuddy')
            self.assertEqual(report['files'], [])
            self.assertEqual(list(root.rglob('*')), [])

    def test_advisory_hosts_do_not_grow_hook_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for host_id in ('trae', 'lingma', 'github-copilot', 'windsurf', 'grok', 'copilot-cli'):
                report = install_gate(root, host_id)
                self.assertEqual(report['status'], 'GAP', host_id)
                self.assertEqual(report['files'], [])
            self.assertEqual(list(root.rglob('*')), [])
