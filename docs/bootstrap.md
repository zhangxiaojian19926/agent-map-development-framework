# 一键接入与完整开发

Python 3.9+，macOS/Linux。命令不安装依赖、不初始化 Git、不创建远程仓库。CodeGraph 适配版本 1.6.0，Codex CLI 0.151.0，OpenSpec CLI 1.11.0；缺失或未适配版本明确报告，不自行修复全局工具。

## 已有工程

从公共分发目录执行：

```bash
python3 tools/framework init --target /path/to/project
```

交互填写稳定项目 ID 和 Agent（codex/manual），一次查看并确认动作范围。Git 边界在默认发现根 `.`、深度 4 内成为候选，确认后登记；无 Git 的 ZIP 目录用下面的 module add，或配置显式声明。已有人工 AGENTS 报冲突，不覆盖，需先人工合并入口。

可复现非交互接入建议先准备 config.json：

```json
{
  "project_id": "my-project",
  "agent": "codex",
  "index": true,
  "hooks": false,
  "openspec": true,
  "discovery_roots": ["modules"],
  "modules": [
    {"id": "api", "path": "modules/api", "writable": true},
    {"id": "worker", "path": "packages/worker", "writable": false}
  ]
}
```

```bash
python3 tools/framework init --target /path/to/project --config config.json --dry-run
python3 tools/framework init --target /path/to/project --config config.json --yes \
  --allow write --allow agent --allow index --allow openspec
```

`--yes` 不代替能力授权。`agent` 允许把登记模块的受支持源码（单文件最大 1 MiB、总上下文最大 200,000 字符）发送给当前 Codex 模型；不应对未审查的私有工程直接授权。Agent 使用临时工作目录、只读沙箱、禁用 shell/插件/应用/hooks，只接收源码包。沙箱不等于源码保密协议；认证、服务留存和费用遵守宿主服务设置。

`index` 允许 CodeGraph 索引与受管排除配置；`hooks` 另行允许非共享、项目内 Git hooks；自定义/既有 hooks 保留并报告冲突。没有守护进程的环境依靠任务入口与收尾检查，不承诺关机或 Agent 离线时即时建图。

## 新需求，没有代码或 Git 仓库

先由 Coding Agent 按顶层流程完成需求、设计、实施计划。下载文件里的 `approved:true` 无效。config 中 `artifacts` 保存这三份已确认正文，键为 requirements/design/plan；modules 可声明尚未实现的路径。当前调用提供逐份正文 UTF-8 SHA256：

```bash
python3 tools/framework new --target /path/to/new-project --config approved.json --yes \
  --allow write --allow openspec \
  --approve requirements=SHA256 --approve design=SHA256 --approve plan=SHA256
```

未批准返回 NEEDS_DESIGN_APPROVAL 且不建目录。哈希证明确认针对哪份内容，不替代人类授权来源。`new` 建骨架，不擅自选技术栈或生成业务实现。空模块标 PLANNED，CodeGraph 为 NOT_APPLICABLE。

随后在目标根启动 Coding Agent，读取 AGENTS、项目资料、模块入口及按需技能。使用 OpenSpec CLI 创建 change，读取实际 instructions/contextFiles；按已批准计划 TDD，做独立评审和实际运行验证。初始化不会偷偷递归运行一个无限制开发 Agent。用户明确要求开发时，Coding Agent 承接下一步。

## 导入与更新模块

安装后命令入口是 `.agent-framework/tools/framework`：

```bash
python3 .agent-framework/tools/framework module clone --target . \
  --id engine --path modules/engine --url https://example.com/owner/engine.git \
  --yes --allow write --allow clone --allow agent --allow index --allow openspec
python3 .agent-framework/tools/framework module add --target . \
  --id archive --path vendor/archive --yes --allow write --allow agent --allow index --allow openspec
python3 .agent-framework/tools/framework module sync --target . --yes --allow write
python3 .agent-framework/tools/framework refresh --target . --yes --allow write --allow agent --allow index --allow openspec
python3 .agent-framework/tools/framework doctor --target .
```

只给配置实际启用能力对应的 grants；hooks 同理单独添加。clone 不递归拉 submodule，不执行下载代码或 hooks；本地测试来源另需 `--allow local-clone`。`module add` 的 ID 是明确身份确认；移动目录用同一 ID 和新路径登记，目录消失保留 missing 历史。

普通 git clone 不可能被本框架全局截获：`doctor` 在批准发现根内报告新候选，sync 更新候选但不调用模型；确认后 add。ZIP 目录没有描述符则不猜身份，显式 add 即可。无论几个模块，同仓共享 repo/index 身份，独立仓库分别记录。

## 输出和恢复

人工资料在 docs/project；实际目录在 module-catalog.generated.json；关系 JSON 是唯一地图来源，Markdown 从其渲染。每条关系带双端引用、精确锚点、SHA256、证据等级及 runtime=NOT_RUN。静态地图永远不是业务测试报告。

`.framework/local-state` 含本机归属、事务、工具日志与批准指纹，默认 0600 文件；不要提交日志和源码包。`.agent-framework` 是带许可证的固定公共包。建议项目自行把 `.framework/` 加到其忽略规则；生成器不覆盖已有 .gitignore。

```bash
python3 .agent-framework/tools/framework resume --target . --run-id bootstrap --yes --allow write
```

resume 重验已写文件，人工改动则停；外部步骤用带当次权限的 refresh 恢复。僵死锁先确认 PID 已结束后人工处理，不自动抢锁或删除数据。配置、人工 AGENTS、排除策略冲突时保留现状。

退出码：0=本命令完成（预览也可为0），2=输入错误，3=确认/冲突，4=外部执行失败，5=部分完成/等待 Agent。doctor 不写文件、不启动模型/索引/业务测试；返回各层状态。地图 READY 不意味着 runtime VERIFIED。

## 工具适配审计

CodeGraph 1.6.0 的 init 在 watcher 禁用且 `--yes` 时可能安装 hooks。适配器使用经源码确认的 CODEGRAPH_FORCE_WATCH=1、CODEGRAPH_NO_WATCH=0，省略 --yes；初始化索引不启动持久 watcher。禁用 telemetry 和隐式下载。status 必须完整，query 必须返回批准源码的真实符号节点才记 READY。codegraph.json 使用默认拒绝及精确源码例外，未来新增未批准目录仍被排除；人工配置不一致时报冲突而非覆盖。

Codex 分析关闭工具，开发任务则由用户明确启动 workspace-write 沙箱，二者权限不同。工具版本升级后需重新验收，不默认视为兼容。

## 可重复真实验收

下面命令会创建一个必须尚不存在的合成测试目录，调用真实 Codex 模型、执行其生成的 Python 代码并初始化 CodeGraph，可能产生模型使用费用。必须显式选择：

```bash
python3 tools/verify-live --target /path/to/new-validation-directory --allow-live
```

它运行三模块已有工程接入、重复运行、真正业务调用、新需求审批拒绝/批准、Codex 开发、独立测试及规格/地图检查。原始输出位于 evidence，汇总在 report.json。普通 CI 不执行此命令，不使用任何模型凭据；只跑离线合成测试。

已执行环境、独立复审、场景证据与未执行边界见[本地验收记录](verification/bootstrap-0.2.0.md)。
