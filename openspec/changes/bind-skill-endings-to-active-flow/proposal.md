## Why

三条路由已经写明停点，但成员技能原文仍把会话带去旧动作。`diagnosing-bugs` 的 Phase 5 仍写应用修复并写回归测试。`code-review` 的改编层仍写重要发现必须先修。`brainstorming` 的改编层把改行为、接口或验收的下一项写成 `openspec-propose` / `openspec-update-change`，再 `to-tickets`，盖过 `flow-08` 的停点。现规格约束的是路由正文，没有要求这三份原文默认服从活动 flow。

## What Changes

- `diagnosing-bugs` 的 Phase 5 不再是默认改码步骤。本技能不应用修复，也不写生产代码。回归测试和修复只在活动路由把 `tdd` 写成下一项时由 `tdd` 做。`flow-01` 与 `flow-14` 读完诊断就停。`discipline.md` 查完根因后不再把「现在写代码」或「先写测试再修复」写成下一步。第 8 行「有明确理由可跳过阶段」保留。Phase 5 不是第二个实现器。
- `code-review` 的 `framework-rules.md` 改为评审不改业务源码，不往 `tasks.md` 追加切片。发现写入交付报告。活动路由把 `tdd` 写成下一项时，修改回到 `tdd`。`flow-04` 与 `flow-09` 没有这句，评审到报告为止。Minor 句保持只进交付报告。这两条路由的入口不改。
- `brainstorming` 的下一项只由活动中的 flow 正文宣布。`flow-02` 宣布进入规格时才是 `openspec-propose` 或 `openspec-update-change`，然后再 `to-tickets`。`flow-08` 的停点优先。上游 `SKILL.md` 架构路径第 6–9 步的收尾改为指向活动 flow 的下一项，除非活动 flow 点名它们。

## Capabilities

### New Capabilities

### Modified Capabilities

- `agent-workflow-routers`: 补上诊断技能默认不改码、评审不改业务源码、brainstorming 收尾服从活动 flow。沿用现有路由口径，不改 `flow-02` 的切片与实现分工，不改 `flow-04`、`flow-08`、`flow-09` 的入口正文。

## Impact

- `skill/matt-pocock/diagnosing-bugs/SKILL.md`
- `skill/matt-pocock/diagnosing-bugs/discipline.md`
- `skill/matt-pocock/code-review/framework-rules.md`
- `skill/superpowers/brainstorming/framework-rules.md`
- `skill/superpowers/brainstorming/SKILL.md` 的架构路径收尾句
- `tests/test_flow_routers.py`
- 不改人格标记、`flow-02` 委派句、宿主安装器，不同步主规格，不归档，不写知识库。
