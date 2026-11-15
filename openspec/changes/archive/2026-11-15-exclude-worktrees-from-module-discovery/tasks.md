## 1. 先写会失败的回归

- [x] 1.1 在改生产代码之前，先写会失败的测试：构造带 `.worktrees/<name>/` 的工程，其内有 `.git` 与源文件；断言模块目录没有该子树的模块路径，任何模块的源文件清单也没有该子树中的文件。验证：此时测试失败，失败原因是子树仍被发现。关联 MOD-01 / MOD-01-WORKTREE。
  证据：改 `EXCLUDED` 之前，`python3 -m unittest` 跑三项新测试，`test_worktree_subtree_stays_out_of_module_catalog` 失败，`AssertionError: True is not false`（`.worktrees/` 子树仍被发现）。
- [x] 1.2 在改生产代码之前，先写会失败的测试：开始一次分析会话，断言会话记录的排除目录名单与发现所用的排除集合相同且包含 `.worktrees`，会话收录的源文件只来自模块目录里已有的源。验证：此时测试失败，失败原因是集合里还没有 `.worktrees`。`analysis_batches.py` 已从 `modules` 导入 `EXCLUDED`，本任务不给它写第二份字面量。关联 MOD-01 / MOD-01-EXCLUDED-SCOPE。
  证据：同一次 RED，`test_session_excluded_directories_match_discovery_set` 失败，`Items in the second set but not the first: '.worktrees'`。
- [x] 1.3 在改生产代码之前，先写会失败的测试：工程的 `.gitignore` 写有 `.worktrees/`，另有一个被 `.gitignore` 点名、但目录名不是 `.worktrees` 的子目录，其中有 `.git` 与源文件。断言 `.worktrees` 子树不进模块目录，而那个仅被 gitignore 点名的子目录仍可被发现。验证：此时测试失败，失败原因是 `.worktrees` 子树仍进入目录；发现代码路径不读取 `.gitignore`。关联 MOD-01 / MOD-01-GITIGNORE。
  证据：同一次 RED，`test_gitignore_does_not_select_discovered_directories` 失败，`AssertionError: True is not false`（`.gitignore` 已写 `.worktrees/`，子树仍进入目录）。合计 `Ran 3 tests`，`FAILED (failures=3)`。

## 2. 改唯一的排除集合

- [x] 2.1 仅在 1.1–1.3 已经失败之后，把 `.worktrees` 加进 `tools/framework_core/modules.py` 现有那一份 `EXCLUDED`。保持 `analysis_batches.py` 的导入，不新增字面量，也不把这份集合收成新抽象或新常量名。验证：重跑 1.1–1.3，三项转为通过。关联 MOD-01 / MOD-01-WORKTREE、MOD-01-EXCLUDED-SCOPE、MOD-01-GITIGNORE。
  证据：只改 `modules.py` 的 `EXCLUDED` 后重跑上述三项，`Ran 3 tests in 0.027s`，`OK`。

## 3. 既有场景保持

- [x] 3.1 重跑 `tests/test_bootstrap_modules.py` 里已有的有界发现、符号链接越界拒绝，以及非 `.worktrees` 嵌套仓库仍能被发现的断言。验证：这些测试仍然通过，不改其期望。关联 MOD-01 / MOD-01-IMPORT、MOD-01-ESCAPE。
  证据：`python3 -m unittest tests.test_bootstrap_modules`，`Ran 5 tests in 0.029s`，`OK`。既有三项期望未改。

## 4. 明确不做

- [x] 4.1 核对完成后的 diff：排除集合只多了 `.worktrees`，没有 `.superpowers`；没有第二份排除名单，也没有新的共享常量。验证：`analysis_batches.py` 仍是 `from .modules import EXCLUDED`，diff 里没有新的 `EXCLUDED =`。关联 MOD-01；design 的 Non-Goals。
  证据：`git diff --stat` 生产代码只有 `tools/framework_core/modules.py | 2 +-`，该 diff 仅在原字面量末尾加上 `.worktrees`。`analysis_batches.py` 不在 diff 中。
- [x] 4.2 核对本 change 没有删除采用方工作树，没有修改 `61.videohao-generator`，也没有处理 `verify-live` 退出码 5。验证：该仓库不在本次 diff 中，任务 2.1 的改动只在本仓库的 `modules.py` 与新增回归。关联 design 的 Non-Goals。
  证据：本仓库 `git status --short` 只有两个测试文件、`modules.py` 和本 change 目录。diff 不含 `videohao-generator`、`.superpowers` 或 `verify-live`。
