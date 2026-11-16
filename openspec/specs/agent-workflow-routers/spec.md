# agent-workflow-routers Specification

## Purpose

规定十五条工作流各自以一个可自动选中的路由技能进入，路由再按固定组合点名成员技能与改编层，并只在已证实的 Coding Agent 载体上投影发现目录或安装写入拦截。

## Requirements

### Requirement: WR-01 十五条路由使用稳定标识

系统 SHALL 为 `flow-01` 至 `flow-15` 各生成一个路由技能，标识与 `docs/guide/from-zero-to-one.md`「15 条一览」的行号一一对应。系统 MUST NOT 另建第十六条工作流入口，也 MUST NOT 把流程标识当作需求标识。

#### Scenario: 十五条路由都存在

- **WHEN** 生成路由产物
- **THEN** 存在 `flow-01` 到 `flow-15` 共十五个路由技能，每个技能的名称与对应工作流行号一致

#### Scenario: 缺少一条路由被报出

- **WHEN** 十五条中任意一条没有路由产物
- **THEN** 结构检查失败并指出缺失的流程标识

### Requirement: WR-02 组合清单是路由正文的事实源

系统 SHALL 用一份组合清单生成路由正文、工作流目录中的技能字段，以及对外指南里每条工作流的技能列。三处技能集合 MUST 与清单一致。系统 MUST NOT 在路由正文里手写一份与清单不同的组合。

#### Scenario: 三处技能集合一致

- **WHEN** 比对组合清单、生成后的路由正文、工作流目录和对外指南的技能列
- **THEN** 同一流程标识下的技能名称与必读改编层一致

#### Scenario: 指南多写一个技能被报出

- **WHEN** 对外指南为某条工作流写出组合清单中没有的技能
- **THEN** 结构检查失败并指出该流程标识和多出的技能名

### Requirement: WR-03 路由可以被模型自动选中

系统 SHALL 让每个路由技能省略 `disable-model-invocation`，并且不把 Codex 侧声明为 `allow_implicit_invocation: false`。描述 MUST 使用第三人称，同时写明用途和触发条件，长度不超过 1024 字符。路由正文 MUST 不超过 500 行，必读文件从正文直接链接，只跳一层。

#### Scenario: 路由描述进入自动调用

- **WHEN** 检查任意一条路由技能的 frontmatter
- **THEN** 不存在 `disable-model-invocation: true`，描述同时包含该工作流的用途和进入条件

#### Scenario: 只声明一侧调用形态被报出

- **WHEN** 某条路由只在 Claude 或 Codex 一侧声明为用户调用型
- **THEN** 形态一致性检查失败并指出该路由

### Requirement: WR-04 成员技能不占第二份自动入口

系统 SHALL 把成员技能保留在原技能目录。系统 MUST NOT 把 `openspec`、`superpowers`、`matt-pocock`、`llm-wiki`、`project-bootstrap` 或 `reverse-engineer` 的技能正文复制到任何宿主发现目录。系统 MUST NOT 把 `retro` 放进任何自动组合。

#### Scenario: 发现目录只有路由

- **WHEN** 检查已投影的宿主发现目录
- **THEN** 其中只有 `flow-01` 至 `flow-15`，没有成员技能的第二份 `SKILL.md`

#### Scenario: 复盘不在自动组合中

- **WHEN** 读取全部十五条路由的必读列表
- **THEN** 列表中不出现 `retro`

### Requirement: WR-05 工作流 2 只有一个自动入口

系统 SHALL 只用 `flow-02` 一条描述覆盖日常开发。只读审计、纯文档、既有规格修复和新行为 MUST 写在该路由正文的内部路径中。系统 MUST NOT 为这四条路径各生成一个可自动选中的技能。

#### Scenario: 四条路径不抢描述

- **WHEN** 列举可自动选中的路由描述
- **THEN** 日常开发只出现 `flow-02` 一条，四条路径只出现在它的正文里

#### Scenario: 文档改变验收时改走新行为

- **WHEN** 请求通过文档改变公开接口或验收含义
- **THEN** `flow-02` 正文要求改走新行为路径，而不是停在纯文档路径

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

### Requirement: WR-07 其余工作流的组合固定

系统 SHALL 让其余路由的必读组合固定为：

- `flow-01`：先点名 `BOOTSTRAP.md` 与 `project-bootstrap`；失败时再点名 `diagnosing-bugs` 与 `discipline.md`。失败路径只停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 MUST NOT 在本路由应用修复：MUST NOT 把最小复现写成回归测试，也 MUST NOT 应用修复。本路由 MUST NOT 写修复，也 MUST NOT 把 `tdd` 写成下一项。设计未批准时停止，不进入 `flow-02`。
- `flow-03`：接口或 seam 点名 `codebase-design`；术语或 ADR 点名 `domain-modeling`。两条不得同时作为同一次触发的必读。参考技能不产生完成状态。
- `flow-04`：评审受管 diff 时点名 `code-review` 与 `framework-rules.md`。存在人工改动冲突时停止。
- `flow-05`：只点名 `llm-wiki`。查询可进行；写入须先列出内容、目标和 alias 并获得本次授权。
- `flow-06`：只在明确要求逆向时点名 `reverse-engineer` 的取证部分。
- `flow-07`：点名 `reverse-engineer` 的证据归并部分。它的触发词 MUST 与 `flow-06` 不同。
- `flow-08`：先点名 `reverse-engineer` 的交接部分，再点名 `brainstorming` 的架构路径，并停在设计对话。MUST NOT 把 `openspec-propose` 或 `to-tickets` 当作下一项。MUST NOT 创建 OpenSpec change，包括未批准的 change。
- `flow-09`：规格已批准且实现之后，点名 `code-review` 与 `framework-rules.md`。找不到 change 时报告无可用规格。
- `flow-10` 至 `flow-13`：不点名成员技能。正文分别绑定研究、候选、渠道和产物登记的既有命令契约。`flow-13` 未完成时 `flow-11` 停止；候选未 `READY` 时 `flow-12` 停止。
- `flow-14`：改技能点名 `writing-skills`；改 Agent 所读文档点名 `writing-for-agents`；失败点名 `diagnosing-bugs` 与 `discipline.md`，并使用与 `flow-01` 失败路径相同的停点：只停在红信号、最小复现和根因，Phase 5 MUST NOT 在本路由应用修复，MUST NOT 把最小复现写成回归测试，也 MUST NOT 应用修复，本路由 MUST NOT 写修复，也 MUST NOT 把 `tdd` 写成下一项。三种模式同属这一条路由。
- `flow-15`：点名 `verification-before-completion`，并且要求已有 `flow-14` 的验证证据。它的触发词 MUST 与 `flow-14` 不同。

#### Scenario: 逆向与产品观察触发词不同

- **WHEN** 比对 `flow-06` 与 `flow-07` 的描述
- **THEN** 两者触发词集合不相交，分别对应取证和证据归并

#### Scenario: 发布候选缺少产物登记时停止

- **WHEN** 进入 `flow-11` 且 `flow-13` 尚未登记产物
- **THEN** 路由要求停止，不把候选判定为 `READY`

#### Scenario: 壳发布与壳验证触发词不同

- **WHEN** 比对 `flow-14` 与 `flow-15` 的描述
- **THEN** 两者触发词集合不相交，分别对应验证和发布

#### Scenario: 初始化失败停在根因

- **WHEN** `flow-01` 因失败点名 `diagnosing-bugs` 与 `discipline.md`
- **THEN** 失败路径只停在红信号、最小复现和根因，Phase 5 不在本路由应用修复，不写回归测试，不应用修复，也不把 `tdd` 写成下一项

#### Scenario: 初始化设计未批准时不进入开发路由

- **WHEN** `flow-01` 的设计未获批准
- **THEN** 路由停止，不进入 `flow-02`，并且没有下一项技能

#### Scenario: 设计交接停在设计对话

- **WHEN** `flow-08` 已点名 `reverse-engineer` 的交接部分并进入 `brainstorming` 的架构路径
- **THEN** 路由停在设计对话，不把 `openspec-propose` 或 `to-tickets` 当作下一项，也不创建 OpenSpec change

#### Scenario: 壳验证失败使用同一停点

- **WHEN** `flow-14` 的失败模式点名 `diagnosing-bugs` 与 `discipline.md`
- **THEN** 失败路径使用与 `flow-01` 相同的停点，而改技能仍只点名 `writing-skills`，改 Agent 所读文档仍只点名 `writing-for-agents`

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

### Requirement: WR-09 改编层被路由点名并登记

系统 SHALL 为 `brainstorming` 提供一份改编层，并把它登记进 `skill/local-layers.json`。活文档 MUST 同时点名该技能和该文件名。路由点名的既有改编层 `discipline.md`、`plan-format.md` 和 `framework-rules.md` MUST 继续满足既有可达性检查。

#### Scenario: 新改编层有活文档指针

- **WHEN** 检查 `brainstorming` 的改编层登记
- **THEN** 登记文件存在，且至少一份活文档在同一语境中点名该技能和该文件名

### Requirement: WR-10 常用宿主使用封闭名册

系统 SHALL 为下列宿主各保存一份能力档案，国际与国内分开列出。档案字段 MUST 包含发现目录、拦截载体、能力类和证据等级。证据等级只允许 `DOCUMENTED`、`RECORDED` 和 `CARRIER_UNKNOWN`。

国际宿主：

- `cursor`：项目发现目录 `.cursor/skills/`，证据等级 `DOCUMENTED`；拦截载体 `.cursor/hooks.json` 的 `preToolUse`，能力类为可阻断。
- `claude-code`：项目发现目录 `CARRIER_UNKNOWN`；拦截载体 `.claude/settings.json` 的 `PreToolUse`，证据等级 `RECORDED`，能力类为可阻断。
- `codex`：项目发现目录 `CARRIER_UNKNOWN`；拦截载体 `.codex/hooks.json`，证据等级 `RECORDED`，能力类为可阻断。用户级 `~/.agents/skills/` 不是安装目标。
- `gemini-cli`：项目发现目录 `CARRIER_UNKNOWN`；拦截载体 `.gemini/settings.json` 的 `BeforeTool`，证据等级 `RECORDED`，能力类为可阻断。用户级 `~/.gemini/skills/` 与 `~/.agents/skills/` 不是安装目标。
- `copilot-cli`：项目发现目录和拦截载体都是 `CARRIER_UNKNOWN`。用户级 `~/.agents/skills/` 只作为共享别名被记载，不是安装目标。能力类为只建议。
- `github-copilot`：发现目录和拦截载体都是 `CARRIER_UNKNOWN`，能力类为只建议。
- `windsurf`：发现目录和拦截载体都是 `CARRIER_UNKNOWN`，能力类为只建议。
- `grok`：项目发现目录和项目拦截载体都是 `CARRIER_UNKNOWN`。既有记录只见用户级钩子且项目配置为空。能力类为只建议。

国内宿主：

- `qwen-code`：项目发现目录 `CARRIER_UNKNOWN`；拦截载体 `.qwen/settings.json`，证据等级 `RECORDED`，能力类为可阻断。
- `codebuddy`：项目发现目录 `CARRIER_UNKNOWN`；无拦截载体，能力类为只建议。
- `trae`：发现目录和拦截载体都是 `CARRIER_UNKNOWN`，能力类为只建议。
- `lingma`：发现目录和拦截载体都是 `CARRIER_UNKNOWN`，能力类为只建议，并且与 `qwen-code` 分开登记。
- `deepseek-harness`：项目发现目录是含 `.git` 的项目根下的 `.dsh/skills/`，证据等级 `DOCUMENTED`。路由必须是该目录的直接子项。用户级 `<dshHome>/skills` 与 `<agentsHome>/skills` 不是安装目标。写入拦截只在 profile 把 `@deepseek-ai/dsh-hooks-claude-code` 的 `configPath` 指向项目内 `.dsh/hooks.json` 时成立；未挂载或配置读取失败时能力类按只建议记录。

#### Scenario: 名册十三个宿主都有档案

- **WHEN** 读取宿主名册
- **THEN** 上列八个国际宿主和五个国内宿主各有一份档案，证据等级只取三种允许值

#### Scenario: 名册外宿主不假装已覆盖

- **WHEN** 请求为名册外的宿主安装路由
- **THEN** 安装失败并报告该宿主不在名册中，不写入任何发现目录或钩子

### Requirement: WR-11 只向已记载的项目发现目录投影

系统 SHALL 把同一份路由正文投影到证据等级不是 `CARRIER_UNKNOWN` 的项目级发现目录。以本要求列出的档案为准，`cursor` 接收 `.cursor/skills/flow-01` 至 `flow-15`，`deepseek-harness` 接收 Git 根 `.dsh/skills/flow-01` 至 `flow-15`。DeepSeek 投影 MUST 是发现根的直接子目录，MUST NOT 嵌套在子目录中，也 MUST NOT 写入 `.agents/skills`。系统 MUST NOT 把路由安装到用户主目录。

#### Scenario: Cursor 收到十五条投影

- **WHEN** 在授权写入后为 `cursor` 安装路由
- **THEN** 目标项目的 `.cursor/skills/` 下出现十五条路由，内容与规范路由正文一致

#### Scenario: DeepSeek harness 收到扁平投影

- **WHEN** 在授权写入后为 `deepseek-harness` 安装路由
- **THEN** Git 根的 `.dsh/skills/flow-01` 至 `flow-15` 各有一份与规范正文一致的 `SKILL.md`，`.agents/skills` 与用户级技能目录都没有新增文件

#### Scenario: 载体未知的发现目录不被创建

- **WHEN** 为 `trae`、`lingma`、`github-copilot`、`windsurf`、`grok`、`copilot-cli`、`codebuddy`、`claude-code`、`codex`、`gemini-cli` 或 `qwen-code` 安装路由
- **THEN** 不创建技能发现目录，缺口报告写明 `CARRIER_UNKNOWN`

### Requirement: WR-12 只在已记载载体上安装写入拦截

系统 SHALL 只为档案中已有拦截载体、且该载体会在项目内自动生效的宿主安装或更新写入门禁。`cursor`、`claude-code`、`codex`、`gemini-cli` 和 `qwen-code` 属于这一组。`deepseek-harness` 的钩子文件按 WR-19 单独安装。门禁 MUST 放行读文件。对业务写入，流程判定不是 `READY` 且不是 `NOT_APPLICABLE` 时，门禁 MUST 拒绝该次调用，并在宿主能够返回给模型的理由中写明应读取的 `flow-*` 路径和缺失步骤。已有适配器 MUST 保留已认证的工具名；尚未观察到的工具名保持未覆盖。`cursor` 的钩子在脚本失败、超时或返回无效结果时 MUST 关闭失败。

#### Scenario: 未批准的写入被拒绝并指向路由

- **WHEN** 可阻断宿主上的已认证写工具被调用，且对应 change 没有有效批准
- **THEN** 该次写入被拒绝，拒绝理由包含应读取的路由路径，目标文件内容不变

#### Scenario: 读路由文件不被拒绝

- **WHEN** 同一宿主读取 `flow-02` 路由或成员技能文件
- **THEN** 读取被放行

#### Scenario: 未知工具名不记成已阻断

- **WHEN** 写操作使用的工具名不在该宿主已认证列表中
- **THEN** 该入口记为未覆盖，不把它报告为已阻断

### Requirement: WR-13 全局技能和用户目录保持不动

系统 SHALL NOT 删除或改写目标项目之外的技能，包括 `~/.agents/skills` 中已有的 OpenSpec 技能。可阻断宿主 MUST 在业务写入完成组合中的当前实现步骤之前拒绝该写入，即使模型先读了全局 `openspec-apply-change`。只建议宿主 MUST 在缺口报告中说明无法请求宿主阻断。

#### Scenario: 用户主目录没有被写入

- **WHEN** 对目标项目执行路由安装
- **THEN** 安装报告的文件路径全部位于目标项目内

#### Scenario: 全局 apply 不能越过实现步骤

- **WHEN** 可阻断宿主中模型先读取全局 `openspec-apply-change`，然后调用已认证写工具修改业务源码，且 `tdd` 步骤尚未被路由点名为当前步骤
- **THEN** 写入被拒绝，理由指向 `flow-02` 和缺失的 `tdd` 步骤

### Requirement: WR-14 CodeBuddy 不获得钩子或记忆文件

系统 SHALL 让 `codebuddy` 继续只安装既有的只读子代理。系统 MUST NOT 创建 `CODEBUDDY.md`、项目钩子或家目录文件。CodeBuddy 对路由的到达方式是读取项目已有的 `AGENTS.md` 指针，系统 MUST NOT 把这种读取报告为自动发现。

#### Scenario: CodeBuddy 安装面不变

- **WHEN** 为 `codebuddy` 执行包含本变更的宿主安装
- **THEN** 不新增 `CODEBUDDY.md` 和钩子文件，已有子代理集合保持不变

### Requirement: WR-15 文件投影不等于现场拦截

系统 SHALL 把路由文件和钩子文件的安装结果与宿主执行轴分开记录。文件与规范一致时，安装轴可以为通过。宿主执行轴 MUST 保持 `NOT_RUN`，直到一次真实会话记录到工具被拒绝且目标文件内容未变。账号、模型或 CLI 缺失 MUST 记为 `NOT_RUN` 或 `INFRA_ERROR`，MUST NOT 记为已阻断。

#### Scenario: 只安装了 Cursor 文件

- **WHEN** Cursor 的路由和钩子文件已写入且没有真实会话
- **THEN** 安装轴通过，宿主执行轴为 `NOT_RUN`

#### Scenario: 真实拒绝后执行轴才通过

- **WHEN** 真实会话中的已认证写工具被拒绝，且拒绝前后目标文件内容一致
- **THEN** 该宿主该入口的执行轴记为已拦截

### Requirement: WR-16 托管段和 doctor 词表不因本变更改写

系统 SHALL NOT 改写 `FRAMEWORK_ENTRY` 托管段，也 SHALL NOT 把新的验收状态写入 `docs/guide/framework-model.md` 的状态词典。阶段表位于托管段之外时，可以增加指向 `skill/flows/flow-*` 的指针。

#### Scenario: 托管段字节保持原样

- **WHEN** 完成本变更的文档指针更新
- **THEN** `FRAMEWORK_ENTRY` 托管段相对变更前的内容一致，状态词典不新增本能力专用状态码

### Requirement: WR-17 技能约束与组合清单一致

系统 SHALL 把 `docs/framework/skill-policy.md` 中「`skill/matt-pocock/` 全部不进入阶段必做步骤」改为与组合清单一致：`flow-02` 点名的 `diagnosing-bugs`、`to-tickets`、`tdd` 和 `code-review` 是对应路径的必读；`codebase-design`、`domain-modeling`、`writing-for-agents` 和 `retro` 仍按各自条件读取。

#### Scenario: 旧的一刀切句子被替换

- **WHEN** 读取更新后的技能约束
- **THEN** 不再把 `to-tickets`、`tdd`、`diagnosing-bugs` 和 `code-review` 整组排除出阶段必读，同时 `retro` 仍不是自动必读

### Requirement: WR-18 路由检查可以被证伪

系统 SHALL 在分发结构检查中验证十五条路由、触发词不相交、成员技能未被投影、名册完整，以及 `CARRIER_UNKNOWN` 没有对应的安装路径。系统 SHALL 提供能让这些检查失败的测试。

#### Scenario: 两条路由共用触发词时检查失败

- **WHEN** 测试让 `flow-14` 与 `flow-15` 使用同一个触发词
- **THEN** 分发结构检查以非零状态退出并指出这两个流程标识

#### Scenario: 猜测路径被写入时检查失败

- **WHEN** 测试为 `trae` 写入一个技能目录
- **THEN** 分发结构检查失败并指出 `trae` 的证据等级是 `CARRIER_UNKNOWN`

### Requirement: WR-19 DeepSeek harness 的发现与条件拦截

系统 SHALL 让 `deepseek-harness` 通过 Git 根 `.dsh/skills/` 下的直接子技能自动发现十五条路由。省略 `disable-model-invocation` 的路由 MUST 被视为模型可调用。系统 SHALL 另写项目内 `.dsh/hooks.json`，其语义沿用 Claude Code 的 `PreToolUse` 拒绝理由，指向当前 `flow-*`。系统 MUST NOT 修改 `~/.dsh` 或 profile。未把 `configPath` 指向该文件时，系统 MUST 按只建议记录，MUST NOT 报告已阻断。配置读取或解析失败时钩子不运行，该次启动 MUST NOT 记为已阻断。工具名未经真实 `PreToolUse` 事件确认前，该入口保持未覆盖。

#### Scenario: 未挂载桥时不报告已阻断

- **WHEN** 项目已有 `.dsh/skills/flow-*` 和 `.dsh/hooks.json`，但运行中的 profile 没有把 `configPath` 指向该钩子文件
- **THEN** 路由可被目录发现，写入拦截的宿主执行轴不是已阻断

#### Scenario: 桥挂载且退出码 2 才记为已拦截

- **WHEN** profile 的 `configPath` 指向 `.dsh/hooks.json`，已确认工具名的 `PreToolUse` 钩子以退出码 2 结束，且目标文件内容不变
- **THEN** 该入口的宿主执行轴记为已拦截

#### Scenario: 钩子配置损坏时不阻断启动

- **WHEN** `.dsh/hooks.json` 无法被桥接读取或解析
- **THEN** 该次启动不记为已阻断，执行轴保持 `NOT_RUN` 或 `INFRA_ERROR`

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

### Requirement: WR-22 评审发现不进入任务清单

系统 SHALL 让 `code-review` 的本地改编层把发现只写入交付报告。该改编层 MUST NOT 把 change 的 task list 写成发现的记录位置，也 MUST NOT 授权往 `tasks.md` 追加切片。`flow-04` 与 `flow-09` MUST 沿用这句，并且它们的入口句和技能点名保持不变。`flow-09` MUST 仍在规格已批准且实现之后才点名评审；找不到 change 时 MUST 报告无可用规格。系统 MUST NOT 为这句去改写 `flow-04` 或 `flow-09` 的路由正文。阅读已有 `tasks.md` 以核对切片 MUST 仍然允许。

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
