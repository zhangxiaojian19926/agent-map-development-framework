# Proposal

## Why

框架引入上游技能时，一律保留上游原文字节不变，另写一层本地改编规则承载本框架自己的要求——seam 预确认、切片写入 change 的任务清单、两轴评审的规格来源、`INFRA_ERROR` 不是 RED、术语表落在项目文档、复盘按本框架的标准走。

这层改编共 **7 个规则文件、1010 行**，分布在 7 个技能里。每一份都声明"与上游冲突时以本地为准"，也都在 `THIRD_PARTY_NOTICES.md` 登记了来源。

**但没有任何指针指向它们。**

| 本地层 | 行数 | 被谁提到 |
|---|---|---|
| `tdd/discipline.md` | 157 | 无 |
| `tdd/test-quality.md` | 198 | 无 |
| `diagnosing-bugs/discipline.md` | 147 | 无 |
| `to-tickets/plan-format.md` | 187 | 无 |
| `code-review/framework-rules.md` | 115 | 无 |
| `retro/framework-rules.md` | 115 | 无 |
| `domain-modeling/framework-rules.md` | 91 | 无 |

AGENTS.md 不提，`docs/framework/skill-policy.md` 不提，能力规格也不提，上游 `SKILL.md` 里更没有链接——上游本来就不会引用框架自己加的文件。`THIRD_PARTY_NOTICES.md` 提到它们，但那是给人类看的法务声明，不是给 Agent 的指针。

**后果是规格与执行之间断开。** `openspec/specs/tdd-practice` 要求"在写测试之前先确定被测 seam 并与用户确认"，规则正文在 `tdd/discipline.md` 里；`plan-slicing` 要求切片与阻塞边写入 change 的任务清单，规则在 `to-tickets/plan-format.md`；`code-review-discipline` 要求规格来源是 OpenSpec change，规则在 `code-review/framework-rules.md`。Agent 走的是"读 AGENTS.md → 读 SKILL.md"，**永远不会走到本地层**。

于是规格说"SHALL 保留"，而"保留"的内容在执行时不存在。

同一批排查里还查出两处路由问题：

- `superpowers:dispatching-parallel-agents` 在 AGENTS.md 被归到 DISCOVERY，在 `docs/framework/development-workflow.md` 被归到 WORKSPACE——同一技能两处归属不同。
- `superpowers:using-superpowers` 是唯一没有任何活文档路由的技能。它的复盘记录早把它标为"每次对话都触发、永久占上下文"，处置被排期到"调用形态那一轮"，那一轮早已过去，决定至今没做。

## What Changes

- 新增 `skill/local-layers.json`，登记每个技能有哪些本地规则层是 Agent 执行时必须一并读取的。
- AGENTS.md 的阶段路由表与参考技能段，为带本地层的技能标出对应文件名——指针放在 Agent 必经的那张表上。
- `tools/check-framework` 新增校验：登记与磁盘一致，且登记的每个文件名在活文档里被提及，防止"登记了但仍然没人知道要读"。
- `superpowers:dispatching-parallel-agents` 的阶段归属统一到 WORKSPACE，与流程契约一致。
- 移除 `superpowers:using-superpowers` 的技能入口，保留它的 `references/`——`executing-plans` 与 `writing-skills` 这两份上游原文引用了那些平台适配文件，不能跟着断。
- 纠正维护者记录里上一轮基于不完整扫描给出的错误建议。

## Capabilities

### New Capabilities

- `local-layer-reachability`: 规定本框架自己的技能改编层必须可被执行它的 Agent 读到，并规定登记与检查方式。

### Modified Capabilities

- `skill-routing`: 把"技能在两处契约里的阶段归属必须一致"写进规格，并补上"技能被移除后其引用文件仍可解析"的边界。

## Impact

- 新增 `skill/local-layers.json`。
- 修改 `AGENTS.md`（阶段路由表两行、参考技能段一处）。
- 修改 `tools/check-framework`（新增 `skill_routing_errors` 与 `local_layer_errors`），修改 `tests/test_doc_contract.py`。
- 修改 `docs/framework/development-workflow.md`（WORKSPACE 行的技能表述）。
- 删除 `skill/superpowers/using-superpowers/SKILL.md`，保留其 `references/` 目录下的五个文件。
- 更新 `docs/maintainer/retro-findings.md`、`docs/maintainer/roadmap.md`、`CHANGELOG.md`。
- 不引入运行时依赖，不改变任何既有阶段的退出条件与交接结果。
