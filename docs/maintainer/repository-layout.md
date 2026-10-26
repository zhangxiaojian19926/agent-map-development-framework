# 公共工程壳仓库布局

本页只说明公共工程壳自身的维护边界。业务项目目录见[项目布局指南](../guide/project-layout.md)，普通初始化不从本页开始。

## 目录责任

| 路径 | 责任 | 是否进入目标项目公共包 |
|---|---|---|
| `README.md`、`BOOTSTRAP.md` | 受众分流与唯一初始化入口 | 是 |
| `AGENTS.md` | 公共开发流程入口 | 是 |
| `docs/guide/` | 工程壳使用者的现行指南 | 是 |
| `docs/framework/` | 跨项目公共规则 | 是 |
| `docs/project-intake.md`、`docs/bootstrap.md`、`docs/integrations.md` | 现行协议、高级 CLI 与集成参考 | 是 |
| `docs/maintainer/` | 公共壳维护者说明 | 否 |
| `docs/archive/` | 历史计划、验收与证据索引 | 否 |
| `skill/` | 随包发布的工作流与支持资源 | 是 |
| `templates/` | 未配置的项目与模块模板 | 是 |
| `tools/framework`、`tools/framework_core/` | 目标项目 CLI 与实现 | 是 |
| `tools/check-framework`、`tools/update-manifest`、`tools/prepare-release` | 公共壳维护工具 | 否 |
| `tests/` | 公共壳回归与集成场景 | 否 |
| `openspec/` | 公共壳自身规格与活跃变更 | 否 |
| `.github/` | 公共壳 CI 与发布 | 否 |
| `framework-manifest.json` | 分发文件与指纹单源 | 是 |

稳定路径 `skill/`、`tools/framework_core/` 和 `docs/framework/` 不因命名偏好迁移。所有文件仍须登记到 `framework-manifest.json`；复制到目标项目不等于需要进入该项目的业务仓库根目录。

## 文档迁移对照

| 原位置 | 目标位置 | 处理方式 |
|---|---|---|
| `docs/framework/` | 不变 | 保留公共规则稳定链接 |
| `docs/project-intake.md` | 不变 | 保留现行协议链接 |
| `docs/bootstrap.md` | 不变 | 保留高级 CLI 参考 |
| `docs/integrations.md` | 不变 | 保留集成参考 |
| 使用者目录与开发指南 | `docs/guide/` | 新增并链接到 README/BOOTSTRAP |
| 维护者布局、验证、发布说明 | `docs/maintainer/` | 新增，不分发到业务项目 |
| `docs/superpowers/plans/` | `docs/archive/plans/` | 已迁移并修正链接；新计划仍按技能约定写入原位置，完成后再归档 |
| `docs/acceptance.md` | `docs/archive/acceptance.md` | 已保留历史内容并修正链接 |
| `docs/verification/` | `docs/archive/verification/` | 已保留历史证据并修正链接；新验证按现行指南归置 |
| 活跃 OpenSpec change | 原位 | 不作为历史资料移动 |

## 所有权和状态

- 当前操作只从 README、BOOTSTRAP、AGENTS 和 `docs/framework/` 等现行入口获取。
- 历史资料只用于证据回溯，不控制当前需求、任务完成状态或发布结论。
- 旧 change 的任务、环境和证据缺口见[旧状态对账](legacy-change-status.md)；该报告不改变旧任务或生命周期状态。
- 公共包运行时采用显式白名单；新增位于允许目录的文件仍需进入清单并接受分发测试。
- 业务项目人工正文、模块规则、知识内容和活跃 change 不属于公共壳升级的可覆盖内容。

## 实施基线

2026-10-26 开始目录治理变更时，完整单元测试为 143 项通过。新变更规划文件尚未登记清单，因此当次 `check-framework` 只报告这些新增文件为 unexpected file；实施结束时必须重新生成清单并取得无失败结果。基线不包含真实宿主、私有仓库、设备或部署验收。
