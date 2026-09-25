## Purpose

让实际可调用的 Coding Agent 在项目边界内主动理解模块和跨模块协作，输出可追溯的结构化地图与文档，明确设计、静态证据、推理和运行验证的不同证明强度。

## ADDED Requirements

### Requirement: MAP-01 真实宿主调用和降级

系统 SHALL 首先实现 Codex CLI 适配和通用手动交接，检测可执行能力与认证可用性；技能文件或交接文件存在不能证明 Agent 已运行。

#### Scenario: MAP-01-AGENT

- 前置条件：所选 Agent 可执行且本次源码发送范围已确认
- **WHEN** 初始化器调度建图
- **THEN** 启动一次受控任务、验证结构化输出及证据；不授予全局或任意写权限
- 超时：Agent 默认 600 秒，可显式调整
- 环境与证据：Host：受控子进程；真实宿主：合成项目调用记录
- 异常分类：AGENT_FAILED / TIMEOUT

#### Scenario: MAP-01-MISSING

- 前置条件：所选 Agent 缺失、损坏或需要认证
- **WHEN** 执行接入
- **THEN** 返回 WAITING_AGENT 和恢复入口，不冒充一键完成、不修复全局安装
- 超时：15 秒
- 环境与证据：Host：损坏 CLI fixture
- 异常分类：WAITING_AGENT

### Requirement: MAP-02 证据关系与设计实际分离

系统 MUST 分开目录包含、构建依赖和运行接口关系；每条实际关系包含来源/目标、类型、证据位置、源码指纹、证据等级及运行验证状态。

#### Scenario: MAP-02-RELATION

- 前置条件：A 客户端与 B 路由存在静态匹配，无真实服务运行
- **WHEN** Agent 生成连接记录
- **THEN** 标 STATIC_SUPPORTED 且 runtime=NOT_RUN；仅同名符号不能确定连接，疑点标 INFERRED
- 超时：Agent 预算内
- 环境与证据：Host：已知真值 fixture、JSON 和引用校验
- 异常分类：INVALID_EVIDENCE / NEEDS_CONFIRMATION

#### Scenario: MAP-02-DESIGN

- 前置条件：批准设计连接 A-B，但实际只有 A-C
- **WHEN** 核对地图
- **THEN** 保留设计与实际两层并报告 SPEC_MISMATCH，不静默修改设计或伪造 B 的实现
- 超时：Agent 预算内
- 环境与证据：Host：双层地图和差异
- 异常分类：SPEC_MISMATCH

### Requirement: MAP-03 入口和文档所有权

系统 SHALL 根据真实入口生成模块 AGENTS 及项目地图，正确计算任意深度链接；已有人工文档不覆盖，未获第三方模块写权时使用项目侧入口。

#### Scenario: MAP-03-DOCS

- 前置条件：一个空入口模块、一个人工 AGENTS 模块、一个只读第三方模块
- **WHEN** 生成文档
- **THEN** 分别创建受管入口、提出合并差异、创建项目侧说明；人工文件指纹不变，所有链接有效
- 超时：60 秒（不含语义分析）
- 环境与证据：Host：多深度 fixture、文档快照和链接验证
- 异常分类：DOC_CONFLICT

### Requirement: MAP-04 更新范围与可信输入

系统 SHALL 以变更源码和受影响关系增量复核；模块文本、Agent 输出和克隆配置视为数据而非授权，生成结果须通过边界及引用验证再发布到受管文件。

#### Scenario: MAP-04-UNTRUSTED

- 前置条件：模块 README 或 Agent 输出要求执行越界命令或写入任意路径
- **WHEN** 分析并接受结果
- **THEN** 拒绝越界路径及指令，不调用业务安装/运行脚本；只有校验通过的结构化字段进入受管地图
- 超时：60 秒（不含 Agent）
- 环境与证据：Host：注入样例、命令审计、文件快照
- 异常分类：UNTRUSTED_OUTPUT / PATH_ESCAPE
