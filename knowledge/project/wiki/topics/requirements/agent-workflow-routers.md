---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/agent-workflow-routers/spec.md
source_sha256: 3df767eb824c31b3a4e2efcdf62d825cbd3e896197ac82d891384a0bd2b4b461
problem_id:
sources:
  - openspec/specs/agent-workflow-routers/spec.md
---

# agent-workflow-routers 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/agent-workflow-routers/spec.md](../../../../../openspec/specs/agent-workflow-routers/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：路由正文为每个已完成步骤写明下一项，不要求成员技能各自提示下一个技能。下一项取自该路由的顺序。新行为在用户选定集成方式后，下一项是 `openspec-sync-specs`。规格同步完成后，下一项是把该需求写入初始化知识库；该 change 含有已验证问题记录时同时写入问题页，然后留下知识回执。系统不再询问是否摄入。回执留下之后，下一项才是 `openspec-archive-change`。提交、推送和合并仍等待用户当次选择。`flow-10` 至 `flow-13` 完成后不点名下一个技能。
- 验证或批准依据：来源规格已同步，变更 `add-completion-knowledge-ingest` 获得单独的初始化与写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。change 仍在活动区，尚未归档。
- 来源哈希：`3df767eb824c31b3a4e2efcdf62d825cbd3e896197ac82d891384a0bd2b4b461`
