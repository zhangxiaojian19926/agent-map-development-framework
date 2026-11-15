## Why

采用方项目的模块目录里出现了幻影模块。计划 `docs/plans/2026-11-15-remaining-batches-and-project-closure.md` 记载：目录中多出 `module-eb717aae36`，路径 `.worktrees/feishu-preflight`，92 个源文件全部位于 `.worktrees/` 下，内容是 `.superpowers/sdd/2026-10-24-feishu-preflight/*/before-fix/` 的历史快照。计划同时记载 376 个「源文件」里有 92 个是工作树快照。它不是业务模块。幻影模块一旦进入客观目录，关系地图、资料档案和覆盖统计都要覆盖它；档案必须覆盖目录里的每个模块，给它写档案会把这次扫描错误写进项目文档，资料接受因此停在 `INCOMPLETE_DOCUMENTATION`。

扫描不认 `.gitignore`。`tools/framework_core/modules.py` 的 `find_candidates` 与 `source_files` 只按 `EXCLUDED` 的目录名剪枝，不读取 `.gitignore`。计划记载采用方项目的 `.gitignore` 已写 `.worktrees/`，扫描仍走进该目录。`docs/maintainer/roadmap.md` §8 写明边界：发现阶段不改用 `.gitignore` 当排除依据，避免在索引之前依赖 git；只把确知的目录名写进排除清单。同文件里，带 `.git` 的非根目录会被登记为 `module-` 加路径摘要，所以工作树会被当成独立模块。

计划与 roadmap §8 都称 `modules.py` 与 `analysis_batches.py` 各有一份 `EXCLUDED`，内容一致，且都不含 `.worktrees`，并引用：

```
EXCLUDED = {'.git', '.framework', '.agent-framework', '.codegraph', '.agents',
            'node_modules', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv'}
```

本次读取源码：`modules.py` 第 11–12 行的集合与这段引文一致，不含 `.worktrees`。全仓库只有这一处 `EXCLUDED =`。`analysis_batches.py` 第 9 行是 `from .modules import EXCLUDED, EXTENSIONS`，第 95 行把 `sorted(EXCLUDED)` 写入分析会话 scope 的 `excluded_directories`，没有第二份字面量。计划里的「两份名单」与当前源码不一致；「不含 `.worktrees`」对这一处集合仍然成立。`module-eb717aae36` 与 92 个文件来自该计划的目录统计，本提案不重算摘要，也不重跑那个项目。

删工作树不能当解法。计划记载 `.worktrees/feishu-preflight` 里有 10 处未提交改动、一个未跟踪的计划文档，以及 92 个未跟踪的会话快照。那些改动留在采用方项目里。

## What Changes

- 在现有 `modules.EXCLUDED` 中加入 `.worktrees`。模块发现与源文件扫描都跳过这个目录名，`.worktrees/` 下的树不进入模块目录，也不计入该树的源文件。
- 分析会话的 `excluded_directories` 继续引用同一集合，因此同一改动让会话 scope 也包含 `.worktrees`。
- 用户确认的约束是：两处 `EXCLUDED` 都加上 `.worktrees`，两份名单保持各自一份，不合并成一个常量。按当前源码，两处使用已经指向 `modules.EXCLUDED`。本 change 只往这个集合加 `.worktrees`，不新增常量，也不把导入拆回两份字面量。
- 回归：构造带 `.worktrees/` 的工程，断言它不进模块目录。
- 行为变化落在既有能力 `module-lifecycle` 的发现边界，不新开 capability。

## Capabilities

### New Capabilities

- 无。排除工作树是收紧既有发现边界，不引入新 capability。

### Modified Capabilities

- `module-lifecycle`（`openspec/specs/module-lifecycle/spec.md`）：MOD-01「来源与有界发现」要写明发现与源文件扫描 MUST 跳过名为 `.worktrees` 的目录，该目录下的内容不得进入客观模块目录。现有规格只要求在确认的根或明确路径内扫描并拒绝越界，没有排除名单，也没有 `.worktrees`。

## Impact

- 将来修改 `tools/framework_core/modules.py` 的 `EXCLUDED`。`tools/framework_core/analysis_batches.py` 继续从 `modules` 导入该集合并写入 `scope.excluded_directories`。
- 将来增加回归：带 `.worktrees/` 的工程 fixture，断言该路径不出现在模块目录。
- 采用方项目 `/Users/zhangjiang/bigmodel_learn/61.videohao-generator` 及其 `.worktrees/feishu-preflight` 不在本 change 中删除或修改。那个项目的目录要等壳修好之后另行刷新，幻影模块才会从它的模块目录消失。
- 范围之外：不把 `.superpowers` 加入排除；不把排除依据改成读取 `.gitignore`；不纳入第 3 批 `verify-live` 的退出码。
