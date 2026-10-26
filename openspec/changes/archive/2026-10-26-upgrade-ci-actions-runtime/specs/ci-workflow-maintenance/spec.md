## Purpose

保持公共工程验证与发布工作流使用受支持的 CI Action 运行时，同时在依赖升级时保护现有验证矩阵、权限和发布行为。

## ADDED Requirements

### Requirement: 受支持的 Action 运行时

系统 SHALL 在验证与发布工作流中使用官方明确声明受支持运行时的稳定 `actions/checkout` 和 `actions/setup-python` 版本；系统 MUST NOT 继续将已知弃用运行时作为工作流的声明版本。

#### Scenario: 升级两个工作流

- **WHEN** 维护者检查验证与发布工作流中的 checkout 和 Python 配置步骤
- **THEN** 两者均使用 `v7` 主版本，其官方 Action 声明为 Node.js 24，不保留旧的 `v4` 或 `v5` 引用

#### Scenario: 实际 CI 验收

- **WHEN** 升级后的验证工作流在 GitHub Actions 完成
- **THEN** Ubuntu 和 macOS 任务均成功，且不出现 checkout 或 setup-python 的 Node.js 20 弃用警告

### Requirement: 工作流行为兼容

系统 MUST 在 Action 升级时保持 Python 版本、验证平台、权限、并发、验证命令和发布步骤的既有含义；离线检查 MUST NOT 冒充实际 CI 或发布验收。

#### Scenario: 验证行为不变

- **WHEN** 验证工作流因 push、pull request 或手动触发运行
- **THEN** 仍使用 Python 3.9 在 Ubuntu 和 macOS 上依次执行框架检查及完整测试，权限和并发策略不变

#### Scenario: 发布边界不变

- **WHEN** 发布工作流被定时或手动触发
- **THEN** 仍先执行相同验证，再按原条件准备版本、提交、打标签和发布，不因 Action 升级自动扩大权限或增加发布触发器

#### Scenario: 仅完成离线验证

- **WHEN** 本地测试通过但尚无升级后 GitHub Actions 的实际运行证据
- **THEN** 实际 CI 状态标记为 `NOT_RUN`，不得宣称警告已在线消除或发布流程已实测
