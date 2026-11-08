"""Routers generated from the combination manifest."""
import importlib.machinery
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

from framework_core.workflows.routers import (description_of, distribution_errors,
                                              load_combinations, render_skill)

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / 'tools/check-framework'


def load_checker():
    loader = importlib.machinery.SourceFileLoader('checker_routers', str(CHECKER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def copy_inputs(root):
    for relative in (
        'tools/framework_core/workflows/combinations.json',
        'tools/framework_core/workflows/catalog.json',
        'tools/framework_core/hosts/roster.json',
        'docs/guide/from-zero-to-one.md',
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / relative, target)
    shutil.copytree(ROOT / 'skill/flows', root / 'skill/flows')


class RouterContractTests(unittest.TestCase):
    def test_fifteen_routers_match_the_manifest(self):
        self.assertEqual(distribution_errors(ROOT), [])
        flows = load_combinations()['flows']
        self.assertEqual([item['id'] for item in flows], ['flow-%02d' % n for n in range(1, 16)])
        for flow in flows:
            text = (ROOT / 'skill/flows' / flow['id'] / 'SKILL.md').read_text(encoding='utf-8')
            self.assertNotIn('disable-model-invocation', text.split('---', 2)[1])
            self.assertLessEqual(len(description_of(flow)), 1024)
            self.assertLessEqual(text.count('\n'), 500)
            self.assertNotIn('`retro`', text)

    def test_successors_are_written_by_the_router(self):
        text = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('下一项是 to-tickets 与 plan-format.md，不采用该技能收尾中的直接 apply', text)
        self.assertIn('下一项是 tdd 与 discipline.md', text)
        self.assertIn('不把 subagent-driven-development 或 dispatching-parallel-agents 列为当前步骤必读', text)
        self.assertIn('不把 llm-wiki 的写入步骤列为必读', text)
        self.assertIn('仍进入规格和 to-tickets', text)
        research = (ROOT / 'skill/flows/flow-10/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('不点名下一个技能', research)
        release = (ROOT / 'skill/flows/flow-15/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('不把 flow-14 写为下一项', release)
        self.assertIn('必须已有 flow-14 的验证证据', release)

    def test_triggers_for_observation_and_release_are_disjoint(self):
        flows = {item['id']: item for item in load_combinations()['flows']}
        for left, right in (('flow-06', 'flow-07'), ('flow-14', 'flow-15')):
            self.assertNotIn(flows[left]['trigger'], description_of(flows[right]))
            self.assertNotIn(flows[right]['trigger'], description_of(flows[left]))

    def test_skill_policy_no_longer_drops_the_stage_skills(self):
        text = (ROOT / 'docs/framework/skill-policy.md').read_text(encoding='utf-8')
        self.assertNotIn('不进入阶段必做步骤', text)
        self.assertIn('`retro` 不是自动必读', text)
        for name in ('diagnosing-bugs', 'to-tickets', 'tdd', 'code-review'):
            self.assertIn(name, text)

    def test_persona_block_and_status_dictionary_stay_put(self):
        current = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        committed = subprocess.check_output(['git', 'show', 'HEAD:AGENTS.md'], cwd=ROOT, text=True)
        def block(text):
            return text.split('<!-- AGENT_PERSONA_START -->', 1)[1].split('<!-- AGENT_PERSONA_END -->', 1)[0]
        self.assertEqual(block(current), block(committed))
        guide = (ROOT / 'docs/guide/framework-model.md').read_text(encoding='utf-8')
        old = subprocess.check_output(['git', 'show', 'HEAD:docs/guide/framework-model.md'], cwd=ROOT, text=True)
        marker = '<!-- status-dictionary:start -->'
        self.assertEqual(guide.split(marker, 1)[1], old.split(marker, 1)[1])

    def test_brainstorming_layer_is_named_by_a_live_document(self):
        registry = json.loads((ROOT / 'skill/local-layers.json').read_text(encoding='utf-8'))
        self.assertIn('framework-rules.md', registry['brainstorming'])
        self.assertTrue((ROOT / 'skill/superpowers/brainstorming/framework-rules.md').is_file())
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        matched = [line for line in agents.splitlines()
                   if 'brainstorming' in line and 'framework-rules.md' in line]
        self.assertTrue(matched)
        layer = (ROOT / 'skill/superpowers/brainstorming/framework-rules.md').read_text(encoding='utf-8')
        self.assertIn('to-tickets', layer)


class RouterFalsificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        copy_inputs(self.root)

    def exit_code(self):
        script = (
            'import importlib.machinery, importlib.util, sys\n'
            'from pathlib import Path\n'
            'loader = importlib.machinery.SourceFileLoader("checker", sys.argv[1])\n'
            'spec = importlib.util.spec_from_loader(loader.name, loader)\n'
            'module = importlib.util.module_from_spec(spec)\n'
            'loader.exec_module(module)\n'
            'errors = module.router_errors(Path(sys.argv[2]))\n'
            'print("\\n".join(errors))\n'
            'raise SystemExit(1 if errors else 0)\n'
        )
        result = subprocess.run([sys.executable, '-c', script, str(CHECKER), str(self.root)],
                                capture_output=True, text=True)
        return result.returncode, result.stdout

    def test_a_shared_trigger_exits_nonzero(self):
        path = self.root / 'tools/framework_core/workflows/combinations.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        flows = {item['id']: item for item in data['flows']}
        flows['flow-15']['trigger'] = flows['flow-14']['trigger']
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for flow in data['flows']:
            skill = self.root / 'skill/flows' / flow['id'] / 'SKILL.md'
            skill.write_text(render_skill(flow), encoding='utf-8')
        code, output = self.exit_code()
        self.assertEqual(code, 1)
        self.assertIn('flow-14', output)
        self.assertIn('flow-15', output)

    def test_a_missing_router_exits_nonzero(self):
        (self.root / 'skill/flows/flow-03/SKILL.md').unlink()
        code, output = self.exit_code()
        self.assertEqual(code, 1)
        self.assertIn('flow-03', output)

    def test_an_extra_guide_skill_exits_nonzero(self):
        path = self.root / 'docs/guide/from-zero-to-one.md'
        text = path.read_text(encoding='utf-8')
        text = text.replace('`writing-for-agents`', '`writing-for-agents`、`retro`', 1)
        path.write_text(text, encoding='utf-8')
        code, output = self.exit_code()
        self.assertEqual(code, 1)
        self.assertIn('flow-02', output)
        self.assertIn('retro', output)

    def test_a_projected_member_skill_exits_nonzero(self):
        leaked = self.root / '.cursor/skills/tdd'
        leaked.mkdir(parents=True)
        (leaked / 'SKILL.md').write_text('member', encoding='utf-8')
        code, output = self.exit_code()
        self.assertEqual(code, 1)
        self.assertIn('tdd', output)
        self.assertIn('cursor', output)

    def test_a_guessed_trae_path_exits_nonzero(self):
        path = self.root / 'tools/framework_core/hosts/roster.json'
        roster = json.loads(path.read_text(encoding='utf-8'))
        for item in roster['hosts']:
            if item['id'] == 'trae':
                item['discovery_dir'] = '.trae/skills'
        path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        guessed = self.root / '.trae/skills/flow-01'
        guessed.mkdir(parents=True)
        (guessed / 'SKILL.md').write_text('guess', encoding='utf-8')
        code, output = self.exit_code()
        self.assertEqual(code, 1)
        self.assertIn('trae', output)
        self.assertIn('CARRIER_UNKNOWN', output)
