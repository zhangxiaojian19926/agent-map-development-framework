---
type: requirement
artifact_kind: requirement
created: 2026-11-14
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/completion-knowledge-ingest/spec.md
source_sha256: 3a137926b7f80d2ec98dc60e62a025506c00b7a99791107bda2bc9a8defde60b
problem_id:
sources:
  - openspec/specs/completion-knowledge-ingest/spec.md
---

# completion-knowledge-ingest 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/completion-knowledge-ingest/spec.md](../../../../../openspec/specs/completion-knowledge-ingest/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：任务已全部勾完且能力规格已同步时，必须在归档前把该需求写成初始化知识库 alias `project`、目录 `knowledge/project/` 中的需求页。仍有未勾选任务时不写。已验证通过的问题在归档前写成同一库的问题页，页面标明 `EXTRACTED` 并引用验证记录；未验证修复、推测或只有计划的问题不写成已解决。临时规避必须写明根因未消除。问题页必须声明 `applies_when` 与 `not_applicable_when`，缺失任一项的页面不作为问题页进入知识回执。这两类完成直接写入，不再询问是否摄入。该授权不包含结晶、删除、新建知识库、修改 alias 注册表或推送。相同来源哈希不重复写。每个完成的 change 留下知识回执，列出页面路径、种类、来源路径和来源哈希；回执可以包含概念页，其来源只能是项目术语表或已同步的能力规格。回执声明第二版结构时必须记录 `influenced`，否则必须显式声明不适用并给出理由；声明第一版结构的回执按引入前的规则判定，不追溯。alias 或目录不存在时记为 `NOT_CONFIGURED`，检查不新建库，该 change 仍是欠账。本能力生效前已归档且没有回执的 change 不回溯。
- 验证或批准依据：来源规格已同步，变更 `add-concept-pages-and-applicability` 获得单独的写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：一次需求开发完成、且其能力规格已同步进 `openspec/specs/` 之后。
- 不适用条件：不适用于仍在活动区、任务未全部勾完的 change；结晶、删除、新建知识库、修改注册表与推送也不在这次写入里。
- 被排除的解释：本页不主张知识库存的是当前需求的权威来源——OpenSpec 规格始终优先，wiki 记的是已验证且以后仍值得复用的经验。
- 来源哈希：`3a137926b7f80d2ec98dc60e62a025506c00b7a99791107bda2bc9a8defde60b`
