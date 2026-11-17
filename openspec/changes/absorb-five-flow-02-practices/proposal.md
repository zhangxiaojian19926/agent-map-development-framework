## Why

`flow-02` 的只读审计、评审、实现中的检查和进入收尾之前，还没有写明五条已经能放进现有账本的做法。只读审计现在只有「不点名实现技能，不写文件」。`code-review` 被点名之后没有按改动风险决定要不要独立只读上下文，也没有亲自跑一次与本次改动相关的局部快测。`tdd` 写生产代码时，同目录纪律仍把「其他测试也要通过」放在每一次变绿里。进入 `finishing-a-development-branch` 之前，路由没有要求先用只读事实说明分支和工作树。这五条都是在现有路径上补句子。会另开账本或另写源码的三条不吸。不实施。

来源是用户给定、已经读过的 <https://github.com/oil-oil/oil-dev-skills> 技能入口。下面用做法写，不把那些技能名写成新的下一项。

### 前提

下列句子均按当前文件核对。与用户给定口径冲突时，以文件为准，并在该条标明。

1. 十五条路由仍是一次只命中一条。`AGENTS.md` 第 93 行写明入口是 `flow-01` 到 `flow-15`，一条请求只命中其中一个，下一项以该路由正文为准。`openspec/specs/agent-workflow-routers/spec.md` 的 WR-01 要求恰好这十五条。WR-05 要求只用 `flow-02` 一条描述覆盖日常开发，只读审计、纯文档、既有规格修复和新行为写在正文内部。这次不新增第十六条，也不把卫生清单做成第五条可自动选中的路径。

2. 切分线已经落在 `flow-02`，这次不移动它。OpenSpec 独占规格账本。`tasks.md` 的切片正文只由 `to-tickets` 写。源码只由 `tdd` 写。这三句在 `AGENTS.md` 第 91 行、`docs/framework/development-workflow.md` 第 22–23 行、`combinations.json` 的 `flow-02` 对象，以及 WR-06、WR-08。诊断停在红信号、最小复现和根因，Phase 5 不应用修复，回归测试和修复只由 `tdd` 写。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片；在 `flow-02` 上，要改源码回到 `tdd`。

3. 路由正文的事实源是组合清单。`tools/framework_core/workflows/routers.py` 的 `render_skill` 用一个 flow 对象生成一份 `SKILL.md`。`write_routers` 对清单里的十五条都写回 `skill/flows/<id>/SKILL.md`。`distribution_errors` 在文件与渲染结果不一致时报 `router body drifted from the combination manifest`。因此 `skill/flows/flow-02/SKILL.md` 不能手改。要改的是 `combinations.json` 里 `id` 为 `flow-02` 的对象，再渲染。`write_routers` 会重写全部十五条；其余对象不改，所以其余十四份与改前一致。

4. 只读审计现在只有一句，和用户给定的探索简报不冲突，只是还没写。`skill/flows/flow-02/SKILL.md` 第 14 行，以及 `combinations.json` 里 `flow-02` 的「只读审计」那一行，都是「不点名实现技能，不写文件。」WR-06 的只读审计条目是同一句。这一句保留。要补的是熟悉度分档、简报四项、只读切片条件和停点。结束仍停在只读审计。`openspec-explore`、`openspec-propose`、`to-tickets` 不写成这一路径的下一项。这三名已经出现在 `flow-02` 的新行为链里，出现在「不是下一项」里不构成把它们加进只读审计。

5. 纯文档路径已经点名 `writing-for-agents`。`flow-02` 正文第 18–19 行：被 Agent 读取的文档改动点名该技能；文档若改变公开接口或验收，改走新行为。卫生清单之后若要改这类文档，仍走这一路径。清单本身不改文件，也不把 `writing-for-agents` 写成只读审计的下一项。

6. 委派条件已经写明，只读切片沿用它，不另造产品名单。`flow-02` 正文第 36–38 行：没有委派授权，或宿主不提供子代理能力时，主 Agent 自己做，并写明未委派；委派只在用户已授权且宿主提供子代理时发生；子代理是任何一个 coding agent 都可以有的能力，不是只有 Claude Code 与 CodeBuddy。WR-21 是同一句。只读审计若要按互不重叠的目录做只读切片，使用这一条件。否则主 Agent 自己读。不引入固定产品名单的外部 CLI。

7. `code-review` 的改编层已经禁止改码和追加切片，风险分档只加句子。`skill/matt-pocock/code-review/framework-rules.md` 第 4–5 行：与上游 `SKILL.md` 冲突时以本文件为准。第 68–77 行：自审必须标明自审，不得报成独立通过。第 81–84 行：评审不改业务源码，不往 `tasks.md` 追加切片；发现写入交付报告；活动路由把 `tdd` 写成下一项时，修改回到 `tdd`；`flow-04` 与 `flow-09` 没有这句，评审到报告为止。第 87–93 行已经要求结论绑定实际跑过的命令。上游 `SKILL.md` 第 11 行和第 58 行仍写两条轴都启动并行子代理。这是文件差异：轻量核对不要求独立只读上下文，所以不能靠手改上游来实现，只能在改编层加句子，由第 4–5 行盖过「总是起子代理」。第 81–84 行不改写回改码，也不恢复 change task list。

8. `flow-04` 与 `flow-09` 的入口不承载这五条。`combinations.json` 里 `flow-04` 只点名 `code-review` 与 `framework-rules.md`，人工改动冲突时停止。`flow-09` 在规格已批准且实现之后点名同一对，找不到 change 时报告无可用规格。`tests/test_flow_routers.py` 的 `test_review_findings_are_not_appended_to_tasks` 要求这两份正文不含「不往 tasks.md 追加切片」。因此风险分档不写进这两份路由正文。它们读到改编层的新句子后，只把问题写入报告，不把修改交回 `tdd`。入口两句保持原样。

9. 局部快测通过不能代替验证，这一句和现行验证技能同向。`skill/superpowers/verification-before-completion/SKILL.md` 第 27–28 行要求跑完整命令再声称通过，第 56 行把依赖部分验证列为红旗，第 71 行写明部分检查不能证明通过。`AGENTS.md` 第 104 行把验证放在 `verification-before-completion`，交接的是最终工作树的新鲜证据。`flow-02` 正文第 46 行先点名这一技能，第 47 行才点名收尾。用户给定的「全量、端到端和打包仍只在这一步用来声称验证通过」与这些句子一致。要补的是 `flow-02` 的 `code-review` 亲自跑一次相关局部快测，并写明这次通过不能代替第 46 行。不改验证技能去接受局部快测作为通过。

10. `tdd` 的循环和「写代码途中」需要分成两段，否则和现行文件冲突。`skill/matt-pocock/tdd/discipline.md` 第 52–68 行仍是 RED、确认失败、GREEN、一次一条。第 70 行写「The test passes, the other tests still pass」。`AGENTS.md` 第 102 行的交接仍是「有效 RED → GREEN → REFACTOR → 相关回归 → TASK_VERIFIED」。`docs/framework/development-workflow.md` 第 91–94 行把 RED 写成先跑能到达目标路径的失败测试，第 4 步 REGRESSION 写成运行受影响范围的测试。文件与「写代码途中只跑秒级检查」同时成立的读法是：切片自己的那一次 RED 失败测试保留，这是现行第 102 行的有效 RED，不是全量；写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查，不把第 70 行的「其他测试」扩成全量、端到端或打包；这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量仍留在 `verification-before-completion`。取消那一次 RED 会改掉已经写明的循环，这次不取消。

11. 收尾技能自己会跑全量，也会在用户选择之后删除工作树。`skill/superpowers/finishing-a-development-branch/SKILL.md` 第 14–16 行在展示菜单前跑项目全量测试。第 169–173 行在判定工作树属于该技能自己创建的目录时执行 `git worktree remove`。`flow-02` 正文第 47 行已经写「提交、推送和合并等待用户当次选择」。这次不改这份技能原文。要补的是点名它之前的只读事实：每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。推送、合并、删除和清理仍等用户当次选择。只读审计的卫生清单也不执行 `git worktree remove`。

12. 本仓库没有另一份名叫高风险目录的名册。已写明不得改写的是 `FRAMEWORK_ENTRY` 托管段和 `<!-- AGENT_PERSONA_START -->` 到 `<!-- AGENT_PERSONA_END -->` 之间的人格正文。风险分档使用用户给定的类别：并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，再加上仓库已经写明的高风险或禁改目录。不在这次新造名册，也不把这份名单写成 `AGENTS.md` 里的新小节。纯界面、文案、辅助脚本且没碰到这些目录时，走轻量核对。

13. 知识页没有改写上述正文。alias `project` 指向 `knowledge/project/`，`status.sh` 为 shell `READY`、ingestion `PRESENT`、10 页。需求页 `agent-workflow-routers` 的 `source_sha256` 为 `82e68c829313c75397b26a91ec24fee51aa172332a9d657ce027e0bdf22a5fa0`，与现行 `openspec/specs/agent-workflow-routers/spec.md` 的 sha256 一致。该页写明只读审计、纯文档和既有规格修复不走新行为必经链，并写明 `flow-04` 与 `flow-09` 的入口不因发现记录位置改写。它没有写探索简报、风险分档或检查节奏。本提案的行为以规格和路由正文为准。不在这次写知识页。

14. 入口只读 doctor 的结果是分发库既有状态：`initialization=PARTIAL`、`documentation=MISSING`、`coverage=MISSING`、`handoff=BLOCKED`、`runtime=NOT_RUN`。本变更不为把它变绿而改工程。

15. 活动 change `openspec/changes/bind-skill-endings-to-active-flow` 已在 `83607ca`。本次工作树没有改动该目录。它的任务 2.2 未勾、没有回执，这是用户给定。本提案不改它，不把它并进新 change，不归档它。

### 排除

1. 吸取会另开账本的做法。不把规格写进 `docs/`，不另建派发契约，不在原因清楚时直接改源码，不自己做合并门禁。规格仍只进 OpenSpec 的 proposal、delta spec、design 和主规格。源码仍只由 `tdd` 写。合并、推送和清理仍等用户当次选择。

2. 吸取固定产品名单的外部 CLI 委托，或把 implement 角色写成实现器。委派条件仍是用户已授权且宿主提供子代理。子代理仍是任何一个 coding agent 都可以有的能力。被委派者仍用 `tdd`。主 Agent 在没有这组条件时自己读、自己做 `tdd` 和 `code-review`。

3. 让诊断技能写复现测试或改产品代码。`diagnosing-bugs` 仍停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 `tdd` 写。缺陷位置核对放在 `code-review`，不放进诊断技能。

4. 把这五条写进 `flow-05`、`flow-06`、`flow-07`、`flow-10`、`flow-11`、`flow-12`、`flow-13`、`flow-14`、`flow-15`。这些对象和渲染正文不动。

5. 改 `flow-01`、`flow-03`、`flow-08`、`flow-14` 的停点。`flow-01` 与 `flow-14` 的失败路径仍停在根因，不写修复，不把 `tdd` 写成下一项。`flow-08` 仍停在设计对话，不创建 OpenSpec change。`flow-03` 的点名保持原句。

6. 改 `flow-04` 或 `flow-09` 的入口和技能点名。风险分档若需要它们看见，只加在 `code-review` 的 `framework-rules.md`。这两条只把问题写入报告，不把修改交回 `tdd`。不把局部快测写进这两条的正文，也不写进改编层，避免它们继承跑测试的义务。

7. 手改 `skill/flows/flow-02/SKILL.md` 而不改 `combinations.json` 的 `flow-02` 对象。WR-02 与 `distribution_errors` 会把差异报成正文漂移。

8. 改人格标记、`FRAMEWORK_ENTRY`、`docs/framework/agent-persona.md`。WR-16 与 WR-21 继续禁止改写托管段。阶段表第 91 行的三条切分线不移动：OpenSpec 独占规格账本，`tasks.md` 只由 `to-tickets` 写，源码只由 `tdd` 写。

9. 重写 `code-review` 的上游 `SKILL.md`、`verification-before-completion`、`finishing-a-development-branch`，或重写 `tdd` 的 RED/GREEN 循环。风险分档、检查节奏和收尾前事实用路由句加改编层的追加句完成。`finishing-a-development-branch` 里已有的 `git worktree remove` 留在用户当次选择之后，卫生清单不执行它。

10. 重写 `AGENTS.md`，或在其中新增一节来安放这些做法。卫生清单不改文件。阶段表第 6–9 行要改的只是与新行为链同一条链的交接句，这是 WR-21 的同次修改，不是卫生清单的改写，也不是新小节。第 80 行的审计行保持「不修改文件」。

11. 改 `flow-02` 的 `mentions`。不把上述来源里的技能名列进组合。`catalog.json` 和 `docs/guide/from-zero-to-one.md` 的技能列因此不动。

12. 把 `bind-skill-endings-to-active-flow`，或工作区里其他未归档 change，并进本 change，或归档它们。

### 结论

只补这五条，不另起一条流程。

只读审计仍不点名实现技能，仍不写文件。按熟悉度分档：单点问题直接检索；单模块再读该模块约束；陌生或跨模块才做结构快照。简报至少含文件与行号、可复用代码、仓库里已经存在的局部快测命令、要用户拍板的问题。只有用户已授权且宿主提供子代理时，才按互不重叠的目录做只读切片；否则主 Agent 自己读。结束仍停在只读审计，不把 `openspec-explore`、`openspec-propose` 或 `to-tickets` 写成下一项。

用户要看仓库卫生时，同一条只读审计只出清单：死链、长期未改的文档是否和当前代码矛盾、没有任何入口执行的测试目录、嵌在主仓库目录里的 worktree、分支合入状态。清单不改文件。之后要改 Agent 所读文档，仍走纯文档并点名 `writing-for-agents`。不重写 `AGENTS.md`，不新增小节，不执行 `git worktree remove`。

`flow-02` 点名 `code-review` 时增加风险分档。纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。发现写入交付报告，不往 `tasks.md` 追加切片。要改源码回到 `tdd`。`code-review` 亲自跑一次与本次改动相关的局部快测。全量、端到端和打包仍只在 `verification-before-completion` 用来声称验证通过。局部快测通过不能代替那一步。这些分档句子若写在 `framework-rules.md`，只追加，不把评审改回改码。`flow-04` 与 `flow-09` 只把这些问题写入报告，不把修改交回 `tdd`，入口不改，也不跑这一次局部快测。

`flow-02` 点名 `tdd` 时：切片自己的那一次 RED 失败测试保留。写这一轮生产代码时只跑编译、类型检查这类秒级检查。这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量仍留在 `verification-before-completion`。`discipline.md` 只在已有的 framework addition 加这一句，不重写第 52–68 行的循环。

进入 `finishing-a-development-branch` 之前，先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。推送、合并、删除和清理仍等用户当次选择。

## What Changes

- `combinations.json` 的 `flow-02` 对象，「只读审计」保留「不点名实现技能，不写文件。」并追加结论中的熟悉度分档、简报四项、只读切片条件和停点。同一节追加卫生清单：只在用户要看仓库卫生时列出那五项，清单不改文件；之后改 Agent 所读文档仍走纯文档并点名 `writing-for-agents`。
- 同一对象，「纯文档」两句保持原句。
- 同一对象，「既有规格修复」仍依次点名 `diagnosing-bugs`、`tdd`、`code-review` 及各自的同目录文件，结果仍写回原 change。在点名 `tdd` 与 `code-review` 的句子上追加结论中的检查节奏、风险分档和一次局部快测。源码仍只由 `tdd` 改。`openspec-update-change` 仍不写实现步骤，也不创建 `tasks.md`。
- 同一对象，「新行为」里点名 `tdd` 的句子追加检查节奏。点名 `code-review` 的句子追加风险分档、活动 change 的三项核对、缺陷位置核对、一次局部快测，并保留「发现写入交付报告，不往 `tasks.md` 追加切片。要改源码回到 `tdd`」。点名 `verification-before-completion` 的句子写明：声称验证通过只用这一步的全量、端到端和打包；局部快测通过不能代替。点名 `finishing-a-development-branch` 之前追加只读分支与工作树事实，以及「没有独立提交或工作区不干净的，不标成可清理」。提交、推送和合并仍等待用户当次选择。
- 同一对象，「下一项」里 `tdd`、`code-review`、验证通过后、进入收尾前的四句改成与上一组相同的链。诊断停点、规格提案、`to-tickets`、委派、装载三步、知识回执和三个退出必经技能的句子保留。
- `flow-02` 以外的 flow 对象不改。`flow-02` 的 `mentions` 不改。改完后用现有 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。不手改出漂移正文。
- `skill/matt-pocock/code-review/framework-rules.md` 只追加风险分档、自审标明、活动 change 三项核对和缺陷位置核对。不删除第 81–84 行。不把「修改回到 `tdd`」写成 `flow-04` 与 `flow-09` 的句子。不追加局部快测。不改上游 `SKILL.md`。
- `skill/matt-pocock/tdd/discipline.md` 的 framework addition 只追加检查节奏那一句。第 52–68 行的 RED/GREEN 循环保留。
- **BREAKING**：已把只读审计接去 `openspec-explore`、`openspec-propose` 或 `to-tickets` 的会话，改为停在简报。已对纯界面、文案或辅助脚本总是启动独立只读上下文的评审，在没碰到高风险目录时改为轻量核对。已用局部快测通过来声称验证通过的会话，改为只在 `verification-before-completion` 的全量、端到端和打包上声称。已把没有独立提交或不干净的工作树标成可清理的会话，改为不标。

### 不改的句子

- `flow-02` 的进入节、纯文档两句、委派两句、三个退出必经技能、诊断停点、`to-tickets` 独占切片、装载三步、知识回执顺序。
- `flow-01`、`flow-03`、`flow-04`、`flow-05`、`flow-06`、`flow-07`、`flow-08`、`flow-09`、`flow-10` 至 `flow-15` 的对象与渲染正文。`flow-04` 与 `flow-09` 只通过改编层的追加句看见风险分档。
- `AGENTS.md` 的人格标记、`FRAMEWORK_ENTRY`、第 80 行审计行、第 91 行三条切分线。第 102–105 行只改交接句，使它们与新的 `flow-02` 新行为链一致。
- `code-review` 上游 `SKILL.md`，`verification-before-completion`，`finishing-a-development-branch`，`diagnosing-bugs` 的 `SKILL.md` 与 `discipline.md`。
- 宿主安装器、`roster.json`、`catalog.json`、`docs/guide/from-zero-to-one.md` 的技能列。

## Capabilities

### New Capabilities

- 无。这是现有路由能力上的五处句子，不新增 capability 目录。

### Modified Capabilities

- `agent-workflow-routers`（`openspec/specs/agent-workflow-routers/spec.md`）：修改 WR-06 的只读审计条目，写入熟悉度分档、简报四项、只读切片条件、停点，以及用户要看仓库卫生时的五项清单。清单不改文件。之后改 Agent 所读文档仍走纯文档并点名 `writing-for-agents`。不把 `openspec-explore`、`openspec-propose` 或 `to-tickets` 写成只读审计的下一项。不新增第五条自动路径。新增 Requirement：`flow-02` 点名 `code-review` 时按结论中的风险分档决定要不要独立只读上下文；没有已授权的只读子代理时报告标明自审；对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码；缺陷修复再核对改动是否在坏数据第一次产生的位置；亲自跑一次相关局部快测，且这次通过不能代替 `verification-before-completion`。该 Requirement 写明分档句子追加在 `framework-rules.md`，不把评审改回改码。`flow-04` 与 `flow-09` 只把这些问题写入报告，不把修改交回 `tdd`，入口不改，也不跑这一次局部快测。新增 Requirement：`flow-02` 点名 `tdd` 时保留切片自己的一次 RED，写生产代码时额外检查只跑秒级的编译和类型检查，这一轮写完后跑关联局部快测并在失败后重跑同一条；全量仍留在验证步骤。进入 `finishing-a-development-branch` 之前先写只读分支与工作树事实，没有独立提交或工作区不干净的不标成可清理。修改 WR-20 里 `tdd`、`code-review`、验证和收尾四句，使下一项与这两条 Requirement 一致。WR-21 的同次修改覆盖阶段表第 6–9 行和 `development-workflow.md` 的对应步骤；不改托管段，不移动三条切分线。WR-22 增加一个 Scenario：`flow-04` 与 `flow-09` 对风险分档中的问题只写报告，不交回 `tdd`。不修改 WR-01、WR-02、WR-05、WR-07、WR-16 的现有句子。不把 `skip_specs` 写入本 change 的 `.openspec.yaml`。

## Impact

- 将来要改的路由事实源是 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的对象，然后用现有 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。其他 flow 对象不动。`mentions` 不变，因此 `catalog.json` 与 `docs/guide/from-zero-to-one.md` 的技能列不动。
- 同一次变更按 WR-21 修改 `AGENTS.md` 第 102–105 行的交接句，以及 `docs/framework/development-workflow.md` 第 8 节的 REGRESSION、第 10 节的评审、第 11 节的验证声称、第 12 节进入收尾前的事实。第 91 行的三条切分线和人格标记、`FRAMEWORK_ENTRY` 不动。第 80 行的审计行保持「不修改文件」，简报和卫生清单的细节只写在 `flow-02` 正文。
- 同一次变更只在 `skill/matt-pocock/code-review/framework-rules.md` 追加风险分档句子，并在 `skill/matt-pocock/tdd/discipline.md` 的 framework addition 追加检查节奏一句。上游全文、验证技能和收尾技能不改。
- `tests/test_flow_routers.py` 的 `test_fifteen_routers_match_the_manifest` 在正文与清单不一致时失败，所以渲染必须来自清单。`test_successors_are_written_by_the_router` 锁定的诊断停点、`不往 tasks.md 追加切片`、`不创建 tasks.md` 和三个退出必经技能必须仍在。`test_review_does_not_edit_business_source` 与 `test_review_findings_are_not_appended_to_tasks` 锁定的「评审不改业务源码」和「发现写入交付报告」必须仍在，并且 `flow-04`、`flow-09` 正文仍不得写入「不往 tasks.md 追加切片」。`test_stage_table_follows_the_single_chain` 与 `test_persona_block_matches_source_and_status_dictionary_stays_put` 继续锁托管段和人格来源相同。
- 风险：上游 `code-review` 仍写总是启动并行子代理。若不读改编层第 4–5 行，轻量核对会被绕开。本提案把分档写进必读的 `framework-rules.md`，不改上游。`discipline.md` 第 70 行若不加那一句限定，写代码途中仍可能扩跑其他测试。`finishing-a-development-branch` 的第 14–16 行仍会再跑全量，第 169–173 行仍含 `git worktree remove`。这两处不在这次改写；声称验证通过仍只认前一步，删除和清理仍等用户当次选择，卫生清单不执行删除。本仓库没有单独的高风险目录名册，分档靠用户给定的类别和已经写明的禁改范围，不靠新造清单。
- 非目标：不在本提案的实施完成之前修改 flow 正文、技能实现或 `AGENTS.md`；不写 `tasks.md`；不设 `skip_specs`；不改宿主安装器；不重写 `AGENTS.md`，不新增小节；不改人格标记、`FRAMEWORK_ENTRY` 和 `agent-persona`；不改 `flow-01`、`flow-03`、`flow-04`、`flow-05`、`flow-06`、`flow-07`、`flow-08`、`flow-09`、`flow-10` 至 `flow-15` 的入口和停点；不把规格写进 `docs/`；不另建派发契约；不在原因清楚时直接改源码；不自己做合并门禁；不引入固定产品名单的外部 CLI；不把 implement 角色写成实现器；不让诊断技能写复现测试或改产品代码；不执行 `git worktree remove`；不把 `openspec/changes/bind-skill-endings-to-active-flow` 并进本 change 或归档；不写知识库内容；不提交、不推送。入口 doctor 的 `initialization=PARTIAL`、`documentation=MISSING`、`coverage=MISSING`、`handoff=BLOCKED`、`runtime=NOT_RUN` 是这次只读检查看到的分发库状态，本变更不为把它变绿而改工程。
