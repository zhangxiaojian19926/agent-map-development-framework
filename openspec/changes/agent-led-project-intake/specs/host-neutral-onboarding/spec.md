## Purpose

为具备文件和执行能力的不同 Coding Agent提供同一初始化协议，将需求判断与确定性写入校验分离，支持无代码工程准备、真实状态报告及跨宿主恢复，不依赖特定厂商CLI才能接入。

## ADDED Requirements

### Requirement: HN-01 通用入口与能力

系统 SHALL 提供可直接读取的 BOOTSTRAP.md；首次可在同一请求提供入口与启动单，不强制安装厂商插件。能力不满足时报告缺口，不伪称完成。

#### Scenario: HN-01-NONCODEX

- 前置条件：非Codex宿主具有读写执行能力，PATH无codex。
- **WHEN** 提供入口、键值对文件和初始化请求
- **THEN** 当前宿主完成协调，不调用codex，不要求用户执行脚本/填配置
- 超时：整体验收20分钟，超时报未完成。
- 证据：Host；真实宿主轨迹和文件验收。
- 异常分类：CAPABILITY_MISSING。

#### Scenario: HN-01-CHATONLY

- 前置条件：宿主只有聊天能力。
- **WHEN** 请求自动初始化
- **THEN** 明确不能执行，仅交付计划，不报告接入完成
- 超时：30秒。
- 证据：Host；宿主输出。
- 异常分类：CAPABILITY_MISSING。

### Requirement: HN-02 当前Agent结果校验

系统 MUST 校验当前Agent分析结果的请求绑定、源码指纹、模块覆盖、证据和路径范围；结果与源文本不能自授权限，静态关系不得声明业务运行通过。

#### Scenario: HN-02-RESULT

- 前置条件：允许范围内源码已形成观察包。
- **WHEN** 当前Agent提交完整有效结果
- **THEN** 发布有证据地图，注明current-session而不伪造外部CLI记录；runtime为NOT_RUN
- 超时：每次校验30秒。
- 证据：Host；校验结果和地图。
- 异常分类：INVALID_EVIDENCE。

#### Scenario: HN-02-STALE

- 前置条件：分析期间源码被改动或结果包含越界/执行指令。
- **WHEN** 提交结果
- **THEN** 拒绝该结果，不覆盖有效地图、不执行结果中的指令
- 超时：每次校验30秒。
- 证据：Host；旧地图hash与错误报告。
- 异常分类：STALE或INVALID_EVIDENCE。

### Requirement: HN-03 基础准备与业务审批分离

系统 SHALL 分别报告接入、理解、开发准备和业务验收；无源码可完成PREPARED，不等于业务实现获批。现有new命令的明确审批检查 MUST 保留。

#### Scenario: HN-03-EMPTY

- 前置条件：没有URL和源码但有新需求。
- **WHEN** 调用通用初始化入口
- **THEN** 生成基础资料，索引N/A；继续需求设计讨论，不先索要三份hash、不自动实现业务
- 超时：30秒。
- 证据：Host；文件与权限记录。
- 异常分类：CONSENT_REQUIRED。

#### Scenario: HN-03-LEGACY

- 前置条件：使用旧new命令而缺批准内容。
- **WHEN** 执行旧调用
- **THEN** 仍拒绝未批准的新建路径，不因新增入口改变旧接口保护
- 超时：30秒。
- 证据：Host；旧回归测试。
- 异常分类：NEEDS_DESIGN_APPROVAL。

#### Scenario: HN-03-HUMAN

- 前置条件：已有人工AGENTS和无关未提交代码。
- **WHEN** 接入框架
- **THEN** 保留原文与代码；安全时添加受管入口，冲突只阻塞相关项；项目链接指向实际资料
- 超时：30秒。
- 证据：Host；前后diff与链接验证。
- 异常分类：RULE_CONFLICT。

### Requirement: HN-04 真实可用性与换宿主验收

系统 MUST 以真实自然语言输入验证用户无需手工命令、执行配置、hash或模式选择；至少一个真实非Codex宿主完成测试后才宣称跨宿主已验证，未运行项保持NOT_RUN。

#### Scenario: HN-04-LIVE

- 前置条件：合成环境提供启动单和正常宿主权限。
- **WHEN** Codex与一个非Codex宿主分别运行命名多仓与新需求路线
- **THEN** 无需人工提供执行参数；确定性检查真实文件、映射和状态；无未授权外部操作
- 超时：每次20分钟。
- 证据：Host；双宿主原始轨迹和独立验收。
- 异常分类：NOT_RUN或SPEC_MISMATCH。

#### Scenario: HN-04-RESUME

- 前置条件：前一宿主已完成部分步骤。
- **WHEN** 换另一宿主并说继续初始化
- **THEN** 从输入与状态恢复，重验当前权限，不重复获取成功模块、不重放发布
- 超时：每次20分钟。
- 证据：Host；交接轨迹和结果。
- 异常分类：CONSENT_REQUIRED或PARTIAL。

### Requirement: HN-05 工程资料完整性

系统 MUST 区分骨架PREPARED与初始化COMPLETE。完整初始化需要项目事实/设计、所有选定模块的局部开发资料和明确交接；空字段、占位模板或仅导航链接不能满足完整性。源码事实、批准设计、推断和未验证命令 SHALL 分别标注来源及状态，不凭文档结构宣称语义正确。

#### Scenario: HN-05-DOCS

- 前置条件：三个已获取模块有当前有效分析，当前授权包含工程资料写入。
- **WHEN** Agent完成资料并请求初始化验收
- **THEN** 项目目标、架构、接口双方、集成顺序、约束及资源均有内容；每模块用途、入口、输入输出、内部职责、依赖、命令前提及验证状态均有来源；任一必需字段为占位或缺失则返回PARTIAL及缺项
- 超时：机器校验30秒；Agent分析单次20分钟，超时保留进度。
- 证据：Host；结构校验、文件内容、引用与Agent语义复核。
- 异常分类：INCOMPLETE_DOCUMENTATION或INVALID_EVIDENCE。

#### Scenario: HN-05-PRESERVE

- 前置条件：一个模块含人工AGENTS，一个只读模块缺入口，一个可写模块缺入口。
- **WHEN** 生成模块开发资料
- **THEN** 人工正文保持原字节；只读模块在项目侧建立等价完整入口；可写模块生成完整局部AGENTS；语义冲突单列交接并阻止COMPLETE，不覆盖人工规则
- 超时：30秒。
- 证据：Host；前后hash、只读目录零写入和导航检查。
- 异常分类：RULE_CONFLICT或CONSENT_REQUIRED。

### Requirement: HN-06 分批分析与完整发布

系统 SHALL 支持超过单包预算的已授权源码分批分析，每包序列化不超过200000字节；绑定清单、框架版本、源码版本与批次，最终统一核对跨模块关系。系统 MUST 在所有批次及最终汇总验证通过前保留旧有效地图，不以部分摘要冒充完整理解。

#### Scenario: HN-06-LARGE

- 前置条件：三个模块源码总量超过600KB，包含一个超过单包预算但可按行分片的文件，调用双方落在不同批次。
- **WHEN** Agent逐批分析并汇总提交
- **THEN** 每包均在预算内，文件行范围无遗漏，跨批调用有两端证据，完整覆盖报告列明支持类型与排除项；全量校验后发布一次有效结果
- 超时：每包机器操作30秒、宿主分析20分钟；不限制用户工程必须在单次会话完成。
- 证据：Host；覆盖清单、批次记录和独立关系断言。
- 异常分类：FILE_SLICE_TOO_LARGE或INVALID_EVIDENCE。

#### Scenario: HN-06-RESUME

- 前置条件：已有地图有效，新会话已接收部分批次。
- **WHEN** 缺批提交、不同内容重复提交、切换宿主或源码发生变化
- **THEN** 缺批和冲突不发布；相同重传幂等；换宿主重验权限后仅继续缺批；源码变化拒绝旧结果，不混合版本，旧地图保持且标STALE
- 超时：每次30秒。
- 证据：Host；前后地图hash、批次接收记录和权限拒绝测试；真实换宿主另按HN-04验收。
- 异常分类：INCOMPLETE_COVERAGE、BATCH_CONFLICT、STALE_SOURCE或CONSENT_REQUIRED。

### Requirement: HN-07 新工程设计与开发交接

系统 SHALL 为已有及全新工程保存可恢复的开发交接；明确版本、目标、规格/计划引用、关键未知项、下一动作及所需授权。没有源码的新工程 SHALL 使用设计路线，不虚构源码图；未批准设计或实施时 MUST NOT 自动开发业务。

#### Scenario: HN-07-NEW

- 前置条件：仅有新需求，无仓库、源码或批准设计。
- **WHEN** 完成基础prepare并继续工程规划
- **THEN** PREPARED保持，实际地图N/A，handoff=NEEDS_DESIGN_APPROVAL；Agent形成拟议模块职责与接口供确认，不生成业务代码或Git；关键设计确认后再核对完整资料，设计关系与实际关系分开
- 超时：机器校验30秒；等待用户决定不记超时失败。
- 证据：Host；目录差异、交接记录和批准范围核对。
- 异常分类：NEEDS_DESIGN_APPROVAL。

#### Scenario: HN-07-CONTINUE

- 前置条件：工程资料完整且相同范围的规格与实施计划已批准。
- **WHEN** 当前或新会话Agent收到继续开发请求
- **THEN** 读取交接和真实OpenSpec状态，核对版本/权限后进入适用任务，不让用户重新填写机器参数或重复批准相同范围；缺关键审批只停止依赖它的操作
- 超时：上下文检查30秒。
- 证据：Host；状态核对及真实宿主轨迹。
- 异常分类：STALE或CONSENT_REQUIRED。

### Requirement: HN-08 新增模块后的资料维护

系统 SHALL 在Agent发现并按授权登记新增模块后检查资料、关系与覆盖缺口；旧资料不能覆盖新事实，不自动启用候选或全局监听。变化后的COMPLETE状态 MUST 重新验收，不能沿用旧完成标记。

#### Scenario: HN-08-ADD

- 前置条件：已有三个模块初始化完成，用户新增第四个仓库或下载目录。
- **WHEN** Agent执行入口检查并在授权后登记新模块
- **THEN** 候选先明确报告，登记后资料/覆盖标缺项，Agent补齐模块入口和受影响关系再验收；原模块ID及人工文档不变，不重复clone成功模块
- 超时：每次机器检查30秒。
- 证据：Host；四模块目录、前后身份与资料hash、关系检查。
- 异常分类：PARTIAL或STALE。

#### Scenario: HN-08-REMOVED

- 前置条件：完成接入的模块后来移动或消失。
- **WHEN** 同步观察并检查工程
- **THEN** 保留历史并报告missing/迁移需求，不自动删除模块资料、不以旧地图宣称COMPLETE
- 超时：30秒。
- 证据：Host；登记历史、文件保留与状态断言。
- 异常分类：PARTIAL或CONFLICT。
