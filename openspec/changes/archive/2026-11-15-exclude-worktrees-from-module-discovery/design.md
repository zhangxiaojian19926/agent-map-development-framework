## Context

动机见 `proposal.md` 的 Why。本设计只记录实现所依赖的源码事实。

本次核对：全仓库 Python 里只有 `tools/framework_core/modules.py` 第 11–12 行有一处 `EXCLUDED = {...}`，集合与计划引文一致，不含 `.worktrees`。`find_candidates` 与 `source_files` 都用这个集合按目录名剪枝；带 `.git` 的非根目录会登记为 `module-` 加路径摘要。`tools/framework_core/analysis_batches.py` 第 9 行 `from .modules import EXCLUDED, EXTENSIONS`，第 95 行把 `sorted(EXCLUDED)` 写入分析会话 `scope.excluded_directories`。`tools/` 内没有第二处读取该字段，会话也不另走一遍目录树。计划里「两份 `EXCLUDED` 字面量」与当前源码不一致。

## Goals / Non-Goals

**Goals:**

- 在现有这一份排除集合中加入 `.worktrees`，使已确认发现根下名为 `.worktrees` 的目录及其整棵子树不进入模块目录，其中源文件也不计入任何模块。
- 分析会话记录的 `excluded_directories` 继续等于这一份集合，因此包含 `.worktrees`。
- 回归：构造带 `.worktrees/` 的工程，断言该子树不进模块目录。

**Non-Goals:**

- 不把 `.superpowers` 加入排除集合。
- 不删除采用方工作树。
- 不修改 `61.videohao-generator`，也不刷新它已经生成的模块目录。
- 不处理第 3 批 `verify-live` 的退出码 5。
- 不新增第二份排除名单，也不把现有一处字面量收成新的抽象或新常量名。
- 不改为读取 `.gitignore`。

## Decisions

1. **只改 `modules.EXCLUDED` 这一处字面量，加入 `.worktrees`。** `analysis_batches.py` 保持导入。发现剪枝和会话 `excluded_directories` 因此同时带上这个名字。已考虑的替代：按计划再抄一份字面量到 `analysis_batches.py`。当前源码没有第二份，用户已确认不新增第二份名单，故不抄。另一替代：新建一个共享常量把「两份」收拢。当前已经是一处定义加导入，再包一层不改变行为，用户已确认不收成新抽象，故不做。

2. **继续按目录名剪枝，不读 `.gitignore`。** 现有扫描只判断子目录名是否在 `EXCLUDED` 中。`.worktrees` 走同一条路径。已考虑改为信任 `.gitignore`。发现阶段不把 gitignore 当排除依据，本 change 保持该边界。

3. **回归用新建的工程，不断言采用方仓库。** 构造一个含 `.worktrees/<name>/` 的工程，其内有 `.git` 与源文件，断言模块目录没有该子树的模块路径，也没有该子树的源文件。会话侧只断言记录的排除目录名单含 `.worktrees`，并与发现所用集合相同。

## Risks / Trade-offs

- [计划仍写着两份字面量] → 实现以本次读到的源码为准，只改一处；不把导入拆回去。
- [采用方目录里已经收录的幻影模块] → 本 change 不重写那个目录。再次同步时，已消失的模块仍按既有 MOD-03 保留 missing 历史。回归覆盖的是新工程里子树从一开始就不进入目录。
- [排除集合只认目录名 `.worktrees`] → 其他名字的工作树目录不会被这条规则跳过。这是有意的窄改动。

## Migration Plan

- 无数据迁移，无安装步骤。
- 不改采用方仓库，不删除其 `.worktrees/feishu-preflight`。
- 回滚时从这一份 `EXCLUDED` 去掉 `.worktrees`。会话记录随同一集合回到改前内容。
