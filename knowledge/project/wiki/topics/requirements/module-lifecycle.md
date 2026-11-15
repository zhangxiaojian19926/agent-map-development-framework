---
type: requirement
artifact_kind: requirement
created: 2026-11-15
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/module-lifecycle/spec.md
source_sha256: b7bce4fd51e810d454c1e64d2c05861a59a0a79bf1fcf340b937cb00567b0b73
problem_id:
sources:
  - openspec/specs/module-lifecycle/spec.md
---

# module-lifecycle 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/module-lifecycle/spec.md](../../../../../openspec/specs/module-lifecycle/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：在已确认的发现根之内，名为 `.worktrees` 的目录及其整棵子树不得进入模块目录，其中的源文件不得计入任何模块。分析会话记录的排除目录名单与发现所用的排除集合相同，且包含 `.worktrees`。源码发现不读取 `.gitignore` 来决定跳过哪些目录。既有的 clone/add/sync、越界拒绝、身份归属与生命周期要求保持不变。
- 验证或批准依据：来源规格已同步，变更 `exclude-worktrees-from-module-discovery` 的任务已全部完成。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。发现根本身名为 `.worktrees` 时，现有剪枝只作用于扫描中遇到的子目录名。
- 触发条件：已确认的发现根下出现名为 `.worktrees` 的目录时。
- 不适用条件：不适用于目录名不是 `.worktrees` 的其他工作树，也不适用于把 `.gitignore` 当作排除依据。
- 被排除的解释：本页不主张删除采用方仓库里的工作树，也不主张把 `.superpowers` 加入排除集合。
- 来源哈希：`b7bce4fd51e810d454c1e64d2c05861a59a0a79bf1fcf340b937cb00567b0b73`
