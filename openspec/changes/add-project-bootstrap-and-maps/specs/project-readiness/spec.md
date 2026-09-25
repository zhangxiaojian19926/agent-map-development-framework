## Purpose

使工程接入结果可复现并与业务完成证明分离，面向新工程和已有工程分别报告导航、宿主、索引、地图、钩子及运行环境状态，提供只读诊断和明确恢复指引。

## ADDED Requirements

### Requirement: READY-01 分层就绪与退出状态

系统 SHALL 输出 READY/PARTIAL/WAITING_AGENT/BLOCKED、每能力状态与原因；业务运行单独记 NOT_RUN/VERIFIED/BLOCKED；只选通用交接时不得报自动 Agent 就绪。

#### Scenario: READY-01-REPORT

- 前置条件：框架文件齐全但 Agent 未运行、索引失败或关系证据缺失
- **WHEN** 完成 init 或 doctor
- **THEN** 不报总 READY，逐能力列缺口、恢复命令和作用范围；排除项不记 PASS
- 超时：doctor 30 秒
- 环境与证据：Host：混合成功 fixture 和 JSON schema
- 异常分类：PARTIAL / WAITING_AGENT / BLOCKED

#### Scenario: READY-01-NO_CODE

- 前置条件：新工程全部模块仅是批准的计划
- **WHEN** 检查就绪
- **THEN** 仅声明开发骨架就绪、代码地图 NOT_APPLICABLE，不声称逻辑分析或业务验收已完成
- 超时：30 秒
- 环境与证据：Host：空工程报告
- 异常分类：无；范围限定结果

### Requirement: READY-02 只读诊断与证据等级

doctor SHALL 默认不安装、同步索引、更新地图或运行测试；发布包检查和工程检查分开；自动测试、Agent 决策复评、真实宿主集成分别记录。

#### Scenario: READY-02-READONLY

- 前置条件：已有工程含业务文件、dirty tree 和过期索引
- **WHEN** 运行 doctor
- **THEN** 文件、Git 配置、进程和网络副作用保持为零；输出过期状态和明确修复入口
- 超时：30 秒
- 环境与证据：Host：快照、受控执行器记录
- 异常分类：STALE / INFRA_ERROR

#### Scenario: READY-02-RELEASE

- 前置条件：准备发布新增初始化能力
- **WHEN** 运行发布验收
- **THEN** macOS/Linux 合成测试通过，真实 CodeGraph 与选定宿主端到端证据绑定版本；缺任一必要真实证据不标完整交付
- 超时：CI 每 job 15 分钟；真实流程逐步限时
- 环境与证据：CI 与本地集成：版本、原始输出、指纹
- 异常分类：NOT_VERIFIED
