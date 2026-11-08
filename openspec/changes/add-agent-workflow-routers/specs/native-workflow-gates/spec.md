## ADDED Requirements

### Requirement: WF-09 宿主档案区分阻断与建议

系统 SHALL 为 `agent-workflow-routers` 名册中的每个宿主记录能力类：可阻断或只建议。可阻断 MUST 只适用于档案中已有拦截载体的宿主。只建议宿主 MUST 输出共享流程判定和缺口，MUST NOT 声称宿主已阻断工具调用。`codebuddy` MUST 保持无项目钩子。

#### Scenario: 只建议宿主不报告已阻断

- **WHEN** `codebuddy`、`trae`、`lingma`、`github-copilot`、`windsurf`、`grok` 或 `copilot-cli` 上请求写入业务源码且批准缺失
- **THEN** 流程判定给出缺失项，宿主执行轴不是已阻断，缺口写明该宿主不能请求原生拦截

#### Scenario: DeepSeek 未挂载钩子桥时不报告已阻断

- **WHEN** `deepseek-harness` 已安装 `.dsh/skills/flow-*` 与 `.dsh/hooks.json`，但 profile 没有把 `configPath` 指向该文件
- **THEN** 流程判定可以给出缺失项，宿主执行轴不是已阻断

#### Scenario: CodeBuddy 仍无钩子

- **WHEN** 对 `codebuddy` 执行宿主安装
- **THEN** 不生成项目钩子和 `CODEBUDDY.md`

### Requirement: WF-10 安装通过与现场拦截分轴

系统 SHALL 把路由或钩子文件的安装结果放在安装事实中，把真实会话的拦截结果放在宿主执行轴。文件与规范一致且没有真实会话时，宿主执行轴 MUST 为 `NOT_RUN`。只有真实工具调用被拒绝且目标文件内容保持一致时，该入口才可记为已拦截。CLI、账号或模型不可用 MUST 记为 `NOT_RUN` 或 `INFRA_ERROR`。

#### Scenario: 钩子文件存在仍是未运行

- **WHEN** `codex` 或 `gemini-cli` 的已记载钩子载体已写入目标项目，但没有真实会话
- **THEN** 宿主执行轴为 `NOT_RUN`，不得写成已阻断

#### Scenario: 真实拒绝才改变执行轴

- **WHEN** `claude-code` 或 `qwen-code` 的已认证写工具在真实会话中被拒绝，且目标文件哈希不变
- **THEN** 该入口的宿主执行轴记为已拦截，交付资格轴仍按是否实际验收单独记录

### Requirement: WF-11 拒绝理由指向当前路由

系统 SHALL 让可阻断宿主的拒绝理由包含当前应读取的 `flow-*` 路径。已认证工具名 MUST 保持该宿主既有列表；未认证工具名 MUST 记为未覆盖。全局技能被先读取时，拒绝理由仍 MUST 指向项目路由，而不是全局技能的下一步。

#### Scenario: 拒绝理由含路由路径

- **WHEN** 可阻断宿主拒绝一次缺少批准的业务写入
- **THEN** 返回给模型的理由包含对应 `flow-*` 路径和缺失项

#### Scenario: 未认证工具不扩写覆盖

- **WHEN** 工具名不在该宿主已认证的读写列表中
- **THEN** 覆盖记为未认证，理由不声称该工具已被这个门禁拦截
