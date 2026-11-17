## ADDED Requirements

### Requirement: WR-23 成员技能原文服从活动路由

系统 SHALL 让会带走会话的成员技能原文服从活动 flow 已经写明的下一项，而不是只在路由正文里再重复一句。现有路由口径保持不变：`flow-02` 的切片正文仍只由 `to-tickets` 写，源码仍只由 `tdd` 写；`flow-04`、`flow-08`、`flow-09` 的入口句保持不变。

`diagnosing-bugs` 的技能原文 MUST 默认不改码。Phase 5 MUST NOT 应用修复，MUST NOT 写回归测试，也 MUST NOT 写生产代码。本阶段 MUST NOT 成为第二个实现器。技能中「有明确理由可跳过阶段」可以保留，但 Phase 5 MUST NOT 再是默认的改码步骤。根因之后的回归测试和修复 MUST 只在活动路由把 `tdd` 写成下一项时由 `tdd` 做。`flow-01` 与 `flow-14` 不把 `tdd` 写成下一项，所以这两条读完诊断就停。同目录 `discipline.md` 在查完根因后 MUST NOT 把「现在写代码」或「先写测试再修复」写成下一步。

`code-review` 的 `framework-rules.md` MUST NOT 授权评审改业务源码，也 MUST NOT 授权往 `tasks.md` 追加切片。发现 MUST 写入交付报告。活动路由把 `tdd` 写成下一项时，修改回到 `tdd`。`flow-04` 与 `flow-09` 没有这句，评审到报告为止。Minor 发现仍只写入交付报告，不往 `tasks.md` 追加切片。阅读已有 `tasks.md` 以核对切片 MUST 仍然允许。

`brainstorming` 的下一项 MUST 只由活动中的 flow 正文宣布。`flow-02` 宣布进入规格时才是 `openspec-propose` 或 `openspec-update-change`，然后再 `to-tickets`。`flow-08` 已宣布停在设计对话、不创建 OpenSpec change、不把 `openspec-propose` 或 `to-tickets` 当作下一项，这句优先，不能被「改行为、接口或验收就进入 propose / to-tickets」盖过。上游 `SKILL.md` 架构路径第 6–9 步把 `openspec-propose` 和 `to-tickets` 写成收尾时，该收尾不是下一项，除非活动 flow 点名它们。

#### Scenario: 诊断技能默认不改码

- **WHEN** 读取 `diagnosing-bugs` 的 Phase 5 与同目录 `discipline.md`
- **THEN** 原文不应用修复，也不写生产代码；查完根因后不把「现在写代码」或「先写测试再修复」写成下一步；回归测试和修复只在活动路由把 `tdd` 写成下一项时由 `tdd` 做；`flow-01` 与 `flow-14` 读完诊断就停

#### Scenario: 评审不改业务源码

- **WHEN** 读取 `code-review` 的 `framework-rules.md` 中重要发现的闭合句
- **THEN** 评审不改业务源码，不往 `tasks.md` 追加切片，发现写入交付报告；活动路由把 `tdd` 写成下一项时修改回到 `tdd`；`flow-04` 与 `flow-09` 没有这句，评审到报告为止；Minor 句仍只写入交付报告

#### Scenario: brainstorming 收尾服从活动 flow

- **WHEN** 读取 `brainstorming` 的 `framework-rules.md`，且活动 flow 为 `flow-08`
- **THEN** 下一项只由活动中的 flow 正文宣布；`flow-08` 停在设计对话、不创建 OpenSpec change、不把 `openspec-propose` 或 `to-tickets` 当作下一项，这句优先；上游架构路径收尾不是下一项，除非活动 flow 点名它们

#### Scenario: flow-02 的规格落点仍在

- **WHEN** 活动 flow 为 `flow-02`，且它宣布进入规格
- **THEN** 下一项是 `openspec-propose` 或 `openspec-update-change`，然后再 `to-tickets`；切片正文仍只由 `to-tickets` 写，源码仍只由 `tdd` 写
