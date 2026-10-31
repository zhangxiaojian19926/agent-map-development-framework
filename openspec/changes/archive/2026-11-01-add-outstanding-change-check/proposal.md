## Why

复盘记录里留下一条真实的仓库级缺口：

> 没有任何检查会提示"这个 change 任务全勾了但没归档"。

代价已经付过一次。2026-10-31 审计八个活动 change 与规格库时，发现**六个 change 的任务 100% 完成，但它们的能力规格从未进 `openspec/specs/`**。规格库因此长期低估了工程壳实际拥有的能力——只读规格的人分不清"已完成的能力"和"不存在的能力"。这六份规格是人工补同步的，而补同步这件事**没有任何机制会提示去做**。

现有的两道 OpenSpec 校验都覆盖不到这个方向：`--all` 校验规格结构，`--archived` 校验已归档 change 的任务完成度。**"完成了却没归档"正好落在两者的缝隙里。**

## What Changes

- 新增只读工具 `tools/check-changes`：找出任务已全部完成却仍留在活动区的 change，并区分它缺的是能力规格同步、还是只差归档。
- 接入三处：`tools/pre-commit-check`（本地序列）、`.github/workflows/validate.yml`（每次推送与拉取请求）、`.github/workflows/release.yml`（打 tag 前）。
- 补测试覆盖各种形态：未完成的 change、没有任务文件的 change、能力未同步、已同步未归档、已归档、`skip_specs` 的 change、退出码与 JSON 输出。
- 更新维护者验证文档的基础检查清单。

## Capabilities

### New Capabilities

- `change-lifecycle`: 规定任务已完成的 change 必须进入规格库并归档，以及用于发现这类欠账的只读检查。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 新增 `tools/check-changes` 与 `tests/test_check_changes.py`。
- 修改 `tools/pre-commit-check`、`.github/workflows/validate.yml`、`.github/workflows/release.yml`、`tests/test_pre_commit_check.py`、`docs/maintainer/verification.md`。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程的语义。
