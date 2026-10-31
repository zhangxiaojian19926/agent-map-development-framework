## Purpose

为普通工程初始化和自动逆向观察提供显式、中文、六段式完成摘要，让用户能够直接核对当前状态、流程产物、条件性缺项、未执行边界、提交责任和唯一下一步，同时保持机器接口与隐私边界稳定。

## ADDED Requirements

### Requirement: SUM-01 显式呈现与机器接口兼容

系统 SHALL 仅在用户为 `doctor` 或自动 `reverse` 显式指定 `--summary` 时输出人类可读摘要；未指定时 MUST 保持既有JSON字段、退出码、授权和副作用语义。摘要 MUST NOT 被当作新的完成状态来源。

#### Scenario: SUM-01-JSON_DEFAULT

- **WHEN** 既有调用方执行 `doctor` 或自动 `reverse` 且未指定 `--summary`
- **THEN** stdout仍为可解析的既有JSON结果，退出码和文件副作用与不引入摘要时一致

#### Scenario: SUM-01-SUMMARY_EXIT

- **WHEN** 用户对同一有效请求指定 `--summary`
- **THEN** stdout为中文六段式摘要，命令完成或部分完成的退出码与对应JSON调用一致，不增加授权、网络、工具或业务执行

#### Scenario: SUM-01-UNSUPPORTED

- **WHEN** 用户在旧 `reverse --scope` 或其他未声明支持摘要的动作中使用 `--summary`
- **THEN** 系统在对应业务动作前返回明确输入错误，不静默忽略该选项

### Requirement: SUM-02 普通工程状态与当前产物

普通工程摘要 SHALL 分为结果、当前流程产物、条件性未生成、未执行与限制、提交与本机状态、下一步六部分，并依据只读诊断和当前文件存在性展示。当前存在的产物 MUST NOT 被描述为本次命令新建，`initialization=COMPLETE` MUST NOT 被解释为业务实现或运行成功。

#### Scenario: SUM-02-COMPLETE_NO_CODE

- **WHEN** 全新需求设计已批准、无白名单源码且初始化检查为 `COMPLETE`
- **THEN** 摘要列出当前项目资料、知识空壳和本机状态，说明地图与模块目录不适用或未生成，并保持业务运行 `NOT_RUN`

#### Scenario: SUM-02-PARTIAL

- **WHEN** 资料、覆盖、交接、地图或已选增强存在缺口
- **THEN** 摘要显示 `PARTIAL` 和具体分层状态，不把骨架存在描述为完整初始化，并给出与缺口对应的唯一下一步

#### Scenario: SUM-02-IDEMPOTENT

- **WHEN** 对已经初始化的工程重复执行只读摘要
- **THEN** 摘要仍只描述当前流程产物，不声称这些文件由本次只读命令创建

### Requirement: SUM-03 逆向分层状态与恢复

自动逆向摘要 SHALL 分别展示总体结果、工具链、逐项观察和运行验证，并列出与当前请求相关的计划、快照、观察、行为契约和公开摘要产物的真实存在状态。计划待批准、观察未授权、缺少provider或部分失败 MUST NOT 被汇总为完整观察成功。

#### Scenario: SUM-03-RECORDED

- **WHEN** 工具链就绪且全部指定观察为 `RECORDED`
- **THEN** 摘要显示当前行为契约及公开摘要状态，同时保持运行验证 `NOT_RUN`，下一步回到普通设计与开发交接

#### Scenario: SUM-03-PARTIAL_PROVIDER

- **WHEN** 静态观察成功而动态观察因 `PROVIDER_MISSING`、`NOT_AUTHORIZED` 或其他原因未完成
- **THEN** 摘要逐项显示真实状态、未完成原因和对应恢复动作，不声称生成了完成态行为契约

#### Scenario: SUM-03-PLAN_PENDING

- **WHEN** 自动逆向仅生成计划并等待批准
- **THEN** 摘要显示计划待批准及当前计划产物，不列出虚构的工具、观察或行为契约成功结果

### Requirement: SUM-04 脱敏与只读边界

摘要 MUST 只使用诊断结果、当前请求中的非秘密标识、工具动作和固定相对路径元数据；MUST NOT 读取或输出原始HTML、JavaScript、DOM、抓包、Cookie、Authorization、反编译正文或设备秘密。`doctor --summary` MUST 保持文件、进程和网络副作用为零。

#### Scenario: SUM-04-SECRET_OUTPUT

- **WHEN** 私有逆向原文包含令牌、Cookie或其他秘密
- **THEN** 人类可读摘要只显示证据路径与状态，不包含秘密正文，公开摘要也不因新增呈现而被改写

#### Scenario: SUM-04-DOCTOR_READONLY

- **WHEN** 在包含过期索引、逆向证据或dirty tree的工程上执行 `doctor --summary`
- **THEN** 文件树、工具执行和网络调用保持零变化，不修复、不安装、不运行业务测试

### Requirement: SUM-05 条件性缺项与唯一下一步

摘要 SHALL 将当前不适用或未生成的内容与失败分开说明，并按当前状态给出一个主下一步；不得把未请求能力列为错误，也不得一次给出多个互相竞争的主行动。

#### Scenario: SUM-05-NO_OPTIONAL_ARTIFACTS

- **WHEN** 新工程未请求源码、索引、OpenSpec、构建或逆向能力
- **THEN** 对应目录标为条件性未生成或不适用，不据此将完整初始化降级为失败

#### Scenario: SUM-05-NEXT_ACTION

- **WHEN** 当前状态为设计待批准、初始化完成、逆向计划待批准、工具失败或动态观察条件不足
- **THEN** 摘要分别选择设计确认、进入首个规格、批准当前计划、处理工具缺口或补齐动态观察条件作为唯一主下一步
