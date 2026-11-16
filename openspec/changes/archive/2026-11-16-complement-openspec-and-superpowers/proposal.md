## Why

OpenSpec 与 Superpowers 现在各写一份任务、各改一次源码，所以两条流程在同一次新行为里并跑。本变更把它们收成一条路径：OpenSpec 独占可校验的规格账本；Superpowers 与 matt-pocock 独占把账本谈清楚、切成切片、用测试改代码并交出证据。同一份 `tasks.md` 只有一个作者，同一段源码只有一个实现器。

这次只定这条契约。不实施路由、技能或阶段表。

### 前提

1. 新行为的现行必经链写在三处，三处互相指向。`AGENTS.md` 第 90 行把「新行为、接口、验收、跨模块设计」指到下一张阶段表。第 100 行写明阶段表的进入条件、步骤、产物、异常回流和退出门禁在 `docs/framework/development-workflow.md`，工作流入口是 `flow-01` 到 `flow-15`，下一项以命中的那条 flow 正文为准。`openspec/specs/agent-workflow-routers/spec.md` 的 WR-02 规定组合清单生成路由正文：`tools/framework_core/workflows/routers.py` 的 `distribution_errors` 在路由文件与 `render_skill` 的输出不一致时报 `router body drifted from the combination manifest`。因此只改 `skill/flows/flow-02/SKILL.md` 会在检查里失败；清单里的 `flow-02` 对象才是正文事实源。

2. `flow-02` 的四条路径已经分开。只读审计是「不点名实现技能，不写文件」。纯文档点名 `writing-for-agents`，文档若改变公开接口或验收就改走新行为。既有规格修复是 `diagnosing-bugs`、`tdd`、`code-review`，结果写回原 change。这三句在 `skill/flows/flow-02/SKILL.md` 第 12–24 行，与 `combinations.json` 里 `flow-02` 的同名小节一致，也与 WR-06 的前三条一致。本次不改这三句的行为，只给既有规格修复补上「要改 change 文字时只点名 `openspec-update-change`，源码仍只由 `tdd` 改」。

3. 新行为的现行正文仍把三件工作写成必经。`flow-02` 第 31 行：已有规格上下文点名 `openspec-explore`，新设计点名 `brainstorming`。第 33–35 行：顺序执行点名 `executing-plans`；然后点名 `openspec-apply-change`，并且只装载 status、instructions 和 contextFiles。第 50 行的下一项是：工作区就绪后进入 `openspec-apply-change`。WR-06 第 86 行和 WR-20 第 154–158 行是同一条链。

4. 任务正文有两个作者。`skill/openspec/openspec-propose/SKILL.md` 第 17–21 行把 `tasks.md` 定义为实现步骤，并要求同一步生成 proposal、delta spec、design 和 tasks。同文件第 107–108 行写明 status 只看文件是否存在，提前写下 `tasks.md` 就会把 `tasks` 标成 done。`skill/matt-pocock/to-tickets/plan-format.md` 第 18–21 行写明切片就是当前 change 的 `tasks.md`，任务状态只有这一处。`flow-02` 第 32 行已经把切片限定为写入当前 change 的 `tasks.md`。

5. 源码有两个实现循环。`skill/openspec/openspec-apply-change/SKILL.md` 第 91–97 行对每个未完成任务「Make the code changes required」，并随即把 `- [ ]` 改成 `- [x]`。`skill/superpowers/executing-plans/SKILL.md` 第 25–31 行按计划逐步执行并标完成。`flow-02` 第 36 行又要求在改业务源码之前点名 `tdd`。WR-08 已经禁止 `openspec-apply-change` 直接改业务源码，也禁止在 `TASK_VERIFIED` 之前勾选；技能原文仍带着相反的循环。读技能原文的会话会把同一段源码做两遍。

6. 勾选和回执的扫描范围已经定死。`tools/framework_core/closure.py` 的 `outstanding_changes` 从第 366 行起只遍历 `openspec/changes` 的直接子目录，并跳过名为 `archive` 的目录。任务未全部勾完时第 380–381 行直接跳过。全部勾完且规格已同步后，第 388–389 行才看该活动目录里的 `knowledge-receipt.json`。`openspec-archive-change` 第 130–144 行在规格已同步时把 `changeRoot` 移进 `archive/`。回执和勾选若写在活动 change 之外，这项检查看不到。

7. 知识写入的「不再询问」已经写在路由下一项和知识规则里，但 WR-06 的压缩句还在要求授权。`flow-02` 第 41 行和第 56 行：规格同步之后、归档之前写入需求页和适用问题页，留下 `knowledge-receipt.json`，不再询问是否摄入，回执留下之后才点名 `openspec-archive-change`。`docs/framework/knowledge-policy.md` 第 69–74 行对这两类同样不再逐次询问。WR-20 第 164 行与这两处一致。WR-06 第 86 行仍写「知识写入只在本次授权后点名 `llm-wiki`」，第 93–96 行的 Scenario 仍是未授权时只询问。本提案以路由正文、WR-20 和知识规则为准，WR-06 的这句和这个 Scenario 是要改掉的冲突。

8. 子代理的安装事实和产品名单是两套，都不能当成 13 个宿主的流程门。`tools/framework_core/hosts/roster.json` 的 `hosts` 有 13 个 id：`cursor`、`claude-code`、`codex`、`gemini-cli`、`copilot-cli`、`github-copilot`、`windsurf`、`grok`、`qwen-code`、`codebuddy`、`trae`、`lingma`、`deepseek-harness`。`shared_agent_files` 只被 `tools/framework_core/hosts/claude_code.py` 第 29 行和 `tools/framework_core/hosts/codebuddy.py` 第 20 行调用，复制 `uap-challenger.md`、`uap-investigator.md`、`uap-verifier.md`。`qwen_code.py` 与 `projection.py` 的 preview 不调用它。`openspec/specs/agent-persona/spec.md` 第 55–57 行把这件事写成 Claude Code 与 CodeBuddy 的安装要求，并写明宿主未安装这些子代理时主 Agent 自己做并写明未委派。`executing-plans` 第 14 行另有一份上游产品名单：Claude Code、Codex CLI、Codex App、Copilot CLI、Gemini CLI。两份名单都不是「13 个宿主共用主路径，子代理是可选能力」。

9. 知识库查询没有改写上述正文。alias `project` 指向 `knowledge/project/`，status 为 shell `READY`、ingestion `PRESENT`、10 页。需求页 `agent-workflow-routers`、`agent-persona`、`change-lifecycle` 所记 `source_sha256` 与这三份现行 spec 一致。三页都写明自己是摘要，当前需求以来源规格为准。本提案的行为以规格和路由正文为准。

### 排除

1. 只改 `flow-02` 正文、不改阶段表。第 90 行仍指向第 102–114 行的旧表：DISCOVERY 仍点名 `openspec-explore`，WORKSPACE 仍把 `executing-plans` 写成顺序执行，APPLY 仍把 `openspec-apply-change` 写成必经实现器。第 1 节因此继续把新行为送进旧链。

2. 只改阶段表、不改 `development-workflow.md`。第 100 行把该文件当作阶段表的详细步骤。其第 31 行仍用 `openspec-explore` 处理已有规格上下文，第 65 行仍把 `executing-plans` 写成顺序执行，第 74 行仍让 `openspec-apply-change` 负责上下文和宏观进度并由另一套执行技能逐项落实。第 126 行先写同步再归档，第 129 行和第 132–138 行的图又把回执放在移动目录之前。留下这份文件，阶段表的指针仍指向旧链。

3. 手改 `flow-02/SKILL.md` 而不改 `combinations.json` 的 `flow-02` 对象。WR-02 和 `distribution_errors` 会把这种差异报成正文漂移。其余 14 条 flow 的对象不在这次编辑里。

4. 把实现步骤留在 `openspec-propose` 或 `openspec-update-change` 里，或让这两处创建 `tasks.md`。第 107–108 行的存在性判定会把空的或写了步骤的 `tasks.md` 标成 done，`to-tickets` 不再是唯一作者。

5. 只改路由、不改 `openspec-apply-change` 与 `executing-plans` 的实现循环。人点名或技能收尾仍会让会话按第 91–97 行和第 25–31 行改源码并勾选，和 `tdd` 形成第二个实现器。

6. 把「子代理」写成只有 Claude Code 和 CodeBuddy 才能走的产品规则，或按 `executing-plans` 第 14 行的产品名单分流。安装事实见前提 8，它不决定委派分支。本变更也不给其余宿主安装 `uap-*` 文件；技能和规格没有把「13 个宿主都装上这三个只读子代理」写成流程完整的条件。`agent-persona` 第 57 行的安装要求继续有效，主 Agent 在不能调用时自己做并写明未委派，这句在人格里，不改。

7. 改 `FRAMEWORK_ENTRY` 托管段或 `docs/framework/agent-persona.md`。WR-16 禁止改写托管段。人格正文与该来源文件必须保持相同。阶段表在 `AGENT_PERSONA_END` 之后，改表不进入托管段。

8. 去掉 propose、update、sync、archive 或主规格，只留 `openspec/specs` 与 validate。这四步和主规格都留下。`tasks.md` 也留下，只是作者改为 `to-tickets`。

9. 改 `flow-08`、`flow-09` 或其他 14 条 flow 的正文。检索 `skill/flows` 后，`openspec-explore`、`openspec-propose`、`openspec-update-change`、`openspec-apply-change`、`openspec-sync-specs`、`openspec-archive-change` 只出现在 `flow-02`。`flow-08` 只点名逆向交接和 `brainstorming` 的架构路径，`flow-09` 只点名 `code-review`。

### 结论

切分线按上面的文件执行，不另起一套流程。

OpenSpec 保留可校验账本：proposal、delta spec、design、主规格，以及 propose、update、sync、archive 这四步。`tasks.md` 的切片正文只由 `to-tickets` 写入。`- [ ]` 改成 `- [x]` 只发生在该切片 `TASK_VERIFIED` 之后，并且这个文件仍在活动 change 目录里。

Superpowers 与 matt-pocock 负责把账本谈清楚、切成切片、用测试改代码并交出证据。同一段源码只有一个实现器：没有委派授权，或宿主不提供子代理能力时，主 Agent 用 `tdd` 实现，并用 `code-review` 做评审判断；两者都有时，被委派的实现器是唯一写这段源码的人，它仍用 `tdd`，主 Agent 不再改同一段。评审判断只走 `code-review`。派发用 `requesting-code-review`，收反馈用 `receiving-code-review`。

诊断停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 不应用修复。回归测试和修复只由 `tdd` 写。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改同样交给 `tdd`，不必另起一条实现。`plan-format.md` 的 Execution handoff 不是下一项。`to-tickets` 只写入切片正文。`- [ ]` 改成 `- [x]` 仍等该切片 `TASK_VERIFIED`。委派仍只在用户已授权且宿主提供子代理时发生，被委派者仍用 `tdd`。

`openspec-explore`、`openspec-apply-change`、`executing-plans` 退出必经链，人点名时仍可使用。点名之后也不能成为第二个 `tasks.md` 作者或第二个实现器。

## What Changes

- 只读审计、纯文档的正文保持现句。
- 既有规格修复保持 `diagnosing-bugs` → `tdd` → `code-review`，结果写回原 change。要改 change 的 proposal、delta spec 或 design 时，只点名 `openspec-update-change`。源码仍只由 `tdd` 改。`openspec-update-change` 不写实现步骤，也不创建 `tasks.md`。
- 新行为的必经链改为下面的顺序。故障先 `diagnosing-bugs` 与 `discipline.md`。诊断停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 不应用修复。回归测试和修复只由 `tdd` 写。澄清意图只走 `brainstorming` 与 `framework-rules.md`。只有要改行为、接口或验收才进入规格；探针停在建议。然后 `openspec-propose` 或 `openspec-update-change`，只落 proposal、delta spec、design。然后 `to-tickets` 与 `plan-format.md` 独占 `tasks.md`。`plan-format.md` 的 Execution handoff 不是下一项。`to-tickets` 只写入切片正文。`- [ ]` 改成 `- [x]` 仍等该切片 `TASK_VERIFIED`。需要隔离才点名 `using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派仍只在用户已授权且宿主提供子代理时发生。有委派授权且宿主提供子代理能力时，才读 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，二者择一，不并行改同一段源码，被委派者仍用 `tdd`。装载上下文是路由上的三步：`openspec status --json`、`openspec instructions apply --json`、读完全部 contextFiles。这三步不再把 `openspec-apply-change` 当必经实现器。然后 `tdd` 与 `discipline.md`。该切片 `TASK_VERIFIED` 之后才把对应任务勾成 `- [x]`。评审判断只走 `code-review` 与 `framework-rules.md`。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改同样交给 `tdd`，不必另起一条实现。然后 `verification-before-completion`。然后 `finishing-a-development-branch`。然后 `openspec-sync-specs`。然后 `llm-wiki` 写需求页、适用问题页和活动 change 里的 `knowledge-receipt.json`，这两类不逐次询问。然后 `openspec-archive-change` 在规格已同步时直接移动目录。
- 四个用户确认点保持为门，不能用技能收尾代替：`brainstorming` 的设计批准；Requirement 与 Scenario 认可；`to-tickets` 的切片批准；`finishing-a-development-branch` 的合并、PR 或保留。
- 人点名仍可用，且不是下一项必经：`openspec-explore`、`openspec-apply-change`、`executing-plans`。
- 目标能力模型：13 个宿主共用上面这条主路径。子代理是任何一个 coding agent 都可以有的能力，不是 Claude Code 或 CodeBuddy 的产品专属。宿主提供该能力且用户已授权委派时走委派分支；不提供时主 Agent 自己做 `tdd` 和 `code-review`，并写明未委派。当前安装事实单独保留：此刻只有 `claude_code.py` 和 `codebuddy.py` 安装那三个只读子代理。本变更不要求给 13 个宿主安装子代理文件。
- **BREAKING**：已按现行 WR-06 必经 `openspec-explore`、`executing-plans` 或 `openspec-apply-change` 的新行为会话，改走上面的链。人点名这三个技能时仍可进入，但不再是下一项，也不再改源码或写实现步骤。

### 用户确认点

1. `brainstorming` 给出的设计被批准之后，才允许进入规格。未批准时停在设计。
2. Requirement 与 Scenario 被认可之后，才允许 `to-tickets` 写切片。
3. `to-tickets` 的切片被批准之后，才允许进入实现。
4. `finishing-a-development-branch` 出示验证结果后，等用户选择合并、PR 或保留。提交、推送和合并仍等这次选择。

### 退出必经、人点名仍可用

- `openspec-explore`：可以用来查看已有规格，不代替 `brainstorming` 的澄清，也不跳过「要改行为、接口或验收才进入规格」。
- `openspec-apply-change`：可以用来重读 status、instructions 和 contextFiles。它不改业务源码，不在 `TASK_VERIFIED` 之前勾选。
- `executing-plans`：可以用来对照已批准切片。它不执行自己的改码循环，也不按第 14 行的产品名单改走委派。

### 门禁

- 阶段表、人格和子代理只通过评审过的 OpenSpec 变更修改。这句话已在人格正文里，本变更不改它。
- 不得修改 `FRAMEWORK_ENTRY` 托管段。阶段表的修改落在 `AGENT_PERSONA_END` 之后的第 2 节。现有 `RULE_CONFLICT` 继续生效。
- WR-16 的托管段字节不变，doctor 状态词典不增加状态码。
- 路由正文与 `combinations.json` 的 `flow-02` 对象一起改，并通过 `distribution_errors`。`mentions` 仍包含这三个退出技能的名字，因此 `catalog.json` 和 `docs/guide/from-zero-to-one.md` 里 flow-02 的技能列保持原集合；只有 mentions 变化时才允许这三处一起改。
- 勾选和 `knowledge-receipt.json` 留在活动 change 目录。归档移动目录之后，`outstanding_changes` 不再扫描该 change。

## Capabilities

### New Capabilities

- 无。这是现有路由能力上的一条路径契约，不新增 capability 目录。

### Modified Capabilities

- `agent-workflow-routers`（`openspec/specs/agent-workflow-routers/spec.md`）：修改 WR-06、WR-08、WR-20，并增加一条 Requirement。WR-06 改为上面的四条路径；新行为不再把 `openspec-explore`、`executing-plans`、`openspec-apply-change` 写成必经；知识写入改为与 WR-20 和 `flow-02` 第 56 行相同的「不再询问」。WR-08 增加单一 `tasks.md` 作者和单一实现器：propose 与 update 不写实现步骤、不创建 `tasks.md`；apply 与 executing-plans 的实现循环与该路由一致。WR-20 的下一项改为结论里的链，并写明三个人点名技能不是下一项。新增 Requirement 写两件事：13 个宿主共用主路径，子代理能力与委派授权同时成立才进入委派分支，否则主 Agent 自己做 `tdd` 和 `code-review`；`AGENTS.md` 阶段表与 `development-workflow.md` 的对应步骤必须和 `flow-02` 在同一次变更里改，且不改托管段。不修改 WR-02、WR-07、WR-14、WR-16 的现有禁止句。
- 不修改 `agent-persona`。第 55–57 行的安装要求保持为当前安装事实。目标能力模型写在 `agent-workflow-routers`，不把它写成「只有两个宿主可以有子代理」。
- 不修改 `change-lifecycle`。活动目录扫描和「先回执、再移动」是前提 6 的既有约束，路由遵守它，不改检查器。

## Impact

- 将来要改的路由事实源是 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的对象，然后用现有渲染得到 `skill/flows/flow-02/SKILL.md`。不手改出一份与清单不同的正文。其他 flow 对象不动。
- 同一次变更改 `AGENTS.md` 第 98 行的分工句和第 102–114 行的阶段表，使第 90 行指向的表与新链一致。分工句改为本提案的切分线，不再把「宏观任务状态」和「实施计划」写成两套账。表内顺序 10 ARCHIVE 与顺序 11 KNOWLEDGE（约第 113–114 行）改为先同步、再把回执留在活动 change、再移动目录，避免读者按顺序号先归档。不改 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间的正文，不改 `docs/framework/agent-persona.md`。
- 同一次变更改 `docs/framework/development-workflow.md` 里与旧链冲突的步骤：第 20–26 行的分工、第 31 行的发现技能、第 45 行「按真实 schema 的依赖顺序生成产物」不得再包括实现步骤、第 65 行的顺序执行、第 74–85 行的装载、第 126 行与第 129 行的收尾顺序。第 132–138 行的图已经是 `SPECS_SYNCED → KNOWLEDGE_RECEIPT → ARCHIVED`，改完后正文与图一致。
- 同一次变更改三份技能原文，否则读原文的会话仍会做第二遍。`skill/openspec/openspec-propose/SKILL.md` 在 proposal、delta spec、design 之后停止，不创建 `tasks.md`，收尾的下一项改为 `to-tickets`，不再把实现步骤放进 tasks，也不再把 `openspec-apply-change` 写成完成后的实现入口。`skill/openspec/openspec-update-change/SKILL.md` 只修订已有的 proposal、delta spec、design；不写实现步骤，不创建 `tasks.md`，不再建议用 apply 把 delta 直接写进源码。`skill/openspec/openspec-apply-change/SKILL.md` 第 91–97 行的改码和立即勾选改为与路由一致：只装载上下文，不改源码，不在 `TASK_VERIFIED` 之前勾选。`skill/superpowers/executing-plans/SKILL.md` 第 25–31 行的执行循环改为与路由一致：不成为实现器；第 14 行的产品名单不再决定是否改走委派。
- 这四份技能是上游文本。propose 与 apply 的 frontmatter 标明 `generatedBy: "1.11.0"`。以后的技能导入可能把循环写回去。规格里的单一作者和单一实现器是持续约束，不能只靠某一次导入后的措辞。
- `tests/test_flow_routers.py` 第 54–63 行锁着现行下一项句子，其中包括进入 `to-tickets`、进入 `tdd`、未授权不点名委派技能、同步后写知识库再归档。实现时更新那些将随新链改变的断言，并保留仍然成立的句子。`test_persona_block_matches_source_and_status_dictionary_stays_put` 继续锁托管段与人格来源相同，以及 `| 1. DISCOVERY |` 在标记之后。
- 不改 `tools/framework_core/closure.py`、`roster.json`、`claude_code.py`、`codebuddy.py`、`qwen_code.py`、`projection.py`、`templates/host/agents/`。不改 `flow-01` 与 `flow-03` 到 `flow-15` 的正文。不改 `README.md` 第 44 行的安装事实句；该句继续描述前提 8，不作为委派门。不把 `skip_specs` 写入本 change 的 `.openspec.yaml`。
- 风险：WR-06 与 WR-20 的知识写入冲突若只改路由、不改 WR-06，规格在落地当天就自相矛盾。archive 技能第 82–85 行在任务未完成时仍请用户确认是否继续，第 101–107 行仍提供「Sync now」；本变更不改这份技能的通用 CLI 步骤，路由必须在回执留下且规格已同步之后才点名它，人若绕过路由提前移动目录，活动区检查就看不到回执。`subagent-driven-development` 的上游循环会派实现子代理；本框架的 `framework-rules.md` 已经把评审收回到 `code-review`，并禁止实现器自行提交。委派分支必须沿用这层，不能再跑一份上游评审或第二份改码。
- 非目标：不在本提案中实施上述修改；不写本 change 的 specs、design、tasks；不给 13 个宿主安装子代理；不改宿主安装器；不删 change 的四步或主规格；不改 doctor 词表；不写知识库内容；不提交、不推送。入口 doctor 的 `initialization=PARTIAL`、`documentation=MISSING`、`coverage=MISSING`、`handoff=BLOCKED`、`runtime=NOT_RUN` 是这次只读检查看到的分发库状态，本变更不为把它变绿而改工程。
