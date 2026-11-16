## MODIFIED Requirements

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

## ADDED Requirements

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
