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

    def test_flow_02_readonly_audit_names_the_brief_and_hygiene_list(self):
        """Seam: the rendered flow-02 read-only audit section.

        Catches a missing familiarity split, a brief that drops one of the
        four items, a read-only slice handed out without delegation, or a
        hygiene list that edits files. Misses whether a later session
        actually follows the sentence.
        """
        text = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        audit = text.split('## 只读审计', 1)[1].split('## 纯文档', 1)[0]
        self.assertIn('不点名实现技能，不写文件。', audit)
        self.assertIn('按熟悉度分档：单点问题直接检索；单模块再读该模块约束；陌生或跨模块才做结构快照。', audit)
        self.assertIn('简报至少含文件与行号、可复用代码、仓库里已经存在的局部快测命令、要用户拍板的问题。', audit)
        self.assertIn('只有用户已授权且宿主提供子代理时，才按互不重叠的目录做只读切片；否则主 Agent 自己读。', audit)
        self.assertIn('结束仍停在只读审计，不把 openspec-explore、openspec-propose 或 to-tickets 写成下一项。', audit)
        self.assertIn('用户要看仓库卫生时，只出清单：死链、长期未改的文档是否和当前代码矛盾、没有任何入口执行的测试目录、嵌在主仓库目录里的 worktree、分支合入状态。', audit)
        self.assertIn('清单不改文件。', audit)
        self.assertIn('仍走纯文档并点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。', audit)
        self.assertIn('不重写 AGENTS.md，不新增小节，不执行 git worktree remove。', audit)
        docs = text.split('## 纯文档', 1)[1].split('## 既有规格修复', 1)[0]
        self.assertIn('被 Agent 读取的文档改动点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。', docs)
        self.assertIn('文档若改变公开接口或验收，改走新行为路径，不停留在纯文档路径。', docs)
        self.assertNotIn('oil-plan', text)
        self.assertNotIn('oil-delegate', text)
        self.assertNotIn('oil-bug-fix', text)

    def test_flow_02_tdd_keeps_one_red_and_limits_the_round(self):
        """Seam: flow-02 sentences that name tdd, and the tdd framework addition.

        Catches a round that expands into the full suite, or a rewrite of the
        RED/GREEN loop. Misses whether the commands a session runs are fast.
        """
        text = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        cadence = ('切片自己的一次 RED 失败测试保留。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。'
                   '这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。'
                   '全量、端到端和打包不在这一步用来声称验证通过。')
        self.assertGreaterEqual(text.count(cadence), 3)
        repair = text.split('## 既有规格修复', 1)[1].split('## 新行为', 1)[0]
        fresh = text.split('## 新行为', 1)[1].split('## 下一项', 1)[0]
        nxt = text.split('## 下一项', 1)[1].split('## 暂停的收尾', 1)[0]
        for section in (repair, fresh, nxt):
            self.assertIn(cadence, section)
        self.assertIn('tdd 进行中：' + cadence, nxt)
        discipline = (ROOT / 'skill/matt-pocock/tdd/discipline.md').read_text(encoding='utf-8')
        loop = ('RED      write one failing test at a confirmed seam\n'
                'VERIFY  watch it fail, and confirm it failed for the right reason\n'
                'GREEN   the smallest implementation that passes it\n'
                'REPEAT  one slice at a time')
        self.assertIn(loop, discipline)
        self.assertIn('The test passes, the other tests still pass', discipline)
        self.assertIn('写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。', discipline)
        self.assertIn('这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。', discipline)
        self.assertIn('全量、端到端和打包不在这里用来声称验证通过。', discipline)
        self.assertIn('不授权把全量、端到端或打包扩进每一次变绿。', discipline)

    def test_flow_02_review_uses_risk_tiers_and_one_local_check(self):
        """Seam: flow-02 sentences that name code-review, and the review rules.

        Catches a light change that still demands a fresh read-only context,
        a local check used as the verification claim, or a fast check copied
        into the adaptation layer. Misses whether the reviewer actually ran.
        """
        text = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        repair = text.split('## 既有规格修复', 1)[1].split('## 新行为', 1)[0]
        fresh = text.split('## 新行为', 1)[1].split('## 下一项', 1)[0]
        nxt = text.split('## 下一项', 1)[1].split('## 暂停的收尾', 1)[0]
        phrases = (
            '走轻量核对，不要求独立只读上下文。',
            '并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。',
            '没有已授权的只读子代理时，报告标明自审。',
            '对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。',
            '缺陷修复再核对改动是否在坏数据第一次产生的位置。',
            '亲自跑一次与本次改动相关的局部快测。',
            '这次通过不能代替 verification-before-completion。',
            '发现写入交付报告，不往 tasks.md 追加切片。',
            '要改源码回到 tdd。',
        )
        for phrase in phrases:
            for section in (repair, fresh, nxt):
                self.assertIn(phrase, section)
        claim = '声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。'
        self.assertIn(claim, fresh)
        self.assertIn(claim, nxt)
        rules = (ROOT / 'skill/matt-pocock/code-review/framework-rules.md').read_text(encoding='utf-8')
        self.assertIn('评审不改业务源码，不往 tasks.md 追加切片。发现写入交付报告。', rules)
        self.assertIn('flow-04 与 flow-09 没有这句，评审到报告为止。', rules)
        self.assertIn('走轻量核对，不要求独立只读上下文。', rules)
        self.assertIn('才需要独立只读上下文。', rules)
        self.assertIn('没有已授权的只读子代理时，报告标明自审。', rules)
        self.assertIn('对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。', rules)
        self.assertIn('缺陷修复再核对改动是否在坏数据第一次产生的位置。', rules)
        self.assertIn('不把评审改回改业务源码。', rules)
        self.assertIn('flow-04 与 flow-09 只把这些问题写入交付报告，不把修改交回 tdd。', rules)
        self.assertNotIn('局部快测', rules)
        for rel, entry in (
            ('skill/flows/flow-04/SKILL.md',
             '评审受管 diff 时点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。'),
            ('skill/flows/flow-09/SKILL.md',
             '规格已批准且实现之后，点名 [code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。'),
        ):
            body = (ROOT / rel).read_text(encoding='utf-8')
            self.assertIn(entry, body)
            self.assertNotIn('不往 tasks.md 追加切片', body)
            self.assertNotIn('局部快测', body)
            self.assertNotIn('轻量核对', body)
            self.assertNotIn('要改源码回到 tdd', body)

    def test_flow_02_states_branch_facts_before_finishing(self):
        """Seam: the flow-02 sentences immediately before finishing the branch.

        Catches a dirty worktree marked cleanable, or a hygiene list that
        removes a worktree. Misses the menu the finishing skill shows later.
        """
        text = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        fresh = text.split('## 新行为', 1)[1].split('## 下一项', 1)[0]
        nxt = text.split('## 下一项', 1)[1].split('## 暂停的收尾', 1)[0]
        facts = ('先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。'
                 '没有独立提交或工作区不干净的，不标成可清理。')
        self.assertIn('进入 finishing-a-development-branch 之前，' + facts, fresh)
        self.assertIn('验证通过后、进入 finishing-a-development-branch 之前：' + facts, nxt)
        self.assertIn('提交、推送、合并、删除和清理仍等待用户当次选择。', fresh)
        self.assertIn('提交、推送、合并、删除和清理仍等待用户当次选择。', nxt)
        self.assertIn('下一项才是 finishing-a-development-branch。', nxt)
        audit = text.split('## 只读审计', 1)[1].split('## 纯文档', 1)[0]
        self.assertIn('不执行 git worktree remove。', audit)
        finishing = (ROOT / 'skill/superpowers/finishing-a-development-branch/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('git worktree remove', finishing)

    def test_stage_table_and_workflow_match_the_five_practices(self):
        """Seam: the stage-table handover cells and the workflow sections they cite.

        Catches a chain that the router states and the stage table does not.
        Misses sessions that skip the table. The persona block and the three
        cut lines are compared with HEAD so this slice cannot move them.
        """
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        previous = subprocess.check_output(['git', 'show', 'HEAD:AGENTS.md'], cwd=ROOT, text=True)
        self.assertIn('<!-- AGENT_PERSONA_START -->', agents)
        self.assertIn('<!-- AGENT_PERSONA_END -->', agents)
        self.assertEqual(
            agents.split('<!-- AGENT_PERSONA_START -->', 1)[1].split('<!-- AGENT_PERSONA_END -->', 1)[0],
            previous.split('<!-- AGENT_PERSONA_START -->', 1)[1].split('<!-- AGENT_PERSONA_END -->', 1)[0],
        )
        self.assertIn('| 查询、解释、审计 | 路由 → 只读探索 → 事实、推断、未验证项与来源;不修改文件 |', agents)
        section = agents.split('<!-- AGENT_PERSONA_END -->', 1)[1].split('## 3.', 1)[0]
        self.assertIn('OpenSpec 独占可校验的规格账本', section)
        self.assertIn('`tasks.md` 的切片正文只由 `to-tickets` 写入', section)
        self.assertIn('主 Agent 用 `tdd` 实现', section)
        rows = {line.split('|')[1].strip(): line for line in agents.splitlines() if line.startswith('| ')}
        self.assertIn('额外检查只跑编译、类型检查这类秒级检查。', rows['6. IMPLEMENT'])
        self.assertIn('有效 RED → GREEN → REFACTOR → 相关回归 → TASK_VERIFIED。', rows['6. IMPLEMENT'])
        self.assertIn('走轻量核对，不要求独立只读上下文。', rows['7. REVIEW'])
        self.assertIn('亲自跑一次与本次改动相关的局部快测。', rows['7. REVIEW'])
        self.assertIn('不往 tasks.md 追加切片。', rows['7. REVIEW'])
        self.assertIn('要改源码回到 tdd。', rows['7. REVIEW'])
        self.assertIn('声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。', rows['8. VERIFY'])
        self.assertIn('先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。', rows['9. INTEGRATE'])
        self.assertIn('没有独立提交或工作区不干净的，不标成可清理。', rows['9. INTEGRATE'])
        self.assertIn('不擅自提交、推送、部署或操作设备', rows['9. INTEGRATE'])
        workflow = (ROOT / 'docs/framework/development-workflow.md').read_text(encoding='utf-8')
        old_workflow = subprocess.check_output(
            ['git', 'show', 'HEAD:docs/framework/development-workflow.md'], cwd=ROOT, text=True)
        self.assertEqual(
            workflow.split('## 2. OpenSpec', 1)[1].split('## 3.', 1)[0],
            old_workflow.split('## 2. OpenSpec', 1)[1].split('## 3.', 1)[0],
        )
        implement = workflow.split('## 8. IMPLEMENT', 1)[1].split('## 9.', 1)[0]
        review = workflow.split('## 10. REVIEW', 1)[1].split('## 11.', 1)[0]
        verify = workflow.split('## 11. VERIFY', 1)[1].split('## 12.', 1)[0]
        integrate = workflow.split('## 12. INTEGRATE', 1)[1].split('## 13.', 1)[0]
        self.assertIn('1. RED:', implement)
        self.assertIn('切片自己的一次 RED 失败测试保留。', implement)
        self.assertIn('写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。', implement)
        self.assertIn('4. REGRESSION:', implement)
        self.assertIn('这一轮改动写完后跑关联的局部快测；失败就修，修完重跑同一条。', implement)
        self.assertIn('全量、端到端和打包不在这一步用来声称验证通过。', implement)
        self.assertIn('走轻量核对，不要求独立只读上下文。', review)
        self.assertIn('亲自跑一次与本次改动相关的局部快测。', review)
        self.assertIn('不往 tasks.md 追加切片。', review)
        self.assertIn('要改源码回到 `tdd`。', review)
        self.assertIn('声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。', verify)
        self.assertIn('先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。', integrate)
        self.assertIn('没有独立提交或工作区不干净的，不标成可清理。', integrate)
        self.assertIn('推送、合并、删除和清理仍等用户当次选择。', integrate)

    def test_only_flow_02_object_changes_and_other_routers_stay(self):
        """Seam: the combination manifest's other flow objects and their rendered files.

        Catches a render that rewrites flow-01 or flow-03 through flow-15, or a
        flow-02 mention list that grows a new skill name.
        """
        current = load_combinations()['flows']
        previous = json.loads(subprocess.check_output(
            ['git', 'show', 'HEAD:tools/framework_core/workflows/combinations.json'],
            cwd=ROOT, text=True))['flows']
        self.assertEqual([item['id'] for item in current], [item['id'] for item in previous])
        for now, before in zip(current, previous):
            if now['id'] == 'flow-02':
                self.assertEqual(now['mentions'], before['mentions'])
                self.assertEqual(now['name'], before['name'])
                self.assertEqual(now['trigger'], before['trigger'])
                self.assertEqual(now['purpose'], before['purpose'])
                continue
            self.assertEqual(now, before)
            text = (ROOT / 'skill/flows' / now['id'] / 'SKILL.md').read_text(encoding='utf-8')
            old = subprocess.check_output(
                ['git', 'show', 'HEAD:skill/flows/%s/SKILL.md' % now['id']], cwd=ROOT, text=True)
            self.assertEqual(text, old)
        bound = subprocess.check_output(
            ['git', 'diff', '--name-only', 'HEAD', '--',
             'openspec/changes/bind-skill-endings-to-active-flow'],
            cwd=ROOT, text=True)
        self.assertEqual(bound, '')
        rendered = (ROOT / 'skill/flows/flow-02/SKILL.md').read_text(encoding='utf-8')
        self.assertEqual(rendered, render_skill(next(item for item in current if item['id'] == 'flow-02')))
        for name in ('oil-plan', 'oil-delegate', 'oil-bug-fix'):
            self.assertNotIn(name, rendered)


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
