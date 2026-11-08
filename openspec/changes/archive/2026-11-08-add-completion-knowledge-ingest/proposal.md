## Why

需求开发完成和问题解决完成之后，知识库仍要等一次询问才写入。不回复就不写，完成门禁也不看知识页，所以初始化时建立的知识库不会跟着工程壳流程变完整。

## What Changes

- 需求开发完成时，把该需求的已同步规格写入初始化知识库的需求页。问题解决完成时，把该问题的已验证记录写入同一知识库的问题页。这两类不再逐次询问。
- **BREAKING**：知识政策里「每次询问、不回复就不写」不再覆盖这两类完成记录。结晶、删除、新建知识库、改注册表和推送仍要单独授权。
- 完成门禁在任务全部勾完时检查知识回执。没有回执、页面缺失或来源哈希不符，该 change 仍算欠账，不能当作已完成。
- `flow-02` 在规格同步之后、归档之前写入这两类页面并留下回执。归档不再询问是否摄入。
- 人格操作句从「问题解决后询问摄入」改为「需求或问题完成后写入初始化知识库」。托管段只通过本变更更新，不在实现时另改标记结构。

## Capabilities

### New Capabilities

- `completion-knowledge-ingest`: 需求与问题在完成后自动进入初始化知识库，并用回执证明写过。

### Modified Capabilities

- `change-lifecycle`: 任务已完成的 change 在同步规格和归档之外，还必须有知识回执。
- `project-closure-check`: 使用者项目的欠账检查同时报出缺失的知识回执。
- `agent-workflow-routers`: `flow-02` 归档后的下一项改为按回执写入，不再询问。
- `agent-persona`: 托管段中的摄入操作句改为完成后写入初始化知识库。

## Impact

- `docs/framework/knowledge-policy.md`、`docs/framework/development-workflow.md`、`docs/framework/agent-persona.md`、根 `AGENTS.md` 的人格段与阶段表。
- `skill/flows/flow-02` 与组合清单中的下一项。
- `tools/framework_core/closure.py`、`tools/check-changes`，以及使用者项目的同一欠账判定。
- 初始化知识库只使用已有的 `knowledge/project/` 与 alias `project`。没有注册表时记为 `NOT_CONFIGURED`，不新建库。
- 已归档且没有回执的历史 change 不回溯。本变更不推送知识库。
