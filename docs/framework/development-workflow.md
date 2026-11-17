# 公共开发流程 — OpenSpec 与 Superpowers

本文件是跨项目可复用的详细流程。入口在 [顶层 AGENTS.md](../../AGENTS.md);技能约束见 [skill-policy](skill-policy.md),跨模块交接见 [collaboration-policy](collaboration-policy.md),知识操作见 [knowledge-policy](knowledge-policy.md)。项目身份、环境、模块和命令由项目文档提供,不在此写实例。

## 1. 按任务选择流程

初始化工程只按 [通用入口](../../BOOTSTRAP.md)。有白名单源码才建关系地图；无源码时留下设计草案。新需求无需仓库、分支或用户计算 hash。设计草案待确认时保持 NEEDS_DESIGN_APPROVAL，不称全完成。用户说“继续”时读取当前 handoff 和真实 OpenSpec 状态、instructions、contextFiles，复用同范围已有批准，只询问缺失决定。实现仍需设计、规格及计划门禁。用户不负责执行内部命令。用户明确要求逆向时，只在本流程之前增加一次静态观察，工具版本见 [逆向工具](reverse-tools.md)。观察结束后仍从设计草案进入本流程。没有这项要求时，不安装逆向工具，阶段和完成条件不变。`package` 不是本流程的必经阶段。

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

- OpenSpec 独占可校验的规格账本：proposal、delta spec、design、主规格，以及 propose、update、sync、archive。`tasks.md` 的切片正文只由 `to-tickets` 写入。勾选只发生在该切片 `TASK_VERIFIED` 之后，且文件仍在活动 change 目录。
- Superpowers 与 matt-pocock 把账本谈清楚、切成切片、用测试改代码并交出证据。同一段源码只有一个实现器。没有委派授权，或宿主不提供子代理能力时，主 Agent 用 `tdd`，并用 `code-review` 做评审判断。两者都有时，被委派者仍用 `tdd`。
- 每个计划步骤关联 Requirement/Scenario 与 OpenSpec task ID;模块责任、接口依赖和集成顺序遵循 公共及项目模块协作约定。
- OpenSpec schema 已有 design 产物时,将讨论结果写入该产物。额外设计或计划文件只通过链接关联,避免复制两份规格。
- 技能执行顺序不等于固定文件名。产物路径、schema 和当前可执行步骤由所选 OpenSpec 根的 CLI 返回结果确定。

## 3. DISCOVERY — 理解与设计

**进入**:目标、问题或架构变化需要澄清。
**技能**:排障先用 `matt-pocock:diagnosing-bugs`，诊断停在红信号、最小复现和根因，Phase 5 不应用修复，回归测试和修复只由 `tdd` 写；澄清意图只用 `superpowers:brainstorming`；人点名仍可用 `openspec-explore`，它不是下一项，也不代替 brainstorming。设计模块接口、决定 seam 位置或判断可测试性时参考 `matt-pocock:codebase-design`。
**步骤**:
1. 完成入口路由、KB 查询,检查目标模块的 Git 根、HEAD 和已有修改。
2. 已存在 CodeGraph 时先查图定位再核对源码;没有索引默认 rg。仅当本次明确授权 index 时由适配器 init 或 sync。CLI 不在 PATH 上时，另有 index-install 才把锁定版本装进项目内 `.framework/tools/codegraph`；不全局安装，不调用 `codegraph install`。新文件先更新受管放行列表再 sync。索引新鲜不等于关系地图已更新。模块内部修改不发布地图。doctor 显示还没有地图或模块结构已失效，且本次可以改代码时，用 `map` 发布一轮。本次改动了模块职责或模块间关系时同样发布一次，不要等用户再次要求。下载配置不能自行授权。
3. 明确可观察目标、范围与非目标、兼容性、受影响模块、验证环境、未确认问题。若干互相独立的开放决策可一次问完整个前沿,每问附推荐答案,依赖未决答案的问题留到下一轮;需要环境事实时自己查,不把查证转给用户。
4. 给出设计与取舍,确认相关授权;只读探索不得变成生产实现。
**退出**:设计方向和任务边界明确。需求歧义只阻塞依赖该决定的工作。

## 4. SPEC — 建立规格

**进入**:设计已收敛,任务需要规格变更。
**技能**:`openspec-propose`;修改既有 change 用 `openspec-update-change`。
**步骤**:
1. 核实实际规划根/store 与 change,不得把向上找到的其他项目根当成本项目。根缺失时说明缺口;仅在授权范围内初始化。
2. 按真实 schema 的依赖顺序生成 proposal、delta spec、design。不生成实现步骤，不创建 `tasks.md`。使用 CLI 返回的 instructions 和路径,遵循已有项目规则。
3. 为 Requirement/Scenario 设置稳定 ID。Scenario 写明前置条件、输入/触发、可观察结果、超时、验证环境/证据和异常分类。
4. 按所用 CLI 的支持方式校验 change;结构有效与用户认可分别记录。
**退出**:规格已校验,用户批准覆盖本次需求与验收;不能用代码改动替代规格更新。

## 5. PLAN — 从规格到步骤

**进入**:规格已批准。
**技能**:`matt-pocock:to-tickets`。
**步骤**:
1. 读取规格、模块入口与约束,把工作切成垂直切片:每个切片切穿各层,单独可演示;宽重构按 expand–contract 展开,不塞进切片。
2. 切片写入当前 change 的 `tasks.md`,逐条声明交付的端到端行为、覆盖的 Req/Scenario、验收条件与阻塞边;阻塞边构成任务图,无阻塞者的切片可立即开始。任务状态只以 `tasks.md` 为准。`to-tickets` 只写入切片正文。`plan-format.md` 的 Execution handoff 不是下一项。`- [ ]` 改成 `- [x]` 仍等该切片 `TASK_VERIFIED`。
3. 每条切片列目标模块/文件、输入输出、接口提供方与消费方、最小测试与预期结果。
4. 跨模块切片显式列依赖顺序、接口责任、可并行边界、集成验收和恢复方式;同一文件只设一个写入责任方。
5. 实施细节计划按项目约定存放,在 change 内引用;检查场景覆盖、占位内容与命名一致性,并确认阻塞边无环、起始切片可独立开始。
**退出**:切片覆盖所有适用场景、阻塞边无环且起始切片可独立开始,并获用户批准;用户已批准同一具体计划时直接继续。

## 6. WORKSPACE — 准备执行

**进入**:计划可执行。
**技能**:需要隔离时用 `superpowers:using-git-worktrees`。无委派授权时不读 `executing-plans`，按已批准切片进入实现。委派只在用户已授权且宿主提供子代理能力时发生，才用 `subagent-driven-development`（并读其同目录 `framework-rules.md`）或 `dispatching-parallel-agents`，二者择一，被委派者仍用 `tdd`。人点名仍可用 `executing-plans`，它不成为实现器，也不按产品名单改走委派。
**步骤**:
1. 逐仓库确认基线与已有修改;保护用户内容,不以外层 Git 状态替代子仓库状态。
2. 确定任务实际目录、环境、测试入口和工作区;需要隔离时创建并核对正确仓库的 worktree。
3. 同一文件只设一个写入责任方,跨模块共享规格统一维护。
**退出**:工作区和最小基线检查可用;环境故障记录为 INFRA_ERROR,不是 RED。

## 7. APPLY — 装载上下文

**技能**:装载是路由上的三步，不把 `openspec-apply-change` 当必经实现器。人点名仍可用 `openspec-apply-change`，它只装载上下文，不改业务源码，不在 `TASK_VERIFIED` 之前勾选。
从已确认的规划根运行:
```bash
openspec status --change <change-id> --json
openspec instructions apply --change <change-id> --json
```
选择 store 时对支持的命令保持相同 `--store <id>`;不用未核实的参数。
每次开始或恢复实现前先装载，不在这一步改业务源码:
1. 读取 schemaName、规划根、changeRoot、状态、任务进度和全部 contextFiles。
2. 将需求、场景、task 与批准计划逐项对应;不假定固定 proposal/design/tasks 文件名。
3. blocked、缺产物、范围不符或缺少必要审批时停止依赖它的实现;不能把 all_done 当作集成/发布证明。
4. 装载完成后进入 `tdd`。不在 `TASK_VERIFIED` 之前勾选。

## 8. IMPLEMENT — 实现与任务验证

**技能**:`matt-pocock:tdd`。
1. RED:写测试前先确认被测 seam,并核对该 seam 与模块接口契约一致,未经确认不写测试;再运行能到达目标路径的失败测试,证明目标行为缺失。切片自己的一次 RED 失败测试保留。期望值来自独立真值源,不由被测代码同样推导。
2. GREEN:最小实现使该场景通过。写这一轮生产代码时，额外检查只跑编译、类型检查这类秒级检查。
3. REFACTOR:只做当前任务必要整理,测试保持通过;设计级重构不在此步,归入评审阶段讨论。
4. REGRESSION:这一轮改动写完后跑关联的局部快测；失败就修，修完重跑同一条。全量、端到端和打包不在这一步用来声称验证通过。需要时用已有 CodeGraph 辅助定位。
5. TASK_VERIFIED:检查实际结果、局限和证据,再更新 OpenSpec 对应任务。部分完成不得勾选。
纯文档使用 §1 的文档验证路径;无可用自动化时明确人工验证方式与证据缺口。不得把编译器缺失、设备不可达、网络或 runner 故障当作有效 RED。

## 9. 异常回流

| 触发 | 技能/动作 | 恢复条件 |
|---|---|---|
| 测试异常或实现失败 | diagnosing-bugs：停在红信号、最小复现和根因，Phase 5 不应用修复；回归测试和修复只由 tdd 写 | 有效失败原因与回归证据 |
| 需求、接口、场景变化 | openspec-update-change → 校验 → 审批 → 更新计划 | 规格和计划重新一致 |
| 实施顺序或步骤漂移 | to-tickets 更新受影响切片 | 不改变已批准需求,重大变化获确认 |
| 环境/设备不可用 | 记录 INFRA_ERROR,查项目约束 | 环境恢复,重跑受影响验证 |
| 实际行为不符规格 | 记录 SPEC_MISMATCH | 修复实现;仅需求确需改变时更新规格,不能为通过测试降低标准 |

## 10. REVIEW — 评审

**技能**:`matt-pocock:code-review` 提供两轴评审方法;`superpowers:requesting-code-review` 提供评审节奏与派发;`superpowers:receiving-code-review` 处理收到的反馈。
提供规格、相关计划、实际 diff 和验证证据。规格以当前 OpenSpec change 为准,提交信息不能替代需求;找不到 change 时如实报告无可用规格并跳过规格轴。规范符合性与规格符合性分轴评审并分别汇报,不合并排序;仓库自身规范优先于气味基线,基线项记为判断项。跨模块变更加评集成维度并记录版本组合,单模块变更显式说明跳过理由。
反馈须核实后处理,重要问题闭合并重跑受影响检查,驳回需记录理由。纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。`code-review` 亲自跑一次与本次改动相关的局部快测。这次通过不能代替 `verification-before-completion`。`code-review` 的发现写入交付报告，不往 tasks.md 追加切片。重要发现的修改回到 `tdd`。要改源码回到 `tdd`。`receiving-code-review` 若要改码，采纳的修改交给 `tdd`，不必另起一条实现。评审结论绑定实际评审的区间、规格版本与支撑命令;范围变动后重评或标注失效。独立评审依赖可用且获授权的评审机制;只有自查时明确标注自查,不得伪称独立评审。

## 11. VERIFY — 整体完成验证

**技能**:`superpowers:verification-before-completion`。
声称验证通过只用这一步的全量、端到端和打包。局部快测通过不能代替这一步。
1. 使用最终工作树/产物的新鲜证据。已提交时记录 commit;未提交则记录 HEAD 加工作树差异/产物标识。
2. 按批准场景执行 Host、Cross-build、Target 或 Integration 中适用的验证;不适用项注明原因。
3. 跨模块单测通过不代表集成通过,核实项目协作文档要求的版本组合和端到端结果。
4. 每个 Req/Scenario 能追踪到 task、模块、Test、环境、结果与证据;缺项如实报告。
5. 本任务若新增、删除、移动模块，或改变了模块对外职责、模块间关系、整体拆分，交付前用 `map` 发布一次并再跑 doctor。只改模块内部时不发布。地图结构已失效却未发布时，交付写 MAP_STRUCTURAL。
**退出**:适用场景通过、重要评审问题解决。证据矩阵见下文;设备、部署等门禁见项目约束。

## 12. INTEGRATE / ARCHIVE / KNOWLEDGE — 交付与收尾

进入 `finishing-a-development-branch` 之前，先用只读事实说明每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。推送、合并、删除和清理仍等用户当次选择。
1. 用 `superpowers:finishing-a-development-branch` 展示验证结果并落实用户的合并、PR、保留等选择。提交、推送、部署和设备授权按项目约束处理。
2. 有 OpenSpec change 时检查任务证据与产物状态，用 `openspec-sync-specs` 同步需要的 delta specs，并核对合并结果。同步完成时不移动目录。
3. 同步与归档顺序执行,不在同步未结束时移动 change。使用实际返回的 changeRoot/planningHome,不要拼接猜测路径。
4. 未完成任务或缺证据不能以“全部完成”归档;用户若明确选择保留未完成状态,如实报告。
5. 规格同步之后、移动目录之前，按 [知识回流](knowledge-policy.md) 把需求页和适用的问题页写入初始化知识库 alias `project`，并在活动 change 目录留下 `knowledge-receipt.json`。这两类不再询问是否摄入。回执留下且规格已同步之后，才用 `openspec-archive-change` 移动目录。结晶、删除、新建知识库、修改注册表和推送仍单独授权。没有注册表时记 `NOT_CONFIGURED`，不新建库。
6. 最终分别报告实现、适用验证、集成/归档与知识摄入状态。知识回执欠账留在完成检查里，不回滚已经验证过的修复。

完整行为变更路线:
```text
DISCOVERY → SPEC_VALIDATED → SPEC_APPROVED → PLAN_APPROVED
→ WORKSPACE_READY → APPLY_CONTEXT_LOADED
→ (TASK_SELECTED → RED → GREEN → REFACTOR → REGRESSION → TASK_VERIFIED)*
→ REVIEWED → CHANGE_VERIFIED → INTEGRATED_OR_RETAINED
→ SPECS_SYNCED → KNOWLEDGE_RECEIPT → ARCHIVED
```
需求页和已验证问题页在归档前写入初始化知识库。其他种类仍单独授权。

## 13. 通用验证证据

每个场景声明适用环境:Host / Cross-build / Target / Integration。未运行写 NOT_RUN,环境故障写 INFRA_ERROR,不适用写 N/A 并说明理由。仅实际执行并符合断言才写 PASS。文档任务校验实际引用、内容归属、规则一致性和 diff,不声称构建或运行通过。

| Req/Scenario | Task | 模块/仓库 | 版本或工作树标识 | Test | 环境 | 证据 | 结果 |
|---|---|---|---|---|---|---|---|
| <id> | <id> | <module-id> | <commit 或 HEAD+diff 标识> | <test> | <env> | <path/hash> | <result> |

追踪链:Scenario → task/module → TestRequest/Test → TestResult → EvidencePacket → 工作树/commit/artifact。
跨模块验证必须记录参与仓库的版本组合、未提交差异和接口/配置版本(不含密钥)。未提交工作可以验证,但发布与归档须绑定最终集成版本。旧报告、索引存在和脚本退出码不能单独证明业务完成。
