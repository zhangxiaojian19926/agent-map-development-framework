# Agent Map Development Framework

这是业务项目内的公共运行时包，用于初始化、目录治理、模块协作、验证和知识流程。公共工程壳自身的测试、发布、维护者资料和历史归档不属于本包。

## 使用入口

1. 按[启动单模板](../templates/PROJECT-START.md)准备已有模块或全新需求。
2. 从[初始化入口](../BOOTSTRAP.md)开始，由当前 Coding Agent 完成只读预览和获准的初始化。
3. 初始化后按[项目布局](../docs/guide/project-layout.md)管理目录，按[日常开发指南](../docs/guide/daily-development.md)接续任务。
4. 使用 `python3 .agent-framework/tools/framework doctor --target .` 从业务项目根目录检查状态；PREPARED 或 READY 不等于业务已运行。

## 文档地图

| 文档 | 作用 |
|---|---|
| [项目布局](../docs/guide/project-layout.md) | 目录所有权、提交规则和模块归置 |
| [日常开发](../docs/guide/daily-development.md) | 任务分流、TDD、评审和交付 |
| [模块生命周期](../docs/guide/module-lifecycle.md) | 新增、修改、移动和跨模块交接 |
| [测试与交付](../docs/guide/testing-and-delivery.md) | 测试分层、证据矩阵和完成门禁 |
| [框架升级](../docs/guide/framework-upgrade.md) | 公共包升级、人工内容保护和回滚 |
| [公共开发流程](../docs/framework/development-workflow.md) | OpenSpec/Superpowers 全周期规则 |
| [高级 CLI](../docs/bootstrap.md) | 初始化与维护命令参考 |
| [集成](../docs/integrations.md) | 技能入口及外部工具边界 |
| [第三方说明](../THIRD_PARTY_NOTICES.md) | 来源、许可证和本地适配 |

公共包中的生成文件由受管流程更新；业务项目人工正文、模块局部规则、知识内容和活跃 change 不因升级被覆盖或归档。提交、推送、发布、设备、部署和知识摄入分别需要对应授权。
