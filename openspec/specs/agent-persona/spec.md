# agent-persona Specification

## Purpose

规定工程壳主 Agent 的常驻人格如何进入托管入口与运行包，以及 Claude 与 CodeBuddy 只安装哪些只读子代理。目的是让每次会话都执行同一份结果与证据协议，同时不另建技能、不改 doctor 词表。

## Requirements

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

### Requirement: 运行包 AGENTS 以同一人格开头并保留阶段表

系统 SHALL 让框架仓库 `AGENTS.md` 用 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 包住与 `docs/framework/agent-persona.md` 相同的人格正文，并把该文件整份复制为业务工程的 `.agent-framework/AGENTS.md`。复制后的文件 MUST 以同一份人格开头，MUST 仍包含现有阶段路由表。两处人格正文 MUST 一致。

#### Scenario: 标记内正文与唯一来源一致

- **WHEN** 比较框架 `AGENTS.md` 中 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间的正文和 `docs/framework/agent-persona.md`
- **THEN** 两处正文相同

#### Scenario: 运行包保留阶段表

- **WHEN** 初始化把框架 `AGENTS.md` 复制到 `.agent-framework/AGENTS.md`
- **THEN** 该文件以人格正文开头，并且仍含有 DISCOVERY 到 KNOWLEDGE 的阶段路由表

### Requirement: Claude 与 CodeBuddy 只安装三个指定只读子代理

系统 SHALL 为 Claude Code 与 CodeBuddy 安装且仅安装三个命名子代理：`uap-investigator`、`uap-challenger`、`uap-verifier`。三者 MUST NOT 具备 `Write`、`Edit` 或 `MultiEdit`。investigator 与 challenger MUST 只有 `Read`、`Grep`、`Glob`；verifier MAY 另有 `Bash` 以便跑已有测试和命令。系统 MUST NOT 安装 orchestrator、implementer、architect、decision-designer 或 range-scout。宿主未安装这些子代理时，主 Agent MUST 自己完成对应工作并写明未委派。

#### Scenario: 只出现三个命名子代理

- **WHEN** 对目标工程应用 Claude Code 或 CodeBuddy 的宿主安装
- **THEN** 安装结果包含且仅包含 `uap-investigator`、`uap-challenger`、`uap-verifier` 三个子代理文件，名称保持不变

#### Scenario: 子代理没有写入工具

- **WHEN** 检查已安装的三个子代理正文
- **THEN** 三者都没有 `Write`、`Edit` 或 `MultiEdit`；investigator 与 challenger 没有 `Bash`；verifier 可以有 `Bash`

### Requirement: 不生成 CODEBUDDY.md

系统 SHALL NOT 在目标工程写入 `CODEBUDDY.md`。CodeBuddy 的项目记忆 MUST 继续使用项目根 `AGENTS.md`。CodeBuddy 宿主安装 MUST NOT 要求 hooks 能力，只要求 `write`。

#### Scenario: 安装 CodeBuddy 不写 CODEBUDDY.md

- **WHEN** 对目标工程应用 CodeBuddy 宿主安装
- **THEN** 目标工程没有 `CODEBUDDY.md`，项目根 `AGENTS.md` 仍是项目记忆入口

#### Scenario: CodeBuddy 不要求 hooks

- **WHEN** 仅授予 `write` 能力并应用 CodeBuddy 宿主安装
- **THEN** 安装可以进行，不因缺少 hooks 被拒绝

### Requirement: doctor 词表不增加验收四态

系统 SHALL NOT 把人格里描述单次交付的通过、部分完成、失败、阻断写入 `docs/guide/framework-model.md` 的状态词典。doctor 的 `READY`、`PARTIAL`、`BLOCKED` MUST 继续只描述工程接入。人格 MUST NOT 把 doctor 的工程接入状态当成单次交付结论。

#### Scenario: 状态词典保持原词

- **WHEN** 检查 `docs/guide/framework-model.md` 已发布状态词典
- **THEN** 词典不新增人格专用的 `PASS`、`PARTIAL`、`FAIL`、`BLOCKED` 作为单次交付状态码，doctor 的 `READY` / `PARTIAL` / `BLOCKED` 含义不变

### Requirement: 不新建技能

系统 SHALL NOT 为本能力新增技能，也 MUST NOT 修改 `openspec/specs/skill-routing/spec.md`。读取 `tdd`、`code-review` 等阶段技能 MUST 仍由主 Agent 执行，不得把八个 UAP 角色登记成子代理或技能。

#### Scenario: 无新技能且路由规格不变

- **WHEN** 完成本变更的文件与规格核对
- **THEN** `skill/` 没有因本能力新增的技能，`openspec/specs/skill-routing/spec.md` 内容与本变更前一致
