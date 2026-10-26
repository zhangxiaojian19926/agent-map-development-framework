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
