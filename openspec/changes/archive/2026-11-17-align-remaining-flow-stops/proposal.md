## Why

其余三条路由还没有接上已经定下的停点。`flow-01` 的失败路径把整份 `diagnosing-bugs` 写成下一项，技能原文的 Phase 5 会接着写回归测试并应用修复。`flow-08` 只禁止「已批准的」OpenSpec change，架构路径的收尾仍把 `openspec-propose` 和 `to-tickets` 写成下一步。`code-review` 的本地改编层仍允许把 Minor 发现记进 change 的 task list，`flow-04` 和 `flow-09` 会读到这句，从而往 `tasks.md` 追加切片。

这次只把这三处收回到已定口径。不实施。

### 前提

下列句子均按当前文件核对。与用户给定口径冲突时，以文件为准，并在该条标明。

1. 十五条路由仍是一次只命中一条。`AGENTS.md` 第 93 行写明入口是 `flow-01` 到 `flow-15`，一条请求只命中其中一个，下一项以该路由正文为准。`openspec/specs/agent-workflow-routers/spec.md` 的 WR-01 要求恰好这十五条，不得另建第十六条。国内外宿主共用主路径已经写在 WR-21：13 个宿主共用 `flow-02` 的主路径；子代理是任何一个 coding agent 都可以有的能力；委派必须同时有用户授权和宿主子代理能力；不为此修改宿主安装器。这次不改 WR-21，不改 `flow-02` 的委派句。该句在 `tools/framework_core/workflows/combinations.json` 的 `flow-02` 对象里，现行正文是「委派只在用户已授权且宿主提供子代理时发生」以及「子代理是任何一个 coding agent 都可以有的能力，不是只有 Claude Code 与 CodeBuddy。当前安装事实不改宿主安装器。」

2. 切分线已经落在 `flow-02`，这次不动它。OpenSpec 独占规格账本。`tasks.md` 的切片正文只由 `to-tickets` 写。源码只由 `tdd` 写。`openspec-explore`、`openspec-apply-change`、`executing-plans` 退出必经，人点名仍可用。这些句子在 `combinations.json` 的 `flow-02` 对象、`AGENTS.md` 第 91 行和第 102–114 行的阶段表、以及 WR-06、WR-08、WR-20。阶段表第 1 行已经写「诊断停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不应用修复。回归测试和修复只由 tdd 写」。第 7 行已经写「发现写入交付报告，不往 tasks.md 追加切片」。这是 `flow-02` 那条链的口径，不是 `flow-01`、`flow-08`、`flow-14` 的正文。

3. 路由正文的事实源是组合清单，三条目标 flow 都在清单里。`tools/framework_core/workflows/routers.py` 的 `render_skill` 用 `combinations.json` 的 flow 对象生成 `skill/flows/<id>/SKILL.md`。`distribution_errors` 在文件与渲染结果不一致时报 `router body drifted from the combination manifest`。`combinations.json` 的 `flows` 含 `flow-01` 至 `flow-15`，其中包括 `flow-01`（约第 5 行）、`flow-08`（约第 226 行）、`flow-14`（约第 325 行）。因此这三份 `SKILL.md` 都不能手改；要改的是对应 flow 对象，再渲染。

4. `flow-01` 的失败句没有停点，设计未批准的停点已经在。进入节写先读 `BOOTSTRAP.md` 与 `project-bootstrap`，失败时再读 `diagnosing-bugs` 与 `discipline.md`，设计未批准时停止、不进入 `flow-02`。下一项节写「失败完成后，下一项是 diagnosing-bugs 与 discipline.md」以及「设计未批准时没有下一项技能」。WR-07 与 WR-20 的「其余工作流」句与这三句一致：失败时的下一项就是这份诊断技能，没有「停在红信号、最小复现和根因」，也没有「Phase 5 不应用修复」。与用户给定口径无冲突：设计未批准仍停止、不进入 `flow-02`，这句保留。要改的是失败路径那一句，它现在把整份技能当成下一项。

5. `diagnosing-bugs` 的 Phase 5 会修码，但技能自己允许在明确理由下跳过阶段。`skill/matt-pocock/diagnosing-bugs/SKILL.md` 第 8 行：「Skip phases only when explicitly justified.」第 114–128 行 Phase 5 的标题是「Fix + regression test」：先把最小复现写成失败测试，再「Apply the fix」。第 130 行起的 Phase 6 把修复已经落地当作清理前提。同目录 `discipline.md` 第 16–25 行的铁律是「NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST」，它禁止没有根因就修，不禁止查完根因之后进入 Phase 5，也没有写「Phase 5 不能跳过」或「本文件优先于路由」。WR-20 写明：成员技能收尾指向其他步骤时，路由写明的下一项优先。`flow-02` 已经用路由句暂停 Phase 5，且没有改这份上游全文。因此路由上的明确停点就是第 8 行所要求的跳过理由，不需要重写 `diagnosing-bugs`。这里不单列技能改写。

6. `flow-14` 的失败模式只点名诊断技能。进入节三句是：改技能点名 `writing-skills`；改 Agent 所读文档点名 `writing-for-agents`；失败点名 `diagnosing-bugs` 与 `discipline.md`。第四句是三种模式各自结束，不把另一种模式写为下一项。失败这句没有停点。前两句和第四句与用户给定口径一致，保留。`flow-14` 要加上的是与 `flow-01` 失败路径相同的停点，不是 `flow-02` 那句「回归测试和修复只由 tdd 写」。文件差异：`flow-02` 的诊断停点后面跟着由 `tdd` 写修复，因为那条链还要进入实现；`flow-01` 与 `flow-14` 的用户给定口径是本路由不写修复，也不把 `tdd` 写成下一项。不能把 `flow-02` 的后半句抄进来。

7. `flow-08` 的禁止句窄于「不创建 change」。purpose 与进入节最后一句都是「产物保持未批准，不创建已批准的 OpenSpec change」。交接仍先点名 `reverse-engineer` 的交接部分，交接完成后的下一项是 `brainstorming` 的架构路径及其 `framework-rules.md`。这句只排除已批准的 change，不排除未批准的 change，也没有把 `openspec-propose` 或 `to-tickets` 排除出下一项。`skill/superpowers/brainstorming/SKILL.md` 第 100–103 行：没有 change 时让 `openspec-propose` 创建产物，第 9 步调用 `to-tickets`。第 149–154 行把架构路径的唯一后续技能写成 `to-tickets`。同目录 `framework-rules.md` 第 13–16 行：改变行为、接口或验收时，下一项是 `openspec-propose` 或 `openspec-update-change`，规格之后是 `to-tickets`。同文件第 21–24 行又写：本文件不宣布 brainstorming 之后的技能，活动中的 `flow-*` 路由写明下一项。两段并存，以第 21–24 行为准：只要 `flow-08` 自己写明停在设计对话，并且不把那两个技能当作下一项，路由句就盖过技能收尾。现在的「不创建已批准的 change」没有盖过。交接仍先 `reverse-engineer`，这句保留。

8. 允许把发现写入 `tasks.md` 的是改编层的一句，不是 `flow-04` 或 `flow-09` 的入口。`skill/matt-pocock/code-review/framework-rules.md` 第 85–86 行：「Minor findings may be recorded for later, in the change's task list or the delivery report.」同文件开头写明与上游 `SKILL.md` 冲突时以本文件为准。`AGENTS.md` 第 111 行同样写明改编层与上游冲突时以本地为准。WR-08 已经要求 `code-review` 的发现写入交付报告，不得往 `tasks.md` 追加切片；阶段表第 7 行是同一句。缺口是这句本地许可仍在，而 `flow-04`、`flow-09` 的正文只点名 `code-review` 与 `framework-rules.md`，没有再重复停点。`flow-04` 的入口是评审受管 diff，人工改动冲突时停止。`flow-09` 的入口是规格已批准且实现之后才点名评审，找不到 change 时报告无可用规格。这两条入口和技能点名与用户给定口径一致，不改。`flow-09` 仍要求已批准规格、找得到 change。

9. 知识库查询没有改写上述正文。alias `project` 指向 `knowledge/project/`，status 为 shell `READY`、ingestion `PRESENT`、10 页。需求页 `agent-workflow-routers` 的 `source_sha256` 为 `f8308e3f9003d8ffa9dc764d40aa6a736820aef63b66bfc63dfb27278547ffce`，与现行 `openspec/specs/agent-workflow-routers/spec.md` 的 sha256 一致。该页写的是 `flow-02` 主路径的摘要，并写明当前需求以来源规格为准。它没有声称 `flow-01` 或 `flow-14` 可以进入 Phase 5，也没有声称 `flow-08` 可以创建未批准的 change。本提案的行为以规格和路由正文为准。

10. 入口只读 doctor 的结果是分发库既有状态：`initialization=PARTIAL`、`documentation=MISSING`、`coverage=MISSING`、`handoff=BLOCKED`、`runtime=NOT_RUN`。本变更不为把它变绿而改工程。

### 排除

1. 改 `flow-02`。它的诊断停点、单一 `tasks.md` 作者、单一实现器、三个退出必经技能，以及委派句，已经是已定口径。WR-21 的「阶段表与流程正文同一条链」只在 `flow-02` 的新行为链被修改时要求同改 `AGENTS.md` 第 2 节和 `docs/framework/development-workflow.md`。这次不改 `flow-02`，因此不触发那条同改。

2. 改 `flow-03` 或 `flow-15`。`flow-03` 只点名 `codebase-design` 或 `domain-modeling`，不点名诊断、规格或评审。`flow-15` 只在已有 `flow-14` 的验证证据后点名 `verification-before-completion`，不把 `flow-14` 写成完成后的下一项。两者都没有这次的三个泄漏口。

3. 改 `flow-05`、`flow-06`、`flow-07`、`flow-10`、`flow-11`、`flow-12`、`flow-13`。`flow-05` 只点名 `llm-wiki`。`flow-06` 只点名 `reverse-engineer` 的取证部分，`flow-07` 只点名证据归并；进入架构路径并可能滑进规格的是 `flow-08`，不是这两条。`flow-10` 至 `flow-13` 不点名成员技能，只绑定既有研究、候选、渠道和产物命令。

4. 改 `flow-04` 或 `flow-09` 的入口和技能点名。它们已经点名 `code-review` 与 `framework-rules.md`。把停点写进那份改编层的 Minor 句，两条路由一起生效。不在这两份路由正文里再写一遍，也不把 `to-tickets` 或 `tdd` 加进它们的 `mentions`。

5. 手改 `skill/flows/flow-01/SKILL.md`、`flow-08/SKILL.md` 或 `flow-14/SKILL.md`，而不改 `combinations.json` 里对应对象。WR-02 与 `distribution_errors` 会把差异报成正文漂移。

6. 重写 `diagnosing-bugs` 的上游全文或 `discipline.md`。前提 5 说明路由句足够。Phase 5 仍留在技能原文里，供被明确授权进入修复的其他路径阅读；`flow-01` 与 `flow-14` 用路由句跳过它。

7. 改 `brainstorming` 的上游全文。前提 7 的第 21–24 行已经把下一项交给活动路由。`flow-08` 写明自己的下一项即可。不把「有界工作仍进入规格」从改编层删掉，那一段继续服务于 `flow-02`。

8. 改阶段表、`development-workflow.md`、人格标记、`FRAMEWORK_ENTRY` 或 `docs/framework/agent-persona.md`。阶段表描述的是 `flow-02` 的链，其中「修复只由 tdd 写」不能挪到 `flow-01`。托管段与人格来源保持相同。WR-16 继续禁止改写托管段和 doctor 状态词典。

9. 把 `openspec-propose` 或 `to-tickets` 写进 `flow-08` 的 `mentions`，或把 `tdd` 写进 `flow-01`、`flow-14` 的 `mentions`。`catalog.json` 和 `docs/guide/from-zero-to-one.md` 的技能列等于 `mentions`。这次三个对象的 `mentions` 成员不变，所以这两处技能列不改。正文里可以出现「不是下一项」的技能名，这不构成把它列入组合。

10. 把已归档的 `2026-11-16-complement-openspec-and-superpowers`，或活动中的 `add-project-bootstrap-and-maps`、`agent-led-project-intake`，并进本 change。那些目录保持原样。

### 结论

已定口径只补这三处，不另起一条流程。

`flow-01` 的失败路径仍点名 `diagnosing-bugs` 与 `discipline.md`，但只停在红信号、最小复现和根因。`diagnosing-bugs` 的 Phase 5 不在本路由应用修复：不把最小复现写成回归测试，也不应用修复。本路由不写修复，也不把 `tdd` 写成下一项。设计未批准时仍停止，不进入 `flow-02`，设计未批准时仍没有下一项技能。先读 `BOOTSTRAP.md` 与 `project-bootstrap` 的句子不变。

`flow-14` 的失败模式加上同一句停点：只停在红信号、最小复现和根因；Phase 5 不在本路由应用修复；本路由不写修复，也不把 `tdd` 写成下一项。改技能的 `writing-skills` 句、改 Agent 所读文档的 `writing-for-agents` 句，以及「三种模式各自结束，不把另一种模式写为下一项」，都不改。

`flow-08` 仍先点名 `reverse-engineer` 的交接部分，交接完成后仍进入 `brainstorming` 的架构路径，然后停在设计对话。不把 `openspec-propose` 或 `to-tickets` 当作下一项。不创建 OpenSpec change，包括未批准的 change。purpose 里的「不创建已批准的 OpenSpec change」换成这句，避免描述与正文互相矛盾。

`code-review` 的 `framework-rules.md` 里允许把 Minor 发现记进 change task list 的那一句，改为：发现只写入交付报告，不往 `tasks.md` 追加切片。`flow-04` 与 `flow-09` 的入口和技能点名不改。`flow-09` 仍要求规格已批准，并且找得到 change。同文件「Where the spec comes from」里阅读已有 `tasks.md` 的句子不改，那是读取切片，不是追加切片。Important 发现「must be fixed」那一句也不在这次替换里。

## What Changes

- `combinations.json` 的 `flow-01` 对象：保留进入节的 `BOOTSTRAP.md` 与 `project-bootstrap` 句，以及「设计未批准时停止，不进入 flow-02」。失败时仍点名 `diagnosing-bugs` 与 `discipline.md`，并写上结论中的停点。下一项节删除「失败完成后，下一项是 diagnosing-bugs 与 discipline.md」，改为同一停点：不写修复，不把 `tdd` 写成下一项。保留「设计未批准时没有下一项技能」。
- `combinations.json` 的 `flow-14` 对象：只改失败那一句，加上与 `flow-01` 相同的停点。`writing-skills` 句、`writing-for-agents` 句、三种模式各自结束那句，以及 purpose，保持原句。
- `combinations.json` 的 `flow-08` 对象：保留「先点名 reverse-engineer 的交接部分」。交接完成后仍点名 `brainstorming` 的架构路径与 `framework-rules.md`，并写明停在设计对话，不把 `openspec-propose` 或 `to-tickets` 当作下一项。purpose 与进入节的「不创建已批准的 OpenSpec change」改为「不创建 OpenSpec change」。
- 这三个对象改完后，用现有渲染得到对应的 `skill/flows/flow-01/SKILL.md`、`flow-08/SKILL.md`、`flow-14/SKILL.md`。不手改出漂移正文。三个对象的 `mentions` 成员不变。
- `skill/matt-pocock/code-review/framework-rules.md` 第 85–86 行那一句改为发现只写入交付报告，不往 `tasks.md` 追加切片。不改该文件其余句子，不改上游 `SKILL.md`。
- **BREAKING**：已按现行 `flow-01` 在失败后进入 Phase 5 修码的会话，改为停在红信号、最小复现和根因。已按现行 `flow-08` 创建未批准 change 或把 `openspec-propose`、`to-tickets` 当作下一项的会话，改为停在设计对话。已按现行改编层把 Minor 发现写入 change task list 的 `flow-04` 与 `flow-09` 评审，改为只写入交付报告。

### 不改的句子

- `flow-02` 全文，包括委派句、诊断停点里的「回归测试和修复只由 tdd 写」、以及三个退出必经技能。
- `flow-03`、`flow-04`、`flow-05`、`flow-06`、`flow-07`、`flow-09`、`flow-10`、`flow-11`、`flow-12`、`flow-13`、`flow-15` 的对象与渲染正文。`flow-04` 与 `flow-09` 只通过上面那一句改编层生效。
- `AGENTS.md` 的人格标记、`FRAMEWORK_ENTRY`、第 2 节阶段表，以及 `docs/framework/development-workflow.md`、`docs/framework/agent-persona.md`。
- `diagnosing-bugs` 的 `SKILL.md` 与 `discipline.md`，`brainstorming` 的 `SKILL.md` 与 `framework-rules.md`，`code-review` 的上游 `SKILL.md`。
- 宿主安装器、`roster.json`、`catalog.json`、`docs/guide/from-zero-to-one.md` 的技能列。

## Capabilities

### New Capabilities

- 无。这是现有路由能力上的三处停点，不新增 capability 目录。

### Modified Capabilities

- `agent-workflow-routers`（`openspec/specs/agent-workflow-routers/spec.md`）：修改 WR-07 中 `flow-01`、`flow-08`、`flow-14` 三条，以及 WR-20「其余工作流的下一项」里对应的三句。`flow-01` 的失败路径改为结论中的停点，设计未批准的停止句保留。`flow-08` 改为停在设计对话，不创建任何 OpenSpec change，并且不把 `openspec-propose` 或 `to-tickets` 当作下一项；交接仍先 `reverse-engineer`。`flow-14` 的失败模式加上同一句停点，改技能与改 Agent 所读文档的点名不变。WR-20 里已有的「诊断完成后不写修复」Scenario 仍只描述新行为链上「回归测试和修复只由 tdd 写」的那一句，不把它的适用范围扩到 `flow-01` 或 `flow-14`；这两条另写 Scenario。新增 Requirement：`code-review` 的 `framework-rules.md` 不得再把 change task list 写成发现的记录位置；发现只写入交付报告，不往 `tasks.md` 追加切片。该 Requirement 点明 `flow-04` 与 `flow-09` 靠这句生效，同时它们的入口、技能点名不变，`flow-09` 仍要求已批准规格且找得到 change。不修改 WR-01、WR-02、WR-06、WR-16、WR-21 的现有句子。不把 `skip_specs` 写入本 change 的 `.openspec.yaml`。

## Impact

- 将来要改的路由事实源是 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-01`、`flow-08`、`flow-14` 的三个对象，然后用现有 `render_skill` 写出三份 `SKILL.md`。其他 flow 对象不动。`mentions` 不变，因此 `catalog.json` 与 `docs/guide/from-zero-to-one.md` 的技能列不动；只有 `mentions` 变化时才允许这三处一起改。
- 同一次变更只改 `skill/matt-pocock/code-review/framework-rules.md` 的 Minor 记录句。阅读已有 `tasks.md` 的句子、Important 发现必须先修的句子、上游 `SKILL.md`，都不改。
- `tests/test_flow_routers.py` 的 `test_successors_are_written_by_the_router` 锁的是 `flow-02` 的下一项句子，其中包括「回归测试和修复只由 tdd 写」。实现时不得为了让新停点出现在该测试里而去改 `flow-02`。`test_fifteen_routers_match_the_manifest` 在正文与清单不一致时失败，所以渲染必须来自清单。`test_persona_block_matches_source_and_status_dictionary_stays_put` 继续锁托管段与人格来源相同。
- 风险：`discipline.md` 仍把「先写测试再修复」写成正确做法。若会话不把路由停点当成第 8 行的明确跳过理由，仍可能进入 Phase 5。本提案判定路由句足够，因而不改该文件；这个残余靠路由句的明确措辞挡住，不靠重写技能。`brainstorming` 的改编层第 13–16 行仍会把改变行为的设计送进规格，但只在活动路由没有写明下一项时生效；`flow-08` 必须自己写明停点，不能只改 purpose、留下「下一项是 brainstorming」而不否定 `openspec-propose`。`framework-rules.md` 的 Important 句仍写「must be fixed before the work proceeds」。这次不改那句。`flow-02` 另有「重要发现的修改回到 tdd」；`flow-04` 与 `flow-09` 没有这句。因此本变更关上的是 task list 这一条泄漏，不是评审人自己改码的每一条可能读法。`flow-08` 的描述若仍保留「不创建已批准的 OpenSpec change」，会和正文的「不创建 OpenSpec change」冲突，所以 purpose 必须一起换。
- 非目标：不在本提案的实施完成之前修改 flow 正文、技能实现或 `AGENTS.md`；不写 `tasks.md`；不改宿主安装器；不改阶段表和 `development-workflow.md`；不重写 `diagnosing-bugs`；不改人格标记、`FRAMEWORK_ENTRY` 和 `agent-persona`；不回滚、不改写 `openspec/changes/archive/2026-11-16-complement-openspec-and-superpowers/`；不把该归档、主规格或知识页放进本 change 目录；不写知识库内容；不提交、不推送。入口 doctor 的 `initialization=PARTIAL`、`documentation=MISSING`、`coverage=MISSING`、`handoff=BLOCKED`、`runtime=NOT_RUN` 是这次只读检查看到的分发库状态，本变更不为把它变绿而改工程。
