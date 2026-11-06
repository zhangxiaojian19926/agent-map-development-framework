# 原生宿主工作流门禁首批实施计划

本文件是待批准计划。[规格](specs/native-workflow-gates/spec.md) 定义验收行为，[设计](design.md) 定义总体边界，[任务](tasks.md) 保存唯一任务状态。

目标是让 Claude Code CLI 与 Qwen Code CLI 对同一项目事实得到相同流程判定，并用真实工具调用验证各自的拦截范围。公共壳原有命令继续兼容。保持现有 Python 标准库实现方式，保留各宿主原生启动和权限模型。本期交付资格为 `NOT_RUN`。

**本计划获批即视为批准 1.2 的信任来源方案。**

## 命令面

`flow` 与 `host` 是两个新动作，各自用 `--request` 读取请求文件，请求里的 `operation` 区分子操作，不占用既有位置参数 `operation`（该参数留给 `module` 的 clone/add/sync）。

| 命令 | 请求 schema | operation | 写入 | 需要能力 |
|---|---|---|---|---|
| `framework flow --request <file>` | `workflow-request/v1` | `route` | 只读 | 无 |
| `framework flow --request <file>` | `workflow-request/v1` | `check` | 只读 | 无 |
| `framework flow --request <file>` | `workflow-request/v1` | `record` | `.framework/local-state/workflows/` | `write` |
| `framework flow --request <file>` | `workflow-request/v1` | `report` | 只读 | 无 |
| `framework host --request <file>` | `host-request/v1` | `preview` | 只读 | 无 |
| `framework host --request <file>` | `host-request/v1` | `apply` | 项目级适配文件 | `write` + `hooks` |
| `framework host --request <file>` | `host-request/v1` | `verify` | 只读 | 无 |

能力要求按 `cli.py` 既有做法在 action 分支内覆盖 `build_plan` 的 `required_capabilities`，不改 `build_plan` 本身。新增 operation 不改 schema 版本号，改语义才升版本。

## 状态码

流程判定、宿主执行、交付资格三轴只用 `docs/guide/framework-model.md` 已发布词典中的状态码（分组见规格 WF-07），不新造第三套词表。判定输出只用 `READY`、`NOT_AUTHORIZED`、`NEEDS_DESIGN_APPROVAL`、`STALE`、`NOT_VERIFIED`、`BLOCKED`、`CONFLICT`、`PARTIAL`、`NOT_APPLICABLE`。

## 1.1 十五条流程的只读路由

- 写入归属：新增 `tools/framework_core/workflows/__init__.py`、`catalog.json`、`catalog.py`，在 `cli.py` 增加 `flow` 分发及请求校验，新增 `tests/test_workflow_routes.py`。
- 请求使用 `schema=workflow-request/v1`、`operation=route`，携带项目角色、任务类别和明确意图。角色与目标资料冲突时返回待确认，未知角色不得取得公共壳维护路由。现有 CLI 参数组合继续走旧路径。
- 目录中逐条登记教程现有十五条工作流的稳定 ID `flow-01` 至 `flow-15`、适用范围、已有入口和条件，与 `docs/guide/from-zero-to-one.md`「15 条一览」表行号一一对应。输出包括主流程、条件流程、不适用与待确认。默认只提供现有入口导航和条件提示。
- RED：调用新增动作，检查业务项目普通开发任务不适用第 14、15 条、公共壳仓库自身第 14 条适用而第 15 条条件适用、输入不足则待确认。GREEN 后逐文件比较输入前后的路径和哈希。验证命令为 `python3 -B -m unittest discover -s tests -p test_workflow_routes.py`。

## 1.2 新行为前置条件与证据

- 写入归属：新增 `workflows/engine.py`、`evidence.py` 和 `tests/test_workflow_evidence.py`，顺序扩展 1.1 的 CLI。
- `flow check` 重新读取真实项目、规划根及 change，校验规范化动作、项目内路径及批准范围。批准内容绑定规格和计划的当前文件指纹、项目标识、change 和作用范围。返回流程判定状态码与理由、允许的下一步和事实绑定。
- **信任来源方案**：首批用用户控制的 OpenSSH 签名批准作为可核验来源。验证器通过固定 namespace 校验原始签名负载，受信公钥来源由用户明确配置在目标工程之外，任务请求无权指定或替换它。系统只核验签名，签名由审批人控制的原生签名方式生成。没有受信来源、验证器缺失或签名不符均不满足门禁。测试使用临时密钥和显式测试信任配置。该机制只证明所验证的内容和签名者，宿主原生权限仍独立生效。与既有 `.framework/local-state/approvals.json` 互不承认：后者是既有 `new` 动作的哈希记录，门禁不因其中存在哈希就放行。
- RED：覆盖批准缺失、伪造字段、修改计划、跨项目重放、越界路径与有效签名对照。GREEN 后验证前置缺失时已授权草案编辑仍可行。运行 `python3 -B -m unittest discover -s tests -p test_workflow_evidence.py`。

## 1.3 四类日常开发分流

- 消费 1.1 的目录和路由契约。顺序扩展 `catalog.py`、`catalog.json`、路由测试和日常开发指南。读取目标目录适用的局部规则。
- 用用户给定目标、验收影响和已有规格引用分类。仅改链接走文档检查，改变验收回 SPEC，已有场景修复返回复现及回归指引。意图不明时继续只读探索。知识摄入与设备发布类请求交回 1.1 的目录路由，不套用这四类。
- RED：用相同 Markdown 路径的两条输入验证语义差异，再加入已有场景修复与只读对照。用 1.1 的命令验证，人工核对指南与路由输出一致。

## 1.4 任务接续与并发

- 消费 1.2 判定契约。新增 `workflows/records.py` 和 `tests/test_workflow_records.py`，接入 `flow` 的 `record` 与 `report` 操作。写入限于 `.framework/local-state/workflows/`，复用现有路径检查、事务和项目锁。
- 锁内先检查请求 ID 与载荷绑定，再比较期望记录版本。同一 ID 同一载荷重试返回原结果，载荷变化或过期版本拒绝并报 `CONFLICT`。恢复只读并以当前事实重新判定。
- 三轴结果落在 `.framework/local-state/workflows/report.json`，由 `flow` 的 `report` 操作只读查询；1.5 与 1.6 追加宿主执行轴结论。
- RED：用两个不同请求竞争同一旧版本，再重试成功请求，验证恰有一次更新。另测拒绝后文件一致、断点恢复和失效批准。运行 `python3 -B -m unittest discover -s tests -p test_workflow_records.py`。
- 失败恢复优先读取现有事务回执，不自动删除锁或覆盖人工编辑。

## 1.5 Claude Code CLI 项目级适配

- 消费 1.2 判定和 1.4 接续契约。新增 `hosts/base.py`、`hosts/claude_code.py`、对应模板和测试，接入 `host` 动作与生成器。适配公共接口归本切片管理。
- 先核对待验收版本的项目规则、信任配置和 hook 协议。`preview` 输出文件、归属与冲突，`apply` 按当次授权写入（需 `write` 与 `hooks`），`verify` 只读核验已认证入口。事件桥只提取项目、动作、目标和任务引用，同步调用共享判定，再编码为原生结果。
- 判定不为 `READY` 时请求宿主阻断该次工具调用并给出拒绝理由，不得默认放行；宿主原生权限仍然独立生效。
- 用合成事件验证拒绝与放行。真实验收在获授权的合成业务项目中，从原生 CLI 新会话启动，分别记录规则发现、工具拒绝、目标文件哈希和合法修改结果。缺少原生轨迹时只报告合成协议验证，宿主执行轴记 `NOT_VERIFIED`，不记为已阻断。
- 运行 `python3 -B -m unittest discover -s tests -p test_host_claude_code.py`。冲突时保留人工设置，回退仅撤销未被人工改动的本次受管项。

## 1.6 Qwen Code CLI 与跨宿主故障矩阵

- 消费 1.5 的适配接口。新增 `hosts/qwen_code.py`、对应模板及 `tests/test_host_qwen_code.py`。公共适配接口如需变化，单独说明对首宿主的影响并复跑首宿主回归。
- 用同一项目、批准和动作比较两个宿主的判定。用真实原生会话分别核对编辑、Shell、未知工具、超时、崩溃、禁用及跨会话恢复。保存脱敏证据和前后文件哈希，分别报告已阻断、已放行、未覆盖或未知；超时与崩溃记 `INFRA_ERROR`，禁用记 `NOT_RUN`，未命中已认证入口记 `NOT_VERIFIED`。
- 运行 `python3 -B -m unittest discover -s tests -p 'test_host_*.py'`。真实宿主不可用或缺少调用授权时保留对应未验收任务，不把合成测试计入真实认证，交付资格记 `NOT_RUN`。

## 交付验证

- 各切片获得有效 RED 后实施最小 GREEN，再运行相关回归。最终变更按仓库既定顺序执行 `python3 tools/pre-commit-check`（`update-manifest` → `check-framework` → 全量单元测试 → diff 检查），并单独执行 OpenSpec 严格校验。
- 新增文件必须登记进 `framework-manifest.json`；清单在隔离实施工作区更新，排除未纳入本变更的本地资料（例如 `docs/plans/dsh-plugin/`）。实际提交、集成和归档按项目流程分别处理。
- 宿主证据记录产品、版本、形态、操作系统、配置指纹、被测操作和副作用。首批验收限于已有代码合成项目的原生接入及新行为门禁。三类初始化完整接入与受保护 CI 保留给后续变更。
