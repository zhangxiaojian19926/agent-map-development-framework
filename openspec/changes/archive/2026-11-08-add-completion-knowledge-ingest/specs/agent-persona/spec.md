## MODIFIED Requirements

### Requirement: 托管段含人格且禁止自行改写

系统 SHALL 在业务项目根 `AGENTS.md` 的 `FRAMEWORK_ENTRY` 托管段中写入与 `docs/framework/agent-persona.md` 相同的人格正文，并保留现有英文操作句：读取 `.agent-framework/AGENTS.md`、任务入口和收尾运行只读 doctor、仅在结构变化时发布地图、实现走已批准的 OpenSpec 与 TDD、需求开发或问题验证完成后写入初始化知识库。系统 SHALL 在人格正文中禁止主 Agent 修改该托管段。人格、阶段表和子代理 MUST 只通过评审过的 OpenSpec 变更修改。人工改写或不完整的托管段 MUST 继续报 `RULE_CONFLICT` 且不得覆盖。系统 MUST NOT 在该操作句中要求对这两类完成再询问一次是否摄入。

#### Scenario: 托管段含人格与操作句

- **WHEN** 对目标工程执行 prepare 并生成根 `AGENTS.md` 托管段
- **THEN** `FRAMEWORK_ENTRY` 区块含有 `docs/framework/agent-persona.md` 的人格正文，并含有读取公共工作流、只读 doctor、地图发布条件、已批准 OpenSpec/TDD、以及完成后写入初始化知识库的英文操作句

#### Scenario: 禁止自行改写托管段

- **WHEN** 阅读托管段中的人格正文
- **THEN** 正文写明不得修改 `FRAMEWORK_ENTRY` 托管段，人格、阶段表和子代理只通过评审过的 OpenSpec 变更修改

#### Scenario: 人工改写仍报 RULE_CONFLICT

- **WHEN** 根 `AGENTS.md` 已有不完整或被人工改写的 `FRAMEWORK_ENTRY` 区块
- **THEN** 生成失败并报 `RULE_CONFLICT`，原文件内容不被覆盖
