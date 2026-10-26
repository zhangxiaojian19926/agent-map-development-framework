## Why

公共工程壳当前混合了使用者指南、维护者资料、历史证据和目标项目运行时文件，业务项目也缺少统一的目录所有权与提交规则。这会增加初次接入和后续协作成本，并可能让历史计划、机器状态或生成文件被误当成当前事实。

## What Changes

- 增加面向使用者的目录布局、日常开发、模块生命周期、测试交付和框架升级指南，并在 README 中区分使用者与维护者入口。
- 建立公共工程壳的文档分层：现行指南、公共规则、接口参考、维护者资料和历史归档分别管理；保留稳定的技能与工具路径，不进行无收益的整体改名。
- 将目标项目 `.agent-framework/` 的复制规则改为显式运行时白名单，排除维护者测试、历史验收、历史计划和发布资料，同时保持现有初始化 CLI、技能和项目人工内容兼容。
- 定义业务项目的目录所有权、生成文件编辑边界、提交策略，以及 `docs/project/`、OpenSpec、知识库和 `.framework/` 的不同职责。
- 规定新模块、跨模块变更、框架升级和最终交付的目录流转与验证要求；已有业务源码保持原位登记，不强制迁移。
- 建立历史资料与旧 OpenSpec change 的清理流程：逐项核对证据，未执行项保持 NOT_RUN，完成后通过正常同步和归档流程处理，不手工伪造完成状态。

## Capabilities

### New Capabilities

- `project-layout-governance`: 规定公共工程壳与业务项目的目录分层、运行时分发边界、文件所有权、历史状态清理及目录相关验收。

### Modified Capabilities

无。当前没有已同步到 `openspec/specs/` 的能力规格；本变更不直接改写其他活跃 change 的需求。

## Impact

- 文档入口：`README.md`、`BOOTSTRAP.md`、`AGENTS.md`、`docs/` 与相关模板链接。
- 初始化生成：`tools/framework_core/generation.py` 及目标项目 `.agent-framework/` 的文件集合。
- 测试与分发：`tests/`、`tools/check-framework`、`framework-manifest.json` 和现有 CI 校验。
- 历史治理：`docs/superpowers/plans/`、`docs/acceptance.md`、`docs/verification/` 及既有未完成 OpenSpec change；只按证据收口，不扩大为实现或真实宿主验收授权。
- 业务项目契约：明确 `framework-project.json`、`module-catalog.generated.json`、`docs/project/`、`openspec/`、`modules/`、`knowledge/`、`.agent-framework/`、`.framework/` 和 `dist/` 的责任边界。
