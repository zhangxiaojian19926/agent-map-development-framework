## Purpose

提供不限模块数量和目录布局的接入契约，区分模块、仓库和索引身份，以批准的发现边界维护客观目录，支持新代码、已有代码和未实现模块且保留移动及缺失历史。

## ADDED Requirements

### Requirement: MOD-01 来源与有界发现

系统 SHALL 支持 clone/add/sync，候选发现不执行模块代码；只扫描确认的根或明确路径，拒绝越界和无法判别的嵌套关系。

#### Scenario: MOD-01-IMPORT

- 前置条件：配置三种不同深度模块，含独立 Git 和无 Git 下载目录
- **WHEN** clone/add 后接入
- **THEN** 自动登记、安排索引与 Agent 交接；无 Git 模块经过身份确认，不隐式 git init；下载地址脱敏
- 超时：clone 默认 300 秒，发现 30 秒
- 环境与证据：Host：本地 Git fixture 与执行日志
- 异常分类：INVALID_MODULE / INFRA_ERROR

#### Scenario: MOD-01-ESCAPE

- 前置条件：候选目录符号链接指向工程外
- **WHEN** 同步候选模块
- **THEN** 拒绝该候选并报告；不读取工程外源码、不静默宣称完整
- 超时：30 秒
- 环境与证据：Host：越界 fixture 与访问记录
- 异常分类：PATH_ESCAPE

### Requirement: MOD-02 稳定身份与索引归属

系统 SHALL 分别保存 module-id、repo-id 和 index-id；同仓多模块可共享索引，独立仓库不误用外层 Git 状态，ID 冲突停止相关接入。

#### Scenario: MOD-02-IDENTITY

- 前置条件：单仓两个模块加一个独立子仓库
- **WHEN** 建立目录
- **THEN** 三个模块具有明确仓库和索引归属；不重复全量索引同一根
- 超时：30 秒（索引另计）
- 环境与证据：Host：catalog 与调用计数
- 异常分类：DUPLICATE_ID / AMBIGUOUS_BOUNDARY

### Requirement: MOD-03 计划模块与生命周期

系统 SHALL 区分 PLANNED、SCAFFOLDED、IMPLEMENTED、VERIFIED，并保留 missing 状态和移动历史；目录名变化不得自动重置身份。

#### Scenario: MOD-03-EMPTY

- 前置条件：批准设计含空模块
- **WHEN** 创建骨架及地图
- **THEN** 模块标记 PLANNED/SCAFFOLDED，索引 NOT_APPLICABLE，不生成伪接口或 VERIFIED
- 超时：30 秒
- 环境与证据：Host：catalog、地图和无索引调用断言
- 异常分类：INVALID_STATE

#### Scenario: MOD-03-MOVE

- 前置条件：已登记模块被移动或删除
- **WHEN** module sync
- **THEN** 有明确身份则保留 ID；不明确时待确认；消失标 missing，不删除历史记录
- 超时：30 秒
- 环境与证据：Host：前后 ID、历史和状态
- 异常分类：IDENTITY_UNCERTAIN
