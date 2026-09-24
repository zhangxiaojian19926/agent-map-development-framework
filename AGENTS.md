# AGENTS.md — 公共开发流程入口

本文件规定开发顺序、每步技能及交接门禁;详细公共规则在 docs/framework,当前项目事实在 docs/project,模块内部职责和命令在各模块 AGENTS.md。规则文档不是工具实现或执行授权。

## 0. 先读谁

首次接入先读 [onboarding](docs/onboarding.md)。本分发仓库只含模板；未建立真实 docs/project 时不要把模板当事实。无 KB 时报告 NOT_CONFIGURED 后继续允许的只读研究，不自动建库。以下模板链接在接入工程时改为实例 docs/project 路径。

1. 读 [项目概览](templates/project/overview.md)、[资源登记](templates/project/resources.md) 和 [项目约束](templates/project/constraints.md),确定项目身份、目标模块和任务边界。
2. 按 [公共知识规则](docs/framework/knowledge-policy.md) 和资源登记的实际命令做 KB-first。任务开始及 SPEC/APPLY/VERIFY 阶段入口查询;阶段内复用,范围、来源或假设变化时刷新。
3. 多模块任务读 [公共协作规则](docs/framework/collaboration-policy.md),再读 [本项目架构](templates/project/architecture.md) 与 [本项目协作](templates/project/collaboration.md)。
4. 读目标模块及实际修改目录适用的 AGENTS.md;子级只增加局部差异,不放宽上层授权和证据要求。缺失时报告并遵守上层。
5. 按下表选流程,调用前完整读取实际 SKILL.md,遵守 [技能约束](docs/framework/skill-policy.md)。名称是调用标识,不是 shell 命令。

公共规则只描述“怎么做”;项目文档说明“本项目由谁做、在哪里做”;模块入口说明“本模块内部怎么做”。不要在三层复制同一份流程。

## 1. 按任务选路径

| 任务 | 路径与交付 |
|---|---|
| 查询、解释、审计 | 路由 → 只读探索 → 事实、推断、未验证项与来源;不修改文件 |
| 纯文档、链接修正 | 路由 → 确认范围 → 精确修改 → 链接/内容/diff 校验;不制造代码 RED |
| 恢复既有规格的修复 | 路由 → systematic-debugging → 有效 RED → 最小修复 → 评审/回归;关联已有 change |
| 新行为、接口、验收、跨模块设计 | 下表完整流程,审批只覆盖已确认的范围 |
| 知识摄入 | 公共知识路由 → 明确内容/全部目标授权 → 按目标 schema 摄入及验证 |
| 设备、部署、发布 | 对应流程 + 本项目操作约束 + 本次具体目标授权 |

文档若改变产品接口或验收含义仍走规格流程。不适用步骤记 N/A 并解释,不能记 PASS。

## 2. OpenSpec 与 Superpowers 如何配合

OpenSpec 管需求、设计、Scenario 和宏观任务状态;Superpowers 管设计讨论、实施计划、TDD、调试、评审与完成验证。每个计划步骤关联 Req/Scenario/task ID,不维护竞争的规格或完成状态。已有设计产物优先复用,其他计划用链接关联。真实 schema、产物路径与执行状态以所选规划根的 CLI 结果为准。

以下是阶段路由;具体进入条件、步骤、产物、异常回流和退出门禁见 [完整开发流程](docs/framework/development-workflow.md)。

| 顺序 | 使用技能 | 必须交接的结果 |
|---|---|---|
| 1. DISCOVERY | openspec-explore; superpowers:brainstorming; 故障先 systematic-debugging | 目标、范围、模块、兼容性、验证环境、方案与待确认项 |
| 2. SPEC | openspec-propose / openspec-update-change | 稳定 Req/Scenario、真实 schema 校验、用户认可 |
| 3. PLAN | superpowers:writing-plans | 关联规格的微步骤、文件/模块、测试、依赖、集成与恢复计划;计划获批 |
| 4. WORKSPACE | 需隔离时 using-git-worktrees; 顺序 executing-plans | 各仓库基线、正确工作区、最小环境检查;委派需授权 |
| 5. APPLY | openspec-apply-change + 已选执行技能 | 重新读取 status/instructions/all contextFiles,核对计划,选定 task |
| 6. IMPLEMENT | superpowers:test-driven-development | 有效 RED → GREEN → REFACTOR → 相关回归 → TASK_VERIFIED |
| 7. REVIEW | requesting-code-review / receiving-code-review | 规格符合性、质量和接口评审;重要问题处理,自查不得冒充独立评审 |
| 8. VERIFY | verification-before-completion | 最终工作树/产物的新鲜证据;适用局部与集成场景分别验证 |
| 9. INTEGRATE | finishing-a-development-branch | 用户选择合并/PR/保留等;不擅自提交、推送、部署或操作设备 |
| 10. ARCHIVE | openspec-sync-specs → openspec-archive-change | 同步核对后归档,未完成/无证据不得宣称完整归档 |
| 11. KNOWLEDGE | 已选知识库技能,按公共知识规则 | 每次问题解决即询问是否摄入,无需等发布;获明确授权才写入 |

表中未写前缀的 Superpowers 技能同属 superpowers。未安装、不可调用或参数不支持时报告,不伪造执行。
技能选择与缺失处理、权限冲突见 [技能约束](docs/framework/skill-policy.md)。当前用户指令和已有明确授权优先,阶段切换不重复索取相同授权。

## 3. 异常与交付

- 实现失败:systematic-debugging 复现和验证根因,再回当前任务。
- 需求/场景改变:openspec-update-change → 校验/确认 → writing-plans 更新;不能为通过测试降低规格。
- 环境故障:INFRA_ERROR,不是 RED;缺少关键决定仅停止依赖它的工作。
- 新模块:按公共协作规则先只读发现,再按授权登记;发现不等于获准执行、建库或安装。
- 每次交付分别说明改动、适用验证、未验证项、集成/归档与知识摄入状态;多模块部分成功分别报告。
- 每次解决问题后主动询问是否摄入对应模块 KB;已有本次内容和目标的明确授权则执行。拒绝、暂缓或未回复不写,也不阻塞已完成工作的交付。
