## MODIFIED Requirements

### Requirement: 完成的 change 必须同步并归档

系统 SHALL 要求任务已全部完成的 change 把它声明的能力规格同步进 `openspec/specs/`，留下符合 `completion-knowledge-ingest` 的知识回执，再把 change 移入 `openspec/changes/archive/`。系统 SHALL NOT 让一个完成的 change 长期留在活动区而不同步。系统 SHALL NOT 在知识回执缺失时把该 change 视为可以归档。

#### Scenario: 能力规格缺失

- **WHEN** 一个 change 的任务已全部完成，但它的能力规格不在 `openspec/specs/` 里
- **THEN** 检查报出该 change 及其缺失的能力

#### Scenario: 已同步但未归档

- **WHEN** 一个 change 的任务已全部完成，能力规格已同步，知识回执已与页面相符，但它仍在活动区
- **THEN** 检查报出该 change 需要走归档流程

#### Scenario: 知识回执缺失

- **WHEN** 一个 change 的任务已全部完成且能力规格已同步，但知识回执缺失、页面不存在，或来源哈希不符
- **THEN** 检查报出该 change 的知识欠账，不把它报成可以归档
