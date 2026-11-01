# Proposal

## Why

框架的欠账检查只保护框架自己，使用者项目里一份都没有。三个真实项目把这条缺口坐实了：`61.videohao-generator` 有 5 个 change、69 个已完成任务，`openspec/specs/` 与 `openspec/changes/archive/` 全空，doctor 长期报 `PARTIAL` 与 `STALE[INVALID_EVIDENCE]`；`23.auto_cut` 有 7 个已完成任务同样没收口。

需要的能力其实都在，只是没送达：

- `tools/check-changes` 的判定逻辑已经是 root-relative 的通用实现，但没有随运行时白名单分发，使用者项目里不存在这个文件。
- `doctor` 已装在 `.agent-framework/tools/` 里，也已准确报出 `PARTIAL` / `STALE` / `READY_FOR_PLANNING`，但它回答的是"初始化到哪一步"，不回答"欠了多少账"，而且没人跑、没人绑定。
- 地图证据失效检测（`STALE_EVIDENCE` / `INVALID_ANCHOR`）已在 `framework_core/maps.py` 里。

结果就是：使用者项目做出半成品，框架不会报警。videohao 那 69 个完成却未同步未归档的任务正躺在这个状态里——因为唯一能发现它的那道检查没跟过去。

## What Changes

- 把欠账判定逻辑下沉到 `tools/framework_core/closure.py`，`tools/check-changes` 改为调用它。功能不减，只搬家，两边共用一份判定。
- 新增 `tools/check-project`：只读扫描**使用者项目**，报告四类欠账——活动 change 中任务已完成但能力规格未同步、能力规格已同步但 change 未归档、地图登记的证据因源码漂移而失效、工程初始化未完成。随运行时白名单分发。
- 欠账检查默认只报告、退出码 0；加 `--strict` 时有欠账才非零退出。Agent 不会被欠账卡死，CI 模板里显式使用 `--strict`。
- 提供使用者项目的持续集成模板，作为可选片段提供，不自动写入用户项目的 CI。
- 在 `61.videohao-generator` 上实跑收口，作为该能力在真实项目上的唯一验收证据。

## Capabilities

### New Capabilities

- `project-closure-check`: 规定面向使用者项目的收口检查——它检查什么、随什么分发、退出码语义、能否接入目标项目的持续集成。

### Modified Capabilities

- `change-lifecycle`: 「检查接入三处」此前只覆盖公共壳自身的三条流水线，补上使用者项目也能自行运行并接入其持续集成。

## Impact

- 新增 `tools/framework_core/closure.py`、`tools/check-project`、`tests/test_project_closure.py`。
- 修改 `tools/check-changes`（改为调用下沉后的判定）、`tools/framework_core/generation.py`（运行时白名单）、`tests/test_bootstrap_generation.py`（载荷夹具）。
- 新增使用者项目持续集成模板到 `templates/`，并更新分发清单与 `docs/maintainer/verification.md`。
- 修改 `61.videohao-generator` 项目：收拢未提交改动、同步 5 个 change 的能力规格、归档可归档的 change、按封存处理需要真人闭环的那一个。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程的语义；不改变任何既有门禁的判据。
