---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/change-lifecycle/spec.md
source_sha256: eb5bb15e4df40c875de0108bec97e8a80dbba8c7c4bc1972928e757424635a60
problem_id:
sources:
  - openspec/specs/change-lifecycle/spec.md
---

# change-lifecycle 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/change-lifecycle/spec.md](../../../../../openspec/specs/change-lifecycle/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：任务已全部完成的 change 必须先把声明的能力规格同步进 `openspec/specs/`，留下符合 `completion-knowledge-ingest` 的知识回执，再移入 `openspec/changes/archive/`。能力规格缺失时，检查报出该 change 及缺失的能力。规格已同步、回执与页面相符、但 change 仍在活动区时，检查报出它需要走归档流程。回执缺失、页面不存在或来源哈希不符时，检查报知识欠账，不把它报成可以归档。检查只读，不移动 change，也不合并规格。没有任务清单的 change 不报；声明跳过规格且任务已完成的 change 仍要归档。
- 验证或批准依据：来源规格已同步，变更 `add-completion-knowledge-ingest` 获得单独的初始化与写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。change 仍在活动区，尚未归档。
- 来源哈希：`eb5bb15e4df40c875de0108bec97e8a80dbba8c7c4bc1972928e757424635a60`
