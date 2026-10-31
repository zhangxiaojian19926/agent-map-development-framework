## Context

现有 `package_project` 只哈希已有 `dist/`，parity 则提供受限 JSON 证据、来源核验和双产物恢复模式。4A 需要新增独立请求与报告，不能扩展 `doctor` 的只读职责，也不能复用公共壳 `prepare-release` 来推断业务项目已获发布授权。

## Goals / Non-Goals

**Goals:**

- 用固定 schema 关联候选、源码版本、构建/功能证据和公开产物。
- 以离线、确定性报告呈现真实差距；dry-run 与正式运行共用计算。
- 复用安全路径、哈希、原子写入和既有 CLI 错误约定。

**Non-Goals:**

- 不构建、不运行测试、不复制产物、不生成平台安装包。
- 不自动填写公开说明，不证明声明证据的历史真实性。
- 不实现市场研究、渠道适配、上传、Git 操作或设备动作。

## Decisions

### D1 新增独立 `candidate --request`，只增加 `write` 授权

请求采用 `release-candidate-request/v1`，固定包含 `id`、`version`、`source_revision`、`evidence`、`artifacts` 和公开 `notes`。候选 ID 为安全 token，版本与源码版本为受限单行公开文本；证据与产物均为安全相对路径和 SHA-256。dry-run 只读，正式生成只要求 `write`，与其他业务动作及 `--summary` 互斥。

备选方案是扩展 `package`；这会改变已有轻量哈希命令的含义并迫使旧调用方处理交付证据，因此不采用。

### D2 使用 `delivery-evidence/v1` 描述已声明证据

每份证据绑定 `source_revision`，包含 `records`：稳定 ID、category（`BUILD`、`FUNCTION`、`INTEGRATION`）、result（`PASS`、`FAIL`、`NOT_RUN`、`INFRA_ERROR`、`N/A`）、公开 test/environment 和可选 artifact。`PASS` 必须有项目内普通附件且哈希匹配；其他结果可带附件但不能升级为通过。N/A 与 INFRA_ERROR 必须有公开原因分类。

候选至少要求一条 BUILD/PASS 和一条 FUNCTION/PASS。INTEGRATION 若被声明则纳入差距，但不替代 FUNCTION。任一 BUILD/FUNCTION/INTEGRATION FAIL 为 FAILED；无失败但有未运行、环境异常、未解释的 N/A 或缺少必需通过项为 GAPS_OPEN。该工具仅证明所声明记录及附件匹配，不证明历史执行。

### D3 显式公开产物白名单，不扫描或打包目录

`artifacts` 逐项声明 path 和 sha256，系统核验项目内普通文件、拒绝链接和私有前缀，并记录 size。首版只允许 `dist/` 下的文件，避免把源码、项目资料或证据意外纳入候选；不递归推断“整个 dist 都应公开”。候选报告索引现有产物，不另建可复制发布包，后者留给具体渠道。

公开说明 `notes` 只接受固定 `summary`、`changes`、`known_limits` 字符串/字符串数组，进行长度与控制字符校验。请求者负责其公开性；证据附件正文不进入渲染器。

### D4 固定双产物与单一状态计算

公开输出为 `docs/delivery/<id>-candidate.md`，私有回执为 `.framework/local-state/delivery/<id>.json`。报告包含受管标记、请求/证据哈希、版本来源、逐项记录、产物清单、差距代码、公开说明和 `release=NOT_RUN`。回执保存规范化请求哈希、全部输入哈希及报告哈希，不保存证据正文。

全部输入有效后计算状态：FAIL 优先；其余必需通过项或记录缺口为 GAPS_OPEN；全部满足为 READY。输入错误在写入前失败。退出码分别保持成功、差距/失败和输入错误的既有风格。

### D5 原子写入、幂等与冲突恢复

dry-run 返回相同状态、差距及预计报告哈希但不写文件。正式执行先写公开报告再写私有回执，第二步失败恢复旧公开报告；首次失败清理本能力新公开报告。重复输入 UNCHANGED，同 ID 合法变化 UPDATED；报告或回执哈希不符、跨来源错配时冲突保留，不自动覆盖。

### D6 离线契约测试和最小文档接入

测试使用临时项目、虚拟证据和附件，覆盖 READY/FAILED/GAPS_OPEN、哈希过期、私密路径、公开说明、dry-run、幂等、冲突、第二份写入恢复、CLI 互斥和既有 package 回归。文档只新增显式使用入口，不改变 BOOTSTRAP 的必经步骤。真实构建、业务测试和发布均 NOT_RUN。

## Risks / Trade-offs

- [声明证据可能被错误填写] → 绑定源码版本、附件和哈希，并保留责任方真实执行及最终验收要求。
- [只允许 dist 降低首版通用性] → 提供明确可审计边界，其他渠道目录由 4C 规格扩展而非隐式放行。
- [公开 notes 仍可能误含秘密] → 固定字段、长度限制和公开责任说明；不声称自动秘密扫描。
- [候选报告不是独立安装包] → 明确其索引性质，4C 才能基于候选生成渠道产物。

## Migration Plan

无旧状态迁移。未使用 `candidate` 的项目没有新文件；既有 `package` 与公共壳 release 不变。回退可移除候选入口和派生报告模块，不删除或修改业务产物、规格与原始证据。
