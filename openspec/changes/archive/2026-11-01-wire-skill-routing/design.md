# Design

## Context

动机见 [proposal.md](proposal.md)。这里记四个比较结论和据此做的取舍。

### 委派路径：`dispatching-parallel-agents` 与 `subagent-driven-development`

两者不竞争，但**阶段不同**：

| | dispatching-parallel-agents | subagent-driven-development |
|---|---|---|
| 输入 | 一堆失败现象 | 一份已批准的实施计划 |
| 每个 agent 做什么 | 独立**调查并修**自己那摊 | 独立**实现**一个切片 |
| 评审 | 无——主会话读摘要、跑全量测试、集成 | 每个 task 一次评审（规格+质量两轴）+ 最后整分支评审 |
| 修复循环 | 无 | 最多 5 轮，ruling 记账 |
| 结束 | 集成 | `superpowers:finishing-a-development-branch` |

**取 `dispatching-parallel-agents`。** 三条理由：

1. **它与框架零重叠。** 它管的是"多个独立失败怎么并行分解"，与 `matt-pocock:diagnosing-bugs` 的单线索假设循环互补而非竞争。它不碰评审、不碰提交。
2. **`subagent-driven-development` 与框架已定的契约重复三处**：它的 task reviewer 就是"规格符合性 + 代码质量"两轴，与 REVIEW 阶段的 `matt-pocock:code-review` 同一套判据两套实现；它的 implementer 自行提交，与框架"提交权在 INTEGRATE 阶段由用户选"冲突；它的 fix loop 与 rulings 账本与 REVIEW 阶段的"重要问题处理"重复。引入它等于让两套完成判据并存——正是框架反复在防的事。
3. **框架已有先例**：被取代的上游技能（`writing-plans` → `to-tickets`、`systematic-debugging` → `diagnosing-bugs`、`test-driven-development` → `tdd`）已从包里彻底移除。路由表不点名 + 包里移除是框架处理"技能被更强版本取代"的方式。

**代价要说清楚**：这样接之后，**实施阶段的并行委派仍然没有落点**。`executing-plans` 是顺序的，`subagent-driven-development` 不接。这是真实缺口，但要补它应该写一个本地改编层（评审走 `matt-pocock:code-review`、提交走 INTEGRATE 阶段），而不是引入第二套评审机制。本批不补，记进 roadmap。

### `writing-skills` 与 `writing-for-agents`

**不重叠，是两层。** 实证：

| | writing-skills (superpowers) | writing-for-agents (matt-pocock) |
|---|---|---|
| 定位 | **创作流程**：怎么把一个技巧验证过再写成技能 | **写作规范**：怎么写 Agent 要读的任何文档 |
| 覆盖 | 只写技能 | 技能 + AGENTS.md/CLAUDE.md + 任何被指针引用的文档 |
| 核心 | TDD 循环：先看它在没有技能时失败 | context pointer 措辞、context load / cognitive load 双预算、渐进披露、co-location、信息层级 |
| 前置 | 必须先懂 `matt-pocock:tdd` | 无 |

关键词互检：`writing-skills` 对 writing-for-agents 的五个手法关键词命中 **0** 次；`writing-for-agents` 对 writing-skills 的验证关键词（RED / baseline / pressure scenario）命中 **0** 次。

**分工**：写作规范一律走 `writing-for-agents`；**新建一个技能**时另走 `writing-skills` 的"先看它失败"验证流程——那正是 writing-for-agents 管不到的一半。

### `using-superpowers`

它的职能是"在**任何**回应之前先查技能表"，且措辞是"哪怕 1% 可能适用也必须调用、不可协商"。

框架已经用两层东西取代了这一层：AGENTS.md 的阶段路由表（比"先查表"更精确——它直接给出本阶段该用哪个）和 `docs/framework/skill-policy.md`（选择、形态、缺失时怎么办）。而它那句"1% 就必须调用"与框架自己的规则**实质冲突**：`skill-policy.md` 写的是"只加载本任务需要的技能和资源"、"技能不得自动扩大范围"。

**建议按先例从包里移除。** 本批不动——移除会改变分发内容，需单独确认。

## Goals / Non-Goals

**Goals:**

- 6 个无落点的技能里接上 4 个，剩 2 个给出明确建议。
- 对外指南能查到每条工作流用哪些技能。
- 阶段路由表仍然只有 11 行，必做环节与退出条件不变。

**Non-Goals:**

- 不移除任何技能。
- 不给实施阶段补并行委派落点。
- 不改任何既有阶段的退出条件、交接结果或门禁判据。

## Decisions

**决策一：`dispatching-parallel-agents` 放 DISCOVERY 的故障分支，不放 WORKSPACE。**

它的"Use when"写的是"3+ 测试文件失败、根因不同""多个独立子系统各自坏了"——这是**排障**。放 WORKSPACE 会让那一行"需隔离时 using-git-worktrees; 顺序 executing-plans"的语义变浑，而且它自带"每个 agent 读摘要后集成"的动作，与框架的 APPLY/IMPLEMENT 阶段职责重叠。

条件短语写成"多个独立失败可并行分解时"，放在 `matt-pocock:diagnosing-bugs` 之后——先单线索诊断，确诊是多个独立问题再并行分解。

**决策二：参考技能段从"三个"改成"五个"，并写清分工。**

原来那句把 `writing-for-agents`、`codebase-design`、`retro` 三个并列。补 `domain-modeling` 时发现它的触发条件与 `codebase-design` 相邻（一个谈领域术语、一个谈模块接口），所以每个都要带自己的触发条件，不能只列名字。

`writing-skills` 与 `writing-for-agents` 的分工必须写在同一句里，否则读者会以为两者重复。

**决策三：AGENTS.md 只在既有行内追加条件短语，不新增行。**

AGENTS.md 是常驻上下文指针，每加一行都在每轮付 context load。所以四处改动全部落在既有行内：DISCOVERY 行追加一个条件短语、KNOWLEDGE 行改写既有短语、参考技能段改写既有段落。净增文字量是有限的。

**决策四：指南的技能表放在第二部分。**

第二部分叫"15 条工作流全景与学习顺序"，是读者建地图的地方。每条工作流用哪些技能属于地图的一部分。表放在 15 条一览表之后——先看有哪些工作流，再看每条用什么。

表只给工作流级结论，不展开工作流 2 路径 D 的十六个技能全链：那张链在 AGENTS.md 的阶段路由表里，指南给一行指向即可。

**决策五：两个待移除的技能本批不动。**

移除会改变分发内容、影响技能计数、需要在清单里清条目。混在本批里会让这次 diff 难审。给出建议、单独确认、单独做。

## Risks / Trade-offs

- **DISCOVERY 行变长。** 该行现在有四个技能与四个条件，读起来密。用条件短语分隔而不是加新行，代价可控。
- **指南的技能表可能随路由表变化而过期。** 它是活文档，路由表一改就该同步。本批不为此加机器检查——路由表是 AGENTS.md 的自由 Markdown，解析它并与指南比对属于 roadmap 第 6 项的核对工具范围，等那个工具做。
- **实施阶段仍无并行委派落点。** 已知缺口，已记入 roadmap，不用一个重复评审的技能去填。
- **`using-superpowers` 与 `subagent-driven-development` 在移除前仍付上下文预算。** 两个技能约六十来 token 一轮，可接受；确认后一次清掉。
