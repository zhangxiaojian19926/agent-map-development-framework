# 逆向工具版本

普通工程初始化不安装、不调用这些工具。只有明确的逆向请求才读取本页和 `tools/framework_core/rea-tools.lock.json`。

有校验值的工具只在 `reverse` 和 `reverse-install` 同时授予时下载。`rea-agents` 用项目内 npm prefix 和受控 cache，禁用安装脚本。Ghidra、Temurin JDK（当前仅 macOS arm64 已写入校验值）和 WABT 用 HTTPS，核对 SHA-256 后在临时区安全解包。自动流程安装到 `.framework/tools/<tool>/<version>/`，健康检查通过并写入 receipt 后原子激活；相同版本、artifact 和健康状态才复用，repair 需获批计划且失败恢复旧目录。JADX、Apktool、Rizin、platform-tools 还没有校验值，所以不下载。TShark 和 sigrok-cli 只检测，不下载。没有逆向授权时这些函数不会运行。`doctor` 的 `reverse` 只读 receipt、计划、快照和证据，不运行工具或联网，也不改变 `initialization=COMPLETE`。

| 工具 | 固定版本 | 系统 |
|---|---|---|
| rea-agents | 6.7.0 | macOS、Linux |
| Ghidra | 12.1.4 | macOS、Linux |
| Eclipse Temurin JDK | 21.0.13+9 | macOS、Linux。校验值未写入 lock 之前不下载 |
| JADX | 1.5.6 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Apktool | 3.0.3 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Rizin | 0.9.1 | macOS、Linux。校验值未写入 lock 之前不下载 |
| WABT | 1.0.42 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Android platform-tools | 实现时锁定的官方包 | macOS、Linux。校验值未写入 lock 之前不下载 |
| pwntools、Unblob、TShark 4.x、sigrok-cli 0.7.2 | Linux 专用 | macOS 返回 HOST_UNSUPPORTED，不下载 |

Ghidra 使用已公布的 SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`。不安装 Hopper、IDA 或 JEB。Node.js 只检测，壳不安装。

## 工具选择与命名操作

旧五字段 scope 继续使用上方主机 bundle。`reverse-scope/v2` 只检查 `target.tools` 声明的必要工具；仅需 REA 时，Ghidra、JADX、WABT 等工具缺失不会阻塞。必要工具缺失且没有 `reverse-install` 时返回 `DEPENDENCY_MISSING`，不下载、不执行目标；有安装授权也只能安装锁中固定且完整性可校验的工具。

动态动作只允许 `reverse-operations.lock.json` 中登记的操作。范围提供操作名和命名目标，不提供任意 argv、shell、重定向或替代目标。默认锁只含 ADB 基线／只读观察和命名网络提供方，不含修改、恢复或批量危险操作；业务项目以后新增此类操作时仍需独立变更、当次授权和实机验收。

自动请求另由 `reverse-catalog.json` 将画像能力映射到最小工具依赖和命名适配器，版本与 artifact 仍由 `rea-tools.lock.json` 锁定。`reverse-request/v1` 的 dry-run 返回 `toolchain-plan/v1`，不写 `.framework`、不联网、不执行进程；批准只绑定当前请求、快照、锁、来源和授权需求。本地画像只读内容，不运行目标。URL 先经 `web-fetch` 形成私有快照，再生成内容计划；快照发现 WASM 或追加动态观察时生成增量计划。

网页默认仅 HTTPS GET、隔离无凭据会话和显式 origin 列表，每次重定向及 DNS 结果都重新检查，限制资源数、总字节和超时。HTML、JavaScript、DOM、console、截图、HAR、Cookie 和 Authorization 均按私有证据处理，公开摘要只含状态和脱敏结论。静态资源分析使用标准库，不启动浏览器；真实浏览器 provider 默认未安装，不能用静态结果冒充动态行为。

## 权限与状态

| 授权 | 只控制 |
|---|---|
| `reverse` | 进入逆向流程 |
| `reverse-install` | 安装锁定且必要的工具 |
| `web-fetch` | 在显式 origin 和预算内获取网页快照 |
| `browser-observe` | 隔离浏览器中的命名 DOM、console 或截图观察 |
| `web-auth` | 使用既有登录态；不包含在网页获取或浏览器授权中 |
| `device-connect` | 连接命名设备 |
| `device-observe` | 只读设备基线和状态观察 |
| `network-capture` | 命名设备及端点的网络观察 |
| `device-change` | 单设备试点和独立恢复动作 |
| `device-rollout` | 已验证试点向兼容命名设备逐台复制 |

工具链、观察、运行验证和设备变更分别报告。没有实际执行时保持 `NOT_RUN` 或 `NOT_AUTHORIZED`；工具 `READY` 不代表运行或修改成功。假执行器只验证离线控制逻辑，真实设备、真实网络、私有认证、可恢复性和部署没有实测证据时必须写 `NOT_RUN`，不得写 `PASS`。
