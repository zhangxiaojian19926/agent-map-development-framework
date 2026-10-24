---
name: reverse-engineer
description: 在工程壳中按锁定的开源工具清单做一次逆向观察，再把摘要交给现有设计和开发流程。
---

# 逆向观察

正常初始化和开发不使用本技能，也不安装工具。

## 何时使用

用户给出本地目标、要模仿的行为，并明确要求逆向。先按 [BOOTSTRAP](../../BOOTSTRAP.md) 建立或打开工程。然后：

```bash
python3 .agent-framework/tools/framework reverse --target "$TARGET" --scope "$SCOPE" --yes --allow write --allow reverse --allow reverse-install
```

`--scope` 是 JSON，字段只有 `id`、`target`、`sha256`、`question`、`action`。`action` 为 `static` 时调用本地 `rea analyze`。`run` 和 `network` 只被记录为未执行，壳不运行目标，也不打开网络。没有 `reverse-install` 时，缺失的必备工具只报告，不下载。已经装好且校验值相符的工具不会重装。没有校验值的工具记入 skipped，不阻止静态观察。

版本见 [逆向工具版本](../../docs/framework/reverse-tools.md)。观察结束后回到 [BOOTSTRAP](../../BOOTSTRAP.md) 第 5 节和 [开发流程](../../docs/framework/development-workflow.md)，不另开一套交付流程。

## 结果

- 原始记录：`.framework/local-state/rea/<id>.json`
- 公开摘要：`docs/project/reverse/<id>.md`。摘要不含反编译正文。
- `doctor` 的 `reverse` 为 `NOT_CONFIGURED`、`READY`、`PROVIDER_MISSING` 或 `STALE`。它不改变 `initialization=COMPLETE`。

观察不能作为关系地图的源码证据，也不能把 `runtime_validation` 写成已运行。设计批准、OpenSpec、计划、实现、验证、打包和知识库仍用工程壳原来的门禁。打包命令是 `package`，只哈希已有的 `dist/`，不执行构建，也不收入逆向目录。
