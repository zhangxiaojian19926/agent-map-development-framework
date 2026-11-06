## Purpose

为工程壳的十五条工作流提供可移植的任务路由和可复核的阶段判定，支持国内外原生 Coding Agent 接续任务，并按实测范围报告工具拦截和故障行为。

## ADDED Requirements

### Requirement: WF-01 统一工作流路由

系统 SHALL 登记 `docs/guide/from-zero-to-one.md`「15 条一览」表定义的十五条工作流，流程稳定 ID 记为 `flow-01` 至 `flow-15` 并与该表行号一一对应。路由输出 SHALL 区分主流程、条件流程、不适用项与待确认项并给出依据。路由和检查 MUST 保持只读。流程 ID MUST NOT 与需求 ID 混用。

#### Scenario: WF-01-ROUTE 业务项目与公共壳分流

- **WHEN** 在业务工程发起普通开发任务
- **THEN** 公共壳验证与发布显示不适用，逆向仅在明确提出时适用，检查前后文件集合与内容一致

#### Scenario: WF-01-SHELL 公共壳仓库自身

- **WHEN** 在公共壳仓库自身发起开发任务
- **THEN** 公共壳验证显示适用并给出该仓库的门禁入口，版本发布显示条件适用，其余工作流按主线与条件分流，检查前后文件集合与内容一致

#### Scenario: WF-01-UNKNOWN 意图不足

- **WHEN** 输入不足以区分普通文档和验收变更
- **THEN** 报告待确认并列出可继续的只读步骤

### Requirement: WF-02 新行为实现前置条件

系统 SHALL 核验实际项目与 OpenSpec 根、change、规格与计划、批准范围及相关指纹。批准证据 MUST NOT 来自调用方自填的布尔值，也 MUST NOT 来自未绑定项目外受信来源的内容哈希。受信来源 MUST 位于目标工程之外，任务请求无权指定、替换或影响它。前置条件缺失时 SHALL 返回拒绝原因、缺失项与补齐步骤。

#### Scenario: WF-02-MISSING 缺少批准

- **WHEN** 规格已存在且计划未获有效批准，调用方请求编辑业务源码
- **THEN** 流程判定为 `NEEDS_DESIGN_APPROVAL` 并返回缺失项，已授权的规格或计划草稿编辑判定为 `READY`

#### Scenario: WF-02-STALE 批准绑定过期

- **WHEN** 已批准的规格或计划内容改变，或引用来自其他项目或 change
- **THEN** 流程判定为 `STALE`，旧批准无法满足实现前置条件

#### Scenario: WF-02-ALLOW 有效批准

- **WHEN** 已核实项目、change、批准来源和绑定，且动作在批准范围内
- **THEN** 流程判定为 `READY` 并返回依据，同时保留原生宿主的权限决定

### Requirement: WF-03 日常任务分类

系统 SHALL 对日常开发流程（`flow-02`）区分只读审计、纯文档、既有规格修复与新行为，并根据实际行为和验收影响决定路由。知识摄入、设备与发布等其余流程的分类由 WF-01 目录承接，本要求不覆盖。

#### Scenario: WF-03-DOC 文档与产品语义

- **WHEN** 一份请求仅修正链接，另一份请求通过文档改变公开接口或验收
- **THEN** 第一份进入文档验证，第二份进入规格流程

#### Scenario: WF-03-FIX 既有规格修复

- **WHEN** 请求恢复已有明确场景
- **THEN** 返回修复路由及复现、回归要求，首批只提供该路径指引

#### Scenario: WF-03-SCOPE 日常开发分类的边界

- **WHEN** 请求属于知识摄入或设备与发布
- **THEN** 按 WF-01 目录路由到对应流程，不套用日常开发四类

### Requirement: WF-04 可恢复任务记录

系统 SHALL 在明确写入授权后保存私有任务记录，检查项目、任务、请求标识和记录版本，并在恢复时重新判定当前事实。并发写冲突 SHALL 报告为 `CONFLICT` 并保留现场，不自动覆盖。

#### Scenario: WF-04-RETRY 幂等与并发冲突

- **WHEN** 两个会话基于同一版本提交不同更新，成功者随后重试相同请求
- **THEN** 只接受首个更新，另一请求返回 `CONFLICT`，重复请求返回原结果

#### Scenario: WF-04-RESUME 跨会话恢复

- **WHEN** 另一宿主恢复任务且批准引用已失效
- **THEN** 保留历史记录并报告最新阻塞，不继承上一会话操作授权

### Requirement: WF-05 原生宿主发现与拦截

系统 SHALL 为 Claude Code CLI 提供获授权的项目级适配。认证 MUST 绑定宿主版本、形态、操作系统、配置、工具入口和实测副作用。流程判定不为 `READY` 时，宿主适配 MUST 请求宿主阻断该次工具调用并给出拒绝理由与补齐步骤，MUST NOT 默认放行；宿主原生权限决定仍然独立生效。

#### Scenario: WF-05-NATIVE 原生新会话

- **WHEN** 从原生 CLI 开启干净会话，并请求在缺少批准时用已认证的编辑入口修改业务文件
- **THEN** 会话发现项目规则，记录实际工具拒绝且目标文件内容保持一致

#### Scenario: WF-05-UNOBSERVED 拒绝判定缺少执行证据

- **WHEN** 仅有内核拒绝记录，缺少原生工具结果或目标文件检查
- **THEN** 宿主执行轴为 `NOT_VERIFIED`，交付资格轴为 `NOT_RUN`，不得据此声称已阻断

### Requirement: WF-06 第二宿主与故障边界

系统 SHALL 为 Qwen Code CLI 复用同一目录、判定与接续契约。每个宿主 MUST 分别报告 Shell、未知工具、hook 超时、崩溃和禁用的实际覆盖。

#### Scenario: WF-06-SAME 同事实同判定

- **WHEN** 两个原生宿主为相同项目和动作提供等价事实
- **THEN** 内核判定和理由一致，宿主执行结果分别报告

#### Scenario: WF-06-FAIL 故障或覆盖缺口

- **WHEN** hook 超时、崩溃、禁用，或工具调用未命中已认证入口
- **THEN** 超时与崩溃记为 `INFRA_ERROR`，禁用记为 `NOT_RUN`，未命中已认证入口记为 `NOT_VERIFIED`，三者都不记为已阻断

### Requirement: WF-07 三轴结果与状态词典

系统 SHALL 分别记录流程判定、宿主执行与交付资格三轴结果，并 SHALL 只使用 `docs/guide/framework-model.md` 已发布状态词典中的状态码，不得另造第三套词表。三轴状态码 MUST 由代码产生且与被检查事实绑定。

流程判定轴：`READY` 前置齐备；`NOT_AUTHORIZED` 缺批准或授权；`NEEDS_DESIGN_APPROVAL` 计划待批准；`STALE` 批准绑定过期；`NOT_VERIFIED` 证据不足；`BLOCKED` 缺前置条件；`CONFLICT` 并发冲突；`NOT_APPLICABLE` 不适用；`PARTIAL` 部分满足。

宿主执行轴：`VERIFIED` 真实执行且已阻断并完成副作用检查；`PASS` 真实执行且门禁放行；`NOT_VERIFIED` 缺工具结果或文件检查；`NOT_RUN` 无真实执行；`INFRA_ERROR` hook 超时或崩溃；`NOT_APPLICABLE` 该入口不在已认证范围；`CONFLICT` 配置冲突。

交付资格轴：`PASS` 要求的验收证据齐全；`FAILED` 有明确失败项；`GAPS_OPEN` 有缺口未补；`NOT_RUN` 没有实际执行，不能写成 `PASS`；`INFRA_ERROR` 环境故障；`N/A` 不适用并说明理由。

#### Scenario: WF-07-AXES 三轴分别记录

- **WHEN** 完成一次阶段判定与宿主验收
- **THEN** 报告分别给出流程判定、宿主执行与交付资格三个状态及各自依据，不用一个状态代替三轴

#### Scenario: WF-07-VOCAB 状态码来自已发布词典

- **WHEN** 报告需要给出状态
- **THEN** 使用的状态码全部在已发布状态词典中登记，且对应事实由随包代码产生

### Requirement: WF-08 信任来源不可篡改

系统 SHALL 只把当前用户不可改写的信任来源计为可核验信任来源：信任来源文件与它所在的目录 MUST NOT 对当前用户可写。信任来源缺失或可被改写时，流程判定 MUST 为 `NOT_VERIFIED` 并给出阻断理由，指明信任来源不可信。信任来源路径 MUST NOT 由请求或环境变量指定。签名私钥 MUST NOT 落在代理可读范围内（离线签名，或带口令且口令不进入代理上下文）；系统无法机械校验这一条，SHALL 在报告与指南中如实声明。

#### Scenario: WF-08-MUTABLE 可改写的信任来源

- **WHEN** 信任来源文件或其所在目录对当前用户可写
- **THEN** 流程判定为 `NOT_VERIFIED`，理由指明信任来源可被改写，本次批准不构成可核验授权

#### Scenario: WF-08-PROTECTED 受保护的信任来源

- **WHEN** 信任来源文件与其所在目录均不可被当前用户改写，且签名有效
- **THEN** 按批准范围给出流程判定，并在报告里声明签名私钥是否可被代理读取无法机械校验

#### Scenario: WF-08-REDIRECT 路径被改指

- **WHEN** 请求或环境试图把信任来源指到代理可写的位置
- **THEN** 系统不采用该来源，流程判定为 `NOT_VERIFIED`
