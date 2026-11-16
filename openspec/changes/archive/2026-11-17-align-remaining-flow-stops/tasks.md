## 1. 三处停点

接缝：公开正文是 `render_skill` 写出的路由，以及 `code-review` 改编层里发现的记录位置。测试从这两处读句子，不探渲染函数内部。接缝抓住停点被写丢、写成下一项、或和清单漂移；不证明一次真实会话会停住。用户已指定用 `tests/test_flow_routers.py` 锁这三处停点和改编层新句。

同一份 `combinations.json` 只有一个写入者，1.1 到 1.3 顺序做。1.4 改另一份文件。不另建计划文档，不把 Execution handoff 当成下一项。

- [x] 1.1 初始化失败停在根因，本路由不写修复
      做什么：用户走工程初始化并遇到失败时，路由仍点名诊断技能，但停在红信号、最小复现和根因；不写回归测试，不应用修复，不把 `tdd` 写成下一项。设计未批准时仍停止，不进入 `flow-02`。
      阻塞于：无
      覆盖：WR-07 初始化失败停在根因；WR-07 初始化设计未批准时不进入开发路由；WR-20 初始化失败没有修复下一项
      验收：`flow-01` 正文含「只停在红信号、最小复现和根因。diagnosing-bugs 的 Phase 5 不在本路由应用修复：不把最小复现写成回归测试，也不应用修复。本路由不写修复，也不把 tdd 写成下一项。」；仍含先读 `BOOTSTRAP.md` 与 `project-bootstrap`，以及「设计未批准时停止，不进入 flow-02。」「设计未批准时没有下一项技能。」；不再含「失败完成后，下一项是 diagnosing-bugs 与 discipline.md。」；不含「回归测试和修复只由 tdd 写」。`mentions` 仍是 `BOOTSTRAP.md`、`diagnosing-bugs`、`discipline.md`、`project-bootstrap`。正文与 `render_skill` 一致。
      模块与文件：路由清单 `tools/framework_core/workflows/combinations.json` 的 `flow-01` 对象；渲染产物 `skill/flows/flow-01/SKILL.md`；测试 `tests/test_flow_routers.py`
      接口：本切片交出上述停点原句。1.2 复用同一句，不改 `flow-01`。
      测试：`test_flow_01_failure_stops_before_a_fix` 先失败于缺少该停点，渲染后通过。

- [x] 1.2 壳验证失败使用与初始化相同的停点
      做什么：公共壳验证的失败模式停在同一处，不写修复，不把 `tdd`、`writing-skills` 或 `writing-for-agents` 写成下一项。改技能与改 Agent 所读文档的点名，以及三种模式各自结束，保持原句。
      阻塞于：1.1
      覆盖：WR-07 壳验证失败使用同一停点；WR-20 壳验证的三种模式不互相交接
      验收：`flow-14` 失败句含与 1.1 相同的停点原句；仍含改技能点名 `writing-skills`、改 Agent 所读文档点名 `writing-for-agents`、以及「三种模式各自结束，不把另一种模式写为下一项。」；不含「回归测试和修复只由 tdd 写」。`mentions` 仍是 `diagnosing-bugs`、`discipline.md`、`writing-for-agents`、`writing-skills`。purpose 原句不变。
      模块与文件：同一清单的 `flow-14` 对象；`skill/flows/flow-14/SKILL.md`；`tests/test_flow_routers.py`
      接口：消费 1.1 的停点原句。不改 `flow-01`。
      测试：`test_flow_14_failure_uses_the_same_stop` 先失败于失败句没有该停点，渲染后通过。

- [x] 1.3 设计交接停在设计对话，不创建 OpenSpec change
      做什么：设计交接仍先做观察交接，再走架构路径，然后停在设计对话。不把 `openspec-propose` 或 `to-tickets` 当作下一项，也不创建 OpenSpec change，包括未批准的。
      阻塞于：1.2
      覆盖：WR-07 设计交接停在设计对话；WR-20 设计交接不进入规格
      验收：`flow-08` 仍先点名 `reverse-engineer` 的交接部分，交接后仍进入 `brainstorming` 的架构路径；正文含「停在设计对话」「不把 openspec-propose 或 to-tickets 当作下一项」「不创建 OpenSpec change，包括未批准的 change。」；purpose 与进入节都不再含「不创建已批准的 OpenSpec change」，改为「不创建 OpenSpec change」。`mentions` 仍是 `brainstorming`、`framework-rules.md`、`reverse-engineer`。
      模块与文件：同一清单的 `flow-08` 对象；`skill/flows/flow-08/SKILL.md`；`tests/test_flow_routers.py`
      接口：不依赖 1.1 的停点原句。三个对象的 `mentions` 都不增加技能名。
      测试：`test_flow_08_stops_in_the_design_conversation` 先失败于仍写「不创建已批准的 OpenSpec change」且没有设计对话停点，渲染后通过。

- [x] 1.4 评审发现只写入交付报告
      做什么：`code-review` 的本地改编层不再允许把发现记进 change 的 task list。`flow-04` 与 `flow-09` 靠读这句生效，它们的入口和技能点名不变。
      阻塞于：1.3
      覆盖：WR-22 壳升级的发现不追加切片；WR-22 差距评审的发现不追加切片；WR-22 找不到 change 时仍无可用规格；WR-22 改编层不再提供任务清单记录位置
      验收：`skill/matt-pocock/code-review/framework-rules.md` 原 Minor 句改为「发现只写入交付报告，不往 tasks.md 追加切片。」；该文件不再含 “change's task list”；Important 必须先修的句子、以及阅读已有 `tasks.md` 的句子保持原句。上游 `SKILL.md` 不改。`flow-04` 仍是评审受管 diff，人工改动冲突时停止。`flow-09` 仍在规格已批准且实现之后点名评审，找不到 change 时报告无可用规格。这两份路由正文不新增「不往 tasks.md 追加切片」。
      模块与文件：`skill/matt-pocock/code-review/framework-rules.md`；`tests/test_flow_routers.py`。不改 `flow-04`、`flow-09` 对象。
      接口：不消费前三片的路由句子。后一片只复跑，不改这句。
      测试：`test_review_findings_are_not_appended_to_tasks` 先失败于 Minor 句仍允许记入 task list，改句后通过。

- [x] 1.5 整库验证，本条保持未勾选
      做什么：确认前四片一起通过既有路由合同、全量单测、分发检查、变更完成检查和 change 严格校验。人格标记仍在。分发库 doctor 维持既有退出码。
      阻塞于：1.1、1.2、1.3、1.4
      覆盖：WR-20 诊断完成后不写修复（仍只锁 `flow-02` 的「回归测试和修复只由 tdd 写」）；WR-07 里未改的触发词与停止句由既有测试回归
      验收：`tests/test_flow_routers.py` 通过，且 `test_successors_are_written_by_the_router` 与 `test_persona_block_matches_source_and_status_dictionary_stays_put` 未被改弱。`python3 -m unittest discover -s tests`、`python3 tools/check-framework`、`python3 tools/check-changes`、`openspec validate align-remaining-flow-stops --type change --strict --no-interactive` 退出码为 0。doctor 退出码 5 不为此改工程。
      模块与文件：不新增产品代码。指纹不一致时只跑 `python3 tools/update-manifest`，不手改哈希。
      接口：消费前四片的正文。不改 `flow-02` 到 `flow-07`、`flow-09` 到 `flow-13`、`flow-15`，不改 `AGENTS.md`、阶段表、人格来源、诊断技能、brainstorming、宿主安装器、roster、catalog、from-zero-to-one。
      测试：上列命令。本条验证通过后仍保持未勾选：全部勾完会让完成检查要求知识回执。本次不写 `knowledge-receipt.json`，不同步主规格，不归档。
