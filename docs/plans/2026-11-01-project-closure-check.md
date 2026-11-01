# 实施计划：使用者项目收口检查

> 配套 [`openspec/changes/2026-11-01-project-closure-check/`](../../openspec/changes/archive/2026-11-01-project-closure-check/)。
> 任务状态只在该 change 的 `tasks.md` 里，本文件不重复它，只写文件、接口、命令。

## 目标

公共壳的欠账检查现在只保护公共壳自己。使用者项目装上公共包后拿不到任何能自动发现欠账的东西，于是四个真实项目里做出的东西都停在"做完了但没收口"的状态。

本计划把欠账判定下沉到公共运行时模块，做一个随包分发的只读检查报出四类欠账，再在真实项目上跑一遍收口。

## 文件

| 文件 | 动作 | 说明 |
|---|---|---|
| `tools/framework_core/closure.py` | 新增 | 欠账判定。四类欠账的判定逻辑都在这里 |
| `tools/check-changes` | 改 | 改为调用 `framework_core.closure`，输出与退出码不变 |
| `tools/check-project` | 新增 | 使用者项目用的只读检查 |
| `tools/framework_core/generation.py` | 改 | 运行时白名单加 `tools/check-project` |
| `templates/project-ci.yml` | 新增 | 使用者项目的持续集成模板 |
| `tests/test_check_changes.py` | 改 | 加载方式加 `tools/` 到 `sys.path` |
| `tests/test_project_closure.py` | 新增 | 四类欠账的 RED 与 GREEN 用例 |

## 接口

```python
# tools/framework_core/closure.py

def outstanding_changes(root):
    """活动区里任务已完成但未同步规格或未归档的 change。

    返回 [{'change', 'tasks', 'problem', 'detail'}, ...]
    """

def map_evidence_problems(root):
    """地图登记的证据与当前源码不符的地方。

    返回 [{'kind', 'detail'}, ...]；kind 区分源码漂移与锚点丢失。
    """

def initialization_problems(root):
    """工程接入未完成的地方。

    返回 [{'dimension', 'status', 'detail'}, ...]
    """
```

`tools/check-project` 消费这三个函数，`tools/check-changes` 只消费第一个。

## 命令

```bash
# 使用者项目里
python3 .agent-framework/tools/check-project --root .
python3 .agent-framework/tools/check-project --root . --strict      # 有欠账则非零退出
python3 .agent-framework/tools/check-project --root . --json       # 机器可读
```

退出码语义：默认恒为 0 并打印报告；`--strict` 时有欠账返回 1，无欠账返回 0。两种模式的欠账清单内容一致。

## 为什么默认只报告

使用者项目接入公共包的当天必然是红的——欠账是历史积累，不是接入失败。默认失败会把 Agent 卡在接入阶段，而公共壳自己的两个老 change 就是这么挂了一年。把"欠账即失败"的决定权交给接入持续集成的人，由他们在模板里显式写 `--strict`。

## 测试命令

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_changes tests.test_project_closure -v
python3 tools/check-framework
python3 tools/check-project --root . --strict
```

## 真实项目收口（另立 change）

目标：`61.videohao-generator`。

### 实测现状（2026-11-01，用本 change 交付的检查跑出来的）

```text
DEBT change fixed-cover-title-logo (10/10 tasks) capabilities are not synced into openspec/specs/: cover-title-logo
DEBT change material-coverage-and-clarity (13/13 tasks) capabilities are not synced into openspec/specs/: audio-material-coverage, enhance-consent
DEBT change reference-audio-pause-material-flow (8/8 tasks) capabilities are not synced into openspec/specs/: reference-audio-material-flow
DEBT change unify-reference-visual-style (10/10 tasks) capabilities are not synced into openspec/specs/: material-subtitle-safety, reference-visual-style
DEBT initialization is PARTIAL: the project is not fully taken in
DEBT documentation is STALE: INVALID_EVIDENCE
```

第五个 change `stabilize-feishu-video-delivery` 没有出现在清单里——它还有 1 个未勾任务（真人闭环），未完成的 change 不算欠账，这与框架的判定一致。

### 收口顺序不能颠倒

1. **先收拢工作树。** 43 项未提交改动（21 个源文件、11 个测试文件）与两个从未进 git 的 change 目录。归档指向一个不存在的状态，等于什么都没证明。
2. **重建关系地图。** 源码变了，地图不再是最新的，`coverage` 才回得到 `COMPLETE`。
3. **重新接受项目资料。** 地图更新后证据锚点才对得上，`documentation` 回得到 `COMPLETE`。
4. **同步规格并归档。** 5 个 change 里 4 个可归档；第 5 个（`stabilize-feishu-video-delivery`）的任务 7.3 是真人闭环——真实私聊、真实飞书消息、真人播放——本环境不可达，标注为不可达并保留在活动区。

第 4 步之后，诊断的初始化维度应当不再报 `PARTIAL`。这是这一步唯一的验收信号。

### 前置条件

工程壳这一侧的前置是本 change 交付的 `tools/check-project`：目标项目的 `.agent-framework/` 装的是旧版运行时载荷，里面还没有这个检查。升级目标项目的运行时载荷走公共壳升级工作流。

### 授权边界

第 1 步要提交目标项目里别人写的工作，第 2 步要跑 Agent 分析并重建地图，第 4 步要写目标项目的规格与归档目录。这些都是对用户项目的写操作，需要单独授权。
