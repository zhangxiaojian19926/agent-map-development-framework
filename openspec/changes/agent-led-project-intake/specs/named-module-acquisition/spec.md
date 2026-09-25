## Purpose

按用户明确提供的模块名称与仓库 URL 获取已有工程的多个独立源码模块，保留稳定的名称、目录和版本关系；通过逐模块证据处理异常与恢复，不以部分成功冒充整体完成。

## ADDED Requirements

### Requirement: AC-01 精确映射与稳定身份

系统 SHALL 将每个安全模块名映射到 modules/<规范化名称>，保留原显示名、稳定内部ID与URL；不同名称的同源仓库不自动合并，列表顺序不改变身份。

#### Scenario: AC-01-NAMES

- 前置条件：两个仓库具有相同basename。
- **WHEN** 输入设备端=URL1、服务端=URL2
- **THEN** 分别下载到对应命名目录，登记name/id/path/source的精确映射
- 超时：每仓300秒。
- 证据：Host；独立Git根和目录记录。
- 异常分类：ACQUISITION_FAILED。

#### Scenario: AC-01-REORDER

- 前置条件：已完成一次命名模块接入。
- **WHEN** 交换条目顺序或两个不同名称引用同一URL
- **THEN** 已有ID不变；不同名称不合并；无变化时不重复clone
- 超时：每检查30秒。
- 证据：Host；运行记录与Git状态。
- 异常分类：SOURCE_CONFLICT。

### Requirement: AC-02 来源版本与空仓库

系统 SHALL 区分远程默认分支、显式branch/tag/commit、空仓库和认证失败；缺失ref MUST NOT 静默回退或创建。新工作分支仅按明确请求和已确认起点处理。

#### Scenario: AC-02-DEFAULT

- 前置条件：远程默认分支不是main。
- **WHEN** 仅提供模块URL
- **THEN** 使用真实默认起点并记录解析commit
- 超时：每查询30秒。
- 证据：Host；Git refs与HEAD。
- 异常分类：REF_UNRESOLVED。

#### Scenario: AC-02-MISSING

- 前置条件：用户指定源分支不存在。
- **WHEN** 尝试初始化
- **THEN** 明确报告该模块起点错误，不换默认分支、不创建新分支
- 超时：每查询30秒。
- 证据：Host；操作日志。
- 异常分类：REF_NOT_FOUND。

#### Scenario: AC-02-EMPTY

- 前置条件：远程可访问且确实无refs。
- **WHEN** 初始化该模块
- **THEN** 标记EMPTY，保留其名称与URL，不伪造commit或索引；可进入新内容准备
- 超时：每查询30秒。
- 证据：Host；Git查询和分层状态。
- 异常分类：INFRA_ERROR。

#### Scenario: AC-02-AUTH

- 前置条件：私有仓库不可认证或网络超时。
- **WHEN** 尝试获取
- **THEN** 报告认证/网络原因；不判EMPTY，不将凭据写入文件
- 超时：每仓300秒。
- 证据：Host；脱敏错误和模块状态。
- 异常分类：AUTH_REQUIRED或NETWORK_ERROR。

### Requirement: AC-03 部分失败与恢复

系统 MUST 为每个请求模块保留结果；失败不删除成功模块，重试须验证来源、版本、文件归属和人工修改，不覆盖不属于本次运行的目录。

#### Scenario: AC-03-PARTIAL

- 前置条件：三个授权模块第二个获取失败。
- **WHEN** 执行并恢复初始化
- **THEN** 成功模块保留，整体PARTIAL；恢复不重复下载成功模块，不掩盖失败
- 超时：每仓300秒。
- 证据：Host；逐模块结果和调用计数。
- 异常分类：PARTIAL。

#### Scenario: AC-03-CONFLICT

- 前置条件：目标同名目录已有用户内容或来源改变。
- **WHEN** 重复执行
- **THEN** 保留用户内容并标CONFLICT；不重置、不删除、不静默换目录
- 超时：30秒。
- 证据：Host；文件指纹和操作日志。
- 异常分类：SOURCE_CONFLICT。

### Requirement: AC-04 下载代码不自动执行

系统 MUST 隔离不可信clone配置和hooks，不自动拉取额外submodule/LFS或运行安装脚本；私有认证仅通过评估的宿主凭据通道，URL不得承载秘密。

#### Scenario: AC-04-UNTRUSTED

- 前置条件：仓库包含执行建议、安装脚本和子模块。
- **WHEN** 完成下载及分析
- **THEN** 不执行脚本/README指令、不额外联网启用子模块、不扩展访问范围
- 超时：每仓300秒。
- 证据：Host；进程和文件审计。
- 异常分类：CONSENT_REQUIRED。

#### Scenario: AC-04-CREDENTIALS

- 前置条件：已有合法宿主认证但不允许读取任意全局Git配置。
- **WHEN** 请求私有来源接入
- **THEN** 仅使用允许的认证链路；不可用则明确阻塞，不泄露秘密或放开不可信配置
- 超时：每仓300秒。
- 证据：Host；脱敏认证测试。
- 异常分类：AUTH_REQUIRED。
