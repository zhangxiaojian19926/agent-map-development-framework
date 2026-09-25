## Purpose

让用户在目标工程尚不存在时，仅提供模块名称与仓库地址的键值对或全新需求，即可由当前 Coding Agent 接管初始化，同时保持输入可追溯、私有资料隔离和明确的操作边界。

## ADDED Requirements

### Requirement: IN-01 命名模块输入

系统 SHALL 接受 PROJECT-START.md 模块区块或裸键值对文本，支持名称 = URL 和名称: URL（含全角冒号）；保持每一对名称与完整 URL 的对应关系，不要求用户填写执行 JSON、hash 或运行命令。

#### Scenario: IN-01-PAIRS

- 前置条件：有当前初始化授权和明确工作区。
- **WHEN** 输入三个名称与 URL，URL含 HTTPS 或 SSH 冒号
- **THEN** 得到三个对应模块，URL不被截断，名称不用仓库basename替换
- 超时：10秒。
- 证据：Host；解析结果和计划。
- 异常分类：INVALID_INPUT。

#### Scenario: IN-01-BARE

- 前置条件：未指定元信息。
- **WHEN** 输入只有中文名称与 URL的文本
- **THEN** 按已有命名模块工程处理，不把中文键当未知配置
- 超时：10秒。
- 证据：Host；解析结果。
- 异常分类：INVALID_INPUT。

### Requirement: IN-02 无效输入先拒绝

系统 MUST 在网络与目标写入前拒绝重复或等价名称、非法目录名称、空URL、凭据URL和歧义行；不得由字典覆盖、静默改名或回退为新工程。

#### Scenario: IN-02-DUP

- 前置条件：目标目录尚不存在。
- **WHEN** 输入同名不同URL或大小写/Unicode等价名称
- **THEN** 列出冲突行；无clone，无目标目录生成
- 超时：10秒。
- 证据：Host；文件树和执行器调用记录。
- 异常分类：NAME_CONFLICT。

#### Scenario: IN-02-PATH

- 前置条件：目标位于获准工作区。
- **WHEN** 输入 ../outside、路径分隔符、保留名、空URL或带密码URL
- **THEN** 拒绝且不输出密码，不发生越界写入
- 超时：10秒。
- 证据：Host；错误报告和文件树。
- 异常分类：INVALID_INPUT。

### Requirement: IN-03 全新需求分流

系统 SHALL 在没有模块仓库表但存在新需求时走基础准备，不要求仓库、分支、模块URL或已批准业务实施计划；坏的模块表 MUST NOT 被视为空新工程。

#### Scenario: IN-03-NEW

- 前置条件：工作区安全且有初始化授权。
- **WHEN** 输入项目名称和目标、仓库暂无
- **THEN** 基础准备可完成，业务设计未批准，不下载、不创建Git或远程
- 超时：30秒。
- 证据：Host；生成文件清单和状态。
- 异常分类：INFRA_ERROR。

#### Scenario: IN-03-BROKEN

- 前置条件：模块区块非空。
- **WHEN** 输入一条格式错误的模块行
- **THEN** 报告行号，停止获取；不切换新工程
- 超时：10秒。
- 证据：Host；结果和零网络调用记录。
- 异常分类：INVALID_INPUT。

### Requirement: IN-04 输入保存与权限隔离

系统 SHALL 在目标外且不属于公共分发的获准启动区保存输入快照、指纹、目标绑定与阶段记录；记录 MUST NOT 被当作永久授权。公开分发不得携带真实项目输入或秘密。

#### Scenario: IN-04-PERSIST

- 前置条件：目标工程不存在，启动区获准。
- **WHEN** 保存请求后在另一个会话恢复
- **THEN** 可定位同一目标和未完成步骤，不依赖旧聊天；先重验当前权限和文件
- 超时：30秒。
- 证据：Host；恢复记录和归属检查。
- 异常分类：CONSENT_REQUIRED。

#### Scenario: IN-04-READONLY

- 前置条件：用户明确只预览，或只有配置中的approved字段而没有当前执行授权。
- **WHEN** 加载完整启动单
- **THEN** 不写目标/启动区、不联网、不由配置提升权限
- 超时：10秒。
- 证据：Host；前后文件树和调用记录。
- 异常分类：CONSENT_REQUIRED。
