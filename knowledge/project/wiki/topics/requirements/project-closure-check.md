---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/project-closure-check/spec.md
source_sha256: 55b254017dcd0bd07072fb41d8dec3f07f57e56f947c27d432d332fc2181cb29
problem_id:
sources:
  - openspec/specs/project-closure-check/spec.md
---

# project-closure-check 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/project-closure-check/spec.md](../../../../../openspec/specs/project-closure-check/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：使用者项目的欠账检查随公共包送达，并与公共壳使用同一份只读判定。同一份报告同时列出活动 change 的知识回执欠账，包括回执缺失、回执指向的页面不存在，以及来源哈希不符。默认写出报告并以成功状态退出；严格模式以失败状态退出；两种模式的欠账清单一致。该检查不创建知识库、不写入知识页、不移动 change。本能力生效前已经归档且没有回执的 change，不被这份报告当成欠账。
- 验证或批准依据：来源规格已同步，变更 `add-completion-knowledge-ingest` 获得单独的初始化与写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。change 仍在活动区，尚未归档。
- 来源哈希：`55b254017dcd0bd07072fb41d8dec3f07f57e56f947c27d432d332fc2181cb29`
