## Why

当前公共包只有规则、模板和知识辅助脚本，用户仍需手工绑定项目路径、接入 Agent、登记模块、初始化索引并维护连接关系。增加统一入口，使已有代码接入和全新需求建工程都能形成可验证、可恢复的开发工作流。

## What Changes

- 增加统一 CLI：`init`、`new`、`module clone/add/sync`、`doctor`、`resume`，支持交互向导及明确配置的非交互调用。
- 区分需求澄清、设计审批、工程创建、代码实现。无代码时建立计划地图，有代码后再建立实际关系及运行证据。
- 引入有界模块发现、稳定身份、仓库/模块/索引分离和无 Git 目录接入。
- 自动化范围经本次本机可信确认后，允许 CodeGraph 初始化/同步、项目级更新触发和受管地图更新；不把克隆来的配置当授权。
- 新增工程接入与地图维护技能，首版以 Codex CLI 适配器为验收目标；通用模式只生成交接，不伪称 Agent 已运行。
- 生成带源码指纹与证据等级的关系记录、模块入口及项目地图；人工内容与机器生成内容分离。
- 增加幂等、冲突检查、断点恢复、就绪分级和跨平台合成验收。
- **BREAKING（规则默认值变更）**：将无条件“不自动 init/sync/hook”改为“仅在确认的自动化范围内执行”；未配置或只读任务仍不执行。
- 区分发布包完整性检查和目标工程就绪检查；版本、文件清单、文档和第三方归属同步维护。

## Capabilities

### New Capabilities

- `project-bootstrap`：双入口、规划根、确认、生成与恢复。
- `module-lifecycle`：模块导入、发现、身份、状态及索引归属。
- `codegraph-maintenance`：索引适配、钩子共存、事件与增量维护。
- `agent-project-maps`：宿主交接、主动分析、关系证据及受管文档。
- `project-readiness`：导航/运行分级、诊断与可重复验收。

### Modified Capabilities

无既有 OpenSpec 主规格；上述规则当前仅存在于公共 Markdown 文档，将由本变更建立对应规格。

## Impact

预计涉及 tools/framework 及其内部库、公共 AGENTS.md、docs/framework、onboarding/integrations/acceptance、项目和模块模板、新技能、测试、CI 与发布清单。保留现有 21 个技能及知识脚本兼容入口，不重写无关第三方技能。
目标环境首版为 macOS/Linux、Python 3.9+；Git、CodeGraph、OpenSpec 和 Agent 是按能力选择的外部工具，真实版本及 CLI 参数需适配验证。
当前仅形成规划产物；尚未更新运行规则或新增可执行初始化器。原业务工程、全局配置、真实设备、知识内容和远程仓库不在本次规划写入范围。
