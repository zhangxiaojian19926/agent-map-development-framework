## 1. 先写会失败的位置测试

- [x] 1.1 在 `tests/test_bootstrap_generation.py` 的 `GenerationTests` 增加一条位置测试，关联 Requirement「运行包 AGENTS 以同一人格开头并保留阶段表」的 Scenario「阅读顺序位于标记之后且不进入人格来源」。断言固定句「标记内先读约束，再读交付姿态，再读工程壳闸门」在 `AGENT_PERSONA_END` 之后、`| 1. DISCOVERY |` 之前，且不在 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间，`docs/framework/agent-persona.md` 不含该句。此时尚未改 `AGENTS.md`，验证新测试失败；并验证 `test_framework_agents_persona_matches_source`、`test_prepare_managed_block_includes_persona_and_forbids_self_edit`、`test_persona_block_matches_source_and_status_dictionary_stays_put` 仍然通过。
  验证：在 `tests/` 运行 `python3 -B -m unittest` 上述四条。结果 `F...`，`Ran 4 tests`，`FAILED (failures=1)`。失败是 `assertIn`：固定句不在 `AGENT_PERSONA_END` 之后的正文里。

## 2. 插入接缝正文

- [x] 2.1 只把 `proposal.md` 中「将写入第 49 行的正文」那两段原样插入框架根 `AGENTS.md` 第 48 行 `<!-- AGENT_PERSONA_END -->` 与第 50 行 `# AGENTS.md — 公共开发流程入口` 之间，替换当前空行。同一 Scenario。不改标记内，不改 `docs/framework/agent-persona.md`，不改阶段表各行，不改 doctor 词、「简单任务直接完成」、委派句和第 47 行。不把接缝写进人格，不把两段合成一节，不改十五条 flow。验证新位置测试通过，且上列三条既有测试仍然通过。
  验证：同一条 `python3 -B -m unittest`。指纹刷新后结果 `....`，`Ran 4 tests`，`OK`。刷新前 `test_prepare_managed_block_includes_persona_and_forbids_self_edit` 因 `DISTRIBUTION_HASH_MISMATCH: AGENTS.md` 失败，没有改测试。

## 3. 核对指纹

- [x] 3.1 运行 `python3 tools/update-manifest`，只核对 `framework-manifest.json` 里 `AGENTS.md` 的指纹与改后文件一致。同一 Scenario。不把工作区里已有的 `.gitignore`、`tools/check-framework` 和归档文档改动纳入本 change，不去改那些文件。不提交，不 push。
  验证：`python3 tools/update-manifest` 后，文件 SHA-256 与清单 `files["AGENTS.md"]` 都是 `71c820b93a437561cebecb4c10e3558e55f746a6c3f43c6e7574f2cbc312a0c0`。清单不含 `.workflow-15-preview.html`。
