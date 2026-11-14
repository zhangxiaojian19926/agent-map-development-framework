# 执行计划：剩余批次与真实项目收口

> 2026-11-15 起执行的记账。上一份是 [`2026-11-14-knowledge-concept-pages.md`](2026-11-14-knowledge-concept-pages.md)（本体语义落进知识层），那批已完成并归档。
> 本文件记录**当前已完成什么、剩下什么、顺序怎么排**，并维护者 [roadmap](../maintainer/roadmap.md) 配套。
> 涉及两个仓库：公共壳 `62.project_arch`（下文称**壳**）与采用方 `61.videohao-generator`（下文称**项目**）。

## 目标

把 roadmap 剩下的批次按"能不能自己做完"重新排序，并让真实项目真正走完一次闭环——这是框架成熟度的唯一计量方式。

## 进度总表

| 批次 | 内容 | 状态 | 证据 |
|---|---|---|---|
| 知识层的概念语义与可纠正性 | 本体语义落进知识层 | **已完成** | 壳 `7f2e4e8`、优化记录两条、roadmap 第 15 行 |
| 第 1 批 真实项目接入验证 | 用 videohao-generator 走完收口 | **进行中** | 项目 `e41bf75`（实现+载荷升级）、`fc412ba`（6 个能力规格同步）；余下回执与归档、文档接受 |
| 第 2 批 知识回流真实验证 | 解决真问题 → 摄入 → 校验 → 再检索得到 | **进行中** | 机制已具备（`knowledge-receipt/v2` + `influenced`）；内容待写真实问题 |
| 第 3 批 verify-live 真实验收复跑 | 让端到端验收能跑通 | **已定位，待修** | 失败点已定位到 `existing-bootstrap` 的期望值过时 |
| 第 4 批 计划/评审端到端探针 | 给 verify-live 加两个合成步骤 | 未开始 | — |
| 第 5 批 规格库与阶段路由一致性复核 | 写只读核对工具并进 CI | 未开始 | — |
| 第 6 批 15 条工作流指南逐条复核 | 指南与现技能逐条对齐 | 未开始 | — |
| 第 7 批 技能路由核对方法 | 防复发 | **已闭环** | `check-framework` 的 `skill_routing_errors` + `local_layer_errors` 均在 CI，差异为零 |

## 已完成

### 壳（`62.project_arch`，分支 `main`）

| 提交 | 内容 |
|---|---|
| `5b13648` | 把工作区里此前就存在的 `.memsearch` 未提交改动单独成条提交（`.gitignore` + `tools/check-framework` 的 SKIP + 刷新指纹） |
| `3c042c2` | 落盘本体论集成的实施计划（`docs/plans/2026-11-14-knowledge-concept-pages.md`）+ roadmap 第 8 批 + CHANGELOG |
| `7f2e4e8` | **实现本体语义**：概念页、适用条件、可纠正状态机、`knowledge-receipt/v2` 与 `influenced`、失败归因五层、doctor 引用计数。两个 change 已归档 |
| `ebd8210` | 维护者账本收尾：优化记录两条、roadmap 第 8 批移出"还没做的"并进完成表、CHANGELOG |
| `ddca382` | 删掉 roadmap 授权表里重复的一行 |

验证：六道门禁全绿（`check-framework` 605 文件/42 技能、`openspec validate --all --strict` 45 项、`--archived` 33 项、`check-changes` PASS、`git diff --check` clean）；486 项单测通过（基线 454，新增 32）；**变异检验**证明新测试在测行为——关掉新校验后 14 项失败，恢复后全绿。

### 项目（`61.videohao-generator`，分支 `main`）

| 提交 | 内容 |
|---|---|
| `e41bf75` | 四个已完成 change 的实现与验收证据一次性进版本库（业务代码 11 个文件、测试、资产、验收报告）；安装载荷从旧版升级到当前分发版；`pytest tests` **563 passed, 1 skipped** |
| `fc412ba` | 把六个能力规格同步进 `openspec/specs/`：`cover-title-logo`、`audio-material-coverage`、`enhance-consent`、`reference-audio-material-flow`、`material-subtitle-safety`、`reference-visual-style` |

`stabilize-feishu-video-delivery` 的 `feishu-video-workflow` **不同步**——它 30 项任务里第 7.3 项（真人飞书闭环）未完成，未完成的能力不进规格库。

## 新发现：框架的源码发现不排除 `.worktrees/`

**这是本轮最有价值的产出，且它正是真实项目才能暴露的东西。**

**症状**：项目的模块目录里多了一个 `module-eb717aae36`，路径 `.worktrees/feishu-preflight`，92 个源文件——全部是 `.superpowers/sdd/2026-10-24-feishu-preflight/*/before-fix/` 下的历史快照副本。它不是业务模块，是 superpowers 工作树被源码扫描当成了独立模块。

**证据**：

```
$ python3 -c "import json; c=json.load(open('module-catalog.generated.json')); ..."
root                   284 个源文件
module-eb717aae36      92 个源文件   ← 全部位于 .worktrees/ 下
```

**根因**：`tools/framework_core/modules.py` 与 `tools/framework_core/analysis_batches.py` 各有一份 `EXCLUDED`，两份内容完全一致，但都不含 `.worktrees`：

```
EXCLUDED = {'.git', '.framework', '.agent-framework', '.codegraph', '.agents',
            'node_modules', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv'}
```

框架的源码发现**不认 `.gitignore`**。项目的 `.gitignore` 明明写着 `.worktrees/`，扫描照样进去。

**影响**：幻影模块污染模块目录、关系地图、资料档案与覆盖统计（376 个"源文件"里有 92 个是工作树快照）。直接后果是项目资料无法接受——档案必须覆盖目录里的每个模块，而给幻影模块写档案等于把 bug 固化进项目文档。

**为什么不删那个工作树**：采用方项目里的 `.worktrees/feishu-preflight` 里有 **10 处未提交改动**（`videohao_gen/bot/steps.py`、`cli.py`、`ffmpeg.py`、`tests/test_asr.py` 等）与一个未跟踪的计划文档，外加 92 个未跟踪的会话快照。删它就是毁掉未完成的工作。

**正解**：框架侧把 `.worktrees` 加进两份 `EXCLUDED`，从源头消除幻影模块，并防止下一个项目再踩。

## 阻塞

| 阻塞 | 卡住谁 | 解法 |
|---|---|---|
| 幻影模块 `module-eb717aae36` | 项目的资料接受（`accept-docs` 报 `INCOMPLETE_DOCUMENTATION`） | 框架侧修 `EXCLUDED` → 重生成目录 → 档案只需 `root` |
| `verify-live` 的 `existing-bootstrap` 期望 exit 0，但 `framework init` 现在退出 5（`WAITING_AGENT`，因为 dossier 与关系地图要 agent 先产出） | 第 3 批 | 二选一：让该步接受"等待 agent"的中间态，或给它补上 agent 分析环节 |
| 项目知识库 8 个目录全空（只有 `requirements/` 有内容） | 第 2 批的"再检索得到" | 先把上面这个真问题写成问题页，再写概念页 |
| 效果评测（时间切分双组） | 无法说本体语义层带来多少收益 | 属效果研究，另立项 |

## 更新后的执行顺序

1. **壳侧**：为 `.worktrees` 排除开一个 OpenSpec change → 改两份 `EXCLUDED` → 加回归用例（构造带 `.worktrees/` 的工程，断言它不进模块目录）→ 同步规格 → 回执 → 归档。
2. **项目侧**：用修好的壳重新 `prepare`/刷新目录 → 幻影模块消失 → 按已重建好的档案接受资料 → `initialization` 回到 `COMPLETE`。
3. **项目侧**：四个 change 写需求页 + `knowledge-receipt/v2` 回执（含 `influenced`）→ 归档 → `check-project` 不再报欠账。**这是第 1 批的闭环判据。**
4. **项目侧**：把"幻影模块"这个真问题写成问题页（带 `applies_when` / `not_applicable_when`、来源哈希、置信度）→ 索引与日志更新 → 换一个会话检索命中。**这是第 2 批的闭环判据。**
5. **项目侧**：写第一张真实的 concept 页——术语定义留在项目文档，扩展语义入库，用来源哈希锚定；验证术语改动后能检出失配。
6. **壳侧**：第 3 批（修 `verify-live` 期望值）→ 第 4 批（加计划/评审探针）→ 第 5 批（一致性核对工具进 CI）→ 第 6 批（指南逐条复核）→ 第 7 批从 roadmap 移出。

第 1–5 步是一条链：框架侧修一处 → 项目侧收口 → 真实知识回流。第 6 步可以并行，不依赖前五步。

## 证据分级

- **已确认**：壳与项目的提交号、门禁与单测结果、幻影模块的目录证据、两份 `EXCLUDED` 的内容比对、工作树内 10 处未提交改动。均由本机实跑与逐文件读取所得。
- **设计**：本文件的批次排序、`.worktrees` 的改法、`verify-live` 的两条候选解法。`EXCLUDED` 的具体改法尚未实现，未在代码里跑过。
- **未验证**：改完 `EXCLUDED` 后项目侧重新收口的完整链路；第 2 批"换一个会话检索命中"要等写入完成才能做；效果评测全部未做。
