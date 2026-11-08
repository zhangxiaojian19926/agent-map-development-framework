---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/agent-persona/spec.md
source_sha256: d22bf4518aa7cc1b0a02444ce5f7cf38d5235b073bfac7afb2a3199d46adbea3
problem_id:
sources:
  - openspec/specs/agent-persona/spec.md
---

# agent-persona 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/agent-persona/spec.md](../../../../../openspec/specs/agent-persona/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：业务项目根 `AGENTS.md` 的 `FRAMEWORK_ENTRY` 托管段必须写入与 `docs/framework/agent-persona.md` 相同的人格正文。操作句保留：读取公共工作流、任务入口和收尾运行只读 doctor、只在结构变化时发布地图、实现走已批准的 OpenSpec 与 TDD，以及需求开发或问题验证完成后写入初始化知识库。该操作句不得再要求对这两类完成询问是否摄入。主 Agent 不得修改托管段。人格、阶段表和子代理只通过评审过的 OpenSpec 变更修改。人工改写或不完整的托管段仍报 `RULE_CONFLICT`，且不得覆盖原文件。
- 验证或批准依据：来源规格已同步，变更 `add-completion-knowledge-ingest` 获得单独的初始化与写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。change 仍在活动区，尚未归档。
- 来源哈希：`d22bf4518aa7cc1b0a02444ce5f7cf38d5235b073bfac7afb2a3199d46adbea3`
