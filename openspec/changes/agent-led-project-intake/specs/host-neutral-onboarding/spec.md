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
