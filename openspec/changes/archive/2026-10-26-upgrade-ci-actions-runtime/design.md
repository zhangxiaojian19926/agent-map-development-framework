## Context

两个工作流各有一对旧 Action 引用。官方 `actions/checkout v7.0.1` 和 `actions/setup-python v7.1.0` 的 `action.yml` 均声明 `runs.using=node24`。本仓库清单登记工作流哈希，因此文件修改后必须同步清单；本地测试无法执行 GitHub Action 本身。

## Goals / Non-Goals

**Goals:**

- 用最小的四处引用修改完成运行时升级。
- 用标准库离线测试锁定版本及不能随升级变化的工作流契约。
- 将线上验证结果与平台自身提示分开记录。

**Non-Goals:**

- 不升级 Python、runner 标签或业务依赖，不改变发布节奏。
- 不固定到提交 SHA，不引入第三方工作流解析依赖。
- 不通过消除所有平台 notice 来扩大变更范围。

## Decisions

### 1. 两个 Action 都使用 `v7` 主版本

沿用仓库已有的主版本引用方式，将 checkout 从 `v4` 改为 `v7`，setup-python 从 `v5` 改为 `v7`。当前官方稳定版本和 Node.js 24 声明已在规划时核实。相比立即固定补丁版本或提交 SHA，该方式 diff 最小并延续既有维护策略；未来若改为 SHA 固定，应另设更新机制与安全需求。

### 2. 用文本契约测试保护升级边界

新增标准库 `unittest`，读取两个 YAML 文件并断言：Action 版本、Python 3.9、验证矩阵、权限、并发、验证命令及发布关键步骤。这里只验证仓库契约，不在本地实现 YAML 解析器或模拟 GitHub Actions。

### 3. 线上验证以运行记录和 annotations 为准

推送后检查目标提交的验证工作流及两个平台任务，并读取检查注解。Node.js 20 警告必须消失；Ubuntu 镜像迁移、macOS 容量等平台提示可保留。发布工作流不主动触发，避免为验证升级而制造版本发布，其实机验收保持 `NOT_RUN`。

## Risks / Trade-offs

- [主版本后续移动引入新行为] → 保留完整 CI 矩阵与文本契约测试；若需不可变供应链，另行设计 SHA 固定和更新流程。
- [新版 Action 与 Python 3.9 或 runner 不兼容] → 以 Ubuntu/macOS 实际 CI 为门禁，失败则保留工作树并回到具体错误，不改验证命令掩盖问题。
- [误触发布产生版本] → 不手动运行发布工作流，只审查其离线契约；发布实测保持 `NOT_RUN`。
- [清单未同步导致初始化拒绝] → 修改后运行 `tools/update-manifest` 和 `tools/check-framework`，再执行完整测试。

## Migration Plan

1. 添加工作流契约测试并确认旧引用测试可作为升级前基线。
2. 仅修改两个工作流的四处 Action 主版本引用。
3. 更新框架清单，执行完整离线测试和严格规格校验。
4. 提交并推送后核对目标提交的 GitHub Actions 运行和注解。
5. 若线上失败，回退这四处引用并重新验证；不通过删除矩阵、降低权限检查或跳过测试来制造成功。
