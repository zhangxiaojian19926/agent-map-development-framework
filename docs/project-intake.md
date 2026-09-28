# 工程启动输入与当前 Agent 协议

用户入口是 [BOOTSTRAP](../BOOTSTRAP.md)，不是一组必须自己执行的脚本。下面是 Agent 和维护者使用的准确接口。

## 输入语法

- 裸格式只含 `名称 = URL`、`名称: URL` 或 `名称：URL`，按第一个分隔解析；模块“项目”不会被当元信息。
- 结构化格式以 `# 工程启动单` 标识；元信息允许项目/目标/仓库，模块放 `## 模块仓库`，可选来源放 `## 来源版本`。
- 来源是 branch/tag/完整 commit SHA，省略则查询远程默认 HEAD；不猜 main，不创建不存在的分支。
- 空行和整行注释可忽略；不裁剪 URL 行尾注释、不执行文本。坏模块行不能降级为新工程，错误带行号。
- 名称保留显示值；目录使用 NFC，中文安全名直接成为 `modules/中文名`。禁止控制字符、分隔符、点路径、平台保留名、尾点/空格；等价 Unicode/大小写碰撞和重复键均拒绝。分隔符两侧空白属于格式空白。
- ASCII 安全名直接作 ID；其他名称用规范化名的 SHA256 前12位加 module-，仍检查冲突。换序不改变 ID，同 URL不同名不合并。
- HTTPS/SSH URL 不允许密码、HTTPS用户名、query或fragment。合成本地绝对路径需要当前 local-clone grant。

## 存储、认证与恢复

目标外私有启动区保存原文快照、request.json、acquisition.json。目标只保存 intake_id、最小名称/路径映射，不复制 URL或原文；这些记录不构成永久权限，启动区不要加入公共仓库。

每模块单独保存状态与来源/HEAD。静态冲突在下载前拒绝；动态失败给每个模块结果，整体 PARTIAL。已完成模块恢复时核对 Git 根、remote、HEAD、配置和用户修改；不重复获取。未完成且已留下目录时报告冲突，保留现场，不自动删除或覆盖。需要修复现场的步骤由 Agent 提议并另核对授权。

Git 使用隔离配置/环境，禁仓库 hooks、fsmonitor、自动 submodule/LFS 和任意凭据 helper。支持经当次 auth 授权的当前用户 SSH-agent socket，SSH不读自定义配置，严格校验已知主机；没有合适认证则 AUTH_REQUIRED。仅 socket 接口的离线测试不代表真实私有仓库认证通过。HTTPS 私有 helper、代理/custom SSH 配置尚不自动适配。

## 当前 Agent 结果协议

旧 v1 `analyze-request` 需要 write/agent，返回 request_id、source_digest、modules 和最多约200KB源码。旧集成仍可调用；新初始化使用下述 v2。程序只持久化绑定，分析过程由当前会话完成；没有秘密隔离沙箱的承诺，源码传给模型仍受宿主政策和用户授权约束。

`accept-analysis --result FILE` 输入为以下形状（id/hash/anchor 必须来自实际观察包）：

```json
{
  "request_id": "current-request-id",
  "source_digest": "current-source-digest",
  "result": {
    "module_summaries": [{"id": "api", "summary": "实际职责"}],
    "relationships": [],
    "uncertainties": ["没有足够证据证明跨模块关系"]
  }
}
```

每条关系含 id/from/to/kind/interface/provenance/runtime_validation/evidence。kind 为 contains、build-dependency、runtime-call、data-exchange；provenance 为 STATIC_SUPPORTED 或 INFERRED；runtime_validation 固定 NOT_RUN。evidence 每项含相对 path、精确源码 anchor、sha256；STATIC_SUPPORTED 必须覆盖两个端点。所有模块都要有非空摘要，不能用同名符号猜联系；同一导入和调用可分别证明 build-dependency/runtime-call。

程序验证请求、目录、源码指纹和证据，接受后消费该请求，发布关系/模块地图及 current-session 记录。它是本地过程记录，不是身份认证签名或外部CLI执行证明。无效结果不覆盖旧地图；过期需重新请求，换宿主需重新确认当前权限。

## 分层结果和兼容

PREPARED：基础入口已建立，不保证完整资料。`documentation` 校验资料及文件指纹；`coverage` 校验 v2 全批覆盖；`handoff` 标记 READY_FOR_PLANNING、NEEDS_DESIGN_APPROVAL 或 BLOCKED。`initialization=COMPLETE` 要求前三项满足、无候选/缺失模块、要求的索引/hooks就绪及实际地图有效。源码、目录、框架或资料变化使旧状态失效。runtime 仍为 NOT_RUN；COMPLETE 不是业务实现获批或运行成功。旧 new 的三份明确批准门禁和旧 CLI 步骤退出码保持不变。

内部 CLI 退出码沿用0/2/3/4/5：0仅当前步骤成功（预览也是0），2输入错误，3授权/冲突，4外部失败，5部分完成。恢复初次接入从同一分发入口和私有启动区继续；后续工程维护从安装包入口操作。

当前协议不要求非Codex调用Codex，但真正宿主兼容需独立实测。最终覆盖及 NOT_RUN 项见 [验收](acceptance.md)。

## v2 分批分析

以下均为当前 Agent 内部动作，不要求用户提供机器参数。四个动作均需要本次 write/agent grants：

1. `analyze-request --protocol v2` 返回 session_id、source_digest、catalog_digest、framework_digest、sources、scope 和 batches。sources 只有路径/hash；batches 有 batch_id、slices 元数据与 PENDING/ACCEPTED。相同绑定恢复原会话。
2. `analysis-batch --session-id ID --batch-id ID` 输出最多200000字节的实际序列化 JSON 源码包：slices 含 path/file_sha256/start_line/end_line/content/slice_id，行号从1起且包含两端。空文件为1/0；单行超限拒绝，不截断。已 ACCEPTED 返回已收结果，不重送源码。
3. `accept-batch --session-id ID --batch-id ID --result FILE` 的 FILE 是 `{"summary":"本批职责、符号、接口与证据位置的有效摘要","uncertainties":[],"slice_ids":["包内ID，原顺序"]}`。最多100000字节；同结果重放幂等，不同结果冲突。摘要保留后续聚合需要的接口信息，不得只写“已读”。
4. 全部 ACCEPTED 后跨批核对双方证据，`finalize-analysis --session-id ID --result FILE`。FILE 直接是 v1 示例的 **result 对象**，不要加 request_id/source_digest 外壳。缺批、过期或无效关系拒绝；成功才发布地图及 COMPLETE coverage。

会话记录在 `.framework/local-state/analysis-session.json`，不复制原始源码，批次摘要仍按本地敏感数据管理。coverage 列明被扫描范围：允许后缀、排除目录、最大深度12、每模块5000文件、每文件1MiB。完整只针对该范围，不代表未扫描语言/大文件/运行配置全部已理解。框架/源码/目录改变时先同步、重新分批；初版不跨版本缓存推断。发布中断保留事务现场，核对当前版本与权限后恢复，不能用旧journal跳过新分析。

## 结构化资料 dossier

`accept-docs --result FILE` 需要 write/agent。FILE 最大1MiB，固定形状：

```json
{
  "project": {"goal": {}, "non_goals": {}, "architecture": {}, "interfaces": {}, "integration_order": {}, "constraints": {}, "resources": {}},
  "modules": [{"id":"实际catalog ID", "purpose":{}, "non_responsibilities":{}, "entrypoints":{}, "inputs":{}, "outputs":{}, "dependencies":{}, "internal_roles":{}, "commands":{}, "limitations":{}, "knowledge":{}}],
  "blockers": [], "rule_conflicts": [], "planning_refs": []
}
```

上例 `{}` 是协议位置示意，提交时必须全部填充；modules 必须覆盖 catalog 中每个模块恰好一次，无模块用空列表。每个字段对象为：

```json
{"value":"具体项目事实或明确限定的推断", "status":"KNOWN", "provenance":"STATIC_SUPPORTED", "evidence":[{"path":"modules/api/app.py","sha256":"当前文件完整SHA256","anchor":"文件内精确原文"}]}
```

- status：KNOWN、NOT_VERIFIED、NOT_CONFIGURED、NOT_APPLICABLE；provenance：STATIC_SUPPORTED、DECLARED、INFERRED。schema 校验不证明语义正确，Agent 仍须逐字段核对；不能把未知职责标成不适用以绕过分析。
- KNOWN/NOT_VERIFIED 必须有当前hash和精确anchor。源码证据须在catalog；用户声明/设计证据须来自 planning_refs。后者只允许明确列出的 `docs/project/*.md` 或 `openspec/*.md` 公开文件，同样带 path/hash/anchor，不能引用私有启动区或 local-state。
- planning_refs 不得引用本次即将生成的overview/architecture/collaboration/constraints/resources/handoff或模块资料页，否则SELF_REFERENTIAL_EVIDENCE（写入会使自身证据失效）。使用独立的design-input等公开源文档，保留已有人工资料，不覆盖它来凑hash。
- NOT_CONFIGURED 仅用于 resources/knowledge，必须 reason；NOT_APPLICABLE 也必须具体 reason。它们可不带 evidence，但仍需有意义的 value。关键事实缺失时加 blockers，不能用此状态虚假完结。
- commands 正常为 NOT_VERIFIED，value 是列表，每项含 command、cwd（目标相对路径）、prerequisites、execution=NOT_RUN，并提供命令依据。没有适用命令时可 NOT_APPLICABLE，value 为说明文字及 reason。这里不执行命令、不安装依赖。
- rule_conflicts：`[{"module_id":"真实ID","description":"原规则与接入的实质冲突"}]`；不写冲突模块的AGENTS，保留完整项目侧资料并标 PARTIAL。blockers 是具体阻塞字符串列表。
- 不提交 TODO/TBD/待填写等占位语。生成器保留人工正文，受管区块被人工修改则拒绝；只读模块在 `docs/project/modules/<id>.md` 获得完整入口。公共工作流仍只在根规则中。

新工程将拟议模块和接口写入公开 `docs/project/design-input.md`，作为 DECLARED planning_ref；此时 catalog 可为空，不建空目录冒充实现。用户真实批准该设计后由 Agent 计算 hash，附 `--approve design=SHA256` 接收资料；修改设计使旧批准失效。此记录仅代表设计决定，继续实施仍核对当前请求和获批计划。

输出包含 overview/architecture/collaboration/constraints/resources、模块局部入口及 handoff。handoff 的机器记录包含版本/模块/规划证据/下一步和权限缺口。doctor 同时检查当前内容指纹，不因文件存在就认为齐全。已有批准的后续任务从实际 OpenSpec上下文继续，不把初始化重新跑一遍。
