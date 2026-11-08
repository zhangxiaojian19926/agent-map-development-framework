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

## 新行为

执行时只把当前步骤列为必读，不把尚未到达的步骤当作当前必读。
故障时先点名 diagnosing-bugs 与 discipline.md。
已有规格上下文点名 [openspec-explore](../../openspec/openspec-explore/SKILL.md)。新设计点名 [brainstorming](../../superpowers/brainstorming/SKILL.md) 与 [framework-rules.md](../../superpowers/brainstorming/framework-rules.md)。
然后点名 [openspec-propose](../../openspec/openspec-propose/SKILL.md) 或 [openspec-update-change](../../openspec/openspec-update-change/SKILL.md)。
然后点名 [to-tickets](../../matt-pocock/to-tickets/SKILL.md) 与 [plan-format.md](../../matt-pocock/to-tickets/plan-format.md)。切片只写入当前 change 的 tasks.md。
需要隔离时点名 [using-git-worktrees](../../superpowers/using-git-worktrees/SKILL.md)。顺序执行点名 [executing-plans](../../superpowers/executing-plans/SKILL.md)。
没有委派授权时，不把 subagent-driven-development 或 dispatching-parallel-agents 列为当前步骤必读。另有委派授权时才点名 [subagent-driven-development](../../superpowers/subagent-driven-development/SKILL.md) 与 [framework-rules.md](../../superpowers/subagent-driven-development/framework-rules.md)，或 [dispatching-parallel-agents](../../superpowers/dispatching-parallel-agents/SKILL.md)。
然后点名 [openspec-apply-change](../../openspec/openspec-apply-change/SKILL.md)，并且只装载 status、instructions 和 contextFiles。
准备修改业务源码之前，点名 [tdd](../../matt-pocock/tdd/SKILL.md) 与 [discipline.md](../../matt-pocock/tdd/discipline.md)。
然后点名 code-review 与 framework-rules.md。派发或接收反馈时再点名 [requesting-code-review](../../superpowers/requesting-code-review/SKILL.md) 与 [receiving-code-review](../../superpowers/receiving-code-review/SKILL.md)。
然后点名 [verification-before-completion](../../superpowers/verification-before-completion/SKILL.md)。
然后点名 [finishing-a-development-branch](../../superpowers/finishing-a-development-branch/SKILL.md)。提交、推送和合并等待用户当次选择。
然后点名 [openspec-sync-specs](../../openspec/openspec-sync-specs/SKILL.md)。
规格同步之后、归档之前点名 [llm-wiki](../../llm-wiki/SKILL.md) 的写入步骤，把需求页和适用的问题页写入初始化知识库，并留下 knowledge-receipt.json。然后才点名 [openspec-archive-change](../../openspec/openspec-archive-change/SKILL.md)。结晶、删除、新建知识库、修改注册表和推送不在这次写入里。

## 下一项

下一项由本路由写明。成员技能结束时不各自提示下一个技能。成员技能的收尾若指向别处，以下一项为准。
diagnosing-bugs 完成后：已有规格上下文的下一项是 openspec-explore，新设计的下一项是 brainstorming。
openspec-explore 或 brainstorming 完成后：下一项是 openspec-propose 或 openspec-update-change。
规格提案完成后：下一项是 to-tickets 与 plan-format.md，不采用该技能收尾中的直接 apply。
to-tickets 且计划已批准后：需要隔离则下一项是 using-git-worktrees；顺序执行则下一项是 executing-plans。另有委派授权时，才把 subagent-driven-development 与 framework-rules.md，或 dispatching-parallel-agents，写为下一项。
工作区就绪后：下一项是 openspec-apply-change，并且只装载上下文。
上下文装载完成后：下一项是 tdd 与 discipline.md。
tdd 到达 TASK_VERIFIED 后：下一项是 code-review 与 framework-rules.md。派发或接收反馈时，再把 requesting-code-review 与 receiving-code-review 写为下一项。
评审闭合后：下一项是 verification-before-completion。
验证通过后：下一项是 finishing-a-development-branch。提交、推送和合并仍等待用户当次选择。
用户选定集成方式后：下一项是 openspec-sync-specs。
规格同步完成后：下一项是把该需求写入初始化知识库，并在该 change 含有 verified-problem.json 且 conclusion 为 pass 时写入问题页，然后留下 knowledge-receipt.json。不再询问是否摄入。回执留下之后，下一项才是 openspec-archive-change。

## 暂停的收尾

本路由的顺序优先于成员技能的收尾提示。
改变行为、接口或验收的有界设计仍进入规格和 to-tickets，不按有界路径直接写实现。探针停在建议。
openspec-apply-change 不直接修改业务源码。当前切片尚未 TASK_VERIFIED 时，禁止把对应任务从 `- [ ]` 改为 `- [x]`。
to-tickets 不写 .scratch，也不要求本包不存在的安装命令。
