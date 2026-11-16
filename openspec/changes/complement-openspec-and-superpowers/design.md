## Context

见 [proposal.md](proposal.md) 的前提与结论。本设计不另起流程。实施只改提案 Impact 点名的事实源，并让路由正文、阶段表、流程正文和四份技能原文表达同一条链。

## Goals / Non-Goals

**Goals:**

- `combinations.json` 里 `flow-02` 对象经现有渲染得到的正文，与 `AGENTS.md` 第 2 节、`docs/framework/development-workflow.md` 的对应步骤、四份技能原文，表达提案已经写明的那条链。
- `tasks.md` 只有 `to-tickets` 一个作者。同一段源码只有 `tdd` 一个实现器。勾选只发生在该切片 `TASK_VERIFIED` 之后。

**Non-Goals:**

- 不改 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间的正文，不改 `docs/framework/agent-persona.md`。
- 不改其他 flow 对象，不改 `flow-01` 与 `flow-03` 到 `flow-15`。
- 不改 `closure.py`、`roster.json`、宿主安装器、`templates/host/agents/`、`change-lifecycle`、`agent-persona` 规格、`README.md` 的安装事实句。
- `mentions` 保持原集合，因此不改 `catalog.json` 和 `docs/guide/from-zero-to-one.md` 的 flow-02 技能列。
- 不写知识库内容，不归档，不提交，不推送。不把 `skip_specs` 写入 `.openspec.yaml`。

## Decisions

1. 正文事实源是 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的对象。改完后用现有 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。不手改出一份与清单不同的正文。
2. 阶段表只改 `AGENT_PERSONA_END` 之后的第 2 节。分工句按提案切分线改写，不再把宏观任务状态和实施计划写成两套账。表内顺序改为先同步、再把回执留在活动 change、再移动目录。
3. `development-workflow.md` 只改与旧链冲突的步骤：分工、发现技能、规格产物不含实现步骤、顺序执行、装载、收尾顺序。第 132–138 行的 `SPECS_SYNCED → KNOWLEDGE_RECEIPT → ARCHIVED` 保持不变，正文与图一致。
4. 四份技能只去掉第二作者和第二实现器。`openspec-propose` 在 proposal、delta spec、design 之后停止。`openspec-update-change` 只修订这三份已有产物。`openspec-apply-change` 只装载上下文。`executing-plans` 不成为实现器，产品名单不决定委派。
5. 诊断停在红信号、最小复现和根因。`code-review` 的发现写入交付报告，不往 `tasks.md` 追加切片。`plan-format.md` 的 Execution handoff 不是下一项。这些句子写进同一条链，不另建修复或评审流程。
6. 子代理是任何一个 coding agent 都可以有的能力。委派仍只在用户已授权且宿主提供子代理时发生。不改宿主安装器。
7. 勾选留在本活动 change 目录。知识回执和归档不在本次授权内，对应任务保持未勾选，避免完成检查把未授权的回执当成必须补写的欠账入口之外的实施。

## Risks / Trade-offs

- [以后的技能导入可能把实现循环写回去] → 规格里的单一作者和单一实现器是持续约束，不能只靠这一次导入后的措辞。
- [任务全部勾选且规格已同步后，完成检查才看 `knowledge-receipt.json`] → 回执与归档任务保持未勾选。不为了让检查变绿而写知识页或移动目录。
- [人若绕过路由提前移动目录，活动区检查就看不到回执] → 路由仍在回执留下且规格已同步之后才点名归档。不改归档技能的通用 CLI 步骤。
- [分发库 doctor 的既有退出码] → 不为此改工程。
