## Context

见 proposal.md 的 Why。行为合同见 `specs/agent-workflow-routers/spec.md` 里修改后的 WR-06、WR-20、WR-21、WR-22，以及新增的 WR-23、WR-24。

路由正文的字节来自 `tools/framework_core/workflows/routers.py`。`render_skill` 用 `combinations.json` 里的一个 flow 对象生成一份 `SKILL.md`。`write_routers` 对十五条都调用它并写回 `skill/flows/<id>/SKILL.md`。`distribution_errors` 在文件与 `render_skill` 的输出不一致时报 `router body drifted from the combination manifest`。`flow-02` 的 `mentions` 决定 `catalog.json` 与 `docs/guide/from-zero-to-one.md` 里该路由的技能列；`sync_catalog` 只在 mentions 要改时才用。

`code-review` 的 `framework-rules.md` 开头写明与上游 `SKILL.md` 冲突时以改编层为准。`tdd` 的 `discipline.md` 已有一节 framework addition。主规格 `openspec/specs/agent-workflow-routers/spec.md` 要到以后的同步步骤才改；这次只留下 delta。

## Goals / Non-Goals

**Goals:**

- 五条做法只进 `flow-02` 的对象，再渲染出一份与清单一致的正文。
- 风险分档用追加句落在改编层，轻量核对不必另起只读上下文。
- 一次局部快测只绑在 `flow-02` 点名 `code-review` 的句子上。
- 阶段表第 6–9 行和 `development-workflow.md` 的对应步骤与这条新链同次写成一致，三条切分线不动。

**Non-Goals:**

- 不手改 `skill/flows/flow-02/SKILL.md` 出一份清单里没有的正文。
- 不改 `flow-02` 的 `mentions`，因此不跑 `sync_catalog`。
- 不把局部快测写进 `framework-rules.md`。
- 不改上游 `code-review`、`verification-before-completion`、`finishing-a-development-branch`，也不重写 `tdd` 的 RED 到 GREEN 循环。
- 不改 `flow-04` 与 `flow-09` 的入口文件。
- 不新造高风险目录名册，不在 `AGENTS.md` 增加小节。
- 不写 `tasks.md`，不同步主规格，不写知识库。

## Decisions

1. 正文事实源是 `combinations.json` 里 `id` 为 `flow-02` 的对象。只改这个对象的 `lines`，然后用现有 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。`write_routers` 会重写全部十五条；其余对象不改，所以其余十四份的渲染结果与改前一致。备选「手改 `SKILL.md`」不行：`distribution_errors` 会报正文漂移。备选「把五条拆成第十六条路由」不行：WR-01 与 WR-05 要求仍是十五条，日常开发仍只有 `flow-02` 一个自动入口。

2. 风险分档、自审标明、活动 change 的三项核对、缺陷位置核对，追加在 `skill/matt-pocock/code-review/framework-rules.md`，放在现有 Closure rules 之后。不删除「评审不改业务源码，不往 tasks.md 追加切片。发现写入交付报告。」也不把「修改回到 `tdd`」写成 `flow-04` 与 `flow-09` 的义务。上游 `SKILL.md` 仍写两条轴总是启动并行子代理；改编层第 4–5 行已经声明冲突时以本文件为准，所以轻量核对不改上游。备选「改上游方法」会把评审技能本身改成另一套流程，也会让 `flow-04` 与 `flow-09` 失去现在读到的两轴方法。

3. 一次局部快测写在 `flow-02` 点名 `code-review` 的句子里，包括既有规格修复、新行为和下一项。不写进 `framework-rules.md`。这样 `flow-04` 与 `flow-09` 读到风险分档，但不会继承跑测试的义务。它们只把问题写入报告。备选「把快测也写进改编层」会让壳升级和差距评审在没有这条授权时跑测试。

4. 检查节奏分成两段，与 WR-24 一致。切片自己的一次 RED 失败测试留在 `discipline.md` 第 52–68 行的循环里。framework addition 只追加一句：写这一轮生产代码时，额外检查只跑编译和类型检查；这一轮写完后跑关联局部快测，失败后重跑同一条；全量、端到端和打包不在这里用来声称验证通过。备选「删掉 RED」会改掉阶段表第 6 行已经写明的有效 RED。备选「只改路由、不改第 70 行」会让「其他测试也要通过」在每一次变绿时继续扩跑。

5. 收尾前的只读事实写在点名 `finishing-a-development-branch` 之前，不改该技能原文。卫生清单同样不调用 `git worktree remove`。技能里已有的删除命令仍留在用户当次选择之后。备选「删掉技能第 6 步」会在这次范围之外改掉用户选择清理之后的既有动作。

6. WR-21 要求新行为链和阶段表同次一致。同一次编辑只改 `AGENTS.md` 第 102–105 行的交接句，以及 `docs/framework/development-workflow.md` 第 8 节的回归、第 10 节的评审、第 11 节的验证声称、第 12 节进入收尾前的事实。第 80 行保持「不修改文件」。第 91 行的三条切分线、人格标记和 `FRAMEWORK_ENTRY` 不动。备选「完全不改阶段表」会让 WR-21 的「同一条链」落空。备选「重写 `AGENTS.md`」会超出卫生清单「不改文件」和「不新增小节」。

## Risks / Trade-offs

- [上游评审仍写总是起子代理] → 分档句放在必读的改编层，并依赖该文件已有的「冲突时以本文件为准」。不改上游。
- [第 70 行仍可能被读成每一次变绿都跑更宽的测试] → framework addition 明确那一句不授权全量、端到端或打包，路由写同一句。
- [收尾技能仍会再跑全量，并含 `git worktree remove`] → 声称验证通过只认前一步；删除和清理仍等用户当次选择；卫生清单不执行删除。不改该技能。
- [本仓库没有单独的高风险目录名册] → 分档使用规格里的类别，加上仓库已经写明的禁改范围。不新造名册。
- [`write_routers` 重写十五条] → 只改 `flow-02` 对象。其余对象的字节不变，渲染结果就不变。

## Migration Plan

没有数据迁移。这五条在路由正文、改编层追加句、纪律追加句和阶段表交接句一起落地后，下一次读到 `flow-02` 的会话按新句子走。回退时把 `flow-02` 对象、两处追加句、阶段表第 6–9 行和 `development-workflow.md` 的对应步骤一起退回，避免正文和阶段表再次分叉。主规格留在以后的同步步骤，不在这次设计里提前改 `openspec/specs/`。
