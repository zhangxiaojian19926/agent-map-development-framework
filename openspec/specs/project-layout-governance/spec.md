# project-layout-governance Specification

## Purpose

为公共工程壳及其生成的业务项目建立清晰、可验证的目录治理契约，使使用者能够区分现行指南、历史资料、业务事实、活跃变更、本机状态和生成内容，并在不破坏既有项目的前提下完成初始化、开发、升级与交付。

## Requirements

### Requirement: Audience-specific documentation navigation

公共工程壳 SHALL 为使用者和维护者提供明确分开的文档入口，并将现行指南、公共规则、接口参考、维护者资料与历史归档区分开。现行入口 MUST NOT 依赖历史计划或历史验收记录传达当前操作步骤，稳定技能与工具路径 MUST NOT 仅因目录美化而被改名。

#### Scenario: First-time user follows the current path

- **WHEN** 新使用者从 README 开始查找如何初始化业务项目
- **THEN** 使用者能够只沿现行入口找到 BOOTSTRAP、启动输入和业务项目目录指南，无需阅读维护者发布资料或历史实施计划

#### Scenario: Maintainer finds repository-specific guidance

- **WHEN** 维护者需要修改公共工程壳、运行验证或发布版本
- **THEN** 维护者入口能够定位仓库布局、验证和发布说明，且这些说明不会被表述为普通业务项目的初始化前置条件

#### Scenario: Historical document is encountered

- **WHEN** 使用者或 Agent 打开历史计划、历史验收或归档资料
- **THEN** 文档位置或明确标识能够表明其历史属性，并且不会将其未完成任务或旧版本数据当作当前状态

### Requirement: Runtime distribution allowlist

初始化或升级目标项目时，系统 SHALL 仅向 `.agent-framework/` 复制目标项目运行所需的明确文件集合。维护者测试、历史验收、历史计划、发布工作流及仅服务于公共工程壳开发的资料 MUST NOT 因位于通用文档目录而被复制。运行时必需的公共规则、技能、模板、CLI 和许可证 MUST 保持完整，已有项目人工内容 MUST 被保留。

#### Scenario: New project receives only runtime content

- **WHEN** 使用有效输入初始化一个新的目标项目
- **THEN** 目标项目的公共包包含运行所需入口、规则、技能、模板、CLI、清单和许可证
- **AND** 目标项目不包含公共壳测试、历史计划、历史验收、发布工作流或维护者专用资料

#### Scenario: Existing project is upgraded

- **WHEN** 在已有业务项目上执行受授权的公共包升级
- **THEN** 仅公共包和受管入口按归属规则更新
- **AND** `docs/project/` 人工正文、模块局部规则、业务源码、知识内容和活跃 OpenSpec change 不被覆盖或归档

#### Scenario: Runtime payload is incomplete

- **WHEN** 运行时白名单遗漏初始化或后续开发所需文件
- **THEN** 分发检查或目标项目验证 MUST 失败并指出缺失内容，不得仅凭复制命令成功报告完整接入

### Requirement: Project directory ownership and persistence

业务项目 SHALL 有可供人工和 Agent 查询的目录所有权说明，覆盖项目声明、生成目录、公共包、本机状态、当前事实、活跃规格、业务模块、验证证据、知识内容和构建产物。说明 MUST 区分可人工编辑、仅由受管流程修改及不得提交的内容，并禁止将 `.framework/` 本机状态作为共享项目事实。

#### Scenario: Contributor classifies a new artifact

- **WHEN** 贡献者需要新增业务源码、需求、验证报告、知识页、缓存或构建产物
- **THEN** 目录指南能够给出唯一的目标位置、责任方和提交规则
- **AND** 不需要把临时文件放入仓库根目录或把活跃任务写入项目事实文档

#### Scenario: Generated file is edited

- **WHEN** 文件被标识为生成器或受管流程所有
- **THEN** 使用者和 Agent 能够识别其所有权及允许的编辑方式
- **AND** 人工正文与受管区块冲突时保持现有冲突保护，不以目录整理为由强制覆盖

#### Scenario: Local state is reviewed for commit

- **WHEN** 提交前检查包含 `.framework/`、私有启动信息、凭据、缓存或构建输出
- **THEN** 项目规则和忽略配置能够阻止或明确提示不应提交的内容，且不将这些内容写入公共项目资料

### Requirement: Business module and change placement

业务项目 SHALL 按真实模块身份登记源码、局部规则、测试和接口责任。已有源码 MUST 保持原位接入，新项目 SHOULD 使用 `modules/<module-id>/` 作为默认顶层业务模块位置；未经批准的拟议模块 MUST NOT 通过空目录冒充实际实现。跨模块工作 MUST 能从共享变更追踪到接口责任、局部验证、集成验证和参与版本。

#### Scenario: Existing source tree is onboarded

- **WHEN** 已有业务源码位于非默认目录或具有既有语言生态结构
- **THEN** 初始化保留原路径和现有文件，仅在项目登记与模块资料中记录真实位置和责任，不强制迁移源码

#### Scenario: Planned module has no implementation

- **WHEN** 新工程设计包含尚未获批准或尚未实现的模块
- **THEN** 拟议模块仅存在于设计或规格中，目录和实际模块目录不得声称其已经存在

#### Scenario: Cross-module change is delivered

- **WHEN** 一个变更修改接口提供方和消费方
- **THEN** 交付记录能够关联共享 Requirement/Scenario、双方模块、局部测试、集成 Scenario 和各仓库版本组合
- **AND** 仅有模块单元测试时不得将集成交付标记为通过

### Requirement: Historical and OpenSpec lifecycle governance

历史资料整理和旧 change 清理 SHALL 以实际任务、最终工作树及适用验证证据为依据。规划产物存在、代码已经存在、单次 CI 通过或目录已经整齐 MUST NOT 单独作为勾选任务或归档变更的依据。未执行场景 MUST 保持 NOT_RUN，未完成 change MUST NOT 被手工移动为已归档。

#### Scenario: Legacy change contains unchecked work

- **WHEN** 旧 change 仍有未勾任务或缺少真实宿主、集成、恢复等证据
- **THEN** 清理过程保留未完成状态和限制说明
- **AND** 只有逐项核实最终证据的任务才能更新，归档继续走正常同步与归档门禁

#### Scenario: Completed historical change is archived

- **WHEN** 一个 change 的适用任务、验证和集成状态均有最终证据
- **THEN** 系统先核对规格同步结果再执行正常归档
- **AND** 历史计划仍保持历史参考资料身份，不作为活跃状态存储

### Requirement: Layout validation and usable delivery flow

公共工程壳 SHALL 将目录治理纳入分发检查和目标项目验证，并提供初始化、日常开发、模块变更、框架升级和最终交付的可跟随流程。验证 MUST 覆盖链接、运行时文件完整性、人工内容保护、本机状态隔离和变更追踪，不得仅以文档文件存在证明流程可用。

#### Scenario: Distribution validation detects layout drift

- **WHEN** 文档链接失效、清单未更新、运行时包含维护者专用文件或必要文件缺失
- **THEN** 公共检查或相关测试失败并给出可定位的错误，CI 不得通过该分发状态

#### Scenario: User follows the standard development flow

- **WHEN** 使用者依次执行初始化、继续变更、模块变更、框架升级或交付指南
- **THEN** 指南能够说明各阶段的输入、目录读写范围、授权边界、验证证据和完成状态
- **AND** 查询、文档、缺陷修复与新行为仍遵循各自既有流程，不因目录指南被统一成无差别全量流程
