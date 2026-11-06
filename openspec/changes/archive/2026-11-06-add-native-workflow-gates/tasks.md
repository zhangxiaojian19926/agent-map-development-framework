## 1. 任务切片

规格与设计已获认可，实施细节见 [实施计划](implementation-plan.md)。本清单是唯一任务状态源。

### 1.1 十五条流程只读路由

- [x] 1.1（S1，无前置）
  - 目标模块与文件：新增 `tools/framework_core/workflows/__init__.py`、`catalog.py`、`catalog.json`；改 `tools/framework_core/cli.py` 增加 `flow` 动作分发；新增 `tests/test_workflow_routes.py`
  - 输入输出：输入 `schema=workflow-request/v1`、`operation=route` 的请求文件（项目角色、任务类别、明确意图）；输出主流程、条件流程、不适用、待确认四类分流与逐条依据；不写任何文件
  - 接口提供方与消费方：提供 `workflows.catalog.route(request)` 与 `workflows.catalog.entries()`；消费方为 `cli.py` 的 `flow` 分发，1.2 与 1.3 复用同一目录契约
  - 覆盖：WF-01；WF-01-ROUTE、WF-01-SHELL、WF-01-UNKNOWN
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p test_workflow_routes.py`；业务工程普通开发任务中第 14、15 条为不适用，公共壳仓库内第 14 条适用而第 15 条条件适用，意图不足为待确认，且调用前后目录与文件指纹一致
  - 阻塞边：无前置，可立即开始
  - 验收条件：每条分流可追溯到教程「15 条一览」表行号，`flow-01` 至 `flow-15` 与需求 ID 不混用

### 1.2 新行为前置条件与证据核验

- [x] 1.2（S2，依赖 1.1）
  - 目标模块与文件：新增 `tools/framework_core/workflows/engine.py`、`evidence.py`；顺序扩展 `cli.py` 的 `flow` 分发；新增 `tests/test_workflow_evidence.py`
  - 输入输出：输入 `operation=check` 的请求（项目、change、动作、批准引用）；输出流程判定状态码、理由、允许的下一步与事实绑定
  - 接口提供方与消费方：提供 `workflows.engine.check(request)` 与 `workflows.evidence.verify(project, change, action)`；消费方为 `cli.py` 的 `flow` 分发、1.4 的记录层、1.5 与 1.6 的宿主适配
  - 覆盖：WF-02；WF-02-MISSING、WF-02-STALE、WF-02-ALLOW
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p test_workflow_evidence.py`；缺批准判 `NEEDS_DESIGN_APPROVAL`、批准过期判 `STALE`、有效批准判 `READY`，自填布尔与未绑定受信来源的哈希均不被接受，跨项目重放判 `STALE`
  - 阻塞边：依赖 1.1 的目录与请求契约
  - 验收条件：判定只读；受信来源位于目标工程之外且请求无法指定或替换它
  - 当前状态：代码与合成事件验证已完成（`workflows/engine.py`、`workflows/evidence.py`、11 条测试、5 项变异全部被捕获）。**原生验收暴露一个缺口**：信任锚点放在 `~/.config/framework/` 下，代理读得到路径也写得进去——被拦之后它读取门禁源码、自造 `payload.json` 并生成自己的 ssh 密钥准备自签批准（见验收记录）。也就是说"请求无权替换"成立、"代理无权替换"不成立。信任来源要按"代理写不进去"重新定义，属于规格变更，待确认后单开切片

### 1.3 四类日常开发分流

- [x] 1.3（S3，依赖 1.1）
  - 目标模块与文件：扩展 `tools/framework_core/workflows/catalog.py`、`catalog.json` 与路由测试；改 `docs/guide/daily-development.md`
  - 输入输出：输入目标路径、验收影响与已有规格引用；输出分类结论与对应路径指引
  - 接口提供方与消费方：消费 1.1 的 `catalog.route`；供 1.5 与 1.6 的宿主适配在生成判定理由时引用
  - 覆盖：WF-03；WF-03-DOC、WF-03-FIX、WF-03-SCOPE
  - 最小测试与预期结果：同一 Markdown 路径的两条输入分别判为文档检查与规格流程，已有场景修复返回复现与回归指引，知识摄入与发布类请求路由到对应流程而非日常开发四类；人工核对 `docs/guide/daily-development.md` 与路由输出逐条一致
  - 阻塞边：依赖 1.1
  - 验收条件：分类只依据实际行为与验收影响，不依据请求自述

### 1.4 私有任务记录与恢复

- [x] 1.4（S4，依赖 1.2）
  - 目标模块与文件：新增 `tools/framework_core/workflows/records.py`；`cli.py` 接入 `flow` 的 `record` 操作；新增 `tests/test_workflow_records.py`
  - 输入输出：输入 `operation=record` 的请求（项目、任务、请求标识、载荷、期望记录版本）；输出写入回执与恢复后的当前判定
  - 接口提供方与消费方：复用 `storage.project_lock` 与 `storage.apply_files`；提供 `workflows.records.commit(request)`、`workflows.records.resume(task_id)` 与 `workflows.records.report()`；消费方为 1.5 与 1.6 的跨会话接续与宿主执行轴写入
  - 覆盖：WF-04；WF-04-RETRY、WF-04-RESUME
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p test_workflow_records.py`；两个不同请求竞争同一旧版本时恰有一次更新、另一请求返回 `CONFLICT`，同 ID 同载荷重试返回原结果，失效批准在恢复时报告最新阻塞
  - 阻塞边：依赖 1.2 的判定契约
  - 验收条件：写入限于 `.framework/local-state/workflows/`；失败恢复优先读事务回执，不自动删锁或覆盖人工编辑

### 1.5 Claude Code CLI 项目级适配

- [x] 1.5（S5，依赖 1.2、1.4）
  - 目标模块与文件：新增 `tools/framework_core/hosts/__init__.py`、`base.py`、`claude_code.py` 与对应模板；`cli.py` 接入 `host` 动作；生成器登记受管配置；新增 `tests/test_host_claude_code.py`
  - 输入输出：输入 `schema=host-request/v1`、`operation=preview|apply|verify` 的请求文件；输出预览文件与归属冲突、应用回执或已认证入口核验结果
  - 接口提供方与消费方：提供 `hosts.base.Adapter` 抽象与 `hosts.claude_code` 实现；消费 1.2 判定与 1.4 记录契约，向 1.6 提供可复用接口
  - 覆盖：WF-05；WF-05-NATIVE、WF-05-UNOBSERVED
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p test_host_claude_code.py`；合成事件下非 `READY` 判定请求阻断并给出拒绝理由、`READY` 判定放行，缺原生轨迹时宿主执行轴为 `NOT_VERIFIED` 且不记为已阻断；真实验收在获授权的合成业务项目中从原生 CLI 新会话执行，记录规则发现、工具拒绝与目标文件哈希
  - 阻塞边：依赖 1.2 与 1.4
  - 验收条件：`host apply` 需要 `write` 与 `hooks` 能力；冲突时保留人工设置，回退只撤销未被人工改动的本次受管项
  - 当前状态：代码与合成事件验证已完成（`hosts/base.py`、`hosts/claude_code.py`、`templates/host/claude-code/settings.json`、9 条测试、4 项变异全部被捕获）。原生会话验收已完成：对照组正常改到文件，实验组被项目级 `PreToolUse` hook 拦下、目标文件哈希不变、会话记录里出现门禁自己的拒绝理由。证据见 [验收记录](../../../../docs/verification/add-native-workflow-gates-native/README.md)

### 1.6 Qwen Code CLI 与跨宿主故障矩阵
- [x] 1.6（S6，依赖 1.5）
  - 目标模块与文件：新增 `tools/framework_core/hosts/qwen_code.py` 与对应模板；新增 `tests/test_host_qwen_code.py`
  - 输入输出：输入同 1.5 的 `host-request/v1`；输出同 1.5，另加跨宿主比较结论
  - 接口提供方与消费方：消费 1.5 的 `hosts.base.Adapter`；公共接口如需变化须单独说明对首宿主的影响并复跑首宿主回归
  - 覆盖：WF-06；WF-06-SAME、WF-06-FAIL
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p 'test_host_*.py'`；相同项目、批准与动作下两宿主流程判定与理由一致，编辑、Shell、未知工具、超时、崩溃、禁用分别有实测结论，缺证据的记 `NOT_VERIFIED` 或 `NOT_RUN`，不把合成测试计入真实认证
  - 阻塞边：依赖 1.5
  - 验收条件：第二个宿主对相同事实给出相同内核判定，并按覆盖矩阵分别报告各宿主的覆盖状态；被验收宿主不可用或缺少调用授权时，真实会话验收显式延后，其覆盖保持 `NOT_RUN`，真实认证留给后续变更
  - 当前状态：适配器、跨宿主同事实同判定与故障矩阵已实现（`hosts/qwen_code.py`、`templates/host/qwen-code/settings.json`、7 条测试、4 项变异全部被捕获）。真实会话验收按上面的验收条件显式延后：Qwen Code CLI 本机未安装，五个故障类保持 `NOT_RUN`、交付资格记 `NOT_RUN`，不把合成测试计入真实认证。原验收条件里的"保留为未验收任务"已改为"显式延后并记 `NOT_RUN`"，规格 WF-06 的门槛未动（内核判定一致 + 覆盖分别报告，两项都已满足）

### 1.7 信任来源不可篡改

- [x] 1.7（S7，依赖 1.2）
  - 目标模块与文件：改 `tools/framework_core/workflows/evidence.py`、`engine.py`；改 `docs/guide/daily-development.md`；新增 `tests/test_workflow_trust.py`
  - 输入输出：输入同 1.2 的 `operation=check` 请求；输出流程判定状态码、理由与信任来源状态
  - 接口提供方与消费方：提供 `evidence.trust_anchor()` 与 `evidence.anchor_protected(path)`；消费方为 `engine.check` 与 `records.commit`/`resume`；生产入口只使用固定系统路径，测试通过参数传入临时信任来源
  - 覆盖：WF-08；WF-08-MUTABLE、WF-08-PROTECTED、WF-08-REDIRECT
  - 最小测试与预期结果：`python3 -B -m unittest discover -s tests -p test_workflow_trust.py`；信任来源可被当前用户改写时判 `NOT_VERIFIED` 并阻断，受保护且签名有效时按批准范围判定，请求试图指定信任来源时被忽略且判 `NOT_VERIFIED`
  - 阻塞边：依赖 1.2 的判定与证据层
  - 验收条件：信任来源路径不由请求或环境变量决定；生产路径为 `/etc/framework/workflow-trust.allowed_signers`；报告显式声明签名私钥是否可被代理读取无法机械校验
  - 当前状态：已实现（`workflows/evidence.py` 固定系统路径 + `anchor_protected` 两级可写性检查、`workflows/engine.py` 映射 `TRUST_SOURCE_MUTABLE` → `NOT_VERIFIED` 并附私钥不可机械校验声明、6 条测试、4 项变异全部被捕获）。既有测试的临时锚点已改为受保护形态（目录 0555、文件 0444）
