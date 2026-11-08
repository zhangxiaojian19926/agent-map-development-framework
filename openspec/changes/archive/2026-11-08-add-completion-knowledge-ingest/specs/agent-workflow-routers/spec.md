## MODIFIED Requirements

### Requirement: WR-20 下一项由路由正文写明

系统 SHALL 在路由正文里为每个已完成步骤写明下一项。系统 MUST NOT 要求成员技能在结束时各自提示下一个技能。下一项 MUST 取自该路由的顺序。成员技能收尾指向其他步骤时，路由写明的下一项优先。新行为只写当前步骤的下一项，不预告尚未到达的步骤。

新行为的下一项 MUST 为：

- `diagnosing-bugs` 完成后：已有规格上下文的下一项是 `openspec-explore`，新设计的下一项是 `brainstorming`。
- `openspec-explore` 或 `brainstorming` 完成后：下一项是 `openspec-propose` 或 `openspec-update-change`。
- 规格提案完成后：下一项是 `to-tickets` 与 `plan-format.md`。
- `to-tickets` 且计划已批准后：需要隔离则下一项是 `using-git-worktrees`；顺序执行则下一项是 `executing-plans`。另有委派授权时，才把 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`，写为下一项。
- 工作区就绪后：下一项是 `openspec-apply-change`，并且只装载上下文。
- 上下文装载完成后：下一项是 `tdd` 与 `discipline.md`。
- `tdd` 到达 `TASK_VERIFIED` 后：下一项是 `code-review` 与 `framework-rules.md`。派发或接收反馈时，再把 `requesting-code-review` 与 `receiving-code-review` 写为下一项。
- 评审闭合后：下一项是 `verification-before-completion`。
- 验证通过后：下一项是 `finishing-a-development-branch`。提交、推送和合并仍等待用户当次选择。
- 用户选定集成方式后：下一项是 `openspec-sync-specs`。
- 规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有已验证问题记录时写入问题页，然后留下知识回执。系统不再询问是否摄入。回执留下之后，下一项才是 `openspec-archive-change`。

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
