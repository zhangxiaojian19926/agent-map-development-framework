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

`analyze-request` 需要 write/agent，返回 request_id、source_digest、modules 和最多约200KB源码。程序只持久化绑定，分析过程由当前会话完成；没有秘密隔离沙箱的承诺，源码传给模型仍受宿主政策和用户授权约束。

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

PREPARED：入口和资料已建立；理解：有证据地图；索引：工具实际验证；development：业务设计/计划另行批准；runtime：真实业务测试才可提升。旧 new 的三份明确批准门禁保持不变，新用户入口走 prepare。

内部 CLI 退出码沿用0/2/3/4/5：0仅当前步骤成功（预览也是0），2输入错误，3授权/冲突，4外部失败，5部分完成。恢复初次接入从同一分发入口和私有启动区继续；后续工程维护从安装包入口操作。

当前协议不要求非Codex调用Codex，但真正宿主兼容需独立实测。最终覆盖及 NOT_RUN 项见 [验收](acceptance.md)。
