## Why

复盘记录里留下了两条命名不一致，都会在日常使用中变成实际的时间损耗：

1. **技能目录名与调用前缀不一致。** 技能组的目录是 `skill/super-powers/`，而技能之间互相引用、阶段路由表点名时用的是 `superpowers:` 前缀。搜目录名和搜前缀会得到两套结果——这在引入技能时已经真实发生过一次。
2. **计划文档的位置仍带着已退役技能的名字。** 计划技能迁到别的分组后，`docs/superpowers/plans/` 仍是文档里声明的计划位置约定，而该目录在仓库里已经不存在，只剩一个磁盘上的空目录。

另外两处相关问题一并处理：发布工作流的 cron 落在整点，实际运行比计划晚了 5.5 小时；运行时排除清单里还有一条早已失效的路径。

## What Changes

- 把 `skill/super-powers/` 改名为 `skill/superpowers/`，使目录名与调用前缀一致。
- 把计划文档位置约定改为 `docs/plans/`，同步更新迁移对照表、目录归属表、运行时排除清单与两处技能内的示例路径，并清理磁盘上的残留空目录。
- 发布工作流的 cron 由 `0 2 * * 1` 改为 `17 2 * * 1`，避开整点的调度高峰。
- 更新复盘记录中对应的两条候选状态。

## Capabilities

### New Capabilities

- `path-alignment`: 规定技能目录名与调用前缀一致、计划文档位置的约定、发布调度避开整点，以及已失效路径引用必须清理。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 目录改名：`skill/super-powers/` → `skill/superpowers/`（11 个技能入口的文件随之移动）。
- 修改 `tools/framework_core/generation.py` 的运行时排除清单、`docs/maintainer/repository-layout.md` 的两张表、`docs/integrations.md`、`THIRD_PARTY_NOTICES.md`、两个技能内的示例路径、`tests/test_bootstrap_generation.py` 的夹具。
- 修改 `.github/workflows/release.yml` 的调度表达式。
- 更新 `docs/maintainer/retro-findings.md` 中两条候选的状态。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程的语义。
