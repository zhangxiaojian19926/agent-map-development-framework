## Context

4A 已提供候选请求校验、READY/FAILED/GAPS_OPEN 推导、公开报告和私有回执，且 `generate(..., dry_run=True)` 会重新核验候选请求、证据、报告及当前资产而不写文件。4C 可以复用这一只读入口，无需扩展或改变 4A 契约。现有 `package` 和公共壳 `prepare-release` 均不承担业务项目渠道适配，不能复用为发布授权。

## Goals / Non-Goals

**Goals:**

- 用固定请求绑定 READY 候选、GitHub 目标和显式资产映射。
- 用静态适配器生成确定性的资产目录、Release 说明和渠道清单。
- 用目录级暂存与多产物恢复保证更新不会留下部分有效状态。
- 保持 4A、4B、普通工作流及公共壳发布的兼容与离线边界。

**Non-Goals:**

- 不实现真实 GitHub Release、上传、Git、部署或发布成功回执。
- 不动态安装渠道插件，不支持任意本地目录或隐式全量资产。
- 不修改 4A 请求、报告、回执 schema，不实现其他渠道。

## Decisions

### D1 新增独立 `channel --request`，只增加 `write` 授权

请求采用 `release-channel-request/v1`，固定包含 `schema`、`id`、`candidate`、`channel`、`assets`。dry-run 只读，正式生成仅要求 `write`；与其他动作、额外 grant、`--summary` 和业务参数互斥。非 READY 返回差距风格退出码，非法输入与冲突沿用现有 CLI 分类。

备选方案是扩展 `candidate` 或 `package`；前者会混淆候选证据与渠道目标，后者会把哈希登记变成复制和渠道行为，因此不采用。

### D2 显式候选引用并复用 4A 只读重核验

`candidate` 固定包含 `id`、`request`、`request_sha256`、`report_sha256`。系统调用 4A dry-run 重新计算候选状态和资产清单，再读取对应私有回执核对请求哈希，并要求结果为 READY、ID 与报告哈希一致。候选请求只用于提取已校验的公开 notes，不把证据附件正文交给渠道渲染器。

这种方式能发现候选报告、证据或资产在 4A 之后发生的变化，且不需要修改 4A 输出。直接相信候选报告中的 READY 文本或仅检查文件存在不予采用。

### D3 首版静态支持 `github-release`

`channel` 固定包含 `type`、`repository`、`tag`、`title`、`draft`、`prerelease`。`type` 首版仅为 `github-release`；repository 仅允许受限 `owner/repo`，禁止 URL、凭据与空白；tag 使用首字符为字母数字且仅含字母数字、点、下划线、连字符的受限形式；title 为受限公开文本；draft 和 prerelease 必须为布尔值。

静态注册表把渠道类型映射到内部适配函数。未知类型返回 `CHANNEL_UNSUPPORTED`，不从请求导入模块或执行命令。真实发布不在适配器中留下隐藏网络入口。

### D4 显式资产映射与资源预算

`assets` 为非空数组，每项固定包含 `path` 和 `name`。path 必须存在于 4A 已重核验的候选资产清单且哈希仍匹配；name 仅允许 `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`，不允许目录分隔符。来源 path 不得重复，name 按 Unicode 大小写折叠后不得冲突。首版最多 100 项、总字节最多 100 MiB，超限返回 `CHANNEL_LIMIT`。

渠道适配只复制所选资产原字节，不重新构建、压缩或执行。这样保留候选哈希的可复核性；隐式复制整个 `dist/` 或允许输出重命名路径不予采用。

### D5 固定公开目录、报告与回执

渠道目录为 `dist/delivery/<request-id>/`，包含映射后的资产、`release-notes.md` 和 `channel-manifest.json`。manifest 使用 `release-channel-manifest/v1`，保存请求 ID、候选 ID 与哈希、渠道公开目标、资产 path/name/size/sha256 和固定 `publish=NOT_RUN`、`execution=NOT_RUN`。Release 说明仅由候选公开 notes 渲染。

公开报告为 `docs/delivery/<request-id>-channel.md`，包含受管标记、请求哈希、来源候选、渠道目标、资产清单和相同 NOT_RUN 状态。私有回执为 `.framework/local-state/delivery/<request-id>-channel.json`，保存规范化请求哈希、目录文件哈希、报告哈希和固定状态，不保存额外正文或凭据。

### D6 目录暂存与多产物恢复

全部输入、渲染和哈希计算在写入前完成。正式执行先在同文件系统的私有临时目录准备完整渠道目录并核验，再依次提交目录、公开报告和私有回执。已有目录先移动到同级临时备份；后续任一步失败时移除新目录并恢复旧目录，报告按旧字节恢复或清理，回执在未成功提交前保持旧版本。临时文件在成功或失败后清理。

dry-run 返回预计 manifest、目录文件和报告哈希但不创建暂存或正式文件。重复输入 UNCHANGED，同 ID 合法变化 UPDATED；任一正式产物缺失、额外文件、人工修改或哈希不匹配均 `CHANNEL_CONFLICT`，不自动修补。首版保证受控写入异常恢复，不把进程强制终止后的自动恢复宣称为已验证能力。

### D7 错误分类、文档和离线验证

错误使用 `CHANNEL_INPUT`、`CHANNEL_NOT_READY`、`CHANNEL_STALE`、`CHANNEL_UNSUPPORTED`、`CHANNEL_CONFLICT`、`CHANNEL_LIMIT`，路径安全继续保留 `SYMLINK` 和 `PATH_ESCAPE`。文档只在测试与交付指南增加可选入口。

测试以临时项目、虚拟 4A 证据与资产建立真实候选，再覆盖 READY 绑定、非 READY、过期哈希、目标与名称非法、私有输入、dry-run、幂等、更新、额外文件、人工冲突、各提交阶段失败、CLI 授权及 4A/4B/公共发布回归。全部测试离线，不创建真实 Release。

## Risks / Trade-offs

- [候选 dry-run 重新核验全部证据增加适配耗时] → 换来来源新鲜度和统一 READY 语义，避免另建一套候选解释器。
- [目录、报告和回执无法形成真正跨文件原子事务] → 使用同文件系统暂存、备份和异常恢复，并明确不宣称强制终止后的自动恢复。
- [受限 tag 和资产名不支持所有 GitHub 合法形式] → 首版优先可审计与跨平台安全，后续需求通过独立规格扩展。
- [复制资产增加磁盘占用] → 限制项数和总字节，且只复制显式选择项。
- [公开 notes 仍可能含错误公开内容] → 复用 4A 固定字段并要求人工发布前复核，不声称自动秘密扫描。

## Migration Plan

无旧数据或 schema 迁移。未运行 `channel` 的项目不产生新路径，既有候选、dist 资产和公共壳发布不变。回退可移除渠道入口和派生模块；不删除业务原始资产、候选资料或人工修改的渠道产物。
