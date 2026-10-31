## Why

两个上游技能族用两种方式声明"这个技能只能由人显式调用"：Claude Code 读 frontmatter 的 `disable-model-invocation: true`，Codex 读 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false`。**只写一侧，等于让某个宿主能自主触发而另一个不能。**

这不是假想问题，本轮引入技能时就发生了两件事：

1. 六个引入的技能漏带了 `agents/openai.yaml`。其中五个上游本来就是模型调用型，漏带只丢了 Codex 的显示名与简介，行为没变；但 **`to-tickets` 上游两侧都是用户调用型**——漏带之后 Claude 侧仍读 frontmatter 判定为用户调用，Codex 侧却看不到声明，判定为模型调用。
2. 更要命的是，`to-tickets` 在本框架是**计划阶段的主技能**。阶段路由由 Agent 按流程推进，如果这个技能在宿主侧是"只能由人点名"，那么计划阶段一到，Agent 根本够不着它——流程会静默降级。

## What Changes

- 为 `code-review`、`codebase-design`、`diagnosing-bugs`、`tdd`、`writing-for-agents` 补上上游的 `agents/openai.yaml`，恢复 Codex 侧的显示名与简介。
- 把 `to-tickets` 改为**模型调用型**：frontmatter 去掉 `disable-model-invocation`，`agents/openai.yaml` 声明允许隐式调用。这是本地改编，需在第三方声明里记录。
- `tools/check-framework` 增加**形态一致性检查**：一个技能若只对一侧声明形态，检查失败。
- `docs/framework/skill-policy.md` 写清两种形态、声明位置、一致性要求，以及阶段路由点名的技能必须能被 Agent 自主到达。

## Capabilities

### New Capabilities

- `invocation-forms`: 规定技能调用形态的声明方式、跨宿主一致性要求、阶段技能与参考技能的形态约束，以及形态不一致时的检查行为。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 新增 6 份 `agents/openai.yaml`（5 份为上游原文，1 份为 to-tickets 的本地改编）。
- 修改 `skill/matt-pocock/to-tickets/SKILL.md` 的 frontmatter，去掉用户调用声明。
- 修改 `tools/check-framework`，增加形态一致性检查并扩展通过信息。
- 新增 `tests/test_invocation_forms.py`。
- 更新 `docs/framework/skill-policy.md`、`docs/integrations.md`、`README.md` 与 `THIRD_PARTY_NOTICES.md`。
- 技能入口总数不变（28），不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
