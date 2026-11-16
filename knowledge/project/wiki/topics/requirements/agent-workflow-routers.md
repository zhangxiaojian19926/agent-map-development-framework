---
type: requirement
artifact_kind: requirement
created: 2026-11-08
confidence: EXTRACTED
status: approved
module_ids: []
source_path: openspec/specs/agent-workflow-routers/spec.md
source_sha256: f8308e3f9003d8ffa9dc764d40aa6a736820aef63b66bfc63dfb27278547ffce
problem_id:
sources:
  - openspec/specs/agent-workflow-routers/spec.md
---

# agent-workflow-routers 需求

本页提取自已同步的能力规格，不是另一份验收标准。当前需求以来源规格为准。

## 记录

- 来源：[openspec/specs/agent-workflow-routers/spec.md](../../../../../openspec/specs/agent-workflow-routers/spec.md)
- 模块：工程壳公共规则，无业务模块
- 结论：已登记的 13 个宿主共用 `flow-02` 的新行为主路径。诊断停在红信号、最小复现和根因，回归测试和修复只由 `tdd` 写。规格只落 proposal、delta spec、design，不创建 `tasks.md`。切片正文只由 `to-tickets` 写入。`openspec-explore`、`executing-plans`、`openspec-apply-change` 退出必经，人点名仍可用，且不再改源码或写实现步骤。装载上下文是三步命令，下一项是 `tdd`。进入委派必须同时有用户授权和宿主子代理能力，否则主 Agent 自己做 `tdd` 和 `code-review` 并写明未委派。子代理是任何一个 coding agent 都可以有的能力，不以 Claude Code 与 CodeBuddy 的产品名单分流，也不为此修改宿主安装器。规格同步后写入需求页和适用问题页并留下回执，然后才归档。`AGENTS.md` 第 2 节与 `docs/framework/development-workflow.md` 与这条链一致，托管段正文不改。
- 验证或批准依据：来源规格已同步，变更 `complement-openspec-and-superpowers` 的实现任务已完成。置信度为 EXTRACTED。
- 限制：本页是规格摘要。OpenSpec 规格仍是当前需求。本变更没有 `verified-problem.json`，因此没有问题页。
- 触发条件：新行为要改行为、接口或验收，并走 `flow-02`。
- 不适用条件：只读审计、纯文档和既有规格修复不走这条新行为必经链。
- 被排除的解释：本页不把给 13 个宿主安装只读子代理文件写成进入委派的条件。
- 来源哈希：`f8308e3f9003d8ffa9dc764d40aa6a736820aef63b66bfc63dfb27278547ffce`
