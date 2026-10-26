# 业务项目目录布局

本指南适用于由公共工程壳接入或创建的业务项目。它只规定目录责任，不替代[公共开发流程](../framework/development-workflow.md)、项目实际约束或模块局部规则。

## 标准结构

新项目推荐单仓、模块化组织；已有项目保留真实源码位置，不为套模板而迁移。

```text
project/
|-- AGENTS.md
|-- README.md
|-- framework-project.json
|-- module-catalog.generated.json
|-- llm-wiki-aliases.json
|-- .agent-framework/
|-- .framework/
|-- docs/
|   |-- project/
|   |-- runbooks/
|   `-- verification/
|-- openspec/
|   |-- specs/
|   `-- changes/
|-- modules/<module-id>/
|-- knowledge/project/
`-- dist/
```

`docs/runbooks/` 和 `docs/verification/` 在有实际运行或验证内容时建立；未获批准的拟议模块只在设计或规格中出现，不创建空目录冒充实现。

## 目录所有权

| 路径 | 内容与责任方 | 编辑方式 | 提交规则 |
|---|---|---|---|
| `AGENTS.md` | 项目入口；人工正文与框架受管区块 | 人工编辑非受管部分，框架只更新受管区块 | 提交；冲突时停止覆盖 |
| `framework-project.json` | 经确认的项目与模块声明 | 初始化或登记流程 | 提交，不手工伪造模块 |
| `module-catalog.generated.json` | 实际模块观察；生成器负责 | 不手改，通过受管同步更新 | 按现有项目契约跟踪，不另建竞争登记 |
| `llm-wiki-aliases.json` | 项目内知识库 alias 注册 | 明确授权后修改 | 提交，不保存凭据 |
| `.agent-framework/` | 固定版本公共工程壳 | 仅框架升级流程 | 建议提交同一版本，不手改 |
| `.framework/` | 锁、日志、批准指纹、本机工具和恢复状态 | 框架运行时 | 不提交，不作为共享事实 |
| `docs/project/` | 当前项目事实、架构、资源、交接和模块资料 | 人工正文与受管生成分开 | 提交；未知和未验证状态如实保留 |
| `openspec/changes/` | 活跃需求、设计、任务与验收 | 当前 change 流程 | 提交，未完成不得冒充归档 |
| `openspec/specs/` | 同步后的正式能力规格 | 规格同步流程 | 提交，不绕过 change 偷改验收 |
| `modules/<module-id>/` | 业务源码、局部规则、模块测试与接口责任 | 模块责任方 | 按各自 Git 边界提交 |
| `docs/runbooks/` | 已核实的运行、部署和恢复步骤 | 操作责任方 | 提交；未执行命令保持 NOT_RUN |
| `docs/verification/` | 最终验证矩阵和证据索引 | 验证责任方 | 提交；绑定版本、环境和结果 |
| `knowledge/project/` | 已确认、可复用的项目知识 | 获明确授权的摄入流程 | 按隐私策略提交，不收单次日志 |
| `dist/` | 构建输出 | 构建系统 | 通常忽略，发布产物交给 CI/Release |

## 状态不能混用

```text
docs/project  = 现在是什么
openspec      = 准备改变什么、当前做到哪一步
knowledge     = 已验证且以后仍值得复用什么
.framework    = 这台机器当前的运行状态
```

静态关系地图不证明业务运行成功；`initialization=COMPLETE` 不代替具体业务 Scenario、集成验证或发布批准。

## 业务源码和测试归置

- 已有源码原地接入，在 `docs/project/resources.md` 和模块资料中记录真实路径。
- 新项目默认把顶层业务模块放入 `modules/<module-id>/`，模块内部遵循实际语言生态。
- 跨模块接口由明确的提供方维护契约，消费方负责适配；共享 Scenario 关联同一个 change。
- 模块局部测试放在模块内。跨模块集成测试放在有明确维护责任的编排仓库或指定责任模块，不能留下无人负责的根级测试。
- 多仓分别记录 HEAD、未提交差异和最终提交；模块单测通过不等于集成通过。

## 使用边界

| 项目 | 约定 |
|---|---|
| 输入 | 新文件类型、模块归属、活跃 change 和实际 Git 边界 |
| 写入范围 | 只写该文件唯一责任目录，不写无关模块或公共包 |
| 授权 | 业务写入、知识摄入、发布和部署分别授权 |
| 验证证据 | 目录归属、模块测试、集成 Scenario、版本组合和必要 diff |
| 完成状态 | 文件位置与责任明确；业务完成仍按适用测试和交付门禁判断 |
