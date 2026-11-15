## 1. 文件与断言必须在工作树里

- [x] 1.1 守住 KI-02「文件或断言不在工作树中被报出」，以及 KI-04「第二版回执带生效记录」的同一条核对：页在清单里、task 在 `tasks.md` 里，但 `file` 不存在或文件文本没有 `assertion` 时，完成检查必须把该 change 留成欠账并指出是哪一条。先改测试、不改生产校验。完成：该测试失败，原因是虚构的 `file`/`assertion` 仍被接受，而不是导入或路径错误。
  证据：改校验前 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest` 跑这两项，`Ran 2 tests`，`FAILED (failures=2)`。两例都是 `AssertionError: 'is still active and should be archived' != 'knowledge receipt is not acceptable'`。不存在的 `src/a.py` 和文件里没有的 `test_a` 仍被接受。
- [x] 1.2 只收紧 `influenced_errors` 这一处，让 1.1 变绿。不新开入口，不把 KI-04 做成第二套机制。完成：1.1 的测试通过；页不在清单、task 不存在、带理由的 `not_applicable` 这三条旧规则仍按原样报出或放行。
  证据：同一命令加上页缺失、task 缺失、`not_applicable` 放行三项，`Ran 5 tests in 0.019s`，`OK`。

## 2. 文件必须写出知识页路径

- [x] 2.1 守住 KI-02「文件未写出知识页路径被报出」，KI-04 用同一条接受条件：文件在，断言在，但文件文本没有这条知识页路径时，必须报出并留在现有欠账。先写会失败的测试。完成：失败原因是这种文件仍被接受。
  证据：只加页路径核对之前，`test_a_v2_receipt_rejects_a_file_that_does_not_cite_the_page` 失败：`AssertionError: 'is still active and should be archived' != 'knowledge receipt is not acceptable'`。`Ran 1 test`，`FAILED (failures=1)`。
- [x] 2.2 在同一处校验里补上「文件文本包含该条知识页路径」。完成：2.1 变绿，1.1 仍然通过。
  证据：页路径、缺文件、缺断言三项 `Ran 3 tests in 0.014s`，`OK`。

## 3. 越出项目根

- [x] 3.1 守住 KI-02「越出项目根的文件被报出」：`file` 离开完成检查所看的项目根时必须报出，即使项目外的文件里同时写了断言和页路径。先写会失败的测试。完成：失败原因是越界路径仍被接受。
  证据：加上 `safe_path` 之前，`test_a_v2_receipt_rejects_a_file_that_escapes_the_project_root` 失败：`AssertionError: 'is still active and should be archived' != 'knowledge receipt is not acceptable'`。项目外的 `../outside.py` 同时写了 `test_a` 和页路径，仍被接受。`Ran 1 test`，`FAILED (failures=1)`。
- [x] 3.2 用现有路径边界拒绝越界，仍走同一条欠账。完成：3.1 变绿，项目根内对得上的记录不被误伤。
  证据：越界、缺文件、缺断言、缺页路径四项 `Ran 4 tests in 0.021s`，`OK`。

## 4. 对得上时放行，旧行为不放宽

- [x] 4.1 守住 KI-02「文件、断言与页路径同时在场时通过对上」和「带理由的不适用不要求工作树文件」，以及既有「页路径不在清单里被报出」「task 标识不存在被报出」。完成：对得上的 v2 回执仍只剩「尚未归档」；`not_applicable` 加理由、v1 不追溯、概念页来源不可核对，期望都不放宽。证据是相关测试的一次新鲜输出。
  证据：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_changes`，`Ran 38 tests in 0.159s`，`OK`。其中对得上的文件只剩 `still active`；页缺失、task 缺失、`not_applicable` 放行、v1 不追溯、概念页来源不可核对仍是原期望。

## 5. 政策与范围

- [x] 5.1 在 `docs/framework/knowledge-policy.md` §11.5 的回执段落写上同一条工作树核对。授权表、概念页仍须本次授权、`find_matches` 不按作废丢页、flow-01 到 flow-15 的 description，都不改。完成：该段与 KI-02 一致，diff 里没有这些范围外的文件。
  证据：§11.5 回执段写明 `file` 与 `assertion` 必须出现在工作树文件文本里且该文件包含知识页路径，越出项目根算对不上，带理由的 `not_applicable` 不要求工作树文件。`git diff --name-only` 的已跟踪改动只有 `knowledge-policy.md`、`tests/test_check_changes.py`、`tools/framework_core/closure.py`。没有 flow description、`wiki.py`、主规格或另一仓库。
