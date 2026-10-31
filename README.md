# Agent Map Development Framework

跨项目复用的 AI 工程协作框架：公共规则 + 完整技能包 + 项目/模块模板 + 验证工具。

## 使用工程壳开发软件

1. 准备一份输入：已有工程填“模块名称 = 仓库 URL”，全新工程只描述项目和目标。见 [启动单模板](templates/PROJECT-START.md)。
2. 把输入与 [BOOTSTRAP.md](BOOTSTRAP.md) 的位置给具备文件/执行能力的 Coding Agent，说：“初始化工程”。
3. Agent 自行预览并按名称下载。有白名单源码时才建立关系地图；全新需求先留下设计草案。同时建立空知识库 `knowledge/project/`（alias `project`）。用户无需选择 init/new、填写 JSON/hash 或执行脚本。
4. Agent 运行 `doctor` 并留下开发交接。只有 `initialization=COMPLETE` 才是完整初始化。新工程尚未确认设计时交付草案和待确认项。基础接入不批准业务实施，也不写入知识内容。
5. 初始化后按 [项目布局](docs/guide/project-layout.md) 管理目录，按 [日常开发指南](docs/guide/daily-development.md) 接续。任何能读写文件并执行 Python 的 Coding Agent 都用同一入口。

## 开发公共工程壳

维护者从 [仓库布局](docs/maintainer/repository-layout.md)、[验证指南](docs/maintainer/verification.md) 和 [发布指南](docs/maintainer/release.md) 开始。以下命令不是业务项目的初始化前置操作：

```bash
python3 tools/check-framework
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## 文档地图

| 文档 | 作用 |
|---|---|
| [项目布局](docs/guide/project-layout.md) | 业务目录所有权、提交规则和模块归置 |
| [日常开发](docs/guide/daily-development.md) | 任务分流、TDD、评审和交付入口 |
| [模块生命周期](docs/guide/module-lifecycle.md) | 新增、修改、移动和跨模块交接 |
| [测试与交付](docs/guide/testing-and-delivery.md) | 测试分层、证据矩阵和完成门禁 |
| [框架升级](docs/guide/framework-upgrade.md) | 公共包升级、人工内容保护和回滚 |
| [公共开发流程](docs/framework/development-workflow.md) | OpenSpec/Superpowers 全周期规则 |
| [初始化](BOOTSTRAP.md) | 当前 Agent 的唯一初始化步骤 |
| [集成](docs/integrations.md) | 技能入口及外部工具边界 |
| [维护者指南](docs/maintainer/repository-layout.md) | 公共壳布局、验证和发布 |
| [历史资料](docs/archive/README.md) | 历史计划与验收，不是当前状态 |
| [第三方说明](THIRD_PARTY_NOTICES.md) | 来源、许可证和本地适配 |

## 包含与不包含

包含 6 个 OpenSpec 技能、13 个 Superpowers 技能、llm-wiki、project-bootstrap、reverse-engineer 和 matt-pocock 的测试驱动、写作与接口设计参考技能及所需支持文件。版本和文件指纹见 [发布清单](framework-manifest.json)。

包含确定性的工程接入 CLI、模块登记、可选 CodeGraph 索引、由当前 Agent 提交证据的关系地图、空知识库壳和只读诊断。逆向工具不在初始化时安装；版本见 [逆向工具](docs/framework/reverse-tools.md)。OpenSpec CLI、Node、模型、Git、业务测试环境、设备及部署工具不随包附带，也不会自动安装。
不提供全局 watcher 或全局 Git hook；一键初始化不等于自动完成未批准的产品需求。
知识脚本是准备/检索/结构检查辅助：PREPARED 或 PLAN_ONLY 不代表语义知识摄入已完成。

不包含任何实际业务工程、个人知识库、设备配置、凭据、历史会话或原项目提交历史。
本版本验证的是发布结构、脚本行为和受控场景；不声称所有宿主、真实设备或生产环境已通过验收。

## 使用与维护

原有 AGENTS.md 不得直接覆盖；先合并入口与冲突，再按项目选择的技能版本使用。
公共更新不覆盖已填写项目资料、模块规则或知识数据。主工作流状态归 OpenSpec，知识库不替代活跃规格。

推送和拉取请求由 `.github/workflows/validate.yml` 在 Ubuntu 与 macOS 上运行清单检查和单元测试。每周一 02:00 UTC（北京时间 10:00）由 `.github/workflows/release.yml` 发布：`CHANGELOG.md` 的 Unreleased 有内容时，补丁版本号加一，写回清单指纹，推送 `vX.Y.Z` tag 和 GitHub Release。没有未发布说明则跳过。手动运行可选 patch、minor 或 major。发布前先跑同一套校验。
