## MODIFIED Requirements

### Requirement: WR-06 工作流 2 按路径点名组合

系统 SHALL 让 `flow-02` 在进入时先点名读取根 `AGENTS.md`、当前 handoff 和只读 doctor。各路径的后续必读 MUST 如下，并且只要求读到当前步骤：

- 只读审计：不点名实现技能，不写文件。
- 纯文档：被 Agent 读取的文档改动点名 `writing-for-agents`。
- 既有规格修复：依次点名 `diagnosing-bugs` 与其 `discipline.md`、`tdd` 与其 `discipline.md`、`code-review` 与其 `framework-rules.md`，结果写回原 change。要改 change 的 proposal、delta spec 或 design 时，只点名 `openspec-update-change`。源码仍只由 `tdd` 改。`openspec-update-change` MUST NOT 写实现步骤，也 MUST NOT 创建 `tasks.md`。
- 新行为按此顺序点名：故障时先 `diagnosing-bugs` 与 `discipline.md`。诊断停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 MUST NOT 应用修复。回归测试和修复只由 `tdd` 写。澄清意图只走 `brainstorming` 与 `framework-rules.md`。只有要改行为、接口或验收才进入规格；探针停在建议。然后 `openspec-propose` 或 `openspec-update-change`，只落 proposal、delta spec、design，不创建 `tasks.md`。然后 `to-tickets` 与 `plan-format.md` 独占 `tasks.md` 的切片正文。`plan-format.md` 的 Execution handoff 不是下一项。需要隔离才点名 `using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才点名 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，二者择一，被委派者仍用 `tdd`。装载上下文是路由上的三步：`openspec status --json`、`openspec instructions apply --json`、读完全部 contextFiles。这三步 MUST NOT 把 `openspec-apply-change` 当必经实现器。然后 `tdd` 与 `discipline.md`。该切片 `TASK_VERIFIED` 之后才把对应任务勾成 `- [x]`。评审判断只走 `code-review` 与 `framework-rules.md`。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改交给 `tdd`。然后 `verification-before-completion`。然后 `finishing-a-development-branch`。然后 `openspec-sync-specs`。然后 `llm-wiki` 写需求页、适用问题页和活动 change 里的 `knowledge-receipt.json`，这两类不逐次询问。然后 `openspec-archive-change`。`openspec-explore`、`executing-plans`、`openspec-apply-change` MUST NOT 列为必经；人点名时仍可使用，且不再改源码或写实现步骤。

#### Scenario: 新行为在写入前点名当前步骤

- **WHEN** 新行为路径准备修改业务源码
- **THEN** 路由已点名当前步骤的成员技能和改编层，且点名了 `tdd` 与 `discipline.md`

#### Scenario: 未授权不点名知识写入

- **WHEN** 要写入的不是需求页或适用问题页，且本次没有单独授权
- **THEN** 路由不把 `llm-wiki` 的写入步骤列为必读

#### Scenario: 规格同步后不再询问知识写入

- **WHEN** 新行为路径中的规格已同步，且要写入的是需求页或适用问题页
- **THEN** 路由点名 `llm-wiki` 的写入步骤，不再询问是否摄入

#### Scenario: 委派未授权不点名并行技能

- **WHEN** 新行为没有委派授权
- **THEN** 路由不把 `subagent-driven-development` 或 `dispatching-parallel-agents` 列为当前步骤必读

#### Scenario: 委派条件不成立时不点名并行技能

- **WHEN** 新行为没有委派授权，或宿主不提供子代理能力
- **THEN** 路由不把 `subagent-driven-development` 或 `dispatching-parallel-agents` 列为当前步骤必读

#### Scenario: 三个人点名技能不是必经

- **WHEN** 新行为路径选择当前必读
- **THEN** 路由不把 `openspec-explore`、`executing-plans` 或 `openspec-apply-change` 列为必经

### Requirement: WR-08 会拆开组合的收尾在路由中暂停

系统 SHALL 让路由正文声明自身顺序优先于成员技能的收尾提示。改变行为、接口或验收的有界设计 MUST 仍进入规格和 `to-tickets`；探针 MUST 停在建议。`tasks.md` 的切片正文 MUST 只有 `to-tickets` 一个作者。`openspec-propose` 与 `openspec-update-change` MUST NOT 写实现步骤，也 MUST NOT 创建 `tasks.md`。`openspec-propose` 收尾中的直接 apply MUST 暂停，下一项是 `to-tickets` 与 `plan-format.md`。`plan-format.md` 的 Execution handoff MUST NOT 成为下一项。`to-tickets` MUST 只写入切片正文。`- [ ]` 改成 `- [x]` MUST 等到该切片 `TASK_VERIFIED`，并且该文件仍在活动 change 目录。`openspec-apply-change` MUST NOT 被路由授权直接修改业务源码，也 MUST NOT 在 `TASK_VERIFIED` 之前勾选任务；它只装载上下文。`executing-plans` MUST NOT 成为实现器，也 MUST NOT 按产品名单改走委派。同一段源码 MUST 只有一个实现器：没有委派授权，或宿主不提供子代理能力时，主 Agent 用 `tdd`；两者都有时，被委派者仍用 `tdd`，主 Agent 不再改同一段。`diagnosing-bugs` 的 Phase 5 MUST NOT 应用修复；回归测试和修复 MUST 只由 `tdd` 写。`code-review` 的发现 MUST 写入交付报告，MUST NOT 往 `tasks.md` 追加切片；重要发现的修改 MUST 回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改 MUST 交给 `tdd`。`to-tickets` MUST 把切片写入当前 change 的 `tasks.md`，MUST NOT 写 `.scratch`，也 MUST NOT 要求本包不存在的安装命令。

#### Scenario: 有界设计不再直接实现

- **WHEN** 新行为被 `brainstorming` 分为有界路径，且该工作改变行为、接口或验收
- **THEN** `flow-02` 仍要求进入规格和 `to-tickets`，不按有界路径直接写实现

#### Scenario: apply 不提前勾选任务

- **WHEN** `openspec-apply-change` 已装载上下文但当前切片尚未 `TASK_VERIFIED`
- **THEN** 路由禁止把对应任务从 `- [ ]` 改为 `- [x]`

#### Scenario: propose 不创建任务文件

- **WHEN** `openspec-propose` 已写出 proposal、delta spec 和 design
- **THEN** 它不创建 `tasks.md`，下一项是 `to-tickets` 与 `plan-format.md`

#### Scenario: executing-plans 不改源码

- **WHEN** 人点名 `executing-plans`
- **THEN** 它不执行改码循环，也不按产品名单改走委派

#### Scenario: 评审发现不追加切片

- **WHEN** `code-review` 得出发现
- **THEN** 发现写入交付报告，不往 `tasks.md` 追加切片，重要发现的修改回到 `tdd`

### Requirement: WR-20 下一项由路由正文写明

系统 SHALL 在路由正文里为每个已完成步骤写明下一项。系统 MUST NOT 要求成员技能在结束时各自提示下一个技能。下一项 MUST 取自该路由的顺序。成员技能收尾指向其他步骤时，路由写明的下一项优先。新行为只写当前步骤的下一项，不预告尚未到达的步骤。

新行为的下一项 MUST 为：

- `diagnosing-bugs` 完成后：停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 `tdd` 写。澄清意图的下一项是 `brainstorming` 与 `framework-rules.md`。`openspec-explore` 不是下一项。
- `brainstorming` 的设计被批准后：只有要改行为、接口或验收才进入规格；探针停在建议。进入规格时下一项是 `openspec-propose` 或 `openspec-update-change`，只落 proposal、delta spec、design。
- 规格提案完成后：下一项是 `to-tickets` 与 `plan-format.md`，不采用该技能收尾中的直接 apply。`plan-format.md` 的 Execution handoff 不是下一项。`to-tickets` 只写入切片正文。
- `to-tickets` 且切片已批准后：需要隔离则下一项是 `using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才把 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，写为下一项，被委派者仍用 `tdd`。`executing-plans` 不是下一项。
- 进入实现前的装载是三步：`openspec status --json`、`openspec instructions apply --json`、读完全部 contextFiles。装载完成后下一项是 `tdd` 与 `discipline.md`。`openspec-apply-change` 不是下一项。
- `tdd` 到达 `TASK_VERIFIED` 后：才把对应任务从 `- [ ]` 改为 `- [x]`。下一项是 `code-review` 与 `framework-rules.md`。
- `code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改交给 `tdd`。派发或接收反馈时，再把 `requesting-code-review` 与 `receiving-code-review` 写为下一项。
- 评审闭合后：下一项是 `verification-before-completion`。
- 验证通过后：下一项是 `finishing-a-development-branch`。提交、推送和合并仍等待用户当次选择。
- 用户选定集成方式后：下一项是 `openspec-sync-specs`。
- 规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有已验证问题记录时写入问题页，然后留下知识回执。系统不再询问是否摄入。回执留下之后，下一项才是 `openspec-archive-change`。

`openspec-explore`、`openspec-apply-change`、`executing-plans` 退出必经，人点名仍可用，且不再改源码或写实现步骤。

其余工作流的下一项 MUST 为：`flow-01` 失败时是 `diagnosing-bugs` 与 `discipline.md`，设计未批准时没有下一项技能。`flow-08` 在 `reverse-engineer` 交接完成后是 `brainstorming` 的架构路径。`flow-14` 的三种模式各自结束，不把另一种模式写为下一项。`flow-15` 不把 `flow-14` 写为完成后的下一项；进入 `flow-15` 之前必须已有 `flow-14` 的验证证据。`flow-10` 至 `flow-13` 完成后不点名下一个技能。

#### Scenario: 提案完成后的下一项是计划

- **WHEN** 新行为路径中的 `openspec-propose` 已完成
- **THEN** 路由写明下一项是 `to-tickets` 与 `plan-format.md`，不采用该技能收尾中的直接 apply

#### Scenario: 无成员技能的工作流不提示下一个技能

- **WHEN** `flow-10` 的研究命令已经完成
- **THEN** 路由不点名下一个技能

#### Scenario: 规格同步后写入知识库

- **WHEN** 新行为路径中的 `openspec-sync-specs` 已完成
- **THEN** 路由写明下一项是写入初始化知识库的需求页和适用的问题页并留下回执，然后才是 `openspec-archive-change`，不采用询问是否摄入

#### Scenario: 三个人点名技能不是下一项

- **WHEN** 新行为路径要选择下一项
- **THEN** 路由不把 `openspec-explore`、`executing-plans` 或 `openspec-apply-change` 写成下一项

#### Scenario: 诊断完成后不写修复

- **WHEN** `diagnosing-bugs` 已完成
- **THEN** 路由停在红信号、最小复现和根因，Phase 5 不应用修复，回归测试和修复只由 `tdd` 写

#### Scenario: 计划格式的交接不是下一项

- **WHEN** `to-tickets` 已写入切片正文
- **THEN** 路由不把 `plan-format.md` 的 Execution handoff 写成下一项，勾选仍等该切片 `TASK_VERIFIED`

## ADDED Requirements

### Requirement: WR-21 十三个宿主共用主路径且阶段表同次修改

系统 SHALL 让已登记的 13 个宿主共用 `flow-02` 的主路径。子代理 MUST 被视为任何一个 coding agent 都可以有的能力，而不是只有 Claude Code 与 CodeBuddy 的产品专属。进入委派分支 MUST 同时满足用户已授权委派且宿主提供子代理能力；否则主 Agent MUST 自己做 `tdd` 和 `code-review`，并写明未委派。系统 MUST NOT 把「给 13 个宿主安装只读子代理文件」写成这条主路径完整的条件，也 MUST NOT 为此修改宿主安装器。当前只有 Claude Code 与 CodeBuddy 安装那三个只读子代理的事实保持不变。

系统 SHALL 在同一次变更里修改 `AGENTS.md` 第 2 节的分工句和阶段表，以及 `docs/framework/development-workflow.md` 里与旧链冲突的步骤，使它们与 `flow-02` 一致。阶段表 MUST 先同步规格，再把回执留在活动 change，再移动目录。系统 MUST NOT 修改 `<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 之间的正文，也 MUST NOT 修改 `docs/framework/agent-persona.md`。

#### Scenario: 委派条件不全时主 Agent 自己做

- **WHEN** 用户未授权委派，或宿主不提供子代理能力
- **THEN** 主 Agent 自己做 `tdd` 和 `code-review`，并写明未委派

#### Scenario: 子代理能力不按两个宿主分流

- **WHEN** 路由说明谁可以进入委派分支
- **THEN** 它把子代理写成任何一个 coding agent 都可以有的能力，不以 Claude Code 或 CodeBuddy 的产品名单作为分流条件

#### Scenario: 阶段表与流程正文同一条链

- **WHEN** `flow-02` 的新行为链被修改
- **THEN** `AGENTS.md` 第 2 节与 `docs/framework/development-workflow.md` 的对应步骤在同一次变更里改成同一条链，托管段字节不变
