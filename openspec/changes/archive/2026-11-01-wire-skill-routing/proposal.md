# Proposal

## Why

工程壳里有 28 个技能，全部随包分发、全部是模型调用型（只有 `retro` 是用户调用型），Agent 随时能取到。但有 6 个技能，**AGENTS.md 的阶段路由表和参考技能段都没有它们的名字**：

| 技能 | 状态 |
|---|---|
| `superpowers:dispatching-parallel-agents` | 包内、能被调用，路由表无落点 |
| `matt-pocock:domain-modeling` | 2026-11-01 批 3 引进，只写了术语表落点，路由表漏了 |
| `llm-wiki` | KNOWLEDGE 阶段写的是"已选知识库技能"，不点名；指南只在工作流 5 附近提一次 |
| `superpowers:writing-skills` | 参考段点的是 `matt-pocock:writing-for-agents`，两者职能相邻但没分工 |
| `superpowers:subagent-driven-development` | 包内，路由表无落点 |
| `superpowers:using-superpowers` | 包内，路由表无落点 |

（`project-bootstrap` 与 `reverse-engineer` 在 AGENTS.md §0 各有一处落点，不算孤儿。）

两个代价：

1. **技能白付上下文预算。** 模型调用型技能的描述常驻上下文，每轮都在。6 个没有任何触发条件的技能，等于每轮白付六份描述的注意力预算，换不回任何行为。
2. **读者和 Agent 都不知道什么时候该用它。** 对外指南里零个技能名、零个框架子命令——它全用散文和提示词描述动作，命令与技能由 Agent 从 BOOTSTRAP 和 AGENTS.md 读。结果是：读者学会了一条工作流，仍然不知道这一条背后站着哪些技能、哪些环节靠技能、哪些靠 CLI 与流程契约。

框架自己已经有判断标准：阶段路由表点名的是必做环节，"已选知识库技能"这种不点名写法等于没有路由。

## What Changes

- AGENTS.md 阶段路由表接上四个技能：
  - DISCOVERY 行补 `superpowers:dispatching-parallel-agents`，条件写明"多个独立失败可并行分解时"——它管的是排障阶段的并行分解，与 `matt-pocock:diagnosing-bugs` 的单线索假设循环互补。
  - KNOWLEDGE 行把"已选知识库技能"改为点名 `llm-wiki`。
  - 参考技能段补 `matt-pocock:domain-modeling`（讨论领域术语与概念边界时）和 `superpowers:writing-skills`（新建技能时，与 `writing-for-agents` 分工）。
- 对外指南第二部分补一张「每条工作流用到的技能」表：15 条工作流各自用哪些技能、哪些工作流不靠技能。读者不必读 AGENTS.md 就能知道每条工作流的技能构成。
- 维护者 roadmap 修正第 6、7 项的过时数字与落点，登记本批。

## Capabilities

### New Capabilities

- `skill-routing`: 规定每个技能都要有可指名的落点（阶段路由或参考位），规定对外指南能查到每条工作流用哪些技能。

### Modified Capabilities

- `agent-craft-skills`: 「工作流接线为参考而非义务」此前只覆盖两个引入的技能，现扩展到四个参考技能各自的位置，并说明分工。

## Impact

- 修改 `AGENTS.md`：阶段路由表两行与参考技能段一处。
- 修改 `docs/guide/from-zero-to-one.md`：第二部分新增「每条工作流用到的技能」表。
- 修改 `docs/maintainer/roadmap.md`：第 6、7 项数字与落点、已完成批次表。
- 不引入运行时依赖，不改变任何既有阶段的退出条件，不改变任何门禁的判据。
- 本批**不做**的事：移除 `superpowers:subagent-driven-development` 与 `superpowers:using-superpowers`。这两项已给出建议，但移除会改变分发内容，需单独确认后再做。
