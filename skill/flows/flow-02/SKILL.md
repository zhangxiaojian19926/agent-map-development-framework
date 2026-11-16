---
name: flow-02
description: 在用户提出「日常开发」时使用。本路由覆盖只读审计、纯文档、既有规格修复和新行为。四条路径只写在正文里。
---

# flow-02 日常开发

## 进入

先读根 AGENTS.md、当前 handoff 和只读 doctor。只读到当前步骤。

## 只读审计

不点名实现技能，不写文件。

## 纯文档

被 Agent 读取的文档改动点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。
文档若改变公开接口或验收，改走新行为路径，不停留在纯文档路径。

## 既有规格修复

依次点名 [diagnosing-bugs](../../matt-pocock/diagnosing-bugs/SKILL.md) 与 [discipline.md](../../matt-pocock/diagnosing-bugs/discipline.md)、[tdd](../../matt-pocock/tdd/SKILL.md) 与 [discipline.md](../../matt-pocock/tdd/discipline.md)、[code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。
结果写回原 change。
要改 change 的 proposal、delta spec 或 design 时，只点名 [openspec-update-change](../../openspec/openspec-update-change/SKILL.md)。源码仍只由 tdd 改。openspec-update-change 不写实现步骤，也不创建 tasks.md。

## 新行为

执行时只把当前步骤列为必读，不把尚未到达的步骤当作当前必读。
故障时先点名 diagnosing-bugs 与 discipline.md。诊断停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不应用修复。回归测试和修复只由 tdd 写。
澄清意图只点名 [brainstorming](../../superpowers/brainstorming/SKILL.md) 与 [framework-rules.md](../../superpowers/brainstorming/framework-rules.md)。只有要改行为、接口或验收才进入规格。探针停在建议。
人点名仍可用 [openspec-explore](../../openspec/openspec-explore/SKILL.md)。它不是下一项，不代替 brainstorming，也不跳过「要改行为、接口或验收才进入规格」。
然后点名 [openspec-propose](../../openspec/openspec-propose/SKILL.md) 或 [openspec-update-change](../../openspec/openspec-update-change/SKILL.md)，只落 proposal、delta spec、design。二者不写实现步骤，也不创建 tasks.md。
然后点名 [to-tickets](../../matt-pocock/to-tickets/SKILL.md) 与 [plan-format.md](../../matt-pocock/to-tickets/plan-format.md)。切片正文只写入当前 change 的 tasks.md。plan-format.md 的 Execution handoff 不是下一项。to-tickets 只写入切片正文。`- [ ]` 改成 `- [x]` 仍等该切片 TASK_VERIFIED。
需要隔离时点名 [using-git-worktrees](../../superpowers/using-git-worktrees/SKILL.md)。无委派授权时不读 executing-plans，按已批准切片进入实现。
没有委派授权，或宿主不提供子代理能力时，不把 subagent-driven-development 或 dispatching-parallel-agents 列为当前步骤必读，主 Agent 自己做 tdd 和 code-review，并写明未委派。
委派只在用户已授权且宿主提供子代理时发生。有委派授权且宿主提供子代理能力时，才点名 [subagent-driven-development](../../superpowers/subagent-driven-development/SKILL.md) 与 [framework-rules.md](../../superpowers/subagent-driven-development/framework-rules.md)，或 [dispatching-parallel-agents](../../superpowers/dispatching-parallel-agents/SKILL.md)，二者择一，不并行改同一段源码，被委派者仍用 tdd。
子代理是任何一个 coding agent 都可以有的能力，不是只有 Claude Code 与 CodeBuddy。当前安装事实不改宿主安装器。
人点名仍可用 [executing-plans](../../superpowers/executing-plans/SKILL.md)。它不是下一项，不成为实现器，也不按产品名单改走委派。
装载上下文是路由上的三步：openspec status --json、openspec instructions apply --json、读完全部 contextFiles。这三步不再把 openspec-apply-change 当必经实现器。
人点名仍可用 [openspec-apply-change](../../openspec/openspec-apply-change/SKILL.md)。它不是下一项，只装载上下文，不改业务源码，不在 TASK_VERIFIED 之前勾选。
准备修改业务源码之前，下一项是 [tdd](../../matt-pocock/tdd/SKILL.md) 与 [discipline.md](../../matt-pocock/tdd/discipline.md)。
该切片 TASK_VERIFIED 之后才把对应任务勾成 `- [x]`。
然后点名 code-review 与 framework-rules.md。code-review 的发现写入交付报告，不往 tasks.md 追加切片。重要发现的修改回到 tdd。
派发或接收反馈时再点名 [requesting-code-review](../../superpowers/requesting-code-review/SKILL.md) 与 [receiving-code-review](../../superpowers/receiving-code-review/SKILL.md)。receiving-code-review 若要改码，采纳的修改同样交给 tdd。
然后点名 [verification-before-completion](../../superpowers/verification-before-completion/SKILL.md)。
然后点名 [finishing-a-development-branch](../../superpowers/finishing-a-development-branch/SKILL.md)。提交、推送和合并等待用户当次选择。
然后点名 [openspec-sync-specs](../../openspec/openspec-sync-specs/SKILL.md)。
规格同步之后、归档之前点名 [llm-wiki](../../llm-wiki/SKILL.md) 的写入步骤，把需求页和适用的问题页写入初始化知识库，并留下 knowledge-receipt.json。不再询问是否摄入。然后才点名 [openspec-archive-change](../../openspec/openspec-archive-change/SKILL.md)。结晶、删除、新建知识库、修改注册表和推送不在这次写入里。
四个确认点保持为门，不能用技能收尾代替：brainstorming 的设计批准；Requirement 与 Scenario 认可；to-tickets 的切片批准；finishing-a-development-branch 的合并、PR 或保留。

## 下一项

下一项由本路由写明。成员技能结束时不各自提示下一个技能。成员技能的收尾若指向别处，以下一项为准。
diagnosing-bugs 完成后：停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 tdd 写。澄清意图的下一项是 brainstorming 与 framework-rules.md。openspec-explore 不是下一项。
brainstorming 的设计被批准后：只有要改行为、接口或验收才进入规格；探针停在建议。进入规格时下一项是 openspec-propose 或 openspec-update-change，只落 proposal、delta spec、design。
规格提案完成后：下一项是 to-tickets 与 plan-format.md，不采用该技能收尾中的直接 apply。plan-format.md 的 Execution handoff 不是下一项。to-tickets 只写入切片正文。
to-tickets 且切片已批准后：需要隔离则下一项是 using-git-worktrees。无委派授权时不读 executing-plans，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才把 subagent-driven-development 与 framework-rules.md，或 dispatching-parallel-agents，写为下一项，被委派者仍用 tdd。executing-plans 不是下一项。
进入实现前的装载是三步：openspec status --json、openspec instructions apply --json、读完全部 contextFiles。装载完成后：下一项是 tdd 与 discipline.md。openspec-apply-change 不是下一项。
tdd 到达 TASK_VERIFIED 后：才把对应任务从 `- [ ]` 改为 `- [x]`。下一项是 code-review 与 framework-rules.md。
code-review 的发现写入交付报告，不往 tasks.md 追加切片。重要发现的修改回到 tdd。receiving-code-review 若要改码，采纳的修改同样交给 tdd。派发或接收反馈时，再把 requesting-code-review 与 receiving-code-review 写为下一项。
评审闭合后：下一项是 verification-before-completion。
验证通过后：下一项是 finishing-a-development-branch。提交、推送和合并仍等待用户当次选择。
用户选定集成方式后：下一项是 openspec-sync-specs。
规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有 verified-problem.json 且 conclusion 为 pass 时写入问题页，然后留下 knowledge-receipt.json。不再询问是否摄入。回执留下之后，下一项才是 openspec-archive-change。
openspec-explore、openspec-apply-change、executing-plans 退出必经，人点名仍可用，且不再改源码或写实现步骤。

## 暂停的收尾

本路由的顺序优先于成员技能的收尾提示。
改变行为、接口或验收的有界设计仍进入规格和 to-tickets，不按有界路径直接写实现。探针停在建议。
openspec-propose 与 openspec-update-change 不写实现步骤，也不创建 tasks.md。
openspec-apply-change 不直接修改业务源码。当前切片尚未 TASK_VERIFIED 时，禁止把对应任务从 `- [ ]` 改为 `- [x]`。
executing-plans 不执行改码循环，也不按产品名单改走委派。
code-review 的发现写入交付报告，不往 tasks.md 追加切片。
to-tickets 不写 .scratch，也不要求本包不存在的安装命令。
