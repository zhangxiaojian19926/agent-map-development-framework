---
type: requirement
artifact_kind: requirement
created: 2026-11-14
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/knowledge-applicability/spec.md
source_sha256: da6fc288a1e3fb4fb49314b8199b5a62882b011dfb205d88d35e8108a70128bd
problem_id:
sources:
  - openspec/specs/knowledge-applicability/spec.md
---

# knowledge-applicability 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/knowledge-applicability/spec.md](../../../../../openspec/specs/knowledge-applicability/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：知识页可以声明 `applies_when` 与 `not_applicable_when`，另有 `preconditions`、`confusable_with`、`supersedes`、`superseded_by`、`derived_from`、`affects` 六个可选字段。结构校验按页面种类分别判定必填：`problem` 与 `concept` 类必须有非空 `applies_when`，`problem` 类还必须有非空 `not_applicable_when`，`requirement` 类不强制。仍留着 `{{占位符}}` 的字段算作未填。新规则只对新对象生效，引入之前已存在的知识页不因缺少这些字段而失效。
- 验证或批准依据：来源规格已同步，变更 `add-concept-pages-and-applicability` 获得单独的写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：写入一条会被以后复用的结论时——问题页与概念页必须说清它在什么前提下成立、什么情况下不能用它。
- 不适用条件：不适用于需求页：需求属于某一次变更的要求，不是可以在该变更之外召回的结论。
- 被排除的解释：本页不主张适用条件能替代验证；它只约束结论可以被召回的条件，不证明结论为真。
- 来源哈希：`da6fc288a1e3fb4fb49314b8199b5a62882b011dfb205d88d35e8108a70128bd`
