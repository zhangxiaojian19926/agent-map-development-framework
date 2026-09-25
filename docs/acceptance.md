# 发布验收与证据边界

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
