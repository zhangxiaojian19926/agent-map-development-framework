# invocation-forms Specification

## Purpose

规定技能调用形态的声明方式与跨宿主一致性要求，让同一个技能在每个宿主上都以同一种方式被触达，并防止阶段路由点名的技能因形态声明缺失而静默失效。

## Requirements

### Requirement: 形态对每个宿主都声明

系统 SHALL 让每个技能对每个宿主声明其调用形态。Claude Code 侧由技能 frontmatter 的 `disable-model-invocation: true` 声明，Codex 侧由 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` 声明。系统 MUST NOT 只对一侧声明形态。系统 SHALL 在两侧都不声明时按模型调用型处理。

#### Scenario: 用户调用型技能两侧一致

- **WHEN** 一个技能对某个宿主声明为用户调用型
- **THEN** 它对另一个宿主也声明为用户调用型

#### Scenario: 两侧都不声明

- **WHEN** 一个技能没有任何形态声明
- **THEN** 它在所有宿主上都是模型调用型，且不构成不一致

#### Scenario: 只声明一侧被发现

- **WHEN** 一个技能只对一侧声明形态
- **THEN** 分发结构检查失败并指出该技能

### Requirement: 阶段技能必须能被自主到达

系统 SHALL 让每条工作流路由为模型调用型，使进入该工作流不依赖用户点名路由技能。系统 SHALL 让阶段路由表点名的成员技能由对应路由在同一次任务中点名读取；成员技能不必各自出现在宿主发现目录。系统 SHALL 允许参考型与编排型技能声明为用户调用型。系统 MUST NOT 因此把 `retro` 改成模型调用型。

#### Scenario: 阶段技能在计划阶段被触达

- **WHEN** 流程进入计划阶段，且宿主发现目录含有 `flow-02`
- **THEN** 模型可以选中 `flow-02`，其正文点名 `to-tickets` 与 `plan-format.md`，用户不必另外点名该成员技能

#### Scenario: 成员技能不各自占发现目录

- **WHEN** 检查宿主发现目录和路由正文
- **THEN** 发现目录含有十五条路由，成员技能只出现在路由点名的原路径中

#### Scenario: 复盘不被自动触发

- **WHEN** 会话结束但用户没有要求复盘
- **THEN** 该复盘技能不被自动触发

### Requirement: 形态规则可被检查

系统 SHALL 在分发结构检查中校验形态一致性，并 SHALL 具备能证明该校验会失败的测试。

#### Scenario: 检查通过

- **WHEN** 运行分发结构检查
- **THEN** 检查通过，且通过信息说明已校验形态一致性

#### Scenario: 校验有效性可证

- **WHEN** 用一个只声明单侧形态的构造样例运行一致性检查
- **THEN** 检查报告该技能形态不一致
