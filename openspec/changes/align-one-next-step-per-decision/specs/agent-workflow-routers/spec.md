## ADDED Requirements

### Requirement: WR-36 同一决定只剩活动 flow 的一个下一步

系统 SHALL 只改 `skill/` 这一处共享文本，使下面 12 个决定各自只剩活动 flow 已经写死的那一个下一步。`skill/` 由已登记的 13 个宿主共用。系统 MUST NOT 把成员技能复制到宿主发现目录。系统 MUST NOT 改 `skill/flows/flow-01/SKILL.md`、`skill/flows/flow-02/SKILL.md`、`skill/flows/flow-08/SKILL.md`、`skill/flows/flow-14/SKILL.md`、`tools/framework_core/workflows/combinations.json` 或 `docs/framework/development-workflow.md`。系统 MUST NOT 修改 `<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 之间的字节，也 MUST NOT 修改 `FRAMEWORK_ENTRY` 托管段。

同一句在流程图、示例或后文里再次作为指令出现时，系统 MUST 一起改。系统 MUST NOT 把其余英文方法正文译成中文。命令、技能 ID、schema 字段、Requirement ID 与 `TASK_VERIFIED` MUST 保持原文。

`tdd` 的 `discipline.md` 在这一轮变绿时 MUST 只看刚写的那条测试，以及这轮结束后的关联局部快测。全量、端到端和打包 MUST 留到 `verification-before-completion`。`:52–:57` 的 `RED` / `VERIFY` / `GREEN` / `REPEAT` 四行 MUST 保持不动。`:71` 的 “fix the code, not the test” MUST 保持不动。

`diagnosing-bugs` 的 `SKILL.md` 记下症状的目的从句 MUST 改为：记下症状是为了后面核对根因能不能解释同一现象。本技能 MUST NOT 因此应用修复，也 MUST NOT 把循环跑绿。Phase 1–4、Phase 5 与 Phase 6 MUST 保持不动。`:61` 的 “green once fixed” MUST 保持不动。

`diagnosing-bugs` 的 `discipline.md` MUST 在根因前后都不改生产代码，并且 MUST NOT 存在「先试三次修复」。三次失败若发生在 `tdd` 里，MUST 由 `tdd` 在活动 flow 把 `tdd` 写成下一项之后处理。`flow-01` 与 `flow-14` MUST 仍不把 `tdd` 写成下一项。铁律 “NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST” MUST 保持不动。环境故障仍是 `INFRA_ERROR` 的句子 MUST 保持不动。

同一份 `discipline.md` 的根因陈述 MUST 点明失败落在内容、取用、验证、流程还是方法。本技能 MUST NOT 因此新建概念页，也 MUST NOT 改 flow 契约。概念页和问题页 MUST 仍走 `flow-02` 的知识步骤。

`brainstorming` 的 `SKILL.md` 在有界清单第 5 步旁边 MUST 写明：批准之后收尾指向活动 flow；要改行为、接口或验收就等 flow 进入规格；探针停在建议；本技能不按有界路径直接写实现。这句 MUST NOT 只留在 `framework-rules.md`。`brainstorming` 的 `framework-rules.md` MUST 保持不动。架构路径里已经指向活动 flow 的句子 MUST 保持不动。每个子项目 MUST 只单独做一轮设计对话，结束时指向当时活动 flow 的下一项。本技能 MUST NOT 替子项目启动 spec、plan 或 implementation。`flow-08` MUST 仍不创建 OpenSpec change。

`tdd` 的 `SKILL.md` 与 `discipline.md` 里「两句都对」的并立 MUST 改为一个下一步：红到绿不夹带设计级重构；当前任务里的重复、命名和辅助函数仍在本技能的整理步做完；改 seam、模块职责或接口放到评审里讨论；真要改源码，回到 `tdd`。`:80–:86` 已经写明的范围清单 MUST 保持不动。

`code-review` 的 `SKILL.md` MUST 把规格写成活动 OpenSpec change。找不到时 MUST 在报告里写无可用规格。系统 MUST NOT 要求运行 `setup-matt-pocock-skills`，也 MUST NOT 把 `docs/`、`specs/` 或 `.scratch/` 写成规格来源。两轴对照和气味基线 MUST 保持不动。气味清单里的 “how to fix” MUST 仍只是发现标签。

`code-review` 的 `SKILL.md` 与 `framework-rules.md` 里「每次都派两个并行子代理」的指令 MUST 改为：低风险不派独立上下文；高风险只在已有授权的只读子代理时派；没有时报告标明自审。评审 MUST NOT 改业务源码。`framework-rules.md` 里除这句以外的「不改源码」和后半报告格式 MUST 保持不动。

`subagent-driven-development` 的 `SKILL.md` MUST 写明被委派者仍用 `tdd`，实现者不提交，不派上游任务评审，评审用 `code-review`。本技能 MUST NOT 把 `finishing-a-development-branch` 写成自己的下一项。`task-reviewer-prompt` MUST NOT 再作为要执行的指令出现在该 `SKILL.md`。委派时机、新鲜子代理，以及控制器不自己改发现的方法句 MUST 保持不动。同目录 `framework-rules.md` MUST 保持不动。

`to-tickets` 的 `SKILL.md` MUST 只把切片正文写入当前 change 的 `tasks.md`。系统 MUST NOT 写 `.scratch`，MUST NOT 要求安装命令，也 MUST NOT 发到外部 tracker。垂直切片和阻塞边的切法 MUST 保持不动。`plan-format.md` 的 Execution handoff MUST NOT 再提供子代理执行或当轮执行的选择，也 MUST NOT 在这里把 `- [ ]` 改成 `- [x]`。勾选 MUST 仍等该切片 `TASK_VERIFIED`。下一项 MUST 由活动 flow 宣布。切片字段和自检 MUST 保持不动。

#### Scenario: 变绿只看刚写的测试和局部快测

- **WHEN** 读取 `skill/matt-pocock/tdd/discipline.md` 的变绿句和完成清单
- **THEN** 这一轮变绿只看刚写的那条测试，以及这轮结束后的关联局部快测；全量、端到端和打包留到 `verification-before-completion`；“The test passes, the other tests still pass” 与 “All tests pass” 不再作为指令出现；红绿循环四行仍在

#### Scenario: 诊断记下症状是为了核对根因

- **WHEN** 读取 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 记下症状的那一句，以及 Phase 5 与 Phase 6
- **THEN** 目的从句是为了后面核对根因能不能解释同一现象；本技能不应用修复，也不把循环跑绿；Phase 5 与 Phase 6 的停点原文仍在

#### Scenario: 诊断技能不试三次修复

- **WHEN** 读取 `skill/matt-pocock/diagnosing-bugs/discipline.md` 里提出修复、三次失败后停止、以及 “A fix that works” 的句子
- **THEN** 本技能在根因前后都不改生产代码；不存在「先试三次修复」；铁律 “NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST” 仍在；环境故障仍是 `INFRA_ERROR`

#### Scenario: 根因分层不新建概念页

- **WHEN** 读取 `skill/matt-pocock/diagnosing-bugs/discipline.md` 的失败分层，包括 “The layer decides what you write down next”
- **THEN** 根因陈述点明失败落在内容、取用、验证、流程还是方法；本技能不因此新建概念页，也不改 flow 契约；概念页和问题页仍走 `flow-02` 的知识步骤

#### Scenario: 有界批准后不直接实现

- **WHEN** 读取 `skill/superpowers/brainstorming/SKILL.md` 的有界清单第 5 步、图终点和 “Bounded: after approval”
- **THEN** 批准之后收尾指向活动 flow；要改行为、接口或验收就等 flow 进入规格；探针停在建议；本技能不按有界路径直接写实现；“Implement via normal workflow” 不再作为指令出现；架构路径里已经指向活动 flow 的句子仍在；`framework-rules.md` 未被本 requirement 改写

#### Scenario: 子项目不自启实现循环

- **WHEN** 读取 `skill/superpowers/brainstorming/SKILL.md` 里拆开大需求的那一句，并读取 `flow-08`
- **THEN** 每个子项目单独做一轮设计对话，结束时指向当时活动 flow 的下一项；本技能不替它启动 spec、plan、implementation；`flow-08` 仍不创建 OpenSpec change

#### Scenario: 窄整理留在实现步

- **WHEN** 读取 `skill/matt-pocock/tdd/SKILL.md` 的整理句和 `discipline.md` 里 “Both are true” 的段落
- **THEN** 红到绿不夹带设计级重构；当前任务里的重复、命名和辅助函数仍在本技能的整理步做完；改 seam、模块职责或接口放到评审里讨论；真要改源码，回到 `tdd`；`:80–:86` 的范围清单仍在

#### Scenario: 规格就是活动 change

- **WHEN** 读取 `skill/matt-pocock/code-review/SKILL.md` 里寻找规格的句子
- **THEN** 规格就是活动 OpenSpec change；找不到就在报告里写无可用规格；不要求运行 `setup-matt-pocock-skills`；不把 `docs/`、`specs/` 或 `.scratch/` 写成规格来源；两轴对照和气味基线仍在

#### Scenario: 低风险不派两个子代理

- **WHEN** 读取 `skill/matt-pocock/code-review/SKILL.md` 的并行子代理指令，以及 `framework-rules.md` 里 “runs Standards and Spec as parallel sub-agents” 的句子
- **THEN** 低风险不派独立上下文；高风险只在已有授权的只读子代理时派；没有时报告标明自审；评审不改业务源码；“Issue both sub-agent calls” 不再作为指令出现；气味清单的 “how to fix” 仍只是发现标签

#### Scenario: 实现者不提交也不派任务评审

- **WHEN** 读取 `skill/superpowers/subagent-driven-development/SKILL.md` 里实现者提交、派任务评审和结束技能的句子
- **THEN** 被委派者仍用 `tdd`；实现者不提交；不派上游任务评审，评审用 `code-review`；本技能不把 `finishing-a-development-branch` 写成下一项；`task-reviewer-prompt` 不再作为指令出现；新鲜子代理和控制器不自己改发现的方法句仍在

#### Scenario: 切片只写入当前 change

- **WHEN** 读取 `skill/matt-pocock/to-tickets/SKILL.md` 的发布步骤
- **THEN** 切片正文只写入当前 change 的 `tasks.md`；不写 `.scratch`，不要求安装命令，不发到外部 tracker；垂直切片和阻塞边的切法仍在

#### Scenario: Execution handoff 不选择执行方式

- **WHEN** 读取 `skill/matt-pocock/to-tickets/plan-format.md` 的 Execution handoff
- **THEN** 不再提供子代理执行或当轮执行的选择，也不在这里把 `- [ ]` 改成 `- [x]`；勾选仍等该切片 `TASK_VERIFIED`；下一项由活动 flow 宣布；切片字段和自检仍在

#### Scenario: 路由测试锁改到新的唯一下一步

- **WHEN** 实现本 requirement 后读取 `tests/test_flow_routers.py` 的 `test_flow_02_tdd_keeps_one_red_and_limits_the_round`
- **THEN** 原先锁着 “The test passes, the other tests still pass” 的断言改为这一轮变绿的唯一下一步；同函数里红绿循环四行的断言仍在；`setup-matt-pocock-skills`、`Issue both sub-agent calls`、`Implement via normal workflow`、`All tests pass` 与 `task-reviewer-prompt` 不再作为上述决定句里的指令出现

#### Scenario: 活动 flow 与三个未归档 change 不动

- **WHEN** 核对本 requirement 允许修改的路径
- **THEN** `flow-01`、`flow-02`、`flow-08`、`flow-14`、`combinations.json` 与 `development-workflow.md` 不因本 requirement 改写；`bind-skill-endings-to-active-flow`、`absorb-five-flow-02-practices` 与 `bind-six-cause-and-claim-checks` 三个目录不改，它们的任务不被勾选
