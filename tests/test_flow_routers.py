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
        self.assertIn('规格同步完成后：下一项是把该需求写入初始化知识库', text)
        self.assertIn('knowledge-receipt.json', text)
        self.assertIn('回执留下之后，下一项才是 openspec-archive-change', text)
        self.assertNotIn('归档完成后：下一项是询问是否摄入', text)
        self.assertIn('仍进入规格和 to-tickets', text)
        self.assertIn('诊断停在红信号、最小复现和根因', text)
        self.assertIn('Phase 5 不应用修复', text)
        self.assertIn('回归测试和修复只由 tdd 写', text)
        self.assertIn('Execution handoff 不是下一项', text)
        self.assertIn('不往 tasks.md 追加切片', text)
        self.assertIn('任何一个 coding agent 都可以有的能力', text)
        self.assertIn('不是只有 Claude Code 与 CodeBuddy', text)
        self.assertIn('当前安装事实不改宿主安装器', text)
        self.assertIn('退出必经，人点名仍可用', text)
        self.assertIn('不创建 tasks.md', text)
        self.assertNotIn('已有规格上下文的下一项是 openspec-explore', text)
        self.assertNotIn('顺序执行则下一项是 executing-plans', text)
        self.assertNotIn('工作区就绪后：下一项是 openspec-apply-change', text)
        self.assertNotIn('顺序执行点名', text)
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

    def test_persona_block_matches_source_and_status_dictionary_stays_put(self):
        current = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        source = (ROOT / 'docs/framework/agent-persona.md').read_text(encoding='utf-8')
        def block(text):
            return text.split('<!-- AGENT_PERSONA_START -->', 1)[1].split('<!-- AGENT_PERSONA_END -->', 1)[0]
        persona = block(current).strip()
        self.assertEqual(persona, source.strip())
        self.assertIn('写入初始化知识库', persona)
        self.assertNotIn('询问是否摄入', persona)
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

    def test_flow_01_failure_stops_before_a_fix(self):
        text = (ROOT / 'skill/flows/flow-01/SKILL.md').read_text(encoding='utf-8')
        stop = ('只停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不在本路由应用修复：'
                '不把最小复现写成回归测试，也不应用修复。本路由不写修复，也不把 tdd 写成下一项。')
        self.assertIn(stop, text)
        self.assertIn('先读 [BOOTSTRAP.md](../../../BOOTSTRAP.md)，再读 [project-bootstrap](../../project-bootstrap/SKILL.md)。', text)
        self.assertIn('设计未批准时停止，不进入 flow-02。', text)
        self.assertIn('设计未批准时没有下一项技能。', text)
        self.assertNotIn('失败完成后，下一项是 diagnosing-bugs 与 discipline.md。', text)
        self.assertNotIn('回归测试和修复只由 tdd 写', text)
        flows = {item['id']: item for item in load_combinations()['flows']}
        self.assertEqual(flows['flow-01']['mentions'],
                         ['BOOTSTRAP.md', 'diagnosing-bugs', 'discipline.md', 'project-bootstrap'])

    def test_flow_14_failure_uses_the_same_stop(self):
        text = (ROOT / 'skill/flows/flow-14/SKILL.md').read_text(encoding='utf-8')
        stop = ('只停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不在本路由应用修复：'
                '不把最小复现写成回归测试，也不应用修复。本路由不写修复，也不把 tdd 写成下一项。')
        self.assertIn(stop, text)
        self.assertIn('改技能点名 [writing-skills](../../superpowers/writing-skills/SKILL.md)。', text)
        self.assertIn('改 Agent 所读文档点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。', text)
        self.assertIn('三种模式各自结束，不把另一种模式写为下一项。', text)
        self.assertIn('本路由覆盖改技能、改 Agent 所读文档和排障三种模式。三种模式各自结束。', text)
        self.assertNotIn('下一项是 writing-skills', text)
        self.assertNotIn('下一项是 writing-for-agents', text)
        self.assertNotIn('下一项是 tdd', text)
        self.assertNotIn('回归测试和修复只由 tdd 写', text)
        flows = {item['id']: item for item in load_combinations()['flows']}
        self.assertEqual(flows['flow-14']['mentions'],
                         ['diagnosing-bugs', 'discipline.md', 'writing-for-agents', 'writing-skills'])

    def test_flow_08_stops_in_the_design_conversation(self):
        text = (ROOT / 'skill/flows/flow-08/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('先点名 [reverse-engineer](../../reverse-engineer/SKILL.md) 的交接部分。', text)
        self.assertIn('brainstorming 的架构路径', text)
        self.assertIn('[brainstorming](../../superpowers/brainstorming/SKILL.md)', text)
        self.assertIn('[framework-rules.md](../../superpowers/brainstorming/framework-rules.md)', text)
        self.assertIn('停在设计对话', text)
        self.assertIn('不把 openspec-propose 或 to-tickets 当作下一项', text)
        self.assertIn('不创建 OpenSpec change，包括未批准的 change。', text)
        self.assertIn('不创建 OpenSpec change。', text)
        self.assertNotIn('不创建已批准的 OpenSpec change', text)
        self.assertNotIn('下一项是 openspec-propose', text)
        self.assertNotIn('下一项是 to-tickets', text)
        flows = {item['id']: item for item in load_combinations()['flows']}
        self.assertEqual(flows['flow-08']['mentions'],
                         ['brainstorming', 'framework-rules.md', 'reverse-engineer'])

    def test_review_findings_are_not_appended_to_tasks(self):
        rules = (ROOT / 'skill/matt-pocock/code-review/framework-rules.md').read_text(encoding='utf-8')
        self.assertIn('发现只写入交付报告，不往 tasks.md 追加切片。', rules)
        self.assertNotIn("change's task list", rules)
        self.assertNotIn('**Important** findings must be fixed before the work proceeds', rules)
        self.assertIn('评审不改业务源码，不往 tasks.md 追加切片。', rules)
        self.assertIn('→ openspec/changes/<change>/tasks.md', rules)
        upstream = (ROOT / 'skill/matt-pocock/code-review/SKILL.md').read_text(encoding='utf-8')
        self.assertNotIn('发现只写入交付报告，不往 tasks.md 追加切片。', upstream)
        flow04 = (ROOT / 'skill/flows/flow-04/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('评审受管 diff 时点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。', flow04)
        self.assertIn('存在人工改动冲突时停止。', flow04)
        self.assertNotIn('不往 tasks.md 追加切片', flow04)
        flow09 = (ROOT / 'skill/flows/flow-09/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('规格已批准且实现之后，点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。', flow09)
        self.assertIn('找不到 change 时报告无可用规格。', flow09)
        self.assertNotIn('不往 tasks.md 追加切片', flow09)

    def test_diagnosing_bugs_does_not_apply_a_fix(self):
        skill = (ROOT / 'skill/matt-pocock/diagnosing-bugs/SKILL.md').read_text(encoding='utf-8')
        discipline = (ROOT / 'skill/matt-pocock/diagnosing-bugs/discipline.md').read_text(encoding='utf-8')
        self.assertIn('Skip phases only when explicitly justified.', skill)
        self.assertNotIn('Apply the fix', skill)
        self.assertNotIn('Fix + regression test', skill)
        self.assertNotIn('Turn the minimised repro into a failing test', skill)
        self.assertIn('不应用修复，也不写生产代码。', skill)
        self.assertIn('回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做。', skill)
        self.assertIn('flow-01 与 flow-14 不把 tdd 写成下一项，所以这两条读完诊断就停。', skill)
        self.assertIn('本阶段不是实现器。', skill)
        self.assertNotIn('now write code', discipline)
        self.assertNotIn('Test first proves the fix', discipline)
        self.assertNotIn('Implement appropriate handling', discipline)
        self.assertIn('不写生产代码。', discipline)
        self.assertIn('查完根因后不先写测试再修复。', discipline)
        self.assertIn('回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做。', discipline)

    def test_review_does_not_edit_business_source(self):
        rules = (ROOT / 'skill/matt-pocock/code-review/framework-rules.md').read_text(encoding='utf-8')
        self.assertNotIn('must be fixed before the work proceeds', rules)
        self.assertIn('评审不改业务源码，不往 tasks.md 追加切片。', rules)
        self.assertIn('发现写入交付报告。', rules)
        self.assertIn('活动路由把 tdd 写成下一项时，修改回到 tdd。', rules)
        self.assertIn('flow-04 与 flow-09 没有这句，评审到报告为止。', rules)
        self.assertIn('**Minor** 发现只写入交付报告，不往 tasks.md 追加切片。', rules)
        flow04 = (ROOT / 'skill/flows/flow-04/SKILL.md').read_text(encoding='utf-8')
        flow09 = (ROOT / 'skill/flows/flow-09/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('评审受管 diff 时点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。', flow04)
        self.assertIn('规格已批准且实现之后，点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。', flow09)

    def test_brainstorming_next_item_is_announced_by_the_active_flow(self):
        rules = (ROOT / 'skill/superpowers/brainstorming/framework-rules.md').read_text(encoding='utf-8')
        skill = (ROOT / 'skill/superpowers/brainstorming/SKILL.md').read_text(encoding='utf-8')
        self.assertNotIn('1. The next step is `openspec-propose` or `openspec-update-change`.', rules)
        self.assertNotIn('2. After the spec, the next step is `to-tickets` and `plan-format.md`.', rules)
        self.assertIn('下一项只由活动中的 flow 正文宣布。', rules)
        self.assertIn('flow-02 宣布进入规格时才是 openspec-propose 或 openspec-update-change，然后再 to-tickets。', rules)
        self.assertIn('flow-08 已宣布停在设计对话、不创建 OpenSpec change、不把 openspec-propose 或 to-tickets 当作下一项。这句优先。', rules)
        self.assertIn('该收尾不是下一项，除非活动 flow 点名它们。', rules)
        self.assertIn('to-tickets', rules)
        self.assertNotIn('invoke to-tickets skill to create the implementation slices', skill)
        self.assertNotIn('to-tickets is the next step', skill)
        self.assertNotIn('the ONLY skill you invoke after brainstorming is to-tickets', skill)
        self.assertNotIn('let `openspec-propose` create the artifacts', skill)
        self.assertNotIn('Invoke to-tickets skill', skill)
        self.assertNotIn('then the to-tickets skill', skill)
        self.assertIn('活动 flow 的下一项', skill)
        flow08 = (ROOT / 'skill/flows/flow-08/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('停在设计对话', flow08)
        self.assertIn('不把 openspec-propose 或 to-tickets 当作下一项', flow08)


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


class SingleChainDocumentTests(unittest.TestCase):
    def test_stage_table_follows_the_single_chain(self):
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('<!-- AGENT_PERSONA_START -->', agents)
        self.assertIn('<!-- AGENT_PERSONA_END -->', agents)
        section = agents.split('<!-- AGENT_PERSONA_END -->', 1)[1].split('## 3.', 1)[0]
        self.assertIn('| 1. DISCOVERY |', section)
        self.assertNotIn('宏观任务状态', section)
        self.assertIn('独占可校验的规格账本', section)
        self.assertIn('Phase 5 不应用修复', section)
        self.assertIn('Execution handoff 不是下一项', section)
        self.assertIn('不往 tasks.md 追加切片', section)
        self.assertIn('任何一个 coding agent 都可以有的能力', section)
        self.assertNotIn('顺序 executing-plans', section)
        self.assertLess(section.index('| 10. KNOWLEDGE |'), section.index('| 11. ARCHIVE |'))

    def test_workflow_contract_follows_the_single_chain(self):
        text = (ROOT / 'docs/framework/development-workflow.md').read_text(encoding='utf-8')
        self.assertNotIn('已有规格上下文用 `openspec-explore`', text)
        self.assertNotIn('顺序执行用 `superpowers:executing-plans`', text)
        self.assertNotIn('`openspec-apply-change` 负责上下文和宏观进度', text)
        self.assertNotIn('再用 `openspec-archive-change` 归档', text)
        self.assertIn('Phase 5 不应用修复', text)
        self.assertIn('Execution handoff 不是下一项', text)
        self.assertIn('不往 tasks.md 追加切片', text)
        self.assertIn('不创建 `tasks.md`', text)
        self.assertIn('SPECS_SYNCED → KNOWLEDGE_RECEIPT → ARCHIVED', text)

    def test_planning_skills_are_not_a_second_author_or_implementer(self):
        propose = (ROOT / 'skill/openspec/openspec-propose/SKILL.md').read_text(encoding='utf-8')
        update = (ROOT / 'skill/openspec/openspec-update-change/SKILL.md').read_text(encoding='utf-8')
        apply = (ROOT / 'skill/openspec/openspec-apply-change/SKILL.md').read_text(encoding='utf-8')
        plans = (ROOT / 'skill/superpowers/executing-plans/SKILL.md').read_text(encoding='utf-8')
        self.assertNotIn('tasks.md (implementation steps)', propose)
        self.assertNotIn('ask me to apply this change', propose)
        self.assertIn('Do not create `tasks.md`', propose)
        self.assertIn('to-tickets', propose)
        self.assertNotIn('carry the delta into code', update)
        self.assertIn('Do not create `tasks.md`', update)
        self.assertIn('Do not write implementation steps', update)
        self.assertNotIn('Make the code changes required', apply)
        self.assertNotIn('Mark task complete in the tasks file', apply)
        self.assertIn('Do not edit business source', apply)
        self.assertIn('TASK_VERIFIED', apply)
        self.assertNotIn('Codex App', plans)
        self.assertNotIn('Mark as completed', plans)
        self.assertIn('does not implement', plans)
        self.assertIn('does not choose delegation', plans)
