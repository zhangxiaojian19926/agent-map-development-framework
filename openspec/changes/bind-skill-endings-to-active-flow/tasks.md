## 1. 原文服从活动路由

- [x] 1.1 在 `tests/test_flow_routers.py` 锁住三句边界：诊断不应用修复、评审不改业务源码、brainstorming 的下一项由活动 flow 宣布且 `flow-08` 的停点优先。验证：先跑这三条断言，确认在改技能原文前失败。
- [x] 1.2 改 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 Phase 5 与同目录 `discipline.md`，使诊断技能不应用修复、不写生产代码。验证：`test_diagnosing_bugs_does_not_apply_a_fix` 通过，且第 8 行跳过句仍在。
- [x] 1.3 改 `skill/matt-pocock/code-review/framework-rules.md` 的重要发现句。验证：`test_review_does_not_edit_business_source` 与 `test_review_findings_are_not_appended_to_tasks` 通过，Minor 句仍只进交付报告，`flow-04` 与 `flow-09` 入口不变。
- [x] 1.4 改 `skill/superpowers/brainstorming/framework-rules.md`，并只改 `SKILL.md` 里把 `openspec-propose` 与 `to-tickets` 写成无条件收尾的句子。验证：`test_brainstorming_next_item_is_announced_by_the_active_flow` 通过，`flow-02` 的规格落点仍在，`flow-08` 正文未改。

## 2. 验证与收尾

- [x] 2.1 跑 `python3 -m unittest discover -s tests`、`python3 tools/check-framework`、`python3 tools/check-changes`、`openspec validate --all --strict`，以及 `python3 tools/framework doctor --target . --summary`。指纹失败时用 `python3 tools/update-manifest`，不手改哈希。验证：前四条退出码为 0；`test_persona_block_matches_source_and_status_dictionary_stays_put` 通过；doctor 退出码如实记录，退出码 5 不为此改工程。
- [ ] 2.2 把本 change 的需求页写入初始化知识库并留下 `knowledge-receipt.json`。未勾原因：本次没有回执授权，不写知识库，不同步主规格，不归档。
