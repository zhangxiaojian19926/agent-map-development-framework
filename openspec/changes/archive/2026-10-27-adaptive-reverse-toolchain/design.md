## Context

现有 `prepare_reverse()` 同时承担显式范围校验、主机 bundle 选择、安装和观察；v2 静态执行固定到 REA。下载器直接写最终工具目录，复用主要依据 npm lock 或 `.sha256`。另一方面，现有操作锁、证据哈希、分层授权、设备状态和只读 doctor 已提供可复用边界。

本变更采用新增自动控制层而非扩大原函数分支：旧 v1/v2 继续走兼容路径，自动请求经画像、计划、安装和命名适配器进入同一证据治理。实现仅使用 Python 标准库和项目内受锁工具，不为普通初始化增加依赖。规格见 `specs/reverse-toolchain-lifecycle/spec.md` 与 `specs/reverse-engineering-governance/spec.md`。

## Goals / Non-Goals

**Goals:**

- 用确定性控制面连接 `reverse-request/v1`、画像、`toolchain-plan/v1`、安装清单和执行适配器。
- 在同一项目内实现最小安装、健康复用、故障恢复和可审计升级。
- 以统一观察记录接入本地二进制、网页快照和可选动态 provider。
- dry-run、授权、计划哈希、网络边界和公开/私有证据均可离线测试。

**Non-Goals:**

- 不实现任意包管理器、系统级 apt/brew/npm 全局安装或模型生成安装脚本。
- 不默认提供真实浏览器、登录态、网络抓包或设备 provider；仅定义受控接口并以假 provider 验证，真实接入另需锁定 artifact 和集成证据。
- 不承诺还原混淆、加壳、反调试或反爬目标，也不自动执行目标二进制。
- 不重写 CodeGraph、普通初始化或设备试点，不在本变更建立跨项目全局工具缓存。
- 不自动补齐当前未固定完整性的 JADX、Apktool、Rizin 等 artifact；它们继续明确阻塞。

## Decisions

### 1. 自动请求与既有 scope 分流

新增 `reverse_request.py` 负责 `reverse-request/v1` 的严格校验和画像。请求包含稳定 `id`、`goal`、`target`、`intent`、`acceptance`、`evidence`、网络限制及可选命名观察；不包含下载 URL、argv 或任意工具版本。

- `target.kind=file/directory`：计算内容指纹，读取有限头部和归档目录，输出 `binary/native`、`android`、`wasm`、`web_snapshot` 或 `unknown` 等事实。
- `target.kind=url`：联网前只产生 URL 边界；由网页快照阶段补齐内容画像。
- 既有 `device` 仍由 v2 设备路径处理，不通过网页或二进制画像。
- 自动路径根据请求生成独立执行上下文；旧五字段和 v2 直接调用保持原校验、观察和冲突语义。

备选方案是直接把自动字段塞入 v2。否决原因是 v2 严格字段和文件 SHA 模型无法自然表达 URL、两阶段画像与计划批准，静默放宽会削弱旧边界。

### 2. 注册表、锁和 Resolver 分离

新增 `reverse-catalog.json` 描述稳定工具 ID、能力、目标类型、依赖、平台、安装器、入口、版本探测和适配器；现有 `rea-tools.lock.json` 继续作为版本和 artifact 完整性锁。操作注册扩展为命名适配器及类型化参数，不开放任意命令。

`reverse_planner.py` 执行纯确定性解析：

```text
request + profile + host + catalog + lock + installation receipts
→ required capabilities
→ dependency closure
→ REUSE / INSTALL / REPAIR / SKIP / BLOCK
→ canonical toolchain-plan/v1 + plan_sha256
```

计划哈希基于排序后的规范 JSON，排除时间戳等非确定字段。批准必须同时匹配请求/快照指纹和计划哈希；工具锁、artifact、网络来源或权限需求变化都会得到不同哈希。自动 CLI 复用现有 `--approve <name>=<sha256>` 通道，由 Agent 计算和传递，用户不手工处理 JSON/hash。

### 3. 两阶段计划与执行状态

新增 `reverse_auto.py` 作为自动编排入口：

```text
REQUEST → PROFILE → PLAN → APPROVAL → RESOLVE/INSTALL
→ HEALTH → ADAPTER OBSERVE → EVIDENCE/BEHAVIOR
```

- 本地静态目标通常一次即可生成完整计划。
- URL 先形成仅含受控获取的准备结果；授予网页获取后保存私有快照，再生成内容工具链计划。
- 新快照发现 WASM 或用户追加动态 DOM 观察时生成新计划，只允许新增必要依赖。
- dry-run 只计算和返回，不创建 `.framework`；非 dry-run 的计划、快照和观察写入私有状态。
- `toolchain_status`、`observation_status`、`runtime_validation` 和 `device_change_status` 继续分开。

### 4. 版本隔离和事务式安装

`reverse_downloads.py` 保留公开兼容包装，底层增加有界事务安装；REA/npm 与归档安装共用收据和健康语义。

目录布局：

```text
.framework/tools/<tool>/<version>/       # 原子激活后的工具与 receipt
.framework/cache/artifacts/<sha256>      # 项目内可选下载缓存
.framework/tmp/install/<run-id>/         # 同文件系统临时区
.framework/local-state/reverse/plans/    # 自动计划
.framework/local-state/reverse/installs/ # 当前工具状态
.framework/local-state/reverse/auto/<id>/# 自动观察、快照和契约
```

安装顺序为 per-tool lock → 再次检查健康 → 有界下载 → hash/integrity → 安全解包或项目内 npm 安装 → 入口、依赖和版本探测 → 写临时 receipt → 原子 rename。npm cache 和 scripts 环境受控，不使用全局 prefix。

ZIP/TAR 在解包前检查绝对路径、`..`、链接、文件数、单文件和总展开大小；只解到本次 staging。最终路径已存在时，只有相同健康安装可复用；获批 `REPAIR` 先将旧目录移入本次临时隔离区，激活失败则恢复，成功后清理。不得直接覆盖未知人工目录。

备选方案是继续原位解压并仅补 `.sha256`。否决原因是中断、并发和恶意归档仍可能留下混合版本，无法满足恢复和复用语义。

### 5. 健康检查不是功能验证

`reverse_install.py` 统一保存安装清单和健康结果。复用检查包括版本、平台、artifact、receipt、入口和依赖；命名版本探测/最小 fixture 仅在逆向准备或显式逆向健康检查中运行。

普通 doctor 只读 receipt、关键文件和证据指纹，不执行工具。工具 `READY` 仅表示可以调用适配器，不表示目标观察、浏览器行为或业务验收通过。损坏返回 `CORRUPT`，版本不支持返回 `UNSUPPORTED_VERSION`，缺 provider 返回 `PROVIDER_MISSING`。

### 6. 命名适配器与既有证据复用

新增 `reverse_adapters.py`，将自动观察映射到注册操作：

- `binary.static.rea`：复用现有 REA JSON 输出。
- `binary.static.ghidra`：使用 Ghidra headless 的固定参数模板和项目内输出目录，JDK 由依赖解析提供。
- `wasm.static.wabt`：调用锁定的 WASM 验证/文本转换入口，输出保存为私有证据。
- `web.static.resources`：标准库解析快照中的 HTML、脚本、样式、WASM 和资源引用，不执行脚本。
- `web.dynamic.browser`：仅调用注入的命名 provider；无 provider 时记录 `PROVIDER_MISSING`。

参数仅允许 `{target_path}`、`{snapshot_path}`、`{output_path}`、`{tool_path}`、`{jdk_path}`、`{device_id}` 等注册占位符，由壳解析为拥有路径。子进程继续走现有限时、限输出、无 shell 的执行器。

观察记录扩展目标身份和适配器版本，但沿用同 ID 同请求幂等、同 ID 不同请求冲突、原文 retain/discard、公开摘要和行为契约。自动网页/二进制使用通用行为契约版本，不硬套设备试点状态。

### 7. 网页快照和 provider 边界

`reverse_web.py` 实现两阶段目标模型：

1. URL allowlist、scheme/host/port、DNS/重定向目标和资源预算校验；默认仅 HTTPS、GET、隔离无凭据会话。localhost、私网、HTTP 和非默认端口需在请求中明确并被授权。
2. 获取初始文档及批准范围内资源，逐资源计算 SHA-256，保存 `snapshot-manifest.json` 和根指纹。禁止 `file:` 等非 HTTP 协议和未经批准的跨域重定向。
3. 静态适配器只读快照；动态 provider 接收命名动作、快照身份、域名边界、资源预算和隔离会话要求。

浏览器、网络和登录态分别需要 `browser-observe`、既有/扩展网络授权和 `web-auth`。provider 返回 DOM、console、截图或 HAR 时统一按私有证据处理；公开摘要只写状态和脱敏结论。默认 CLI 不注入 provider，因此真实动态能力缺失时诚实返回 `PROVIDER_MISSING`。

### 8. CLI、运行时分发和文档

`reverse --dry-run` 在带自动 `--request` 时返回真实计划；旧无 request 的 dry-run 保持通用权限预览。新增授权只加入 CLI 能力枚举和自动路径，普通初始化配置不自动获得这些授权。

新增 Python 模块、注册表和技能文档加入运行时白名单；测试 fixture 和真实 provider 不进入分发。文档提供三条用户路径：普通初始化不受影响、初始化时按选定 profile 预热、首次逆向按需补装。目录指南继续规定 `.framework/` 不提交。

## Risks / Trade-offs

- [自动画像误判或未知格式] → 以内容证据为准，返回 `PROFILE_UNKNOWN`，允许用户显式能力覆盖但仍经 Resolver，不安装全量 bundle。
- [工具锁覆盖平台不完整] → 计划阶段返回 `HOST_UNSUPPORTED`/`INTEGRITY_UNPINNED`，不自动换源或下载最新版。
- [安装中断或并发导致混合版本] → per-tool lock、staging、健康后原子激活、repair 隔离恢复和故障注入测试。
- [网页重定向、DNS 或资源造成 SSRF/资源耗尽] → 每次请求和重定向重新校验，限制协议、IP 范围、大小、数量、超时和方法；本地/私网显式授权。
- [网页原始证据泄露凭据] → 隔离无凭据默认、独立 `web-auth`、私有存储和公开摘要脱敏。
- [版本探测增加开销] → 缓存健康收据，仅在计划/准备或显式健康检查运行；普通 doctor 不执行。
- [适配器假测试通过但真实工具不兼容] → 默认 CI 验证参数和控制逻辑，真实工具单列集成证据；未运行保持 `NOT_RUN`。
- [新旧工具目录并存增加磁盘占用] → 不自动删除旧版本，报告可清理项；清理另需明确动作，避免破坏历史观察复现。

## Migration Plan

1. 先加入新注册表、画像、计划与安装模块及测试，不改变旧 scope 输入。
2. 将新安装写入版本隔离目录；旧安装仅作为兼容检测输入，不自动移动或删除。新适配器通过收据解析路径，旧 REA 路径保留兼容 fallback。
3. 自动请求和网页目标走新编排；既有 v1/v2、设备试点和恢复函数保持原入口，公共证据辅助函数只做兼容扩展。
4. 更新 CLI、白名单和文档后运行全量普通初始化、索引、地图、打包与逆向回归。
5. 若新自动路径出现严重问题，可停止传递自动 request 并继续使用旧 scope；不删除新版本目录或历史证据，回滚代码不触发清理。已生成的自动计划因 schema 独立不会被旧代码误当作 v2。
