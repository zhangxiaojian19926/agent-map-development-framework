## Purpose

在明确自动化范围内管理真实代码索引及新鲜度，尊重已有工具、Git 钩子和工作树边界，通过可观察的更新状态提供可靠导航，避免重复监听、全局修改和静默失效。

## ADDED Requirements

### Requirement: CG-01 初始化与真实索引检查

系统 SHALL 对获准且存在支持源码的索引根执行 init 或 sync，随后检查状态与代表性查询；索引目录存在、退出码零或空结果不足以证明覆盖。

#### Scenario: CG-01-INDEX

- 前置条件：同仓共享索引和独立子仓库均有源码
- **WHEN** 执行接入
- **THEN** 每个 index-id 初始化一次，记录支持/排除范围、版本和查询证据；失败逐根报告
- 超时：每索引默认 300 秒，可显式调整
- 环境与证据：Host：受控 CLI；真实工具：合成源码查询
- 异常分类：INDEX_FAILED / TIMEOUT

#### Scenario: CG-01-TOOL

- 前置条件：工具缺失或参数与适配版本不符
- **WHEN** 预检
- **THEN** 显示缺失能力和获准安装选项；不自动使用全局 install --yes，不启动隐式下载
- 超时：15 秒
- 环境与证据：Host：缺失工具与不兼容 CLI fixture
- 异常分类：DEPENDENCY_MISSING / UNSUPPORTED_VERSION

### Requirement: CG-02 钩子安全共存

系统 MUST 解析 core.hooksPath、Git 公共目录和工作树范围；仅在可验证的接入方式下安装项目钩子，未知既有钩子保留并报冲突。

#### Scenario: CG-02-HOOK

- 前置条件：仓库已有任意脚本钩子或共享 worktree hook
- **WHEN** 安装更新机制
- **THEN** 不覆盖或盲目追加；未获共享范围授权则保留；报告 HOOK_CONFLICT，入口检查仍可用
- 超时：30 秒
- 环境与证据：Host：Git fixture、内容指纹、作用域审计
- 异常分类：HOOK_CONFLICT

#### Scenario: CG-02-EVENT

- 前置条件：已安装受管钩子且连续发生 checkout/merge/commit
- **WHEN** 触发事件
- **THEN** 合并脏标记，正确绑定工作树，不调用 LLM、不提交文档、不阻断 Git；失败可在 doctor 观察
- 超时：钩子处理 2 秒，索引异步单独计时
- 环境与证据：Host：执行计数、延迟、状态
- 异常分类：SYNC_PENDING / INFRA_ERROR

### Requirement: CG-03 新鲜度与恢复

系统 SHALL 复用已验证的 CodeGraph 监听能力，任务入口和完成检查兜底；不得默认新建全局 watcher，未提交变化也必须触发相关复核。

#### Scenario: CG-03-STALE

- 前置条件：Agent 不在线期间源码变化或普通 clone 新模块
- **WHEN** 下次 Agent 入口或显式同步
- **THEN** 在批准范围内发现变化、刷新相关索引并安排地图复核；不承诺离线即时执行
- 超时：发现 30 秒，后续步骤分别限时
- 环境与证据：Host：文件指纹、队列、回归结果
- 异常分类：STALE / PARTIAL
