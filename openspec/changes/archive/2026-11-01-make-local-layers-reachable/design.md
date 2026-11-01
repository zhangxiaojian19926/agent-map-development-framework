# Design

## Context

动机见 [proposal.md](proposal.md)。这里记取舍。

Agent 读技能的实际路径只有一条：AGENTS.md 的阶段路由表给出技能名 → Agent 打开该技能的 `SKILL.md`。任何不在这条路径上的文件，Agent 都不会读——除非有显式指针。

本地改编层正好落在这条路径之外：它们是同目录的兄弟文件，上游 `SKILL.md` 不引用它们（上游不可能引用框架自己加的文件），框架自己的文档也没有指向。

## Goals / Non-Goals

**Goals:**

- 执行任一带本地层的技能时，Agent 能确定地读到该层的规则。
- 登记与磁盘一致，且登记的内容不会再次变成无人指向的死文件。
- 技能在两处契约里的阶段归属一致。

**Non-Goals:**

- 不改任何上游 `SKILL.md` 的字节。
- 不把全部本地文件都登记成"必读"——技法参考、验证脚本、创作史不需要每次加载。
- 不新增运行期依赖。

## Decisions

**决策一：指针写在 AGENTS.md 的单元格里。**

三个候选：

| 方案 | 问题 |
|---|---|
| 在上游 `SKILL.md` 里加指针 | 破坏"上游原文字节不改"，且改动落在 6 个上游文件里 |
| 单独建清单文件，指针在清单里 | 变成"读指针 → 再读清单 → 再读本地层"两级跳转；清单本身成了新的无落点文件 |
| **在阶段路由表的单元格里直接写文件名** | 指针与触发条件在同一处，Agent 读到表就知道要带什么 |

第三个赢。它符合写给 agent 的文档的指针原则：**指针的措辞决定触发可靠性**。单元格里写"（并读其同目录 discipline.md）"，与技能名出现在同一格，Agent 没有理由只读前半句。

代价是表格变长。七处标注分布在四个单元格里，每处约二十字。

**决策二：登记文件放在 `skill/local-layers.json`，只登记必读的规则层。**

21 个本地文件里，只有 7 个是"Agent 执行该技能时必须一并读取的规则"：

- 技法参考（`condition-based-waiting.md`、`root-cause-tracing.md`、`defense-in-depth.md`）——按需查，不必读
- 验证脚本与创作史（`find-polluter.sh`、`CREATION-LOG.md`、`test-pressure-*.md`）——按需跑或按需读
- 规则层（`discipline.md`、`framework-rules.md`、`plan-format.md`、`test-quality.md`）——每次执行该技能都要读

把必读的和按需的混在一起登记，等于让登记失去意义。

`skill/` 已经在运行时白名单里，登记文件随包分发，目标项目里的 Agent 也能读到同一份登记。

**决策三：检查双向。**

- 登记里每个文件必须真实存在于该技能目录（防止登记指向已删文件）。
- 登记里每个技能名必须是真实的技能入口（防止拼写错误）。
- **登记的每个文件名必须在活文档里被提及**——这一条是防复发的关键：只登记不提及，等于回到今天的状况。

**决策四：`dispatching-parallel-agents` 统一归到 WORKSPACE。**

两处不一致时，以 `docs/framework/development-workflow.md` 为准——它是"完整开发流程"的事实源，AGENTS.md 的表是它的精简指针，指针与事实源冲突时以事实源为准。

契约第 6 节的原话是"仅在获得委派授权时用 `subagent-driven-development` 或 `dispatching-parallel-agents`"，AGENTS.md 的 WORKSPACE 行改成同样的条件。

**决策五：移除 `using-superpowers` 的技能入口，保留 `references/`。**

`executing-plans/SKILL.md` 与 `writing-skills/SKILL.md` 这两份上游原文引用了 `../using-superpowers/references/codex-tools.md` 等五个平台适配文件。删整个目录会断链，而断链会被分发结构检查判为失败。

所以只删 `SKILL.md`——它才是那个"每次对话都触发、永久占上下文"的入口。`references/` 变成一个只有平台适配参考的目录，仍被上游文件引用，链接照常解析。

**决策六：`subagent-driven-development` 保留并加改编层，不移除。**

上一轮我基于不完整扫描建议移除它，撤回。事实是它早已在流程契约第 6 节有委派落点，而它与框架的重复确实存在：上游的任务级评审是 `matt-pocock:code-review` 两轴评审的第二套实现，implementer 还自行提交，与"提交权在 INTEGRATE 阶段由用户选"冲突。

移除会丢掉并行实施的能力；留着不管则两套完成判据并存。用框架既有的模式解决——**上游原文字节不动，另写一层改编**，写明评审走框架的两轴方法、implementer 不自行提交。这层改编同时成为本批新机制的第一个用例：它有登记、有指针、有检查。

**决策七：纠正上一轮的错误建议。**

上一轮我基于只扫 AGENTS.md 的不完整扫描，得出"6 个技能无落点"和"建议移除 `subagent-driven-development`"。全量扫描活文档后，真实情况是：只有 `using-superpowers` 一个无落点；`subagent-driven-development` 在流程契约里早有落点；`dispatching-parallel-agents` 两处都有但归属不一致。

建议撤回，改为记录这次扫描方法本身的教训：**判断"有没有落点"必须扫全部活文档，不能只扫常驻的那一份。**

## Risks / Trade-offs

- **AGENTS.md 变长。** 每轮常驻的上下文增加约一百五十字。换来的是七份规则真正生效——否则它们每轮都在包里、每轮都不被读，是更贵的浪费。
- **登记文件与磁盘可能再次不一致。** 检查双向覆盖了这一点：登记项必须存在，且必须被活文档提及。
- **移除 `using-superpowers` 后，其 `references/` 目录名与技能不再对应。** 保留它是为了不断上游链接，代价是目录语义略怪。链接可解析比目录名好看重要。
- **检查的解析是启发式的。** 阶段归属的判定靠正则匹配章节标题与技能名。标题格式变化时检查会漏报，不会误报——漏报是安全的方向。
