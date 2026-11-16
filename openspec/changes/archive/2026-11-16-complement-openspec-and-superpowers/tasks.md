## 1. 路由正文

- [x] 1.1 只改 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的对象，再用现有渲染写出 `skill/flows/flow-02/SKILL.md`。验证：`distribution_errors` 为空，渲染正文含新链句子，且不再含旧的下一项句子；其他 flow 对象与 `mentions` 不变。

## 2. 阶段表与流程正文

- [x] 2.1 改 `AGENTS.md` 第 2 节的分工句和阶段表，使顺序先同步、再留回执、再移动目录。验证：`<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 仍在，标记内字节与改前相同，`| 1. DISCOVERY |` 在标记之后。
- [x] 2.2 改 `docs/framework/development-workflow.md` 里与旧链冲突的分工、发现、规格产物、顺序执行、装载和收尾步骤。验证：旧链句子消失，新链句子在，图仍是 `SPECS_SYNCED → KNOWLEDGE_RECEIPT → ARCHIVED`，且与阶段表的技能落点一致。

## 3. 技能原文

- [x] 3.1 改 `skill/openspec/openspec-propose/SKILL.md`：proposal、delta spec、design 之后停止，不创建 `tasks.md`，下一项改为 `to-tickets`。验证：正文不再把 `tasks.md` 列为实现步骤，也不再把 `openspec-apply-change` 写成完成后的实现入口。
- [x] 3.2 改 `skill/openspec/openspec-update-change/SKILL.md`：只修订已有 proposal、delta spec、design；不写实现步骤，不创建 `tasks.md`。验证：正文不再建议用 apply 把 delta 写进源码。
- [x] 3.3 改 `skill/openspec/openspec-apply-change/SKILL.md`：只装载上下文，不改业务源码，不在 `TASK_VERIFIED` 之前勾选。验证：正文不再要求对每个未完成任务改码并立即勾选。
- [x] 3.4 改 `skill/superpowers/executing-plans/SKILL.md`：不成为实现器，产品名单不再决定是否改走委派。验证：正文不再按产品名单分流，也不再逐步改码并标完成。

## 4. 验证

- [x] 4.1 跑 `openspec validate complement-openspec-and-superpowers --type change --strict --no-interactive`，退出码为 0。
- [x] 4.2 跑 `tests/test_flow_routers.py` 与 `python3 -m unittest discover -s tests`，失败则修到通过，不降低既有断言。
- [x] 4.3 跑 `python3 tools/check-framework`。若只因指纹或新文件未登记失败，用 `python3 tools/update-manifest` 刷新或按现有流程登记，再跑到通过。不手改哈希，不削弱检查。
- [x] 4.4 跑只读 `python3 tools/framework doctor --target . --summary`。分发库退出码 5 保持原样，不为此改工程。
- [x] 4.5 规格同步后把需求页写入 alias `project`，回执留在活动 change 的 `knowledge-receipt.json`。检查能看见且可接受后再归档。验证：`knowledge_receipt_detail` 为空，目录随后进入 `openspec/changes/archive/`。
