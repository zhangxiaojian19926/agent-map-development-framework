---
name: reverse-engineer
description: 在工程壳中按授权执行静态/动态逆向观察，留存可复核证据与行为契约，并可选执行有备份和恢复门禁的设备试点。
---

# 逆向观察

正常初始化和开发不使用本技能，也不安装工具。

## 何时使用

用户给出本地目标、要模仿的行为，并明确要求逆向。先按 [BOOTSTRAP](../../BOOTSTRAP.md) 建立或打开工程。然后：

```bash
python3 .agent-framework/tools/framework reverse --target "$TARGET" --scope "$SCOPE" --yes --allow write --allow reverse --allow reverse-install
```

没有 `reverse-install` 时，缺失的必备工具只报告，不下载。已经装好且校验值相符的工具不会重装。版本、最小工具选择和操作锁见 [逆向工具与授权边界](../../docs/framework/reverse-tools.md)。

### 自动目标驱动流程

自动请求使用 `schema=reverse-request/v1`。调用方只提供稳定 `id`、目标、意图、验收、命名观察、证据和行为契约；本地文件/目录提供当前内容 SHA-256，URL 提供完整 URL 和明确网络边界。请求不得包含工具下载地址、任意版本、argv、shell 或输出路径。

```text
请求 → 本地画像 / URL 授权与私有快照 → 最小工具链计划
     → 用户批准计划 → 安装或健康复用 → 命名适配器 → 私有证据与公开摘要
```

先预览，再由当前 Agent 将返回的计划哈希传入批准参数；用户无需手工编辑内部计划：

```bash
python3 .agent-framework/tools/framework reverse --target "$TARGET" --request "$REQUEST" --dry-run
python3 .agent-framework/tools/framework reverse --target "$TARGET" --request "$REQUEST" \
  --yes --allow write --allow reverse --allow reverse-install --approve toolchain=<PLAN_SHA256>
```

URL 还需要 `web-fetch`。浏览器 DOM/脚本观察、网络记录、既有登录态分别需要 `browser-observe`、`network-capture`、`web-auth`，静态授权不会隐式包含它们。默认没有真实浏览器 provider，动态观察诚实返回 `PROVIDER_MISSING`。HTTP、localhost/私网、跨域和资源预算必须在请求中明确限制；壳不执行目标二进制、不自动绕过反爬、认证或混淆。

自动状态位于 `.framework/local-state/reverse/auto/<id>/`，版本化工具位于 `.framework/tools/<tool>/<version>/`。安装动作变化会产生新计划；相同目标和语义工具链的已完成观察保持幂等，未授权或缺 provider 的观察可在同计划补齐条件后恢复。

自动 `reverse --request` 命令可附加 `--summary`，复用原报告与退出码并输出六段式中文摘要。摘要只展示状态、工具动作及固定产物路径，不读取或输出 HTML、脚本、DOM、抓包、反编译正文或凭据；不加参数仍输出原 JSON。旧 `reverse --scope` 和其他动作不支持该参数，会在业务执行前返回输入错误。

### 可选产品行为观察

只有需要根据已授权观察重建产品或 UI 时，才由当前 Agent 整理 `product-recon-draft/v1` 草案。先 dry-run 取得计划哈希，再复制 `.agent-framework/templates/product-recon-draft.json`，填写稳定 S/F/C/E ID、证据引用、provenance、confidence、已观察/未观察状态和排除范围。框架不从自由文本猜测屏幕或流程，也不自动读取原始证据生成草案。

```bash
python3 .agent-framework/tools/framework reverse --target "$TARGET" --request "$REQUEST" \
  --product-recon "$DRAFT" --dry-run
python3 .agent-framework/tools/framework reverse --target "$TARGET" --request "$REQUEST" \
  --product-recon "$DRAFT" --yes --allow write --allow reverse \
  --approve toolchain=<PLAN_SHA256>
```

事实条目只能引用当前计划中已成功且 provenance 相符的观察；推断不得引用观察，未观察状态保持未观察。完整 `product-recon.json` 位于自动逆向私有目录，公开摘要只增加 ID、统计、证据分类和固定交接状态，不复制草案自由文本。相同草案幂等，合法更新原子替换派生视图，非法更新保留旧产物。该视图只交回设计和 OpenSpec，不自动创建需求、批准实现或声明运行验证通过；未提供 `--product-recon` 时既有行为不变。

### 兼容 v1 静态观察

旧 `--scope` JSON 字段只有 `id`、`target`、`sha256`、`question`、`action`。`action=static` 调用本地 `rea analyze`；`run` 和 `network` 只记录为未执行，壳不运行目标，也不打开网络。旧调用方无需增加 v2 字段。

### v2 多轮观察

`schema=reverse-scope/v2` 时，范围还包含 `goal`、`acceptance`、`observations`、`evidence` 和 `behavior`。`target.kind=file` 绑定普通文件路径与 SHA-256；`target.kind=device` 绑定命名设备、基线指纹和基线操作。只声明并准备目标需要的工具。每轮观察使用稳定独立 ID；同 ID 同请求幂等，同 ID 不同请求拒绝，新观察追加而不覆盖历史。

动态观察分别需要 `device-connect`、`device-observe` 或 `network-capture`。只执行操作锁中的命名只读操作，以 argv 数组和命名目标调用，不接受任意 shell。无实际操作提供方时返回 `PROVIDER_MISSING`，不伪造结果。

行为契约只引用已成功且类型匹配的观察：`STATIC_SUPPORTED`、`DYNAMIC_OBSERVED` 或无证据的 `INFERRED`。契约用于设计和 OpenSpec 交接，不自动批准实现，也不能作为源码地图证据。

### 可选设备试点与复制

只有范围含 `device_plan` 才进入设备变更流程。`action=pilot` 需要 `device-change`，并在修改前核对单台设备、当前基线、独立备份文件 SHA-256、计划内操作、验收和恢复操作。状态持久化为 `RECOVERY_READY`、`PILOT_APPLIED`、`PILOT_VERIFIED`、`ROLLBACK_READY`；任一步失败停止该设备，不自动重试。

`action=rollback` 是独立动作，需要 `device-change` 和先前的 `ROLLBACK_READY`，成功后状态为 `ROLLED_BACK`，运行验证回到 `NOT_RUN`。`action=rollout` 另需 `device-rollout` 和有效试点，只逐台处理相同兼容基线的命名设备；每台有独立备份、基线和结果，一台失败汇总为 `PARTIAL`，不能冒充全部成功。默认操作锁不启用真实修改或恢复命令。

## 结果与边界

- v1 记录：`.framework/local-state/rea/<id>.json`；原文在同目录 `<id>.raw`。
- v2 范围、观察、原文、行为契约和设备状态：`.framework/local-state/reverse/v2/<id>/`。
- 公开摘要：`docs/project/reverse/<id>.md`，不包含反编译正文、抓包原文或设备秘密。
- `evidence.raw=retain` 时私有原文与 SHA-256 留存；`discard` 时只留哈希并明确标记 `RAW_DISCARDED`。
- `doctor` 只读检查目标和证据指纹，可为 `NOT_CONFIGURED`、`READY`、`PROVIDER_MISSING` 或 `STALE`；不执行观察、不连接设备、不修复，也不改变 `initialization=COMPLETE`。
- 工具链、观察、运行验证和设备变更状态分别报告。未实际运行必须保持 `NOT_RUN`，不得写 `PASS`；离线假执行器通过不等于真实设备、网络、私有认证、备份可恢复性或部署验收通过。

观察结束后回到 [BOOTSTRAP](../../BOOTSTRAP.md) 第 5 节和 [开发流程](../../docs/framework/development-workflow.md)，不另开一套交付流程。设计批准、OpenSpec、计划、实现、验证、打包和知识库仍用工程壳原来的门禁。打包命令是 `package`，只哈希已有的 `dist/`，不执行构建，也不收入逆向目录。
