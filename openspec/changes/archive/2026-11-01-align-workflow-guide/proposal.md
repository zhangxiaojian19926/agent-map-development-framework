## Why

把 `docs/guide/from-zero-to-one.md` 的 15 条工作流与当前框架逐条比对后，发现文档与框架自身契约不一致。这份指南是读者照着执行的操作手册，不一致等于发了一份会跑偏的手册。

1. **摘要流程行漏一步。** `development-workflow.md` 的完整行为变更路线写成 `TASK_SELECTED → RED → GREEN → REFACTOR → TASK_VERIFIED`，漏了同文件 §8 的第 4 步 `REGRESSION`。分节里写着、指南工作流 2 的路径 D 里也写着，只有摘要行没有。`git log -L` 确认是 2026-09-25 首次提交就带的老问题。

2. **指南工作流 14 漏了一道门禁。** 流程行与提示词只列四项，CI 里已跑六道——2026-11-01 新增 `check-changes` 时改了 CI 与维护者文档，漏改了面向读者的指南。

3. **三处文档都写着同一个失效的发布时刻。** 调度从 `0 2 * * 1` 改为 `17 2 * * 1`（避开整点高峰）时，只改了工作流、规格和 CHANGELOG。指南工作流 15、`docs/maintainer/release.md`、`README.md` 至今仍写"02:00 UTC（北京时间 10:00）"，实际是 02:17 UTC / 10:17。

第 3 条说明：逐条比对指南能发现指南的问题，发现不了 README 和维护者文档的问题——这类漂移必须靠机器检查，不能靠人记得。

三处的共同点是**没有任何机制会提示它们漂移**。修完不加以检查，下次加门禁、改调度、改实现阶段步骤时还会再漂一次。

## What Changes

- 补齐 `docs/framework/development-workflow.md` 实现阶段摘要行中的 `REGRESSION`，使摘要行与 §8 的分节步骤一致。
- 补齐 `docs/guide/from-zero-to-one.md` 工作流 14 的流程行与提示词，列出当前全部六道门禁（含 `openspec validate --archived` 与 `check-changes`）。
- 修正三份文档中已过期的定时发布时刻：`docs/guide/from-zero-to-one.md` 工作流 15、`docs/maintainer/release.md`、`README.md`，统一为 02:17 UTC / 10:17 北京时间。
- 在 `tools/check-framework` 中新增文档契约检查：实现阶段摘要行必须包含分节声明的全部步骤；指南工作流 14 必须列出 CI 实际运行的全部门禁；所有陈述发布调度时刻的活文档必须与发布工作流的调度表达式一致。
- 为新增检查补单元测试：既验证检查能发现偏差（RED），也验证当前仓库实际通过（GREEN）。

## Capabilities

### New Capabilities

- `workflow-guide-consistency`: 规定框架的流程契约、对外指南与 CI 实际执行三者之间的一致性要求，以及用于发现这类漂移的自动检查。

### Modified Capabilities

- `tdd-practice`: 明确实现阶段的任务循环步骤序列，把 `REGRESSION` 写进规格事实源，而不是只存在于分节正文。

## Impact

- 修改 `docs/framework/development-workflow.md` 的完整行为变更路线摘要行。
- 修改 `docs/guide/from-zero-to-one.md` 的工作流 14（流程行与提示词）与工作流 15（定时时刻）。
- 修改 `docs/maintainer/release.md` 与 `README.md` 的定时发布时刻。
- 修改 `tools/check-framework`，新增 `doc_contract_errors` 检查并接入 `main()`。
- 新增 `tests/test_doc_contract.py`。
- 更新 `docs/maintainer/verification.md` 的基础检查清单与 `framework-manifest.json` 分发清单。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程的语义；不改变任何门禁本身的判据，只增加对文档描述的校验。
