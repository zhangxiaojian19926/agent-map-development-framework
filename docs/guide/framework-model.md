# 框架模型速查

> 这份文档只回答一件事：正文里的机制名和状态码到底指什么，看到它下一步做什么。
>
> 第一次读[《从零到一玩转工程壳》](from-zero-to-one.md)时，先扫第 1～5 节建立心智模型；之后按第 7 节回查状态码。
> 目录与文件归属见[业务项目目录布局](project-layout.md)；规则出处见[完整开发流程](../framework/development-workflow.md)。

## 1. doctor：一份只读的体检报告

`doctor` 不安装依赖、不跑索引、不更新地图、不运行项目测试、不提交推送。它只回答"这个工程现在处于什么状态"，并把下一步命令列在 `next_actions` 里。

### 1.1 十个维度

| 维度 | 回答的问题 | 状态取值 |
|---|---|---|
| `status` | 整体能不能往下推进 | `READY` / `PARTIAL` / `BLOCKED` / `WAITING_AGENT` / `PREPARED` |
| `scaffold` | 公共壳运行包是否完好 | `READY` / `BLOCKED` |
| `initialization` | 工程接入完成到什么程度 | `COMPLETE` / `PARTIAL` / `BLOCKED` |
| `documentation` | 项目资料是否与当前源码一致 | `COMPLETE` / `STALE` / `MISSING` |
| `coverage` | 源码是不是都被分析过 | `COMPLETE` / `STALE` / `MISSING` / `NOT_APPLICABLE` |
| `handoff` | 能不能进入计划阶段 | `READY_FOR_PLANNING` / `NEEDS_DESIGN_APPROVAL` / `MISSING` / `STALE` / `BLOCKED` |
| `maps` | 关系地图能不能用 | `READY` / `STALE` / `NOT_RUN` / `NOT_APPLICABLE` / `SPEC_MISMATCH` |
| `runtime` | 业务是不是真的跑起来过 | `NOT_RUN` / `VERIFIED` / `BLOCKED` |
| `onboarding` | 首次启动是不是就绪 | `PREPARED` / `NOT_PREPARED` / `BLOCKED` |
| `knowledge` | 知识库的壳与内容 | `SCAFFOLDED` / `NOT_CONFIGURED` / `CONFLICT` |

`knowledge` 还带一个 `ingestion` 字段，取 `EMPTY` / `PRESENT` / `NOT_APPLICABLE`——**壳存在不等于已摄入知识**。

### 1.2 顶层 `status` 怎么来的

`READY` 需要同时成立：公共壳运行包完好、项目资料 `COMPLETE`、源码覆盖 `COMPLETE`（或 `NOT_APPLICABLE`）、交接 `READY_FOR_PLANNING`、关系地图 `READY`（或 `NOT_APPLICABLE`）、索引与 hooks 就绪、且没有待认领的候选模块。

任何一项不满足就降为 `PARTIAL`；公共壳运行包损坏是 `BLOCKED`；工程还没被当前 Agent 分析过是 `WAITING_AGENT`；只有一句需求、还没有源码的空工程是 `PREPARED`。

### 1.3 doctor 不做什么

它不修复、不安装、不索引、不改地图、不跑测试、不提交推送。看到 `STALE` 或 `MISSING` 时，doctor 给出修复入口，**是否执行由你决定**。

## 2. 关系地图：谁调用谁

关系地图记录模块之间的调用边，每条边都带**证据**——指向具体源文件、文件哈希和一句锚点文字。

- **什么时候必须重建**：模块新增、删除、移动，对外职责改变，或模块间关系改变时，用 `map` 发布一次。
- **什么时候不用重建**：模块内部的改动不用更新地图，也不要为此打断用户。CodeGraph 同步不发布地图。
- **只读任务不写地图。**
- 地图里的证据会过期。源码改了而地图没重建，就是 `STALE`；`INVALID_ANCHOR` 表示哈希对得上但锚点那句话被改掉了。

地图里的模块摘要来自静态阅读，**不等于业务回归通过**。

## 3. handoff：把工程交到下一棒

交接是"上一个环节做完、下一个环节可以接手"的那份记录，由 `docs/project/handoff.md` 与本机状态共同支撑。

| 交接状态 | 含义 | 下一步 |
|---|---|---|
| `READY_FOR_PLANNING` | 资料齐备，可以进计划阶段 | 写 OpenSpec change |
| `NEEDS_DESIGN_APPROVAL` | 设计草案在等人确认 | 先与用户对齐设计 |
| `MISSING` | 交接记录不在了 | 重新接受 dossier 以恢复 |
| `STALE` | 交接与当前源码对不上 | 重新接受 dossier |
| `BLOCKED` | 前置条件缺失 | 看 `next_actions` 第一条 |

**交接 `READY_FOR_PLANNING` 不等于业务实现完成**，它只说明可以开始写计划了。

## 4. OpenSpec 的四个区

```text
openspec/changes/         活跃 change：准备改变什么、当前做到哪一步
openspec/changes/archive/ 已归档 change：做完并留了证据
openspec/specs/           正式能力规格：这个工程已经稳定具备什么
knowledge/project/        已验证且以后仍值得复用什么
```

一个 change 的任务全部勾完，就要先把它的能力规格**同步**进 `openspec/specs/`，再把 change **归档**。同步和归档是两个动作，顺序不能颠倒；两者都做完，规格库才与工程实际拥有的能力一致。

**规格库记录"要求什么"，不记录"实现了多少"**——实现完成度只看 change 的任务与验证证据。

## 5. 授权：十六种能力分开给

框架把"能做什么"拆成十六种能力，每种单独授权，不会因为给了其中一种就自动得到其余：

| 能力 | 覆盖的动作 |
|---|---|
| `write` | 写入目标工程的文件 |
| `agent` | 运行当前 Agent 的分析批次 |
| `index` / `index-install` | 建立或更新源码索引 / 安装索引工具 |
| `hooks` | 安装工程钩子 |
| `clone` / `local-clone` | 拉取远程模块仓库 / 拉取本地模块仓库 |
| `openspec` | 执行 OpenSpec 规格动作 |
| `auth` | 使用凭据通道 |
| `reverse` / `reverse-install` | 执行逆向观察 / 安装逆向工具 |
| `web-fetch` / `browser-observe` / `network-capture` / `web-auth` | 网页获取 / 浏览器观察 / 网络抓取 / 网页认证 |
| `package` | 登记构建产物 |

缺授权时框架返回 `CONSENT_REQUIRED` 并列出还缺哪些，不会自己降级或绕过。

<!-- status-dictionary:start -->
## 6. 技能的本地改编层

框架引入上游技能时，一律保留上游原文字节不变，另写一层本地规则承载本框架自己的要求：seam 预确认、切片写入 change 的任务清单、两轴评审的规格来源、`INFRA_ERROR` 不是 RED、术语表落在项目文档、复盘按本框架的标准走。

这些文件是上游 `SKILL.md` 的同目录兄弟，上游不会引用它们，框架自己的文档过去也没有指向它们——于是它们在包里，却永远不被读到。规格说"SHALL 保留"，而"保留"的内容在执行时不存在。

现在每个带本地层的技能，在阶段路由表或参考技能段里都标出了要一并读取的文件名。规则如下：

- **与上游原文冲突时以本地为准。** 本地层文件的开头都写明了这一点。
- **只登记必须每次读取的规则层。** 技法参考、验证脚本、创作史按需查阅，不进登记。登记见 `skill/local-layers.json`。
- **入口层再指向其余文件。** 每个入口层都用链接指向同目录的其余本地文件，读入口层即已覆盖。
- **登记与磁盘必须一致。** 分发结构检查会核对：登记项真实存在，登记的技能名是真实的技能入口，且登记的文件名在活文档里被提及——不存在"登记了但没人知道要读"的状态。

## 7. 状态词典

按域分组。**状态是事实的分类，不是完成度的打分**——看到状态先查它属于哪一域。

### 7.1 工程接入（doctor）

| 状态 | 含义 | 下一步 |
|---|---|---|
| `READY` | 该项已完成且新鲜 | 继续下一维度 |
| `PARTIAL` | 部分完成 | 读 `next_actions` |
| `BLOCKED` | 缺前置条件 | 读 `next_actions` 第一条 |
| `WAITING_AGENT` | 等当前 Agent 产出分析 | 跑分批分析 |
| `PREPARED` | 空工程骨架就绪，业务未获批 | 与用户确认设计 |
| `COMPLETE` | 该维度完成 | 无 |
| `STALE` | 曾经完成，但与现状不符 | 重新接受 dossier 或重建地图 |
| `MISSING` | 从未建立 | 按 `next_actions` 建立 |
| `NOT_APPLICABLE` | 此工程不适用 | 无需处理 |
| `NOT_CONFIGURED` | 未启用该能力 | 按需启用 |
| `SPEC_MISMATCH` | 地图与项目声明不一致 | 核对 `framework-project.json` |
| `MISSING_INDEX` | 索引库文件不在 | 重建索引 |
| `ANALYZED` | Agent 分析完成且地图是最新的 | 可以发布地图 |
| `SCAFFOLDED` | 知识库壳在 | 摄入内容才算有知识 |
| `EMPTY` | 壳在但没有内容 | 摄入 |
| `PRESENT` | 有内容 | 无 |
| `CONFLICT` | 与现状冲突 | 人工裁决，不自动覆盖 |

### 7.2 开发与验证

| 状态 | 含义 | 下一步 |
|---|---|---|
| `READY_FOR_PLANNING` | 资料齐备 | 写 change |
| `NEEDS_DESIGN_APPROVAL` | 设计待批准 | 先与用户对齐 |
| `NOT_RUN` | 没执行过 | 执行，或如实标 `NOT_RUN` |
| `VERIFIED` | 真实执行并通过 | 无 |
| `PASS` / `FAILED` | 通过 / 失败 | 无 |
| `INFRA_ERROR` | 环境故障，**不是**失败 | 修环境后重跑 |
| `NOT_AUTHORIZED` | 缺授权 | 取得对应能力授权 |
| `NOT_VERIFIED` | 证据不足 | 补证据 |
| `DRY_RUN` | 只预览，没写入 | 确认后再执行 |

### 7.3 交付与发布

| 状态 | 含义 | 下一步 |
|---|---|---|
| `READY` | 候选证据齐备，可进发布审批 | 按流程申请发布 |
| `GAPS_OPEN` | 有缺口未补 | 补证据后重跑 |
| `FAILED` | 有明确失败项 | 修掉失败项 |
| `CHANNEL_NOT_READY` | 候选没到可发布状态 | 先解决候选 |
| `NOT_READY` | 未达就绪 | 同上 |
| `SKIP` | 无说明，本次跳过 | 无 |

### 7.4 逆向与知识

| 状态 | 含义 | 下一步 |
|---|---|---|
| `PREPARED` | 计划已生成 | 执行 |
| `PLAN_ONLY` | 只出了计划，没摄入 | 授权摄入 |
| `NOT_OBSERVED` | 没有观察到 | 补观察或如实标注 |
| `UNCHANGED` / `UPDATED` | 未变化 / 已更新 | 无 |

### 7.5 地图证据错误

这四种都出现在地图或 dossier 校验里，**修法各不相同**：

| 错误 | 原因 | 修法 |
|---|---|---|
| `STALE_EVIDENCE` | 源码哈希与地图记录不符 | 源码改了，重建地图 |
| `INVALID_ANCHOR` | 哈希对得上，但锚点那句话不在文件里了 | 重新取锚点 |
| `INVALID_EVIDENCE` | 证据结构本身损坏 | 重新接受 dossier |
| `MISSING_EVIDENCE` | 声明了证据却没给 | 补证据 |
| `REVERSE_NOT_SOURCE` | 拿逆向证据当源码证据 | 换成源码证据 |

### 7.6 逆向产物与交付物

`docs/project/reverse/<id>.md` 是脱敏公开摘要；完整的原始输出、行为契约与设备状态只在 `.framework/local-state/reverse/` 里。**公开摘要不是完整观察，也不代表需求或实现状态。**
<!-- status-dictionary:end -->
