# 公共开发流程 — OpenSpec 与 Superpowers

本文件是跨项目可复用的详细流程。入口在 [顶层 AGENTS.md](../../AGENTS.md);技能约束见 [skill-policy](skill-policy.md),跨模块交接见 [collaboration-policy](collaboration-policy.md),知识操作见 [knowledge-policy](knowledge-policy.md)。项目身份、环境、模块和命令由项目文档提供,不在此写实例。

## 1. 按任务选择流程

| 任务 | 路径 | 最小交付 |
|---|---|---|
| 查询、解释、只读审计 | 入口 → 探索 → 证据报告 | 当前事实、推断、未验证项与来源 |
| 纯文档、链接、说明修正 | 入口 → 确认范围 → 修改 → 文档验证 → 交付 | 路由、链接、内容一致性与 diff 检查;不制造代码 RED |
| 恢复已有规格的小修复 | 入口 → 调试 → 有效 RED → 修复 → 评审验证 → 交付 | 复现与回归证据;已有 change 则同步其任务 |
| 新行为、接口、验收或跨模块设计变化 | 完整流程 §3–§12 | 经批准的规格、计划、实现及适用环境证据 |
| 仅知识摄入 | 入口 → 公共知识规则与授权 → 摄入验证 | 指定 KB 的真实页面、索引、日志与校验 |
| 设备、部署、发布 | 对应开发路径 + 项目操作约束 | 具体目标与本次授权、操作证据、恢复边界 |

“文档任务”若实际改变产品接口或验收含义,仍走完整规格流程。工作区准备、任务验证和归档只执行适用步骤,不得把不适用项记为 PASS。

## 2. OpenSpec 与 Superpowers 分工

- OpenSpec 是当前变更的需求、设计、验收场景和宏观任务记录;任务完成状态以它为准。
- Superpowers 负责设计讨论、可执行计划、测试驱动实现、调试和评审。计划细化 OpenSpec 任务,不另建竞争的需求或完成状态。
- 每个计划步骤关联 Requirement/Scenario 与 OpenSpec task ID;模块责任、接口依赖和集成顺序遵循 公共及项目模块协作约定。
- OpenSpec schema 已有 design 产物时,将讨论结果写入该产物。额外设计或计划文件只通过链接关联,避免复制两份规格。
- 技能执行顺序不等于固定文件名。产物路径、schema 和当前可执行步骤由所选 OpenSpec 根的 CLI 返回结果确定。

## 3. DISCOVERY — 理解与设计

**进入**:目标、问题或架构变化需要澄清。
**技能**:已有规格上下文用 `openspec-explore`;新设计用 `superpowers:brainstorming`;排障先用 `superpowers:systematic-debugging`。
**步骤**:
1. 完成入口路由、KB 查询,检查目标模块的 Git 根、HEAD 和已有修改。
2. 已存在 CodeGraph 时先查图定位再核对源码;没有索引则用 rg,不自动初始化。
3. 明确可观察目标、范围与非目标、兼容性、受影响模块、验证环境、未确认问题。
4. 给出设计与取舍,确认相关授权;只读探索不得变成生产实现。
**退出**:设计方向和任务边界明确。需求歧义只阻塞依赖该决定的工作。

## 4. SPEC — 建立规格

**进入**:设计已收敛,任务需要规格变更。
**技能**:`openspec-propose`;修改既有 change 用 `openspec-update-change`。
**步骤**:
1. 核实实际规划根/store 与 change,不得把向上找到的其他项目根当成本项目。根缺失时说明缺口;仅在授权范围内初始化。
2. 按真实 schema 的依赖顺序生成产物。使用 CLI 返回的 instructions 和路径,遵循已有项目规则。
3. 为 Requirement/Scenario 设置稳定 ID。Scenario 写明前置条件、输入/触发、可观察结果、超时、验证环境/证据和异常分类。
4. 按所用 CLI 的支持方式校验 change;结构有效与用户认可分别记录。
**退出**:规格已校验,用户批准覆盖本次需求与验收;不能用代码改动替代规格更新。

## 5. PLAN — 从规格到步骤

**进入**:规格已批准。
**技能**:`superpowers:writing-plans`。
**步骤**:
1. 读取规格、模块入口与约束,将每个宏观 task 拆成可执行步骤。
2. 每步列目标模块/文件、输入输出、关联 Req/Scenario、最小测试与预期结果。
3. 跨模块任务显式列依赖顺序、接口责任、可并行边界、集成验收和恢复方式。
4. 计划按技能约定存放,在 change 内引用;检查场景覆盖和遗漏。
**退出**:计划覆盖所有适用场景并获批准;用户已批准同一具体计划时直接继续。

## 6. WORKSPACE — 准备执行

**进入**:计划可执行。
**技能**:需隔离时用 `superpowers:using-git-worktrees`;顺序执行用 `superpowers:executing-plans`。仅在获得委派授权时用 `subagent-driven-development` 或 `dispatching-parallel-agents`。
**步骤**:
1. 逐仓库确认基线与已有修改;保护用户内容,不以外层 Git 状态替代子仓库状态。
2. 确定任务实际目录、环境、测试入口和工作区;需要隔离时创建并核对正确仓库的 worktree。
3. 同一文件只设一个写入责任方,跨模块共享规格统一维护。
**退出**:工作区和最小基线检查可用;环境故障记录为 INFRA_ERROR,不是 RED。

## 7. APPLY — 装载上下文

**技能**:`openspec-apply-change` 负责上下文和宏观进度,选定的 Superpowers 执行技能负责逐项落实。
从已确认的规划根运行:
```bash
openspec status --change <change-id> --json
openspec instructions apply --change <change-id> --json
```
选择 store 时对支持的命令保持相同 `--store <id>`;不用未核实的参数。
每次开始或恢复实现:
1. 读取 schemaName、规划根、changeRoot、状态、任务进度和全部 contextFiles。
2. 将需求、场景、task 与批准计划逐项对应;不假定固定 proposal/design/tasks 文件名。
3. blocked、缺产物、范围不符或缺少必要审批时停止依赖它的实现;不能把 all_done 当作集成/发布证明。
4. 选择一个当前 task,陈述范围、最小验证和所需环境。

## 8. IMPLEMENT — 实现与任务验证

**技能**:`superpowers:test-driven-development`。
1. RED:先运行能到达目标路径的失败测试,证明目标行为缺失。
2. GREEN:最小实现使该场景通过。
3. REFACTOR:只做当前任务必要整理,测试保持通过。
4. REGRESSION:运行受影响范围的测试;需要时用已有 CodeGraph 辅助定位。
5. TASK_VERIFIED:检查实际结果、局限和证据,再更新 OpenSpec 对应任务。部分完成不得勾选。
纯文档使用 §1 的文档验证路径;无可用自动化时明确人工验证方式与证据缺口。不得把编译器缺失、设备不可达、网络或 runner 故障当作有效 RED。

## 9. 异常回流

| 触发 | 技能/动作 | 恢复条件 |
|---|---|---|
| 测试异常或实现失败 | systematic-debugging:复现 → 根因假设 → 最小实验 → 修复 | 有效失败原因与回归证据 |
| 需求、接口、场景变化 | openspec-update-change → 校验 → 审批 → 更新计划 | 规格和计划重新一致 |
| 实施顺序或步骤漂移 | writing-plans 更新受影响部分 | 不改变已批准需求,重大变化获确认 |
| 环境/设备不可用 | 记录 INFRA_ERROR,查项目约束 | 环境恢复,重跑受影响验证 |
| 实际行为不符规格 | 记录 SPEC_MISMATCH | 修复实现;仅需求确需改变时更新规格,不能为通过测试降低标准 |

## 10. REVIEW — 评审

**技能**:`superpowers:requesting-code-review`、`superpowers:receiving-code-review`。
提供规格、相关计划、实际 diff 和验证证据;先检查需求符合性,再检查实现质量、回归和跨模块接口。
反馈须核实后处理,重要问题闭合并重跑受影响检查。独立评审依赖可用且获授权的评审机制;只有自查时明确标注自查,不得伪称独立评审。

## 11. VERIFY — 整体完成验证

**技能**:`superpowers:verification-before-completion`。
1. 使用最终工作树/产物的新鲜证据。已提交时记录 commit;未提交则记录 HEAD 加工作树差异/产物标识。
2. 按批准场景执行 Host、Cross-build、Target 或 Integration 中适用的验证;不适用项注明原因。
3. 跨模块单测通过不代表集成通过,核实项目协作文档要求的版本组合和端到端结果。
4. 每个 Req/Scenario 能追踪到 task、模块、Test、环境、结果与证据;缺项如实报告。
**退出**:适用场景通过、重要评审问题解决。证据矩阵见下文;设备、部署等门禁见项目约束。

## 12. INTEGRATE / ARCHIVE / KNOWLEDGE — 交付与收尾

1. 用 `superpowers:finishing-a-development-branch` 展示验证结果并落实用户的合并、PR、保留等选择。提交、推送、部署和设备授权按项目约束处理。
2. 有 OpenSpec change 时检查任务证据与产物状态,用 `openspec-sync-specs` 同步需要的 delta specs,核对合并结果,再用 `openspec-archive-change` 归档。
3. 同步与归档顺序执行,不在同步未结束时移动 change。使用实际返回的 changeRoot/planningHome,不要拼接猜测路径。
4. 未完成任务或缺证据不能以“全部完成”归档;用户若明确选择保留未完成状态,如实报告。
5. 每次问题解决后按 [知识回流](knowledge-policy.md) 主动询问是否摄入;已有本次明确授权则执行。无需等发布归档才询问。
6. 最终分别报告实现、适用验证、集成/归档与知识摄入状态。知识回流待确认不阻塞已完成修复的交付。

完整行为变更路线:
```text
DISCOVERY → SPEC_VALIDATED → SPEC_APPROVED → PLAN_APPROVED
→ WORKSPACE_READY → APPLY_CONTEXT_LOADED
→ (TASK_SELECTED → RED → GREEN → REFACTOR → TASK_VERIFIED)*
→ REVIEWED → CHANGE_VERIFIED → INTEGRATED_OR_RETAINED
→ SPECS_SYNCED → ARCHIVED
```
知识回流在问题闭合时触发,与发布归档分开记录。

## 13. 通用验证证据

每个场景声明适用环境:Host / Cross-build / Target / Integration。未运行写 NOT_RUN,环境故障写 INFRA_ERROR,不适用写 N/A 并说明理由。仅实际执行并符合断言才写 PASS。文档任务校验实际引用、内容归属、规则一致性和 diff,不声称构建或运行通过。

| Req/Scenario | Task | 模块/仓库 | 版本或工作树标识 | Test | 环境 | 证据 | 结果 |
|---|---|---|---|---|---|---|---|
| <id> | <id> | <module-id> | <commit 或 HEAD+diff 标识> | <test> | <env> | <path/hash> | <result> |

追踪链:Scenario → task/module → TestRequest/Test → TestResult → EvidencePacket → 工作树/commit/artifact。
跨模块验证必须记录参与仓库的版本组合、未提交差异和接口/配置版本(不含密钥)。未提交工作可以验证,但发布与归档须绑定最终集成版本。旧报告、索引存在和脚本退出码不能单独证明业务完成。
