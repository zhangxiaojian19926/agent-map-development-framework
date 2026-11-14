---
type: requirement
artifact_kind: requirement
created: 2026-11-14
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/knowledge-influence-tracking/spec.md
source_sha256: f7fca23050fbb32a7e2f4375d89e276d7e468f569aaa43ee4628d528fb14c06d
problem_id:
sources:
  - openspec/specs/knowledge-influence-tracking/spec.md
---

# knowledge-influence-tracking 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/knowledge-influence-tracking/spec.md](../../../../../openspec/specs/knowledge-influence-tracking/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：知识回执可以声明第二版结构 `knowledge-receipt/v2` 并记录 `influenced`，即这页知识改变了哪条断言、哪个文件、哪个 task。校验要求每条记录的页路径在同一张回执的页面清单里、task 标识在该 change 的任务清单里，对不上就报出；没有这一项时必须显式声明不适用并给出理由。第一版回执按引入前的规则判定，不追溯。doctor 的知识维度报告每个知识页的引用次数与从未被引用的页，让知识的投入产出可核算。诊断失败另需归属到内容、访问、验证、流程或方法其中一层——归属决定写到哪个知识库，归因决定该改哪一层。
- 验证或批准依据：来源规格已同步，变更 `add-knowledge-correction-and-influence` 获得单独的写入授权。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：一次 change 完成并留下知识回执，且这轮的知识确实改变了某个 task 的实现或断言时。
- 不适用条件：不适用于只做查询、纯文档或没有产生可复用知识的变更；这类变更应显式声明不适用并给出理由。
- 被排除的解释：本页不主张 `influenced` 证明知识在语义上正确——它证明声明的影响可被追溯，正确性仍是评审的判断。
- 来源哈希：`f7fca23050fbb32a7e2f4375d89e276d7e468f569aaa43ee4628d528fb14c06d`
