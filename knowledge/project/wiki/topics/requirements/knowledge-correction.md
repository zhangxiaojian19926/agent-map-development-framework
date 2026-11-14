---
type: requirement
artifact_kind: requirement
created: 2026-11-14
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/knowledge-correction/spec.md
source_sha256: f61864102c6092d50f2084d31e892091ca780c66f44c0ad1617de7a08098324b
problem_id:
sources:
  - openspec/specs/knowledge-correction/spec.md
---

# knowledge-correction 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/knowledge-correction/spec.md](../../../../../openspec/specs/knowledge-correction/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：知识页的状态在已批准、已验证与临时规避之外，还能表达被取代、撤回与待复核。状态转移有可核对的规则：被取代必须声明 `superseded_by` 指向真实存在的页，撤回必须声明 `retraction_reason`，两者都不得再被任何页的 `applies_when` 引用。进入待复核的页能列出引用它的下游，原始事件保留但不再作为已确认规则指导新任务。页面状态的声明处是知识库 schema，另有一条机器检查比对 schema 与代码接受的集合，避免两者漂移；页面状态不写进对外指南的框架状态词典，那本词典收的是框架自身的大写状态码。
- 验证或批准依据：来源规格已同步，变更 `add-knowledge-correction-and-influence` 获得单独的写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：一条已写入的结论被新的证据推翻、适用范围改变，或被另一条结论取代时。
- 不适用条件：不适用于尚未写入知识库的推测，也不适用于只是措辞需要调整而结论未变的页面。
- 被排除的解释：本页不主张撤回等于删除：原始事件与证据保留，只是不再作为已确认规则被引用。
- 来源哈希：`f61864102c6092d50f2084d31e892091ca780c66f44c0ad1617de7a08098324b`
