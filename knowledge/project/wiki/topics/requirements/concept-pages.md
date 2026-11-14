---
type: requirement
artifact_kind: requirement
created: 2026-11-14
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/concept-pages/spec.md
source_sha256: ddc5184b463a95a82c560441357d2cd77af3eb4ec6eedc13ef9d76a0ccd39a1d
problem_id:
sources:
  - openspec/specs/concept-pages/spec.md
---

# concept-pages 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/concept-pages/spec.md](../../../../../openspec/specs/concept-pages/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：概念是可摄入的知识页种类，`artifact_kind` 为 `concept`，目录 `wiki/topics/concepts/`，与其他工程页共用同一份模板与前置字段。概念页必须声明 `source_path` 与 `source_sha256`，来源只能是项目术语表 `docs/project/GLOSSARY.md` 或已同步的能力规格，来源改动后能检出哈希失配。术语的定义仍留在术语表并由人工维护，概念页只承载扩展语义——适用条件、易混淆对象、状态作用域、工程映射、关键约束与验证入口——并通过来源路径与术语表互指，两边都不复制对方的内容，因此不产生第二真相源。
- 验证或批准依据：来源规格已同步，变更 `add-concept-pages-and-applicability` 获得单独的写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：工程需要一个概念已确定、且该术语的扩展语义值得被以后复用的项目时。
- 不适用条件：不适用于只在本工程外使用的通用词汇，也不适用于尚未确定含义的术语。
- 被排除的解释：本页不主张概念页可以替代术语表里的定义，也不主张它可以替代能力规格。
- 来源哈希：`ddc5184b463a95a82c560441357d2cd77af3eb4ec6eedc13ef9d76a0ccd39a1d`
