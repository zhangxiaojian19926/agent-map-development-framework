## Why

同一决定在英文步骤和活动 flow 里各写了一个下一步时，会话会跟着较长的英文步骤走，中文硬约束被盖过。这次只改那几句英文决定，让它和活动 flow 已经写死的停点说同一件事。这不是把英文技能译成中文。

行号按 2026-11-17 读到的文件核对。漂了就用读到的新行号，不沿用旧约数。

## What Changes

### 本期做

只改 `skill/` 里这一处共享文本。`skill/` 由已登记的 13 个宿主共用（主规格 WR-21）。成员技能不复制到宿主发现目录（WR-04），所以不另改 13 份投影。

改的是下面 10 个文件里、会把下一步带岔的决定句。同一句在流程图、示例或后文里再次作为指令出现时，算同一处，必须一起改；留下一处，检索仍会看到第二套动作。点名的主句约 18 处，重复节点并入原决定，不另开第 13 个决定。

目标句用中文写出要达成的唯一下一步，供审阅。这里不是已经落盘的补丁。

1. `skill/matt-pocock/tdd/discipline.md` — 决定 1、决定 7
2. `skill/matt-pocock/tdd/SKILL.md` — 决定 7
3. `skill/matt-pocock/diagnosing-bugs/SKILL.md` — 决定 2
4. `skill/matt-pocock/diagnosing-bugs/discipline.md` — 决定 3、决定 4
5. `skill/superpowers/brainstorming/SKILL.md` — 决定 5、决定 6
6. `skill/matt-pocock/code-review/SKILL.md` — 决定 8、决定 9
7. `skill/matt-pocock/code-review/framework-rules.md` — 决定 9，只动并行子代理那一句
8. `skill/superpowers/subagent-driven-development/SKILL.md` — 决定 10
9. `skill/matt-pocock/to-tickets/SKILL.md` — 决定 11
10. `skill/matt-pocock/to-tickets/plan-format.md` — 决定 12

### 本期不做

- 不改 `skill/flows/flow-01/SKILL.md`、`flow-02/SKILL.md`、`flow-08/SKILL.md`、`flow-14/SKILL.md`，也不改 `tools/framework_core/workflows/combinations.json`、`docs/framework/development-workflow.md`。活动 flow 已经写死的停点是判据。
- 不改 `AGENTS.md` 里 `<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 之间的任何字节，不删标记。不改 `FRAMEWORK_ENTRY` 托管段。不改 `docs/framework/agent-persona.md`。
- 不改这三个未归档 change 的任何文件：`openspec/changes/bind-skill-endings-to-active-flow`、`openspec/changes/absorb-five-flow-02-practices`、`openspec/changes/bind-six-cause-and-claim-checks`。不勾它们的任务，不归档它们。
- 不把 43 份英文技能译成中文。不翻译 `generatedBy` 的 OpenSpec 技能、渲染出来的 flow `SKILL.md`、以及下面点名留下的上游方法正文。
- 命令、技能 ID、schema 字段、Requirement ID、`TASK_VERIFIED` 保持原文。
- 不写 `tasks.md`。不改测试。不提交，不推送。
- 不碰旁边的 61.videohao-generator 仓库。
- 不写知识库内容。本次查询见 Impact。

已核对、并且已经和中文或活动 flow 说同一件事、因此不写入本期改动的：

- `skill/superpowers/verification-before-completion/SKILL.md` 全文。
- `skill/superpowers/brainstorming/framework-rules.md` 全文。它是判据。有界路径不直接写实现、探针停在建议、`flow-08` 不创建 OpenSpec change，都已经写在这里。
- `skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 Phase 5（`:114–:122`）与 Phase 6（`:124–:134`）。Phase 5 已经停在根因，不写修复，不改生产代码。Phase 6 已经写明离开本技能不要求原循环变绿。
- `skill/matt-pocock/code-review/framework-rules.md` 里「评审不改业务源码」（`:81`）和后半报告格式。`:55` 除外，那句要改。
- `skill/superpowers/executing-plans/SKILL.md`。
- `openspec-propose`、`openspec-update-change`、`openspec-apply-change` 的停点句。

编号说明：主规格停在 WR-22。未归档的 `absorb-five-flow-02-practices` 已用 WR-23、WR-24；`bind-skill-endings-to-active-flow` 也用了 WR-23；`bind-six-cause-and-claim-checks` 已用 WR-30 至 WR-35。本 change 新增 WR-36，避免和这些未归档增量抢同一个 Requirement ID。不修改它们的 delta。

### 1. 变绿跑哪些测试

现状引文：`skill/matt-pocock/tdd/discipline.md:70`「The test passes, the other tests still pass, and the output is clean.」同文件 `:140`「All tests pass」。`:88` 后半句仍把这句英文留成规则，只补了一句「不授权把全量、端到端或打包扩进每一次变绿」。

错误动作：变绿时去确认「其他测试仍通过」，完成清单再要求「全部测试通过」。会话会把全量、端到端或打包拉进这一轮。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:63`「全量、端到端和打包不在这一步用来声称验证通过。」`:66`「评审闭合后：下一项是 verification-before-completion。声称验证通过只用这一步的全量、端到端和打包。」

改完后的唯一下一步：这一轮变绿只看刚写的那条测试，以及这轮结束后的关联局部快测；全量、端到端和打包留到 `verification-before-completion`。`:88` 里引用旧英文的那半句一并换掉，否则旧句还在。`:88` 前半的中文局部快测留下。

明确不改的相邻句：`:52–:57` 红绿循环四行（`RED` / `VERIFY` / `GREEN` / `REPEAT`）不动。`:71`「fix the code, not the test」与中文同向，不列。`:141`「Output is clean」只描述这一步已经跑过的那次输出是否干净，不单独变成第二套测试范围。

### 2. 诊断后段要不要把循环修绿

现状引文：`skill/matt-pocock/diagnosing-bugs/SKILL.md:76`「so later phases can verify the fix actually addresses it.」

错误动作：记下症状是为了后面几个阶段核对「修复有没有对上这个现象」，于是本技能接着把循环跑绿。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:58`「diagnosing-bugs 完成后：停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 tdd 写。」`skill/flows/flow-01/SKILL.md:16`「本路由不写修复，也不把 tdd 写成下一项。」`skill/flows/flow-14/SKILL.md:12` 是同一停点。

改完后的唯一下一步：记下症状是为了后面核对根因能不能解释同一现象；本技能不应用修复，也不把循环跑绿。只改 `:76` 这句目的从句。

明确不改的相邻句：Phase 1–4 留下。Phase 5（`:114–:122`）与 Phase 6（`:124–:134`）已经是这个停点，不列。`:61`「green once fixed」说的是循环要有能力在修好之后变绿，当下动作仍是先有一条能变红的命令，不单列。`:74`「Wrong bug = wrong fix」不单列。

### 3. 根因查清后诊断技能自己改生产代码

现状引文：

- `skill/matt-pocock/diagnosing-bugs/discipline.md:22`「If you have not completed Phase 1, you cannot propose fixes.」
- `:68–:69`「STOP after the third failed attempt. Do not start fix #4.」
- `:79–:81`「Discuss it with your human partner before attempting another fix. Three attempts that fail the same way is an architectural signal, not a debugging technique.」
- `:139`「A fix that works is not the end of the investigation.」

同决定的其余指令副本，必须一起改，否则检索仍看到「先试修复」：`:62` 标题「When three fixes fail, question the architecture」；`:94`「3+ failures = architectural problem. Question the pattern, don't fix again.」；`:105–:106`「One more fix attempt」。

错误动作：Phase 1 做完就可以提出修复；本技能自己先试修复，三次失败才停，第四次不许再试。这把修生产代码留在诊断技能里。

活动 flow 已写死：同决定 2。`flow-02:58` 把回归测试和修复交给 `tdd`，并且只在路由把 `tdd` 写成下一项之后。`flow-01:16` 与 `flow-14:12` 连 `tdd` 都没有。中文 `:27`、`:38–:39` 已经写「本技能仍不改产品代码」「本技能不写生产代码」。

改完后的唯一下一步：本技能在根因前后都不改生产代码；不存在「先试三次修复」。三次失败若发生在 `tdd` 里，由 `tdd` 在活动 flow 把 `tdd` 写成下一项之后处理。`flow-01` 与 `flow-14` 连 `tdd` 都没有。

明确不改的相邻句：`:18–:20` 铁律「NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST」留下，没有根因就不许改。`:24–:25` 只定义「报错消失但没解释原因不算修复」，不授权本技能改码。`:37–:44` 环境故障是 `INFRA_ERROR`，不列。`:90` 已经改成「查完根因后不先写测试再修复」，不列。`:27` 与 `:38–:39` 的中文不改。

### 4. 根因陈述之后写知识页或改 flow 契约

现状引文：`skill/matt-pocock/diagnosing-bugs/discipline.md:157–:166`「The layer decides what you write down next」，接着把内容写成 `concept` 页，把流程写成去改 flow 契约（`:150` 点名 `development-workflow.md`）。同一决定的表在 `:145–:151`：`What to change` 与 `Where it lands` 两列已经把「加概念页」「改 flow 契约」写成下一步。

错误动作：根因归到某一层之后，本技能接着新建概念页，或去改 flow 契约。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:69`「规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有 verified-problem.json 且 conclusion 为 pass 时写入问题页」。概念页和问题页走这一步，不在诊断技能里写。

改完后的唯一下一步：在根因陈述里点明失败落在内容、取用、验证、流程还是方法；本技能不因此新建概念页，也不改 flow 契约。概念页和问题页仍走 `flow-02` 的知识步骤。

明确不改的相邻句：五层的名字留下，只用来写进根因陈述。`:153–:155`「哪个知识库」与「哪一层」要分开记录的区分留下，但记录本身不在本技能里落成新页或改契约。`:169` 之后的脱敏留下。

### 5. 有界设计批准后直接实现

现状引文：

- `skill/superpowers/brainstorming/SKILL.md:92`「Implement — proceed with the normal development workflow (TDD applies); no plan document」
- `:115` 与 `:134`「Implement via normal workflow (no plan doc)」
- `:150–:152`「Bounded: after approval, implementation proceeds directly through the normal development workflow; no plan document.」

错误动作：有界设计一旦批准，本技能直接进入实现，不经过规格。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:75`「改变行为、接口或验收的有界设计仍进入规格和 to-tickets，不按有界路径直接写实现。探针停在建议。」`:59`「只有要改行为、接口或验收才进入规格；探针停在建议。」`skill/superpowers/brainstorming/framework-rules.md:11` 是同一句，本文件不改。

改完后的唯一下一步：批准之后收尾指向活动 flow；要改行为、接口或验收就等 flow 进入规格；探针停在建议；本技能不按有界路径直接写实现。这句放在有界清单第 5 步（`:92`）旁边，不只留在 `framework-rules.md` 末段。`:115`、`:134`、`:150–:152` 改成同一个终点。

明确不改的相邻句：架构路径 `:103`、`:149`、`:247` 已经是「收尾指向活动 flow 的下一项」，不列。`:85` 探针停在建议，不列。`framework-rules.md` 全文不改。

### 6. 大需求拆开后自己走 spec → plan → implementation

现状引文：`skill/superpowers/brainstorming/SKILL.md:167`「Each sub-project gets its own spec → plan → implementation cycle.」

错误动作：每个子项目由本技能启动一轮 spec、plan、implementation。

活动 flow 已写死：`skill/flows/flow-08/SKILL.md:4` 与 `:12`「不创建 OpenSpec change，包括未批准的 change。」`:11` 停在设计对话，不把 `openspec-propose` 或 `to-tickets` 当作下一项。`flow-02:59` 只在要改行为、接口或验收、并且路由宣布进入规格时，才把规格写成下一项。

改完后的唯一下一步：每个子项目单独做一轮设计对话，结束时指向当时活动 flow 的下一项；本技能不替它启动 spec、plan、implementation。`flow-08` 不创建 OpenSpec change。

明确不改的相邻句：`:165–:166` 先帮用户把独立片段拆开，这句留下。`:168` 之后「一次只问一个问题」留下。

### 7. 当前任务里的窄整理归谁做

现状引文：`skill/matt-pocock/tdd/SKILL.md:38`「Refactoring is not part of the loop. It belongs to the review stage」。`skill/matt-pocock/tdd/discipline.md:90–:93`「Both are true here: the cleanup that keeps the current task readable happens with the implementation; the restructuring that changes what the module is happens at review.」

错误动作：红到绿完全不许整理，整理整段推给评审；同时又说「两句都对」。会话可以选「现在不整理」或「现在就改模块」。

活动 flow 已写死：`docs/framework/development-workflow.md:92`「REFACTOR:只做当前任务必要整理,测试保持通过;设计级重构不在此步,归入评审阶段讨论。」`skill/flows/flow-02/SKILL.md:65`「要改源码回到 tdd。」本文件 `development-workflow.md` 不改，它是判据。

改完后的唯一下一步：红到绿不夹带设计级重构；当前任务里的重复、命名和辅助函数仍在本技能的整理步做完；改 seam、模块职责或接口放到评审里讨论；真要改源码，回到 `tdd`。

明确不改的相邻句：`discipline.md:80–:86` 已经把当前任务内的重复、命名、辅助函数留在实现阶段，把挪 seam、改模块职责、改接口放到评审讨论，这几条留下。`:38` 与 `:90–:93` 改成和它们同一句话，不再用「两句都对」并立。

### 8. 找不到规格时去跑安装技能，或到 docs、.scratch 里找

现状引文：`skill/matt-pocock/code-review/SKILL.md:13`「tell the user to run `/setup-matt-pocock-skills`」。`:27–:32` 先找提交里的 issue，再找用户给的路径，再找 `docs/`、`specs/`、`.scratch/`。描述行 `:3` 把规格写成 “originating issue/spec”，与这套查找是同一决定。

错误动作：找不到规格就让用户跑本包不存在的安装技能，或到 `docs/`、`.scratch/` 里认一份规格。

活动 flow 已写死：`skill/matt-pocock/code-review/framework-rules.md:7–:9`「Do not ask the user to run a setup skill that does not exist here.」`:15`「the specification is the OpenSpec change」。`:33–:36` 找不到就报告 “no spec available”。`skill/flows/flow-02/SKILL.md:65` 对照的是活动 OpenSpec change。`:7–:40` 的规格来源段本期不改。`:55` 归决定 9。

改完后的唯一下一步：规格就是活动 OpenSpec change；找不到就在报告里写无可用规格。

明确不改的相邻句：`:9–:10` 两轴的问题定义留下。`:34–:42` 气味基线、`:43–:56` 气味清单留下。清单里的 “how to fix” 是发现标签，不是现在改源码，不把它写成冲突，也不改这些标签。

### 9. 每次评审都拉起两个子代理

现状引文：

- `skill/matt-pocock/code-review/SKILL.md:3`「Runs both reviews in parallel sub-agents」
- `:11`「Both axes run as parallel sub-agents」
- `:23`「not inside two parallel sub-agents」
- `:58–:60`「Spawn both sub-agents in parallel」「Issue both sub-agent calls together」
- `skill/matt-pocock/code-review/framework-rules.md:55–:56`「The upstream method runs Standards and Spec as parallel sub-agents so neither pollutes the other.」

错误动作：每次评审都拉起两个并行子代理，低风险也不例外，没有子代理时仍要派。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:65`「纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。……没有已授权的只读子代理时，报告标明自审。」`framework-rules.md:89` 是同一句。`:81`「评审不改业务源码」。

改完后的唯一下一步：低风险不派独立上下文；高风险只在已有授权的只读子代理时派；没有时报告标明自审。评审不改业务源码。

明确不改的相邻句：`:81`「评审不改业务源码」和 `:87–:89` 的风险分档、报告格式留下。气味清单的 “how to fix” 不改。两轴对照留下，只是不再把「两条轴一定并行派子代理」写成每次都发生的指令。

### 10. 委派实现者提交，并另派一套任务评审

现状引文：`skill/superpowers/subagent-driven-development/SKILL.md:70`「Implementer implements, tests, commits, self-reviews」。`:290`「dispatch the task reviewer」。`:352`「Template: task-reviewer-prompt.md」。`:487`「Use superpowers:finishing-a-development-branch.」

同一决定的指令副本，必须一起改：图中 `:71`、`:91`、`:96–:99`、`:120`；正文 `:324`、`:345`、`:469`；文末示例 `:527`、`:542`、`:567`。这些行仍在命令实现者提交、派 `task-reviewer-prompt`，或把 `finishing-a-development-branch` 写成这个技能的下一项。

错误动作：被委派的实现者自己提交；控制器再派一套上游任务评审；做完后这个技能自己提示 `finishing-a-development-branch`。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:40`「被委派者仍用 tdd」。`:50`「提交、推送、合并、删除和清理仍等待用户当次选择。」`:56`「成员技能结束时不各自提示下一个技能。」`:65` 评审用 `code-review`。`skill/superpowers/subagent-driven-development/framework-rules.md:19`「Do not dispatch the upstream task-reviewer-prompt.md.」`:40`「The implementer does not commit.」这份 `framework-rules.md` 已经是判据，本期不改。

改完后的唯一下一步：被委派者仍用 `tdd`，实现者不提交；不派上游任务评审，评审用 `code-review`；本技能结束时不自己提示下一个技能，因此不把 `finishing-a-development-branch` 写成下一项。提交仍等用户当次选择。`task-reviewer-prompt.md` 这个文件可以留下，但 `SKILL.md` 不再把它写成要执行的指令。

明确不改的相邻句：何时才读这个技能，仍由活动 flow 决定，本技能不另写一套委派时机。`:55`「Fresh subagent per task」留下。控制器不自己改发现的句子留下，包括 `:494` 附近「Controller fixes pollute your context」。`:46–:47` 的改编层读法已经是「implements, tests, reports, self-reviews」，不改那份 `framework-rules.md`。

### 11. 切片写到 .scratch，或先要求安装技能

现状引文：`skill/matt-pocock/to-tickets/SKILL.md:3` 把切片写成发给配置好的 tracker。`:10`「tell the user to run `/setup-matt-pocock-skills`」。`:57–:62` 按该安装命令配置的 tracker 发布：本地写到 `.scratch/<feature-slug>/issues/`，或者发到 GitHub、Linear 等外部 tracker。

错误动作：先要求用户跑不存在的安装命令，再把切片写进 `.scratch` 或外部 tracker。

活动 flow 已写死：`skill/matt-pocock/to-tickets/plan-format.md:19–:21`「Write them into the current OpenSpec change's tasks.md」。`skill/flows/flow-02/SKILL.md:37`「切片正文只写入当前 change 的 tasks.md。」`:80`「to-tickets 不写 .scratch，也不要求本包不存在的安装命令。」`:19–:21` 已经同向，不列为本期要改的句子。

改完后的唯一下一步：切片正文只写入当前 change 的 `tasks.md`；不写 `.scratch`，不要求安装命令，不发到外部 tracker。

明确不改的相邻句：`:28–:39` 垂直切片和阻塞边、宽重构的 expand–contract 切法留下。`:69` 之后的单票模板若只描述一张切片的字段，可以留下；它不得再被 `:57–:62` 用来把切片发到 `.scratch` 或外部 tracker。

### 12. 计划批准后由 Execution handoff 选择执行方式

现状引文：`skill/matt-pocock/to-tickets/plan-format.md:173–:182`「After the plan is approved, offer the execution choice」，选项是子代理执行或当轮执行，「Either way, the slice state is updated in the change's tasks.md」。

错误动作：计划一批准，就在这里让人选择子代理执行或当轮执行，并开始改 `tasks.md` 的勾选。

活动 flow 已写死：`skill/flows/flow-02/SKILL.md:37`「plan-format.md 的 Execution handoff 不是下一项。`- [ ]` 改成 `- [x]` 仍等该切片 TASK_VERIFIED。」`:60` 是同一句。

改完后的唯一下一步：不再提供子代理执行或当轮执行的选择，也不在这里改勾选；下一项由活动 flow 宣布。

明确不改的相邻句：`:39` 起的切片字段留下。`:155–:169` 自检留下。`:19–:21` 写入当前 change 的 `tasks.md` 留下。

### 验收

实现阶段才改测试。本次不改 `tests/test_flow_routers.py`。

`tests/test_flow_routers.py:289` 在 `test_flow_02_tdd_keeps_one_red_and_limits_the_round` 里锁着「The test passes, the other tests still pass」。实现时这条改成决定 1 的唯一下一步，并断言旧句不再作为指令出现。同函数 `:284–:288` 红绿循环四行的断言不动。`:290–:293` 对中文局部快测的断言保留，并跟上决定 1 改写后的 `:88`。

同一次实现补上这些字符串不再作为指令出现：`setup-matt-pocock-skills`、`Issue both sub-agent calls`、`Implement via normal workflow`、`All tests pass`、`task-reviewer-prompt`。检索范围是上面 10 个文件里被本提案点名的决定句，不是全库删除文件名。`task-reviewer-prompt.md` 文件本身可以留下。

改完后对每个决定检索两套动作，只剩活动 flow 那一个下一步，再跑 `tests/test_flow_routers.py`。`:67`、`:713`、`:726` 锁的是 flow 正文里的「Execution handoff 不是下一项」，那些断言不动，因为 flow 正文不动。

这些场景写在 delta spec 里。本次不改测试，也不为了让现有断言继续通过而把旧英文留着。

**BREAKING**：已经按「变绿时其他测试仍要通过」「有界批准后直接实现」「每次评审都派两个子代理」「实现者自己提交并派任务评审」「切片写入 .scratch 或外部 tracker」「Execution handoff 里选择执行方式并改勾选」在做的会话，改为上面各条的唯一下一步。

## Capabilities

### New Capabilities

- 无。不新增 capability 目录。

### Modified Capabilities

- `agent-workflow-routers`：新增 Requirement `WR-36`。12 个决定的英文决定句改为活动 flow 已经写死的那一个下一步。不修改 WR-01 至 WR-22 的现有句子，也不改 flow 正文。不把 `skip_specs` 写入本 change 的 `.openspec.yaml`。

## Impact

- 将来要改的只有上面 10 个共享技能文件里的决定句。`skill/flows/`、`combinations.json`、`docs/framework/development-workflow.md`、`AGENTS.md` 托管段和人格标记都不改。13 个宿主读的是这一处 `skill/`，不改宿主安装器，也不往发现目录复制第二份。
- 知识查询已做，只读。注册表 `llm-wiki-aliases.json` 把 alias `project` 指到 `knowledge/project/`。`bash skill/llm-wiki/scripts/query.sh knowledge/project "技能停点 下一项"` 退出码 0，命中 `wiki/topics/requirements/agent-workflow-routers.md`（10 处）、`completion-knowledge-ingest.md`（4 处）、`knowledge-influence-tracking.md`（4 处）。需求页 `source_sha256` 为 `82e68c829313c75397b26a91ec24fee51aa172332a9d657ce027e0bdf22a5fa0`，与现行 `openspec/specs/agent-workflow-routers/spec.md` 的 sha256 一致。该页写明当前需求以来源规格为准，没有把这 12 句英文决定写成已经只剩一个下一步。本提案以规格和活动 flow 正文为准。不写知识页。
- 未归档的 `absorb-five-flow-02-practices` 曾经把 `:70` 的英文留下，只用中文声明它不授权扩成全量。那个 change 的目录不动。本提案改的是仍留在 `discipline.md` 里的那句英文，以及 `:88` 里引用旧英文的半句。`bind-skill-endings-to-active-flow` 已经把 Phase 5 停在根因，本提案不重开 Phase 5。`bind-six-cause-and-claim-checks` 的根因解释、二分和「这些动作不算修复」不动。
- 风险：只改点名的一行、留下流程图或示例里的同一句，验收检索会失败。实现时按每个决定列出的副本一起改。气味清单的 “how to fix”、红绿四行、铁律、Phase 5 与 Phase 6 若被顺手改写，会超出本期。
- 非目标：本次不修改技能正文，不写 `tasks.md`，不写 `design.md`。schema 只在跨模块新架构、新外部依赖、安全或迁移复杂性、或会改变规格的未决技术选择时才要求 `design.md`。这里没有新依赖，也没有新架构；停点已经由活动 flow 写死。不改测试，不提交，不推送。入口 doctor 未跑成，原因见交付说明，本变更不为它安装工具。
