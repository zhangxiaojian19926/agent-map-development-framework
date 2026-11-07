## 1. 人格正文与托管段

- [x] 1.1 新增 `docs/framework/agent-persona.md`，写入 `7099de8` 短协议全文与壳绑定，并验证文件存在且含自改禁令
- [x] 1.2 用 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 把同一正文放到框架 `AGENTS.md` 开头，并验证阶段表仍在标记之后
- [x] 1.3 改 `tools/framework_core/generation.py`：托管段读取 `agent-persona.md` 再拼上现有英文操作句，并验证 `RULE_CONFLICT` 行为不变
- [x] 1.4 更新 `tests/test_bootstrap_generation.py`：断言托管段含人格与自改禁令、冲突用例仍报 `RULE_CONFLICT`、标记内正文与来源文件一致；运行 `python3 -B -m unittest discover -s tests -p test_bootstrap_generation.py`

## 2. 宿主只读子代理

- [x] 2.1 新增 `templates/host/agents/` 下 `uap-investigator.md`、`uap-challenger.md`、`uap-verifier.md`，并验证三者无 Write/Edit/MultiEdit，且 investigator/challenger 无 Bash
- [x] 2.2 改 Claude Code 安装器，从共享目录复制三个子代理到 `.claude/agents/`，并验证安装文件含 settings 与三个 `uap-*.md`
- [x] 2.3 新增 CodeBuddy 适配器并在 `hosts/base.py` 登记；`requires_hooks` 为假；验证只复制三个文件到 `.codebuddy/agents/`，不写 `CODEBUDDY.md`
- [x] 2.4 更新 `tests/test_host_claude_code.py` 并新增 `tests/test_host_codebuddy.py`，运行 `python3 -B -m unittest tests.test_host_claude_code tests.test_host_codebuddy`

## 3. 词表与技能边界

- [x] 3.1 核对 `docs/guide/framework-model.md` 状态词典未增加人格验收四态，并验证 `openspec/specs/skill-routing/spec.md` 与 `skill/` 未被本变更修改

## 4. 验收记录与归档

- [x] 4.1 写 `docs/verification/2026-11-07-universal-agent-protocol.md`，更新 README / CHANGELOG Unreleased / THIRD_PARTY_NOTICES，重算清单并跑六道门禁。只证明文件、安装和门禁。
- [x] 4.2 将 `agent-persona` 同步进 `openspec/specs/` 并按正常流程归档。真实项目闭环、知识回流与跨模型效果本期不证明，不得随归档勾成已完成。
