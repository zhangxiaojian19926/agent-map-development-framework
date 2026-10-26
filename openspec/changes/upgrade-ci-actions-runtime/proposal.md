## Why

当前验证与发布工作流使用的 `actions/checkout@v4` 和 `actions/setup-python@v5` 仍声明 Node.js 20，CI 已产生弃用警告并由平台强制切换运行时。需要升级到官方明确声明 Node.js 24 的稳定主版本，同时保持现有验证和发布行为不变。

## What Changes

- 将验证与发布工作流中的 `actions/checkout` 统一升级到 `v7`，将 `actions/setup-python` 统一升级到 `v7`。
- 保留 Python 3.9、Ubuntu/macOS 验证矩阵、权限、并发、发布条件和全部验证命令。
- 增加离线工作流契约测试，防止版本回退或升级时误改验证、权限和发布边界。
- 通过实际 CI 运行确认新版 Action 可执行且不再出现 Node.js 20 弃用警告；平台 runner 迁移和容量提示不属于本变更的消除目标。

## Capabilities

### New Capabilities

- `ci-workflow-maintenance`: 规定公共工程验证与发布工作流的 Action 运行时维护、兼容边界和实际 CI 验收要求。

### Modified Capabilities

无。本变更不修改项目初始化、开发交付或逆向治理能力的需求含义。

## Impact

- 影响 `.github/workflows/validate.yml`、`.github/workflows/release.yml` 及对应测试、框架清单。
- 官方当前稳定版本为 `actions/checkout v7.0.1` 与 `actions/setup-python v7.1.0`，两者 `action.yml` 均声明 `runs.using=node24`；工作流沿用主版本引用 `v7`。
- 不改变业务源码、Python 版本、依赖安装方式、发布权限或发布频率。
- 离线测试不能代替 GitHub Actions 实跑；真实 CI 结果和警告需单独记录。
