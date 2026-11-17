## MODIFIED Requirements

### Requirement: WR-06 工作流 2 按路径点名组合

系统 SHALL 让 `flow-02` 在进入时先点名读取根 `AGENTS.md`、当前 handoff 和只读 doctor。各路径的后续必读 MUST 如下，并且只要求读到当前步骤：

- 只读审计：不点名实现技能，不写文件。按熟悉度分档：单点问题直接检索；单模块再读该模块约束；陌生或跨模块才做结构快照。简报 MUST 至少含文件与行号、可复用代码、仓库里已经存在的局部快测命令、要用户拍板的问题。只有用户已授权且宿主提供子代理时，才按互不重叠的目录做只读切片；否则主 Agent MUST 自己读。结束仍停在只读审计，MUST NOT 把 `openspec-explore`、`openspec-propose` 或 `to-tickets` 写成下一项。用户要看仓库卫生时，只出清单：死链、长期未改的文档是否和当前代码矛盾、没有任何入口执行的测试目录、嵌在主仓库目录里的 worktree、分支合入状态。清单 MUST NOT 改文件。之后要改 Agent 所读文档，仍走纯文档并点名 `writing-for-agents`。卫生清单 MUST NOT 重写 `AGENTS.md`，MUST NOT 新增小节，也 MUST NOT 执行 `git worktree remove`。
- 纯文档：被 Agent 读取的文档改动点名 `writing-for-agents`。
- 既有规格修复：依次点名 `diagnosing-bugs` 与其 `discipline.md`、`tdd` 与其 `discipline.md`、`code-review` 与其 `framework-rules.md`，结果写回原 change。点名 `tdd` 时 MUST 保留切片自己的一次 RED 失败测试。写这一轮生产代码时，额外检查 MUST 只跑编译、类型检查这类秒级检查。这一轮改动写完后 MUST 跑关联的局部快测；失败后 MUST 修并重跑同一条。全量、端到端和打包 MUST NOT 在这一步用来声称验证通过。点名 `code-review` 时 MUST 按风险分档决定是否需要独立只读上下文，对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码，缺陷修复再核对改动是否在坏数据第一次产生的位置，并亲自跑一次与本次改动相关的局部快测。这次通过 MUST NOT 代替 `verification-before-completion`。发现写入交付报告，不往 `tasks.md` 追加切片。要改源码回到 `tdd`。要改 change 的 proposal、delta spec 或 design 时，只点名 `openspec-update-change`。源码仍只由 `tdd` 改。`openspec-update-change` MUST NOT 写实现步骤，也 MUST NOT 创建 `tasks.md`。
- 新行为按此顺序点名：故障时先 `diagnosing-bugs` 与 `discipline.md`。诊断停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 MUST NOT 应用修复。回归测试和修复只由 `tdd` 写。澄清意图只走 `brainstorming` 与 `framework-rules.md`。只有要改行为、接口或验收才进入规格；探针停在建议。然后 `openspec-propose` 或 `openspec-update-change`，只落 proposal、delta spec、design，不创建 `tasks.md`。然后 `to-tickets` 与 `plan-format.md` 独占 `tasks.md` 的切片正文。`plan-format.md` 的 Execution handoff 不是下一项。需要隔离才点名 `using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才点名 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，二者择一，被委派者仍用 `tdd`。装载上下文是路由上的三步：`openspec status --json`、`openspec instructions apply --json`、读完全部 contextFiles。这三步 MUST NOT 把 `openspec-apply-change` 当必经实现器。然后 `tdd` 与 `discipline.md`。切片自己的一次 RED 失败测试 MUST 保留。写这一轮生产代码时，额外检查 MUST 只跑编译、类型检查这类秒级检查。这一轮改动写完后 MUST 跑关联的局部快测；失败后 MUST 修并重跑同一条。全量、端到端和打包 MUST NOT 在这一步用来声称验证通过。该切片 `TASK_VERIFIED` 之后才把对应任务勾成 `- [x]`。评审判断只走 `code-review` 与 `framework-rules.md`。纯界面、文案、辅助脚本且没碰到高风险目录时 MUST 走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才 MUST 使用独立只读上下文。没有已授权的只读子代理时，报告 MUST 标明自审。MUST 对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复 MUST 再核对改动是否在坏数据第一次产生的位置。`code-review` MUST 亲自跑一次与本次改动相关的局部快测。这次通过 MUST NOT 代替随后的验证。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。要改源码回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改交给 `tdd`。然后 `verification-before-completion`。声称验证通过 MUST 只用这一步的全量、端到端和打包。局部快测通过 MUST NOT 代替这一步。进入 `finishing-a-development-branch` 之前，MUST 先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，MUST NOT 标成可清理。然后 `finishing-a-development-branch`。提交、推送、合并、删除和清理仍等待用户当次选择。然后 `openspec-sync-specs`。然后 `llm-wiki` 写需求页、适用问题页和活动 change 里的 `knowledge-receipt.json`，这两类不逐次询问。然后 `openspec-archive-change`。`openspec-explore`、`executing-plans`、`openspec-apply-change` MUST NOT 列为必经；人点名时仍可使用，且不再改源码或写实现步骤。

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

#### Scenario: 只读审计按熟悉度出简报

- **WHEN** `flow-02` 走只读审计
- **THEN** 它不点名实现技能，不写文件，并按单点直接检索、单模块再读该模块约束、陌生或跨模块才做结构快照来分档；简报至少含文件与行号、可复用代码、仓库里已经存在的局部快测命令、要用户拍板的问题

#### Scenario: 只读切片只在已授权时切开

- **WHEN** 只读审计没有用户的委派授权，或宿主不提供子代理
- **THEN** 主 Agent 自己读，不按目录把只读工作交给子代理

#### Scenario: 只读审计停在简报

- **WHEN** 只读审计的简报已经写出
- **THEN** 路由仍停在只读审计，不把 `openspec-explore`、`openspec-propose` 或 `to-tickets` 写成下一项

#### Scenario: 卫生清单不改文件

- **WHEN** 用户要看仓库卫生，并且当前路径是 `flow-02` 的只读审计
- **THEN** 路由只列出死链、长期未改的文档是否和当前代码矛盾、没有任何入口执行的测试目录、嵌在主仓库目录里的 worktree、分支合入状态，并且不改文件、不重写 `AGENTS.md`、不新增小节、不执行 `git worktree remove`

### Requirement: WR-20 下一项由路由正文写明

系统 SHALL 在路由正文里为每个已完成步骤写明下一项。系统 MUST NOT 要求成员技能在结束时各自提示下一个技能。下一项 MUST 取自该路由的顺序。成员技能收尾指向其他步骤时，路由写明的下一项优先。新行为只写当前步骤的下一项，不预告尚未到达的步骤。

新行为的下一项 MUST 为：

- `diagnosing-bugs` 完成后：停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 `tdd` 写。澄清意图的下一项是 `brainstorming` 与 `framework-rules.md`。`openspec-explore` 不是下一项。
- `brainstorming` 的设计被批准后：只有要改行为、接口或验收才进入规格；探针停在建议。进入规格时下一项是 `openspec-propose` 或 `openspec-update-change`，只落 proposal、delta spec、design。
- 规格提案完成后：下一项是 `to-tickets` 与 `plan-format.md`，不采用该技能收尾中的直接 apply。`plan-format.md` 的 Execution handoff 不是下一项。`to-tickets` 只写入切片正文。
- `to-tickets` 且切片已批准后：需要隔离则下一项是 `using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才把 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，写为下一项，被委派者仍用 `tdd`。`executing-plans` 不是下一项。
- 进入实现前的装载是三步：`openspec status --json`、`openspec instructions apply --json`、读完全部 contextFiles。装载完成后下一项是 `tdd` 与 `discipline.md`。`openspec-apply-change` 不是下一项。
- `tdd` 进行中：切片自己的一次 RED 失败测试保留。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量、端到端和打包不在这一步用来声称验证通过。
- `tdd` 到达 `TASK_VERIFIED` 后：才把对应任务从 `- [ ]` 改为 `- [x]`。下一项是 `code-review` 与 `framework-rules.md`。
- `code-review` 按风险分档决定是否需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。亲自跑一次与本次改动相关的局部快测。这次通过不能代替 `verification-before-completion`。发现写入交付报告，不往 `tasks.md` 追加切片。重要发现的修改回到 `tdd`。要改源码回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改交给 `tdd`。派发或接收反馈时，再把 `requesting-code-review` 与 `receiving-code-review` 写为下一项。
- 评审闭合后：下一项是 `verification-before-completion`。声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。
- 验证通过后、进入 `finishing-a-development-branch` 之前：先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。下一项才是 `finishing-a-development-branch`。提交、推送、合并、删除和清理仍等待用户当次选择。
- 用户选定集成方式后：下一项是 `openspec-sync-specs`。
- 规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有已验证问题记录时写入问题页，然后留下知识回执。系统不再询问是否摄入。回执留下之后，下一项才是 `openspec-archive-change`。

`openspec-explore`、`openspec-apply-change`、`executing-plans` 退出必经，人点名仍可用，且不再改源码或写实现步骤。

其余工作流的下一项 MUST 为：`flow-01` 的失败路径停在红信号、最小复现和根因，Phase 5 不在本路由应用修复，不写修复，不把 `tdd` 写成下一项；设计未批准时没有下一项技能，不进入 `flow-02`。`flow-08` 在 `reverse-engineer` 交接完成后进入 `brainstorming` 的架构路径并停在设计对话；`openspec-propose` 与 `to-tickets` 不是下一项；不创建 OpenSpec change。`flow-14` 的三种模式各自结束，不把另一种模式写为下一项；失败模式使用与 `flow-01` 相同的停点，不写修复，不把 `tdd` 写成下一项。`flow-15` 不把 `flow-14` 写为完成后的下一项；进入 `flow-15` 之前必须已有 `flow-14` 的验证证据。`flow-10` 至 `flow-13` 完成后不点名下一个技能。

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

- **WHEN** 新行为路径中的 `diagnosing-bugs` 已完成
- **THEN** 路由停在红信号、最小复现和根因，Phase 5 不应用修复，回归测试和修复只由 `tdd` 写

#### Scenario: 计划格式的交接不是下一项

- **WHEN** `to-tickets` 已写入切片正文
- **THEN** 路由不把 `plan-format.md` 的 Execution handoff 写成下一项，勾选仍等该切片 `TASK_VERIFIED`

#### Scenario: 初始化失败没有修复下一项

- **WHEN** `flow-01` 的失败路径已经得到红信号、最小复现和根因
- **THEN** 路由不把 `tdd` 写成下一项，也不写修复

#### Scenario: 设计交接不进入规格

- **WHEN** `flow-08` 的设计对话已经完成
- **THEN** 路由不把 `openspec-propose` 或 `to-tickets` 写成下一项，也不创建 OpenSpec change

#### Scenario: 壳验证的三种模式不互相交接

- **WHEN** `flow-14` 的失败模式已经停在红信号、最小复现和根因
- **THEN** 路由不把 `writing-skills`、`writing-for-agents` 或 `tdd` 写成下一项

#### Scenario: 写代码途中不扩跑全量

- **WHEN** `flow-02` 的 `tdd` 正在写这一轮生产代码
- **THEN** 额外检查只跑编译、类型检查这类秒级检查，切片自己的一次 RED 失败测试仍保留，全量、端到端和打包不在这一步用来声称验证通过

#### Scenario: 局部快测不代替验证

- **WHEN** `flow-02` 的 `code-review` 已经跑过与本次改动相关的局部快测
- **THEN** 路由仍把 `verification-before-completion` 写成下一项，并且不用这次局部快测通过来声称验证通过

#### Scenario: 收尾前先写只读事实

- **WHEN** `flow-02` 的验证已经通过，尚未点名 `finishing-a-development-branch`
- **THEN** 路由先说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动，并且不把没有独立提交或工作区不干净的标成可清理

### Requirement: WR-21 十三个宿主共用主路径且阶段表同次修改

系统 SHALL 让已登记的 13 个宿主共用 `flow-02` 的主路径。子代理 MUST 被视为任何一个 coding agent 都可以有的能力，而不是只有 Claude Code 与 CodeBuddy 的产品专属。进入委派分支 MUST 同时满足用户已授权委派且宿主提供子代理能力；否则主 Agent MUST 自己做 `tdd` 和 `code-review`，并写明未委派。系统 MUST NOT 把「给 13 个宿主安装只读子代理文件」写成这条主路径完整的条件，也 MUST NOT 为此修改宿主安装器。当前只有 Claude Code 与 CodeBuddy 安装那三个只读子代理的事实保持不变。

系统 SHALL 在同一次变更里修改 `AGENTS.md` 第 2 节的分工句和阶段表，以及 `docs/framework/development-workflow.md` 里与旧链冲突的步骤，使它们与 `flow-02` 一致。阶段表 MUST 先同步规格，再把回执留在活动 change，再移动目录。系统 MUST NOT 修改 `<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 之间的正文，也 MUST NOT 修改 `docs/framework/agent-persona.md`。系统 MUST NOT 修改 `FRAMEWORK_ENTRY` 托管段。系统 MUST NOT 移动这三条切分线：OpenSpec 独占规格账本，`tasks.md` 的切片正文只由 `to-tickets` 写，源码只由 `tdd` 写。当新行为链改的是实现检查、评审分档、验证声称或进入收尾前的事实时，阶段表第 6–9 行与 `docs/framework/development-workflow.md` 的对应步骤 MUST 在同一次变更里写成同一条链。

#### Scenario: 委派条件不全时主 Agent 自己做

- **WHEN** 用户未授权委派，或宿主不提供子代理能力
- **THEN** 主 Agent 自己做 `tdd` 和 `code-review`，并写明未委派

#### Scenario: 子代理能力不按两个宿主分流

- **WHEN** 路由说明谁可以进入委派分支
- **THEN** 它把子代理写成任何一个 coding agent 都可以有的能力，不以 Claude Code 或 CodeBuddy 的产品名单作为分流条件

#### Scenario: 阶段表与流程正文同一条链

- **WHEN** `flow-02` 的新行为链被修改
- **THEN** `AGENTS.md` 第 2 节与 `docs/framework/development-workflow.md` 的对应步骤在同一次变更里改成同一条链，托管段字节不变

#### Scenario: 检查与评审的新句子进入同一条链

- **WHEN** `flow-02` 的新行为链写入实现时的秒级检查、评审风险分档、一次局部快测、验证声称或收尾前的只读事实
- **THEN** 阶段表第 6–9 行与 `docs/framework/development-workflow.md` 的对应步骤写成同一条链，三条切分线保持不动，人格标记与 `FRAMEWORK_ENTRY` 托管段保持不动

### Requirement: WR-22 评审发现不进入任务清单

系统 SHALL 让 `code-review` 的本地改编层把发现只写入交付报告。该改编层 MUST NOT 把 change 的 task list 写成发现的记录位置，也 MUST NOT 授权往 `tasks.md` 追加切片。`flow-04` 与 `flow-09` MUST 沿用这句，并且它们的入口句和技能点名保持不变。`flow-09` MUST 仍在规格已批准且实现之后才点名评审；找不到 change 时 MUST 报告无可用规格。系统 MUST NOT 为这句去改写 `flow-04` 或 `flow-09` 的路由正文。阅读已有 `tasks.md` 以核对切片 MUST 仍然允许。风险分档中的问题在 `flow-04` 与 `flow-09` MUST 只写入交付报告，MUST NOT 把修改交回 `tdd`，也 MUST NOT 要求这两条亲自跑局部快测。

#### Scenario: 壳升级的发现不追加切片

- **WHEN** `flow-04` 点名 `code-review` 与 `framework-rules.md` 并得出发现
- **THEN** 发现只写入交付报告，不往 `tasks.md` 追加切片，入口仍是评审受管 diff，人工改动冲突时停止

#### Scenario: 差距评审的发现不追加切片

- **WHEN** `flow-09` 在规格已批准且找得到 change 之后点名 `code-review` 与 `framework-rules.md` 并得出发现
- **THEN** 发现只写入交付报告，不往 `tasks.md` 追加切片

#### Scenario: 找不到 change 时仍无可用规格

- **WHEN** `flow-09` 找不到 change
- **THEN** 路由报告无可用规格，并且不创建切片来代替规格

#### Scenario: 改编层不再提供任务清单记录位置

- **WHEN** 读取 `code-review` 的 `framework-rules.md` 中原先允许把 Minor 发现记入 change task list 的句子
- **THEN** 该句改为发现只写入交付报告，不往 `tasks.md` 追加切片

#### Scenario: 壳升级与差距评审不把风险问题交回实现

- **WHEN** `flow-04` 或 `flow-09` 在风险分档中得出问题
- **THEN** 问题只写入交付报告，不把修改交回 `tdd`，不要求亲自跑局部快测，入口句和技能点名保持不变

## ADDED Requirements

### Requirement: WR-23 flow-02 的评审按风险分档并跑一次局部快测

系统 SHALL 在 `flow-02` 点名 `code-review` 时按改动风险决定要不要独立只读上下文。纯界面、文案、辅助脚本，且没碰到高风险目录时，系统 MUST 走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，系统 MUST 才要求独立只读上下文。系统 MUST NOT 为此新造一份目录名册。没有已授权的只读子代理时，报告 MUST 标明自审。系统 MUST 对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复 MUST 再核对改动是否在坏数据第一次产生的位置。发现 MUST 写入交付报告，MUST NOT 往 `tasks.md` 追加切片。要改源码 MUST 回到 `tdd`。`code-review` MUST 亲自跑一次与本次改动相关的局部快测。全量、端到端和打包 MUST 仍只在 `verification-before-completion` 用来声称验证通过。局部快测通过 MUST NOT 代替那一步。风险分档的句子若写在 `code-review` 的 `framework-rules.md`，系统 MUST 只追加句子，MUST NOT 把评审改回改业务源码。`flow-04` 与 `flow-09` MUST 只把这些问题写入报告，MUST NOT 把修改交回 `tdd`，入口 MUST 保持不变，并且 MUST NOT 因这句去跑局部快测。

#### Scenario: 轻量改动不要求独立只读上下文

- **WHEN** `flow-02` 的 `code-review` 看到的改动是纯界面、文案或辅助脚本，且没碰到高风险目录，也没碰到仓库已写明的禁改目录
- **THEN** 评审走轻量核对，不要求独立只读上下文，发现仍写入交付报告

#### Scenario: 高风险改动才要求独立只读上下文

- **WHEN** `flow-02` 的改动涉及并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，或仓库已写明的高风险或禁改目录
- **THEN** 评审要求独立只读上下文；没有已授权的只读子代理时，报告标明自审

#### Scenario: 评审对照活动 change 并且缺陷看首次产生处

- **WHEN** `flow-02` 的 `code-review` 面对一个活动 OpenSpec change，且本次工作是缺陷修复
- **THEN** 评审核对允许修改的路径、本期不做、方案点名必须复用的代码，并核对改动是否在坏数据第一次产生的位置；要改源码回到 `tdd`，不往 `tasks.md` 追加切片

#### Scenario: 一次局部快测不能声称验证通过

- **WHEN** `flow-02` 的 `code-review` 已亲自跑过与本次改动相关的局部快测并且通过
- **THEN** 这次通过不代替 `verification-before-completion`，声称验证通过仍只使用那一步的全量、端到端和打包

### Requirement: WR-24 flow-02 的实现检查节奏与收尾前只读事实

系统 SHALL 在 `flow-02` 点名 `tdd` 时保留切片自己的一次 RED 失败测试。写这一轮生产代码时，额外检查 MUST 只跑编译、类型检查这类秒级检查。这一轮改动写完后，系统 MUST 跑关联的局部快测；失败后 MUST 修并重跑同一条。全量、端到端和打包 MUST 仍留在 `verification-before-completion`，MUST NOT 在 `tdd` 这一步用来声称验证通过。`tdd` 的 `discipline.md` 若需要与这句一致，系统 MUST 只在已有的 framework addition 追加句子，MUST NOT 重写 RED 到 GREEN 的循环。进入 `finishing-a-development-branch` 之前，系统 MUST 先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，系统 MUST NOT 标成可清理。推送、合并、删除和清理 MUST 仍等用户当次选择。卫生清单与这份只读事实 MUST NOT 执行 `git worktree remove`。

#### Scenario: 一轮写完后重跑同一条局部快测

- **WHEN** `flow-02` 的 `tdd` 写完这一轮改动，关联的局部快测失败
- **THEN** 实现者修复后重跑同一条局部快测，并且不把全量、端到端或打包提前用来声称验证通过

#### Scenario: 不干净的工作树不标成可清理

- **WHEN** `flow-02` 准备进入 `finishing-a-development-branch`，某条分支没有独立提交，或某个工作树有未提交改动
- **THEN** 只读事实写明该分支或工作树的位置、相对主干是否已推送、是否已进入主干、是否有未提交改动，并且不把它标成可清理；推送、合并、删除和清理仍等用户当次选择
