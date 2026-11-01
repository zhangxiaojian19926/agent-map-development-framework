# 优化记录

> 记录公共工程壳每一轮优化的起因、改动与验证证据。**一条记录对应一个已归档的 change**，没有验证证据的改动不进这里。
>
> 与 [roadmap](roadmap.md) 的分工：roadmap 写**还没做的**，本文件写**做完了的**。

## 怎么读

每条记录四段：**起因**（发现了什么）、**改动**（做了什么）、**验证**（拿什么证明）、**结论**（现在是什么状态、还剩什么）。

验证一栏只写实际跑过的东西。没跑过的写 NOT_RUN，没环境的写 INFRA_ERROR，本地绿灯不等于真实宿主通过。

## 2026-11-01 · 文档契约对齐与指南教学层

**起因**

把 `docs/guide/from-zero-to-one.md` 的 15 条工作流与当前框架逐条比对，查出 5 处漂移：流程契约的完整行为变更路线摘要行漏了实现阶段的 `REGRESSION` 步（2026-09-25 首次提交即存在）；指南工作流 14 只列 4 道门禁而 CI 已跑 6 道；指南、维护者发布文档、README 三处都写着改动前的定时发布时刻 02:00 UTC，而实际调度已是 02:17 UTC。

比指南本身更值得注意的是：指南**零个技能名、零个框架子命令**——它全用散文和提示词描述动作，命令与技能由 Agent 从 BOOTSTRAP 和 AGENTS.md 读。结果是读者学会了一条工作流，仍然不知道它背后站着哪些技能。

**改动**

- 修 5 处漂移；`tools/check-framework` 新增文档契约检查（实现阶段摘要行、指南门禁清单、活文档里的发布时刻），期望值从事实源推导。
- 新增 `docs/guide/framework-model.md`：doctor 十个维度、关系地图、交接、OpenSpec 四个区、十六种授权能力，加按五个域分组的完整状态词典。
- 指南新增「15 条工作流全景与学习顺序」「一条主线走到底」两个部分、顶部三步读法、末尾 15 题读后自检；修正原有的分部重号。
- 新增状态词表校验：文档声明的每个状态码必须在随包代码里真实存在。

**验证**

344 项单测；`check-framework` 覆盖 444 个文件；CI run#51、#52、#53 双平台 15 步全过。

**结论**

漂移修正，机制补上，文档从"使用手册"变成"教程"。状态词典的 40 个 token 全部从代码字面量提取后逐个核对，没有一个是凭印象写的。

---

## 2026-11-01 · 技能接上落点

**起因**

28 个技能全在包里、全部模型调用型、Agent 随时能取到，但有 6 个在 `AGENTS.md` 的路由表和参考段里都没有名字。模型调用型技能的描述常驻上下文，无落点的技能每回合白付预算。

**改动**

`AGENTS.md` 的 DISCOVERY 行接上 `superpowers:dispatching-parallel-agents`、KNOWLEDGE 阶段点名 `llm-wiki`、参考技能段补 `matt-pocock:domain-modeling` 与 `superpowers:writing-skills`；指南补「每条工作流用到的技能」表。

**验证**

344 项单测；CI run#54 双平台全过。

**结论**

6 个孤儿接上 4 个。但**当时的结论是错的**——见下一条。

---

## 2026-11-01 · 本地改编层可达化

**起因**

上一条做完的当晚，全量扫描活文档后发现两件事：

**一、上一条的扫描方法有缺陷。** 只扫 `AGENTS.md` 就得出"6 个技能无落点"，并建议移除 `superpowers:subagent-driven-development`。全量扫描后：真正无落点的只有 `superpowers:using-superpowers` 一个；`subagent-driven-development` 在 `docs/framework/development-workflow.md` 第 6 节早已有委派落点；`dispatching-parallel-agents` 是**两处归属不同**，不是没落点。上一条的建议与既有契约冲突，已撤回。

**二、更严重的问题：框架自己的 1010 行合规层，一直是执行时不存在的东西。** 7 个本地改编规则文件（seam 预确认、切片写入 change 的任务清单、两轴评审的规格来源、`INFRA_ERROR` 不是 RED、术语表落点、复盘标准），每一个都声明"与上游冲突时以本地为准"，每一个都在 `THIRD_PARTY_NOTICES.md` 登记了来源——**却一个指针都没有**。AGENTS.md 不提，`skill-policy.md` 不提，能力规格也不提，上游 `SKILL.md` 更不可能引用框架自己加的文件。

Agent 走的是"读 AGENTS.md → 打开 SKILL.md"，**永远走不到本地层**。于是规格说"SHALL 保留"，而"保留"的内容在执行时不存在。

**改动**

- 每个带本地层的技能，在阶段路由表或参考技能段里标出要一并读取的文件名——指针与技能名同处一格，放在 Agent 必经的路上。
- 新增 `skill/local-layers.json` 登记必读规则层；`tools/check-framework` 双向核对"登记项存在"与"登记项被活文档提及"。
- 新增两项检查：每个在包内的技能必须有落点；同一技能在两处契约里的阶段归属必须一致。
- 移除 `superpowers:using-superpowers` 的技能入口，保留 `references/`（上游 `executing-plans` 与 `writing-skills` 引用着那些平台适配文件）。
- `superpowers:subagent-driven-development` 保留并加本地改编层：上游的任务级评审是 `matt-pocock:code-review` 两轴的第二套实现、implementer 还自行提交，改编层让框架的评审与集成契约占上风。
- `tools/update-manifest` 改为从文件系统推导技能分组计数。

**验证**

350 项单测（+6）；`check-framework` 覆盖 458 个文件、27 个技能；CI run#55 双平台 15 步全过。

**结论**

1010 行规则第一次真正可达。技能数 28 → 27。

---

## 2026-11-01 · 收口检查送达使用者项目

**起因**

四个真实项目都接过公共壳，四个都没走完闭环。公共壳的欠账检查只保护公共壳自己——使用者项目拿到的是"只读文档 + 工具"，拿不到任何能自动发现欠账的东西。

实测 `61.videohao-generator`：5 个 change、69 个已完成任务，`openspec/specs/` 与 `openspec/changes/archive/` 全空，诊断报 `initialization=PARTIAL`、`documentation=STALE[INVALID_EVIDENCE]`。

**改动**

- 欠账判定下沉到 `tools/framework_core/closure.py`（随运行时载荷分发），`tools/check-changes` 改为调用它，公共壳自己的检查输出与退出码不变。
- 新增 `tools/check-project`：使用者项目用的只读检查，报四类欠账——未同步规格的 change、未归档的 change、失效的地图证据、未完成的初始化。默认只报告退出 0，`--strict` 才失败。
- 新增 `templates/project-ci.yml`：使用者项目的持续集成模板，可选片段，**不自动写入用户已有配置**。
- 运行时白名单加 `tools/check-project`。

**验证**

360 项单测（+10，含四类欠账各一条 RED 与一条 GREEN、运行前后仓库不变、两种模式清单一致、公共壳与项目侧判定一致、目标项目已有 CI 不被改写）；`check-framework` 覆盖 466 个文件；CI 双平台全过。

在真实项目上实测，新检查报出的欠账与人工盘点一致：

```text
DEBT change fixed-cover-title-logo (10/10 tasks) capabilities are not synced into openspec/specs/: cover-title-logo
DEBT change material-coverage-and-clarity (13/13 tasks) capabilities are not synced into openspec/specs/: audio-material-coverage, enhance-consent
DEBT change reference-audio-pause-material-flow (8/8 tasks) capabilities are not synced into openspec/specs/: reference-audio-material-flow
DEBT change unify-reference-visual-style (10/10 tasks) capabilities are not synced into openspec/specs/: material-subtitle-safety, reference-visual-style
DEBT initialization is PARTIAL: the project is not fully taken in
DEBT documentation is STALE: INVALID_EVIDENCE
```

**结论**

工具与分发这一侧闭环了。**真实项目上的收口另立 change**：它要写另一个仓库（目标项目的规格与归档），且第 1 步要提交别人写的工作、第 2 步要跑 Agent 重建地图，需要单独授权。步骤与实测现状见 [`docs/plans/2026-11-01-project-closure-check.md`](../plans/2026-11-01-project-closure-check.md)。

---

## 累计

| 指标 | 优化前 | 现在 |
|---|---|---|
| 能力规格 | 32 | 35 |
| 归档 change | 24 | 27 |
| 技能入口 | 28 | 27（移除 `using-superpowers`） |
| 单元测试 | 328 | 360 |
| 分发文件 | 418 | 466 |
| 分发结构检查覆盖 | 指纹、链接、语法、技能计数 | 加文档契约、状态词表、技能路由、本地改编层 |

## 本轮暴露的方法教训

- **判断"某个东西有没有落点"必须扫全部活文档，不能只扫常驻那一份。** 只扫 `AGENTS.md` 会漏掉 `docs/framework/development-workflow.md` 这类流程契约里的路由，进而给出与既有契约冲突的建议。这个错误本轮犯过一次。
- **规格说"SHALL 保留"，不等于保留的内容会被读到。** 事实源与执行事实源之间可能断开，而且断开时没有任何机制报警。本地改编层就是这个断开的实例。
- **人工比对只能覆盖被比对的那一份文档。** 同类漂移的其他副本要靠全仓搜索找——本轮"三处文档写着同一个过时时刻"就是逐条比对指南时看不见的。
