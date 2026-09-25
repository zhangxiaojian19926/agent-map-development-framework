# 发布验收与证据边界

## Agent 主导初始化：当前验收状态（未发布）

2026-09-26，本地未提交实现的 94 项离线测试在 macOS 与隔离 Linux Python 3.9 容器分别通过。分发清单检查通过（174 个文件、22 个技能），OpenSpec `agent-led-project-intake` 严格校验通过。这些是本地证据，不是远端 CI 或发布结果。后续修改必须重跑受影响验证。

已覆盖：任意数量的名称/URL 输入、同源不同名、来源版本解析、逐模块获取及部分失败恢复、无 URL 的新工程、当前会话地图接收、人工入口保护、散落源码识别，以及重复初始化不覆盖后来登记的模块。追加评审回归验证：已配置目标及非法项目名在下载前拒绝，准备后出现候选模块时保留 PARTIAL 与登记提示。原有 CLI 回归保留。

| 验收层 | 当前证据及边界 |
|---|---|
| 真实 Codex 初始化 | 已有多仓与全新需求两条路线有 PASS 记录；该记录早于最后两项恢复/发现修复，不代表最终工作树的重新实跑 |
| 技能决策演练 | 旧技能对照与新版实际 PREPARED 演练已运行；Codex 子 Agent 演练不是非 Codex 兼容证明 |
| 非 Codex 真实初始化 | NOT_RUN：Claude 默认环境有认证，但隔离用户设置后认证不可用；未读取密钥或放开全局插件/hooks来绕过 |
| 跨宿主中断恢复 | NOT_RUN；离线状态恢复测试不替代真实跨宿主执行 |
| 私有 Git 认证 | 显式 SSH-agent 接口有离线回归；真实私有源尚未验收，HTTPS credential helper 不自动加载 |
| 业务运行 | NOT_RUN；基础 PREPARED 或地图 READY 不代表需求已开发或业务可运行 |
| 独立评审、发布与归档 | 以活跃 change 的任务记录为准；未取得完整评审结论或最终版本证据时不得勾选整个验收完成 |

尚需收口的设计核对包括：框架版本指纹与启动计划绑定、人工受管区块冲突后的项目侧交接、真实验收探针对模块提交及内容的独立核对。不得用上述测试数量代替这些语义检查。验证日志及真实启动输入保留在独立验证目录，不进入公共分发包。

## 工作流覆盖矩阵

| 环节 | 规则/技能 | 验收要求 |
|---|---|---|
| 首次接入 | onboarding + AGENTS | 未配置项目/KB 时不伪造事实、不自动写 |
| 只读/文档任务 | 开发流程 | 无生产改动，文档按链接和内容验证 |
| 设计/规格 | explore + brainstorming + propose/update | 目标、场景、审批和真实规划根 |
| 计划 | writing-plans | 步骤关联 Req/Scenario/task/module |
| 工作区 | worktrees + executing-plans | Git 边界、用户修改和可用环境 |
| 实现 | apply + TDD | 有效 RED、GREEN、回归、证据再勾任务 |
| 多模块 | collaboration + handoff | 单仓/多仓、版本组合和共享场景 |
| 委派 | dispatching / subagent-driven | 可用且获授权，单文件责任明确 |
| 调试 | systematic-debugging | 根因实验，基础设施不当 RED |
| 评审 | requesting/receiving | 规格符合性及重要问题处理 |
| 验证 | verification-before-completion | 最终工作树/产物绑定 |
| 集成 | finishing | 已授权的保留/提交/合并/推送选择 |
| 同步/归档 | sync + archive | 顺序同步并核对，未完成不伪称完成 |
| 知识 | llm-wiki + knowledge-policy | 模块路由、确认、raw/页面/索引/日志和证据 |
| 设备/部署 | 项目专用能力 + 公共权限约束 | 未授权不执行；未测记 NOT_RUN |
| 模块接入 | collaboration + module template | 先只读确认，不能把目录发现当启用 |

## 自动检查

从分发仓库根运行 python3 tools/check-framework 和 python3 -m unittest discover -s tests -v。
检查文件白名单/指纹、技能入口、实际本地链接、脚本语法及合成 KB 行为。
测试覆盖注册路径、显式 alias、工作区边界、中文/空格、三库查询、写入确认、非空目录、批量部分失败、严格结构检查、只读图谱和删除计划。
新增接入回归覆盖无写预览、审批指纹、人工文件保护、中断恢复、锁、模块移动/missing、真实本地 Git clone、hooks 共存、伪成功拒绝、地图引用、Agent 摘要完整性和只读 doctor。真实验证入口为 [bootstrap](bootstrap.md) 中的 tools/verify-live，默认测试不会调用模型或联网。

源码索引、Agent 分析、业务黑盒验证分别保存，不能相互代替。真实模型输出即使声称成功，也必须通过框架外部的固定黑盒探针；Agent 自己写的测试通过不是唯一验收依据。

## 人工及 Agent 验收

必须另核对：规格与计划语义覆盖、模块分工、技能应用决策、来源真实性、知识主题关联和隐私。
自动脚本不证明 Agent 在所有压力场景均合规，也不证明 OpenSpec CLI、模型宿主、硬件或业务集成已运行。

本版将结构检查与真实脚本回归作为发布门禁，并进行受控 Agent 决策演练。未执行的真实宿主、设备、provider 和发布部署不记 PASS。
语义摄入由获得本次授权的 Agent 完成，脚本 PREPARED/PLAN_ONLY 不作为摄入成功凭据。
