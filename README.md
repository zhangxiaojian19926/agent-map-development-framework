# Agent Map Development Framework

跨项目复用的 AI 工程协作框架：公共规则 + 完整技能包 + 项目/模块模板 + 验证工具。

## 开始使用

1. 准备一份输入：已有工程填“模块名称 = 仓库 URL”，全新工程只描述项目和目标。见 [启动单模板](templates/PROJECT-START.md)。
2. 把输入与 [BOOTSTRAP.md](BOOTSTRAP.md) 的位置给具备文件/执行能力的 Coding Agent，说：“初始化工程”。
3. Agent 自行预览、按名称下载、基础准备、分析并校验模块地图；用户无需选择 init/new、填写 JSON/hash 或执行脚本。
4. 基础接入不批准业务实施，下一步按 [开发流程](docs/framework/development-workflow.md) 确认设计与计划；缺凭据/权限只询问必要信息。非Codex不强制调用Codex，已实测覆盖以[验收记录](docs/acceptance.md)为准。

维护者验证（不是用户接入前置操作）：
```bash
python3 tools/check-framework
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## 文档地图

| 文档 | 作用 |
|---|---|
| [开发流程](docs/framework/development-workflow.md) | 任务分流与 OpenSpec/Superpowers 全周期协作 |
| [技能规则](docs/framework/skill-policy.md) | 调用、权限、冲突与停止条件 |
| [多模块协作](docs/framework/collaboration-policy.md) | 模块职责、接口、交接、集成与接入 |
| [知识规则](docs/framework/knowledge-policy.md) | KB 查询、建立、路由、摄入与确认 |
| [接入](docs/onboarding.md) | 新工程、已有工程、更新及退出 |
| [集成](docs/integrations.md) | 22 个技能入口及外部工具边界 |
| [验收](docs/acceptance.md) | 工作流覆盖和实际验证范围 |
| [第三方说明](THIRD_PARTY_NOTICES.md) | 来源、许可证和本地适配 |

## 包含与不包含

包含 6 个 OpenSpec 技能、14 个 Superpowers 技能、llm-wiki 和 project-bootstrap 技能及所需支持文件。版本和文件指纹见 [发布清单](framework-manifest.json)。

包含确定性的工程接入 CLI、模块登记、受控索引/Agent 分析、证据地图和只读诊断。OpenSpec CLI、Agent 模型/宿主、Git、业务测试环境、设备及部署工具不随包附带，也不会自动安装。
不提供全局 watcher 或全局 Git hook；一键初始化不等于自动完成未批准的产品需求。
知识脚本是准备/检索/结构检查辅助：PREPARED 或 PLAN_ONLY 不代表语义知识摄入已完成。

不包含任何实际业务工程、个人知识库、设备配置、凭据、历史会话或原项目提交历史。
本版本验证的是发布结构、脚本行为和受控场景；不声称所有宿主、真实设备或生产环境已通过验收。

## 使用与维护

原有 AGENTS.md 不得直接覆盖；先合并入口与冲突，再按项目选择的技能版本使用。
公共更新不覆盖已填写项目资料、模块规则或知识数据。主工作流状态归 OpenSpec，知识库不替代活跃规格。
