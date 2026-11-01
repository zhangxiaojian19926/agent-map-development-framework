# 实施任务

> 切片依据 [to-tickets](../../../../skill/matt-pocock/to-tickets/SKILL.md)：每条是一个端到端可验证的垂直切片，附阻塞边。
> 详细实施细节（文件、接口、命令）在 [`docs/plans/2026-11-01-project-closure-check.md`](../../../../docs/plans/2026-11-01-project-closure-check.md)，那里不重复任务状态。

## 1. 欠账检查到达使用者项目

- [x] 1.1 欠账判定下沉到公共运行时模块，公共壳自己的检查行为不变
  - 交付行为：欠账判定成为运行时载荷里的一份实现，公共壳现有的"完成却没归档"检查调用它且结论完全一致
  - 阻塞于：无
  - 覆盖：`project-closure-check` / 两边判定一致；`change-lifecycle` / 本地在提交前发现、发布前被拦
  - 验收：公共壳自己的检查输出与下沉前逐字一致；下沉后的模块随公共包进入使用者项目
  - 模块与文件：`tools/framework_core/closure.py`（新增）；`tools/check-changes`（改为调用）；`tools/framework_core/generation.py`（运行时白名单）
  - 接口：新增 `closure.outstanding_changes(root)`，返回 `[{change, problem, capabilities}]`；`closure.map_evidence_problems(root)` 返回地图证据问题列表；`closure.initialization_problems(root, report)` 返回初始化缺口列表
  - 测试：现有 `tests/test_check_changes.py` 全绿（行为等价的证据）；新增单测断言同一仓库在两侧得到同一结论

- [x] 1.2 使用者项目能自己跑出四类欠账清单
  - 交付行为：使用者项目装上公共包后，运行随包分发的检查就能看到未同步规格的 change、未归档的 change、失效的地图证据与未完成的初始化
  - 阻塞于：1.1
  - 覆盖：`project-closure-check` / 使用者项目能直接运行、报出未同步的 change、报出未归档的 change、报出失效的地图证据、报出未完成的初始化、检查不修改仓库、默认只报告、严格模式失败
  - 验收：在真实项目上运行能报出该项目的实际欠账；运行前后仓库内容不变；默认退出码 0，`--strict` 时有欠账则非零退出且清单与默认模式相同
  - 模块与文件：`tools/check-project`（新增）；`tools/framework_core/generation.py`（白名单）；`tests/test_project_closure.py`（新增）
  - 接口：消费 `closure.outstanding_changes` 与 `closure.map_evidence_problems`；输出人可读报告与 `--json` 机器可读报告
  - 测试：四类欠账各有一条 RED 用例（造出偏差 → 检查报出）与一条 GREEN 用例（当前仓库通过）；一条用例断言运行前后仓库不变

## 2. 使用者项目能把检查接进自己的持续集成

- [x] 2.1 持续集成模板按需提供，不改用户已有配置
  - 交付行为：使用者项目能取到一份可用的持续集成模板并自行采用，模板跑欠账检查与规格校验
  - 阻塞于：1.2
  - 覆盖：`project-closure-check` / 模板可取用、不改用户已有配置
  - 验收：模板随公共包分发且标明 OpenSpec CLI 的固定版本；公共包升级不写改使用者项目已有的持续集成配置
  - 模块与文件：`templates/project-ci.yml`（新增）；`tools/framework_core/generation.py`（白名单已含 `templates/`）；`tests/test_project_closure.py`
  - 接口：模板调用 `tools/check-project --strict` 与 `openspec validate --all --strict`
  - 测试：模板通过分发结构检查的链接与语法校验；一条用例断言目标项目安装后已有持续集成配置未被改写

## 3. 真实项目收口（另立 change）

收口 `61.videohao-generator` 写的是那个项目自己的仓库与规格，不属于本 change 的任务范围。它在工程壳这一侧的前置条件是本 change 交付的 `tools/check-project`——先安装到该项目的运行时载荷，才能在那里跑。

收口的详细步骤与实测现状见 [`docs/plans/2026-11-01-project-closure-check.md`](../../../../docs/plans/2026-11-01-project-closure-check.md) 的最后一节。

## 4. 验证与归档

- [x] 4.1 `python3 tools/check-framework` 通过
- [x] 4.2 `python3 -m unittest discover -s tests` 全量通过
- [x] 4.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 4.4 `openspec validate --archived --no-interactive` 通过
- [x] 4.5 `python3 tools/check-changes` 无欠账
- [x] 4.6 提交后 `git diff --check HEAD^ HEAD` 无空白错误
- [x] 4.7 同步能力规格到 `openspec/specs/` 并归档本 change
