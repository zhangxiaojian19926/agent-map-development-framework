# 测试与交付

完成声明必须绑定最终工作树或提交及实际验证证据。文档存在、脚本启动、静态地图 READY 或模块单测通过都不能单独证明业务完成。

## 测试分层

| 层级 | 责任 | 证据 |
|---|---|---|
| 模块单元/局部测试 | 模块责任方 | 有效失败、最小修复、受影响回归 |
| 契约测试 | 接口提供方与消费方共同确认 | 输入输出、错误、超时和兼容性 |
| 跨模块集成 | 明确的集成责任方 | 共享 Scenario、参与仓库版本组合 |
| Host/Cross-build/Target | 项目约束指定的验证责任方 | 实际环境、命令、产物和结果 |
| 发布验收 | 发布责任方 | 最终集成版本、适用场景和恢复边界 |

未执行写 NOT_RUN，环境故障写 INFRA_ERROR，不适用写 N/A 并解释，只有实际断言通过写 PASS。

## 可选功能差距追踪

需要把产品目标、已批准 Scenario、tasks 和验证记录放在同一追踪链时，验证责任方可准备 `feature-parity-request/v1` 与 `verification-evidence/v1`，再独立运行 `parity --request`。证据文件和 artifact 位于 `docs/verification/<change>/`，每条记录关联 Req/Scenario、已完成 task、测试、环境、结果和产物 SHA-256。报告生成器不运行测试，不补写证据，不修改 task。

只有 FUNCTION/PASS 和有效 artifact 支持 VERIFIED；VISUAL/ACCESSIBILITY/BRAND 保留为独立诊断。MUST 项未实现、未验证或缺失必须 Scenario 时为 GAPS_OPEN，匹配功能 FAIL 时为 FAILED；S1–S4 开放问题按显式策略阻断或报告。公开报告不复制私有产品自由文本，私有回执记录来源与报告指纹。dry-run、重复、更新和失败恢复均确定性处理，不能以完成分数、文件存在或 Agent 声明替代实际验收。

## 可选发布候选检查

需要把已声明的构建与功能验证整理成发布候选时，责任方准备 `release-candidate-request/v1`，绑定候选 ID、版本、源码版本、公开说明、证据及 `dist/` 中明确允许公开的文件。证据使用 `delivery-evidence/v1`，每条记录包含 BUILD/FUNCTION/INTEGRATION 类别、结果、环境和公开附件哈希；PASS 必须有有效附件。工具只核验声明与附件匹配，不证明历史执行，也不运行构建或测试。

先执行 `python3 .agent-framework/tools/framework candidate --target . --request <请求> --dry-run`。确认结果后，仅在本次获准写入时增加 `--allow write`。公开报告写入 `docs/delivery/<id>-candidate.md`，私有回执位于 `.framework/local-state/delivery/<id>.json`。READY 仍需至少一条 BUILD/PASS 和 FUNCTION/PASS；失败为 FAILED，缺少通过记录或其他未执行项为 GAPS_OPEN。报告始终保留 release=NOT_RUN，重复执行幂等，人工修改冲突保留，第二份写入失败恢复旧报告。

候选报告只索引显式产物，不复制文件、不生成平台安装包，也不提交、推送、打 tag、上传、部署或创建 Release。真实发布仍需独立渠道适配、明确目标和本次授权。

## 交付顺序

1. 将每个 Req/Scenario 关联到 task、模块、测试、环境和证据。
2. 完成规格符合性和代码质量评审，重要问题闭合后重跑检查。
3. 结构变化时更新地图和项目资料，再运行最终 doctor。
4. 展示结果，由用户选择保留、提交、PR、合并、部署或发布。
5. 有 change 时先同步规格再归档；未完成任务或缺证据不得宣称完整归档。
6. 问题闭合后一次列明知识内容与目标，获明确授权才摄入。

## 流程卡

| 项目 | 约定 |
|---|---|
| 输入 | 已批准 Scenario、最终 diff、参与模块版本、验证环境和交付目标 |
| 写入范围 | 测试、验证报告、必要项目资料、受管规格同步；外部动作另行授权 |
| 授权 | 评审机制、设备、部署、提交、推送、发布和知识写入分别核对 |
| 验证证据 | 测试输出、评审结论、集成结果、最终 commit 或工作树/diff 标识 |
| 完成状态 | 适用场景通过、重要问题闭合；提交、集成、归档和知识状态分别说明 |
