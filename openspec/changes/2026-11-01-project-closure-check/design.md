# Design

## Context

动机见 [proposal.md](proposal.md)。这里只记约束实现的事实。

运行时白名单决定了什么东西会进使用者项目。当前 `RUNTIME_DIRECTORIES` 是 `skill/`、`templates/`、`tools/framework_core/`、`docs/framework/`、`docs/guide/`，另加 `tools/framework` 这一个显式脚本。`tools/check-framework`、`tools/check-changes`、`tools/pre-commit-check` 都**不在**其中——它们检查的是公共壳自己。

三处可复用的既有资产：

| 资产 | 位置 | 可复用程度 |
|---|---|---|
| 欠账判定 | `tools/check-changes` 的 `find_outstanding(root)` | 已是 root-relative 通用实现，只差分发 |
| 地图证据校验 | `tools/framework_core/maps.py` 的 `validate_map` | 已在运行时载荷内 |
| 只读诊断 | `tools/framework_core/readiness.py` 的 `inspect_project` | 已在运行时载荷内 |

实测的真实项目状态（`61.videohao-generator`，2026-11-01）：

- 5 个 change、70 个任务、69 个已完成；`openspec/specs/` 与 `openspec/changes/archive/` 全空。
- `doctor` 报 `initialization=PARTIAL`、`handoff=READY_FOR_PLANNING`、`documentation=STALE[INVALID_EVIDENCE]`。
- 工作树有 43 项未提交改动（21 个源文件 + 11 个测试文件），最后一次提交是 2026-10-25 17:40。
- 5 个 change 中有 2 个目录（`reference-audio-pause-material-flow`、`unify-reference-visual-style`）**完全没进 git**。
- `documentation=STALE` 有两个成因：源码漂移（`source_digest` 不匹配）与 dossier 证据失效（`INVALID_EVIDENCE`）。前者源于"改了没提交"，修法是提交并重接受 dossier；后者是锚点过期，两者修法不同。
- `stabilize-feishu-video-delivery` 的任务 7.3 是**真人闭环**（真实私聊、真实飞书消息、真人播放），本环境不可达。

## Goals / Non-Goals

**Goals:**

- 使用者项目能自己发现四类收口欠账，且判定与公共壳一致。
- 检查随公共包送达，不要求公共壳仓库在场。
- 在一个真实项目上把欠账真正清零，作为该能力的唯一验收证据。

**Non-Goals:**

- 不把 `check-framework` 送进使用者项目（见决策一）。
- 不自动改写使用者项目已有的持续集成配置。
- 不代替使用者项目做规格同步与归档——检查只报告，下一步由项目自己的 change 流程走。
- 本轮不处理框架自身两个老 change 的归宿（roadmap 第 5 项），那是独立决定。

## Decisions

**决策一：新增独立工具 `tools/check-project`，不改 `check-framework` 的身份。**

`check-framework` 校验的对象是**公共壳自身**——分发清单与指纹、相对链接、脚本语法、技能入口数、文档契约。它有 200 多行针对框架自身文档的检查（实现阶段摘要行、指南门禁清单、发布时刻），这些在使用者项目里既无意义也会误报；它校验的 `framework-manifest.json` 在使用者项目里语义也完全不同。

考虑过的替代：

- **把 `check-framework` 装进运行时让它自适应两种身份**——工具数不增，但职责混在一起，越修越乱。
- **扩 `doctor` 加 `--closure` 模式**——使用者项目已经有 doctor，零新增分发；但 doctor 回答的是"这个项目初始化到什么程度"，欠账是"change 生命周期到哪一步"，两个问题混在一起会让 doctor 本来就六维的输出更难读。

结论：工具按**被检查的对象**划分，不按"谁装它"划分。`check-framework` 查公共壳，`check-project` 查使用者项目。

**决策二：判定逻辑下沉到 `tools/framework_core/closure.py`，两边共用一份。**

`framework_core/` 本来就在运行时白名单里。把 `find_outstanding` 从 `tools/check-changes` 搬进 `closure.py`，`tools/check-changes` 改为调用它——**功能不减只搬家**，公共壳自己的那道检查行为不变。`tools/check-project` 基于同一个模块再叠加地图证据与初始化状态。

这样使用者项目与公共壳对"一个 change 是否已完成"的结论必然一致。框架自己的原则是不另建竞争的完成状态；把同一份判定抄一遍是最容易违反它的地方。

**决策三：默认只报告，`--strict` 才失败。**

使用者项目接入公共包的当天必然是红的——欠账是历史积累，不是接入失败。如果默认失败，Agent 会在接入阶段就被卡住，而框架自己的两个老 change 就是这么挂了一年的。

默认成功退出 + 报告，Agent 可以正常推进；把"欠账即失败"的决定权交给接入持续集成的人，由他们在模板里显式写 `--strict`。

**决策四：持续集成模板只提供，不自动写入。**

框架不擅自改用户项目的 CI 配置。模板作为可选片段放在 `templates/` 下，标明 OpenSpec CLI 的固定版本，让使用者自己决定采用与否。

**决策五：地图证据的两种失效必须分开报。**

`STALE_EVIDENCE`（源码哈希与地图记录不符）和 `INVALID_ANCHOR`（哈希对得上但锚点字符串不在文件里）的修法完全不同：前者是"改了源码没更新地图"，后者是"改写文件时把锚点删了"。合成一句话"证据失效"会让人不知道该做什么。检查必须分别报出。

**决策六：真实项目收口前，先把它的工作树收成提交。**

videohao 那 69 个已完成任务对应的实现有 366 行改动从未进 git，两个 change 目录也从未进 git。如果直接同步规格并归档，归档指向的是一个不存在的状态——这正是框架自己的任务 6.4 说的"证据未绑定最终工作树"。

所以批 3 的第一步是收拢工作树（提交改动、纳入两个未跟踪的 change 目录），之后才谈同步与归档。

**决策七：需要真人闭环的那一格，按封存处理，不假装完成。**

`stabilize-feishu-video-delivery` 的任务 7.3 需要真实私聊、真实飞书消息与真人播放。本环境拿不到，也不该假装拿得到。处理方式是：把该任务明确标注为"本环境不可达"并保留在活动区，同时把该 change 的其余部分收口——**这与框架自身两个老 change 的处境是同一个问题**，在真实项目上复现了。这个复现本身就是有价值的证据。

## Risks / Trade-offs

- **运行时载荷变大** → 新增一个脚本与一个模块，量级可忽略；分发清单会记录全部新增文件。
- **目标项目接持续集成需要网络装 OpenSpec CLI** → 模板里标明固定版本，并在模板注释里写明该依赖；不带该依赖时欠账检查本身仍可运行，只有规格结构校验需要它。
- **收口会写用户项目** → 已获本次授权；不推送、不改用户已有持续集成配置。
- **收口后源码再动，证据又漂移** → 这正是模板里 `--strict` 的用途：下一次持续集成会把漂移报出来，而不是等到人手工对账。
- **下沉逻辑动到公共壳自己的检查** → `check-changes` 改为调用后必须行为等价，由公共壳自身的门禁与既有单测守住。
