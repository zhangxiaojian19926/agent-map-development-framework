## Context

见 [proposal.md](proposal.md) 的前提与结论，以及 [specs/agent-workflow-routers/spec.md](specs/agent-workflow-routers/spec.md)。本设计只定怎么改，不另起流程。

路由正文的字节来自 `tools/framework_core/workflows/routers.py`。`render_skill` 用 `combinations.json` 里的一个 flow 对象生成一份 `SKILL.md`。`write_routers` 对清单里的十五条都调用它并写回 `skill/flows/<id>/SKILL.md`。`distribution_errors` 在文件与 `render_skill` 的输出不一致时报 `router body drifted from the combination manifest`。`sync_catalog` 是另一个函数，只在 `mentions` 要改技能列时才用。

`diagnosing-bugs` 第 8 行允许在明确理由下跳过阶段。Phase 5 的标题是「Fix + regression test」，其中一步是「Apply the fix」。同目录 `discipline.md` 的铁律只禁止没有根因就修；第 33–35 行把真红信号写成「now write code」，合理化表把「先写测试再证明修复」写成正确做法。两处都没有「Phase 5 不能跳过」或「本文件优先于路由」。WR-20 写明：成员技能收尾指向其他步骤时，路由写明的下一项优先。`flow-02` 已经用路由句暂停 Phase 5，没有改这份技能。

## Goals / Non-Goals

**Goals:**

- 三个 flow 对象改完后，对应 `SKILL.md` 的字节等于 `render_skill` 的输出。
- `flow-01` 与 `flow-14` 的失败句本身就是跳过 Phase 5 的明确理由：停在红信号、最小复现和根因，本路由不写修复，也不把 `tdd` 写成下一项。
- `flow-08` 的 purpose 与进入节都说不创建 OpenSpec change，并停在设计对话。
- `code-review` 的 `framework-rules.md` 只改 Minor 那一句。`flow-04` 与 `flow-09` 靠读这句生效。

**Non-Goals:**

- 不改 `diagnosing-bugs` 的 `SKILL.md` 与 `discipline.md`。Phase 5 仍留在技能原文里，供被明确授权进入修复的路径阅读。
- 不手改三份 `SKILL.md`。不改其余十二条 flow 对象，因此不调用 `sync_catalog`，也不改 `catalog.json` 与 `docs/guide/from-zero-to-one.md`。
- 不改 `flow-04`、`flow-09` 的对象。不删 `framework-rules.md` 里阅读已有 `tasks.md` 的句子，也不改 Important 发现必须先修的句子。
- 其余排除见提案。本设计不扩大那份名单。

## Decisions

1. 先改 `combinations.json` 里 `id` 为 `flow-01`、`flow-08`、`flow-14` 的对象，再用现有 `write_routers` 写回十五条 `SKILL.md`。`write_routers` 会重写全部十五条；其余对象不改，所以其余十二份的渲染结果与改前一致。备选是只对这三个对象调用 `render_skill` 再写入对应文件，效果相同。备选「手改三份 SKILL.md」不行：`distribution_errors` 会报正文漂移。
2. 路由句是跳过 Phase 5 的明确理由，不改技能原文。备选是改写 Phase 5，让技能自己不再应用修复。那会动到 `flow-02` 仍要阅读的同一节，而技能第 8 行已经把「明确理由」留给路由。只写「下一项不是 `tdd`」、不点名 Phase 5、也不写「本路由不写修复」，盖不住 Phase 5 的「Apply the fix」和 `discipline.md` 的「now write code」：那两句是在诊断技能内部写修复，不是把下一项指到另一个技能。所以停点必须写进点名 `diagnosing-bugs` 的路由句。这不构成把重写 Phase 5 放进本次范围。
3. `flow-01` 只改失败路径和下一项里的失败句。进入节的 `BOOTSTRAP.md` 与 `project-bootstrap` 句，以及「设计未批准时停止，不进入 flow-02」，保持原句。下一项不再把整份 `diagnosing-bugs` 写成失败完成后的下一项。`flow-14` 只改失败那一句，加上同一停点。不把 `flow-02` 的「回归测试和修复只由 tdd 写」抄进这两条。`writing-skills` 句、`writing-for-agents` 句和「三种模式各自结束」保持原句。
4. `flow-08` 的 purpose 和进入节里的「不创建已批准的 OpenSpec change」一起换成「不创建 OpenSpec change」。只改其中一处会让描述和正文互相矛盾。交接仍先点名 `reverse-engineer` 的交接部分；交接完成后仍进入 `brainstorming` 的架构路径，然后停在设计对话，不把 `openspec-propose` 或 `to-tickets` 当作下一项。三个对象的 `mentions` 成员不变。正文里出现「不是下一项」的技能名，不把它加进 `mentions`。
5. `framework-rules.md` 第 85–86 行的 Minor 句改为：发现只写入交付报告，不往 `tasks.md` 追加切片。备选是把同一句再写进 `flow-04` 和 `flow-09`。这两条已经点名该文件，且该文件与上游冲突时以本地为准，所以不改它们的入口和技能点名。`flow-09` 的「规格已批准且实现之后」和「找不到 change 时报告无可用规格」保持原句。
6. 规格增量已经写在 delta spec。现行 WR-20 的「诊断完成后不写修复」Scenario，WHEN 是「`diagnosing-bugs` 已完成」，没有写成只限新行为路径。实施时按 delta 把这个 WHEN 收窄到新行为路径，让「回归测试和修复只由 tdd 写」留在那条链上。不改 WR-08。`flow-01` 与 `flow-14` 用各自的 Scenario，不借用这半句。

## Risks / Trade-offs

- [write_routers 重写十五条，误改了别的对象] → 其余对象不编辑。渲染后的 diff 只应出现 `flow-01`、`flow-08`、`flow-14` 的 `SKILL.md`，加上清单和那一句改编层。别的 flow 正文若变了，停下来，不把它当成这次的范围。
- [Phase 5 与「now write code」仍在技能原文里] → 路由句写成第 8 行所要求的明确跳过理由，并写明本路由不写修复。WR-20 让这句优先于技能收尾。本次不改技能。
- [brainstorming 仍把 openspec-propose 和 to-tickets 写成后续] → `flow-08` 自己写明停在设计对话。`brainstorming` 的 `framework-rules.md` 第 21–24 行把下一项交给活动路由。不改那份技能。
- [Important 发现仍写 must be fixed] → 本次只关上 task list 这一条泄漏。不把「重要发现回到 tdd」加进 `flow-04` 或 `flow-09`。
- [test_successors_are_written_by_the_router 锁着 flow-02 的「回归测试和修复只由 tdd 写」] → 不改 `flow-02`，也不为了让新停点出现在这个测试里而把这半句抄进 `flow-01` 或 `flow-14`。
- [flow-08 的 purpose 仍留「不创建已批准的」] → purpose 与进入节一起换。

## Migration Plan

没有部署。回滚是：还原三个 flow 对象，再跑一次 `write_routers`，并还原 `framework-rules.md` 的 Minor 句。delta spec 留在本 change，直到另一次归档。本次不实施。
