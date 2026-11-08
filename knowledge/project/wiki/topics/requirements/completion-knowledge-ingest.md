---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/completion-knowledge-ingest/spec.md
source_sha256: 7b0e91a2e8de63ffebd75ccbf8fda8e4588f767f414c3672f5f8896946d1be87
problem_id:
sources:
  - openspec/specs/completion-knowledge-ingest/spec.md
---

# completion-knowledge-ingest 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/completion-knowledge-ingest/spec.md](../../../../../openspec/specs/completion-knowledge-ingest/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：任务已全部勾完且能力规格已同步时，必须在归档前把该需求写成初始化知识库 alias `project`、目录 `knowledge/project/` 中的需求页。仍有未勾选任务时不写。已验证通过的问题在归档前写成同一库的问题页，页面标明 `EXTRACTED` 并引用验证记录；未验证修复、推测或只有计划的问题不写成已解决。临时规避必须写明根因未消除。这两类完成直接写入，不再询问是否摄入。该授权不包含结晶、删除、新建知识库、修改 alias 注册表或推送。相同来源哈希不重复写。每个完成的 change 留下知识回执，列出页面路径、种类、来源路径和来源哈希。alias 或目录不存在时记为 `NOT_CONFIGURED`，检查不新建库，该 change 仍是欠账。本能力生效前已归档且没有回执的 change 不回溯。
- 验证或批准依据：来源规格已同步，变更 `add-completion-knowledge-ingest` 获得单独的初始化与写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。change 仍在活动区，尚未归档。
- 来源哈希：`7b0e91a2e8de63ffebd75ccbf8fda8e4588f767f414c3672f5f8896946d1be87`
