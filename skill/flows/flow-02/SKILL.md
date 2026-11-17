---
name: flow-02
description: 在用户提出「日常开发」时使用。本路由覆盖只读审计、纯文档、既有规格修复和新行为。四条路径只写在正文里。
---

# flow-02 日常开发

## 进入

先读根 AGENTS.md、当前 handoff 和只读 doctor。只读到当前步骤。

## 只读审计

不点名实现技能，不写文件。按熟悉度分档：单点问题直接检索；单模块再读该模块约束；陌生或跨模块才做结构快照。简报至少含文件与行号、可复用代码、仓库里已经存在的局部快测命令、要用户拍板的问题。只有用户已授权且宿主提供子代理时，才按互不重叠的目录做只读切片；否则主 Agent 自己读。结束仍停在只读审计，不把 openspec-explore、openspec-propose 或 to-tickets 写成下一项。
用户要看仓库卫生时，只出清单：死链、长期未改的文档是否和当前代码矛盾、没有任何入口执行的测试目录、嵌在主仓库目录里的 worktree、分支合入状态。清单不改文件。之后要改 Agent 所读文档，仍走纯文档并点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。不重写 AGENTS.md，不新增小节，不执行 git worktree remove。

## 纯文档

被 Agent 读取的文档改动点名 [writing-for-agents](../../matt-pocock/writing-for-agents/SKILL.md)。
文档若改变公开接口或验收，改走新行为路径，不停留在纯文档路径。

## 既有规格修复

依次点名 [diagnosing-bugs](../../matt-pocock/diagnosing-bugs/SKILL.md) 与 [discipline.md](../../matt-pocock/diagnosing-bugs/discipline.md)、[tdd](../../matt-pocock/tdd/SKILL.md) 与 [discipline.md](../../matt-pocock/tdd/discipline.md)、[code-review](../../matt-pocock/code-review/SKILL.md) 与 [framework-rules.md](../../matt-pocock/code-review/framework-rules.md)。
点名 tdd 时，切片自己的一次 RED 失败测试保留。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量、端到端和打包不在这一步用来声称验证通过。
点名 code-review 时按风险分档决定是否需要独立只读上下文。纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。亲自跑一次与本次改动相关的局部快测。这次通过不能代替 verification-before-completion。发现写入交付报告，不往 tasks.md 追加切片。要改源码回到 tdd。
结果写回原 change。
要改 change 的 proposal、delta spec 或 design 时，只点名 [openspec-update-change](../../openspec/openspec-update-change/SKILL.md)。源码仍只由 tdd 改。openspec-update-change 不写实现步骤，也不创建 tasks.md。写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，落盘前在仓库里核对。对不上就改这句或标成待确认。将要新建的文件不要求事先存在。不另写 docs/ 规格，不另建任务契约。核对通过不等于 Requirement 已被认可。

## 新行为

执行时只把当前步骤列为必读，不把尚未到达的步骤当作当前必读。
故障时先点名 diagnosing-bugs 与 discipline.md。诊断停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不应用修复。回归测试和修复只由 tdd 写。
澄清意图只点名 [brainstorming](../../superpowers/brainstorming/SKILL.md) 与 [framework-rules.md](../../superpowers/brainstorming/framework-rules.md)。只有要改行为、接口或验收才进入规格。探针停在建议。
人点名仍可用 [openspec-explore](../../openspec/openspec-explore/SKILL.md)。它不是下一项，不代替 brainstorming，也不跳过「要改行为、接口或验收才进入规格」。
然后点名 [openspec-propose](../../openspec/openspec-propose/SKILL.md) 或 [openspec-update-change](../../openspec/openspec-update-change/SKILL.md)，只落 proposal、delta spec、design。二者不写实现步骤，也不创建 tasks.md。写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，落盘前在仓库里核对。对不上就改这句或标成待确认。将要新建的文件不要求事先存在。不另写 docs/ 规格，不另建任务契约。核对通过不等于 Requirement 已被认可。
然后点名 [to-tickets](../../matt-pocock/to-tickets/SKILL.md) 与 [plan-format.md](../../matt-pocock/to-tickets/plan-format.md)。切片正文只写入当前 change 的 tasks.md。plan-format.md 的 Execution handoff 不是下一项。to-tickets 只写入切片正文。`- [ ]` 改成 `- [x]` 仍等该切片 TASK_VERIFIED。
需要隔离时点名 [using-git-worktrees](../../superpowers/using-git-worktrees/SKILL.md)。无委派授权时不读 executing-plans，按已批准切片进入实现。
没有委派授权，或宿主不提供子代理能力时，不把 subagent-driven-development 或 dispatching-parallel-agents 列为当前步骤必读，主 Agent 自己做 tdd 和 code-review，并写明未委派。
委派只在用户已授权且宿主提供子代理时发生。有委派授权且宿主提供子代理能力时，才点名 [subagent-driven-development](../../superpowers/subagent-driven-development/SKILL.md) 与 [framework-rules.md](../../superpowers/subagent-driven-development/framework-rules.md)，或 [dispatching-parallel-agents](../../superpowers/dispatching-parallel-agents/SKILL.md)，二者择一，不并行改同一段源码，被委派者仍用 tdd。
子代理是任何一个 coding agent 都可以有的能力，不是只有 Claude Code 与 CodeBuddy。当前安装事实不改宿主安装器。
人点名仍可用 [executing-plans](../../superpowers/executing-plans/SKILL.md)。它不是下一项，不成为实现器，也不按产品名单改走委派。
装载上下文是路由上的三步：openspec status --json、openspec instructions apply --json、读完全部 contextFiles。这三步不再把 openspec-apply-change 当必经实现器。
人点名仍可用 [openspec-apply-change](../../openspec/openspec-apply-change/SKILL.md)。它不是下一项，只装载上下文，不改业务源码，不在 TASK_VERIFIED 之前勾选。
准备修改业务源码之前，下一项是 [tdd](../../matt-pocock/tdd/SKILL.md) 与 [discipline.md](../../matt-pocock/tdd/discipline.md)。切片自己的一次 RED 失败测试保留。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量、端到端和打包不在这一步用来声称验证通过。
该切片 TASK_VERIFIED 之后才把对应任务勾成 `- [x]`。
然后点名 code-review 与 framework-rules.md。纯界面、文案、辅助脚本且没碰到高风险目录时走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。code-review 亲自跑一次与本次改动相关的局部快测。这次通过不能代替 verification-before-completion。code-review 的发现写入交付报告，不往 tasks.md 追加切片。重要发现的修改回到 tdd。要改源码回到 tdd。
派发或接收反馈时再点名 [requesting-code-review](../../superpowers/requesting-code-review/SKILL.md) 与 [receiving-code-review](../../superpowers/receiving-code-review/SKILL.md)。receiving-code-review 若要改码，采纳的修改同样交给 tdd。
然后点名 [verification-before-completion](../../superpowers/verification-before-completion/SKILL.md)。声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。
进入 finishing-a-development-branch 之前，先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。对还没进主干、且要用户决定或仍在进行的分支，读改动最多的一两个文件，用一句人话写改了什么，并给一条建议和理由。建议合并前用 git merge-tree --write-tree --name-only 看冲突文件，这条命令不改分支、不改工作目录。云端分支已删除不能单独当成可清理。只看是不是主干祖先会漏掉 squash，也会把还没提交的新分支误判成已合入。squash 或 rebase 之后整体补丁已在主干且工作区干净，可以标成可清理候选。推送、合并、删除仍等用户当次选择。读不到 PR 就不要猜。不新做看板脚本。仍不执行 git worktree remove。然后点名 [finishing-a-development-branch](../../superpowers/finishing-a-development-branch/SKILL.md)。提交、推送、合并、删除和清理仍等待用户当次选择。
然后点名 [openspec-sync-specs](../../openspec/openspec-sync-specs/SKILL.md)。
规格同步之后、归档之前点名 [llm-wiki](../../llm-wiki/SKILL.md) 的写入步骤，把需求页和适用的问题页写入初始化知识库，并留下 knowledge-receipt.json。不再询问是否摄入。然后才点名 [openspec-archive-change](../../openspec/openspec-archive-change/SKILL.md)。结晶、删除、新建知识库、修改注册表和推送不在这次写入里。
四个确认点保持为门，不能用技能收尾代替：brainstorming 的设计批准；Requirement 与 Scenario 认可；to-tickets 的切片批准；finishing-a-development-branch 的合并、PR 或保留。

## 下一项

下一项由本路由写明。成员技能结束时不各自提示下一个技能。成员技能的收尾若指向别处，以下一项为准。
diagnosing-bugs 完成后：停在红信号、最小复现和根因。Phase 5 不应用修复。回归测试和修复只由 tdd 写。澄清意图的下一项是 brainstorming 与 framework-rules.md。openspec-explore 不是下一项。
brainstorming 的设计被批准后：只有要改行为、接口或验收才进入规格；探针停在建议。进入规格时下一项是 openspec-propose 或 openspec-update-change，只落 proposal、delta spec、design。写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，落盘前在仓库里核对。对不上就改这句或标成待确认。将要新建的文件不要求事先存在。不另写 docs/ 规格，不另建任务契约。核对通过不等于 Requirement 已被认可。
规格提案完成后：下一项是 to-tickets 与 plan-format.md，不采用该技能收尾中的直接 apply。plan-format.md 的 Execution handoff 不是下一项。to-tickets 只写入切片正文。
to-tickets 且切片已批准后：需要隔离则下一项是 using-git-worktrees。无委派授权时不读 executing-plans，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理时发生；此时才把 subagent-driven-development 与 framework-rules.md，或 dispatching-parallel-agents，写为下一项，被委派者仍用 tdd。executing-plans 不是下一项。
进入实现前的装载是三步：openspec status --json、openspec instructions apply --json、读完全部 contextFiles。装载完成后：下一项是 tdd 与 discipline.md。openspec-apply-change 不是下一项。
tdd 进行中：切片自己的一次 RED 失败测试保留。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。这一轮改动写完后跑关联的局部快测，失败就修，修完重跑同一条。全量、端到端和打包不在这一步用来声称验证通过。
tdd 到达 TASK_VERIFIED 后：才把对应任务从 `- [ ]` 改为 `- [x]`。下一项是 code-review 与 framework-rules.md。
code-review 按风险分档决定是否需要独立只读上下文。纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。亲自跑一次与本次改动相关的局部快测。这次通过不能代替 verification-before-completion。发现写入交付报告，不往 tasks.md 追加切片。重要发现的修改回到 tdd。要改源码回到 tdd。receiving-code-review 若要改码，采纳的修改交给 tdd。派发或接收反馈时，再把 requesting-code-review 与 receiving-code-review 写为下一项。
评审闭合后：下一项是 verification-before-completion。声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。
验证通过后、进入 finishing-a-development-branch 之前：先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。对还没进主干、且要用户决定或仍在进行的分支，读改动最多的一两个文件，用一句人话写改了什么，并给一条建议和理由。建议合并前用 git merge-tree --write-tree --name-only 看冲突文件，这条命令不改分支、不改工作目录。云端分支已删除不能单独当成可清理。只看是不是主干祖先会漏掉 squash，也会把还没提交的新分支误判成已合入。squash 或 rebase 之后整体补丁已在主干且工作区干净，可以标成可清理候选。推送、合并、删除仍等用户当次选择。读不到 PR 就不要猜。不新做看板脚本。仍不执行 git worktree remove。下一项才是 finishing-a-development-branch。提交、推送、合并、删除和清理仍等待用户当次选择。
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
