# 十二个决定各留一个下一步

**Goal:** 让 WR-36 的 12 个决定各自只剩活动 flow 已经写死的那一个下一步。同一决定在流程图、示例和后文里的指令副本进同一切片。

**Architecture:** 每个切片改完，读者在该决定点名的文件里只能检索到一个下一步。测试与正文在同一切片里完成：先写会失败的断言，确认失败是因为旧英文指令还在，再改正文。

**Tech Stack:** 本仓库的技能 Markdown 与 `python3 -m unittest`。

**Spec:** `openspec/changes/align-one-next-step-per-decision/specs/agent-workflow-routers/spec.md` 的 Requirement WR-36。

**Slices:** 本文件。不另写计划文档，不写 `.scratch`，不新建 `design.md`。

## 全局约束

这些约束算进每一个切片。行号按 2026-11-17 读到的文件；漂了就用读到的句子，不沿用旧约数。

- 只改该切片「允许改」列出的路径。`skill/flows/flow-01/SKILL.md`、`skill/flows/flow-02/SKILL.md`、`skill/flows/flow-08/SKILL.md`、`skill/flows/flow-14/SKILL.md`、`tools/framework_core/workflows/combinations.json`、`docs/framework/development-workflow.md` 不改。
- 不改 `AGENTS.md` 里 `<!-- AGENT_PERSONA_START -->` 与 `<!-- AGENT_PERSONA_END -->` 之间的任何字节，不删这两个标记。不改 `FRAMEWORK_ENTRY` 托管段。不改 `docs/framework/agent-persona.md`。
- 不改 `openspec/changes/bind-skill-endings-to-active-flow`、`openspec/changes/absorb-five-flow-02-practices`、`openspec/changes/bind-six-cause-and-claim-checks` 的任何文件，不勾它们的任务，不归档。
- 不把其余英文方法译成中文。命令、技能 ID、schema 字段、Requirement ID、`TASK_VERIFIED` 保持原文。
- 不写知识页，不归档本 change，不提交，不推送。`- [ ]` 保持未勾，直到该切片 `TASK_VERIFIED`。本文件不提供子代理执行或当轮执行的选择。
- 不碰旁边的 61.videohao-generator 仓库。
- `tests/test_flow_routers.py` 只有一个写入者。七个切片按下面的阻塞边串行。前面的切片只跑自己那一个测试方法；只有 1.7 跑整份 `tests/test_flow_routers.py`。
- 已有断言锁住、本计划不改的邻句包括：`skill/matt-pocock/tdd/discipline.md:18` 的 `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`；同文件「这些动作不算修复」整段；`skill/matt-pocock/diagnosing-bugs/discipline.md:24-25` 的 “A fix that makes the error message go away”；同文件「本技能仍不改产品代码。」；`skill/matt-pocock/code-review/framework-rules.md:81` 与 `:87-89`；`skill/superpowers/brainstorming/framework-rules.md` 全文。

## 1. 同一决定只剩一个下一步

- [x] 1.1 变绿只看刚写的测试和这一轮的局部快测
      做什么：读者读 `tdd` 的变绿句和完成清单时，这一轮只去看刚写的那条测试，以及这轮结束后的关联局部快测。全量、端到端和打包留到 `verification-before-completion`。决定 1 在 `:70`、`:88`、`:140` 的三处副本一起改完，这一条就能单独验证。
      阻塞于：无
      覆盖：WR-36，Scenario 变绿只看刚写的测试和局部快测；Scenario 路由测试锁改到新的唯一下一步（本切片只改 `test_flow_02_tdd_keeps_one_red_and_limits_the_round` 里锁旧英文的那一处，并让 “All tests pass” 与 “The test passes, the other tests still pass” 不再作为指令出现）；Scenario 活动 flow 与三个未归档 change 不动
      验收：`skill/matt-pocock/tdd/discipline.md` 同时满足下面三条。`:52-57` 的四行仍是原来的 `RED` / `VERIFY` / `GREEN` / `REPEAT`。`:71` 仍是 “If the test fails, fix the code, not the test.”。`:141` 仍是 “Output is clean — no errors, no warnings”。`:88` 前半的中文局部快测，以及「不授权把全量、端到端或打包扩进每一次变绿。」「切片自己的一次 RED 失败测试仍保留。」都还在。`:18` 与「这些动作不算修复」整段不动。
      模块与文件：框架分发库，单模块。允许改 `skill/matt-pocock/tdd/discipline.md` 的三处，以及 `tests/test_flow_routers.py` 里 `test_flow_02_tdd_keeps_one_red_and_limits_the_round` 现在约 `:289` 的那一条断言。不许改 `:52-57`、`:71`、`:141`、`:18`、`:73` 附近的「这些动作不算修复」，也不许改该测试约 `:284-288` 与 `:290-293`。
      接口：本切片留下的唯一下一步句子是「这一轮变绿只看刚写的那条测试，以及这轮结束后的关联局部快测；全量、端到端和打包留到 verification-before-completion」。1.4 会改同一份 `discipline.md` 的整理段，不得改回这三处。本切片不消费其他切片的句子。
      并行边界：技能正文与 1.4 共享 `discipline.md`，与其他切片不共享。测试文件按阻塞边串行。
      步骤：先只改测试。把约 `:289` 的 `self.assertIn('The test passes, the other tests still pass', discipline)` 换成下面四行，插在红绿四行断言之后、`:290` 的中文断言之前：

      ```python
      self.assertNotIn('The test passes, the other tests still pass', discipline)
      self.assertNotIn('All tests pass', discipline)
      self.assertIn('这一轮变绿只看刚写的那条测试，以及这轮结束后的关联局部快测', discipline)
      self.assertIn('全量、端到端和打包留到 verification-before-completion', discipline)
      ```

      然后只跑这一条。RED 必须是 `assertNotIn` 失败，因为旧英文仍在 `discipline.md`。失败若是导入错误、红绿四行找不到，或 `:290-293` 的中文断言失败，先修断言，不改正文。RED 确认后，把三处正文改成与测试相同的句子，句子里的技能 ID 不加反引号：

      - `:70` 的 “The test passes, the other tests still pass, and the output is clean.” 整句换成唯一下一步。下一行 `:71` 不动。
      - `:88` 删掉引号里的 “The test passes, the other tests still pass”。在「全量、端到端和打包不在这里用来声称验证通过。」之后写上同一句唯一下一步。其后的「不授权把全量、端到端或打包扩进每一次变绿。」留着，这样 `:293` 不用改。
      - `:140` 的 “All tests pass” 换成同一句唯一下一步。`:141` 不动。

      再跑同一条，预期通过。不跑整份文件，不提交，不勾选。
      检索：在 `skill/matt-pocock/tdd/discipline.md` 搜索 `The test passes, the other tests still pass` 与 `All tests pass`，零处。搜索「这一轮变绿只看刚写的那条测试」，命中变绿句、`:88` 与完成清单，且没有第二套「把全量或端到端拉进这一轮」的指令。红绿四行仍在 `:52-57`。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_flow_02_tdd_keeps_one_red_and_limits_the_round`。改正文前失败，失败原因是旧英文仍在。改正文后同一条通过。

- [x] 1.2 诊断出口停在根因，不修代码也不写知识页
      做什么：读者读完诊断技能，下一步只是把根因陈述出来。记下症状是为了后面核对根因能不能解释同一现象。本技能不应用修复，不把循环跑绿，根因前后都不改生产代码，也不存在「先试三次修复」。根因陈述点明失败落在内容、取用、验证、流程还是方法，本技能不因此新建概念页，也不改 flow 契约。决定 2、3、4 的全部指令副本在这一条里一起改完。
      阻塞于：1.1
      覆盖：WR-36，Scenario 诊断记下症状是为了核对根因；Scenario 诊断技能不试三次修复；Scenario 根因分层不新建概念页；Scenario 活动 flow 与三个未归档 change 不动
      验收：`skill/matt-pocock/diagnosing-bugs/SKILL.md` 约 `:76` 的目的从句变成「记下症状是为了后面核对根因能不能解释同一现象；本技能不因此应用修复，也不把循环跑绿。」Phase 5（约 `:114-122`）与 Phase 6（约 `:124-134`）原文仍在。`:61` 的 “green once fixed” 仍在。`:74` 的 “Wrong bug = wrong fix” 仍在。`discipline.md` 的铁律 “NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST”、`:24-25` 的症状修复定义、`:27` 与 `:38-39` 的中文、`:37-44` 的 `INFRA_ERROR`、`:90` 的「查完根因后不先写测试再修复」都仍在。五层的名字仍在，只出现在根因陈述里。`:153-155` 仍区分「哪个知识库」和「哪一层」，并写明记录不在本技能里落成新页或改契约。`:169` 之后的脱敏仍在。
      模块与文件：框架分发库，单模块。允许改 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 `:76` 目的从句；`skill/matt-pocock/diagnosing-bugs/discipline.md` 的 `:22`、`:62` 标题、`:68-81`、`:94`、`:105-106`、`:139-166`。允许在 `tests/test_flow_routers.py` 的 `RouterContractTests` 末尾新增一个方法。不许改 Phase 1–4 的其余条目、Phase 5、Phase 6、铁律代码块、环境故障段、`:90`。
      接口：不读取 1.1 的变绿句子。后续切片不改这两份诊断文件。本切片只追加测试方法，不改 1.1 改过的 `test_flow_02_tdd_keeps_one_red_and_limits_the_round`。
      并行边界：诊断技能文件没有别的切片写入。测试文件因 1.1 已写入而阻塞于 1.1。
      步骤：先在 `RouterContractTests` 末尾添加 `test_diagnosis_has_one_next_step`。方法读取这两份文件，按这个顺序断言：

      ```python
      self.assertNotIn('so later phases can verify the fix actually addresses it', skill)
      self.assertNotIn('If you have not completed Phase 1, you cannot propose fixes.', discipline)
      self.assertNotIn('When three fixes fail, question the architecture', discipline)
      self.assertNotIn('STOP after the third failed attempt.', discipline)
      self.assertNotIn('Do not start fix #4.', discipline)
      self.assertNotIn('One more fix attempt', discipline)
      self.assertNotIn('A fix that works is not the end of the investigation.', discipline)
      self.assertNotIn('The layer decides what you write down next', discipline)
      self.assertIn('记下症状是为了后面核对根因能不能解释同一现象', skill)
      self.assertIn('本技能不因此应用修复，也不把循环跑绿', skill)
      self.assertIn('不应用修复，也不写生产代码。', skill)
      self.assertIn('green once fixed', skill)
      self.assertIn('NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST', discipline)
      self.assertIn('INFRA_ERROR', discipline)
      self.assertIn('本技能在根因前后都不改生产代码', discipline)
      self.assertIn('不存在「先试三次修复」', discipline)
      self.assertIn('失败落在内容、取用、验证、流程还是方法', discipline)
      self.assertIn('本技能不因此新建概念页，也不改 flow 契约', discipline)
      self.assertIn('概念页和问题页仍走 flow-02 的知识步骤', discipline)
      self.assertIn('本技能仍不改产品代码。', discipline)
      ```

      只跑这个方法。RED 必须是前面的 `assertNotIn` 失败，因为那些旧英文仍在。然后改正文，再跑同一条，预期通过。

      `:76` 只换目的从句，清单项开头的 “You have captured the exact symptom (error message, wrong output, slow timing)” 留下。`discipline.md` 的 `:22` 改为「本技能在根因前后都不改生产代码，也不提出由本技能执行的修复。不存在「先试三次修复」。」`:62-81` 整段换成：本技能在根因前后都不改生产代码；不存在「先试三次修复」；三次失败若发生在 `tdd` 里，由 `tdd` 在活动 flow 把 `tdd` 写成下一项之后处理；`flow-01` 与 `flow-14` 连 `tdd` 都没有。`:94` 与 `:105-106` 里仍在说「再试一次修复」或 “don't fix again” 的格子和红旗，改成同一句，不再留下 “One more fix attempt”。`:139` 起的「修完还要归层、然后写 concept 页或改 `development-workflow.md`」换成：根因陈述点明失败落在内容、取用、验证、流程还是方法；本技能不因此新建概念页，也不改 flow 契约；概念页和问题页仍走 `flow-02` 的知识步骤。表里五层的名字和「失败看起来像什么」留下；“What to change” 与 “Where it lands” 不再把「加概念页」「改 flow 契约」写成下一步。`:157-166` 那五条「下一笔写什么」全部换成上面这一句。不提交，不勾选。
      检索：在这两份文件搜索 `so later phases can verify the fix actually addresses it`、`STOP after the third failed attempt`、`One more fix attempt`、`The layer decides what you write down next`、`A concept page`，零处。Phase 5 的「不应用修复，也不写生产代码。」仍只出现在 Phase 5，不被本切片改写。铁律与 `INFRA_ERROR` 仍在。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_diagnosis_has_one_next_step`。改正文前失败，失败原因是旧英文仍在。改正文后同一条通过。

- [x] 1.3 有界批准和子项目都不由本技能进入实现
      做什么：读者批准有界设计之后，看到的下一步是收尾指向活动 flow：要改行为、接口或验收就等 flow 进入规格，探针停在建议，本技能不按有界路径直接写实现。大需求拆开后，每个子项目只再做一轮设计对话，结束时指向当时活动 flow 的下一项；本技能不替它启动 spec、plan、implementation。决定 5 在清单、图和段尾的副本，与决定 6 的那一句，在这一条里一起改完。
      阻塞于：1.2
      覆盖：WR-36，Scenario 有界批准后不直接实现；Scenario 子项目不自启实现循环；Scenario 路由测试锁改到新的唯一下一步（本切片负责 “Implement via normal workflow” 不再作为指令出现）；Scenario 活动 flow 与三个未归档 change 不动
      验收：`skill/superpowers/brainstorming/SKILL.md` 的有界清单第 5 步、图里原先的 “Implement via normal workflow (no plan doc)”（约 `:115` 与 `:134`），以及约 `:150-152` 的 Bounded 句，都变成同一句：「批准之后收尾指向活动 flow；要改行为、接口或验收就等 flow 进入规格；探针停在建议；本技能不按有界路径直接写实现。」约 `:167` 的子项目句变成：「每个子项目单独做一轮设计对话，结束时指向当时活动 flow 的下一项；本技能不替它启动 spec、plan、implementation。flow-08 不创建 OpenSpec change。」架构路径里已经写着「收尾指向活动 flow 的下一项」的句子仍在，包括约 `:103`、`:149`、`:247`。约 `:85` 的探针仍停在建议。`framework-rules.md` 一个字节都不改。`flow-08` 不改。
      模块与文件：框架分发库，单模块。允许改 `skill/superpowers/brainstorming/SKILL.md` 的有界第 5 步（约 `:92`）、图节点与指向它的边（约 `:115`、`:134`）、Bounded 句（约 `:150-152`）、子项目句（约 `:167` 的最后一句）。允许在 `tests/test_flow_routers.py` 末尾新增一个方法。不许改 `skill/superpowers/brainstorming/framework-rules.md`，不许改约 `:85`、`:103`、`:149`、`:165-166`、`:168` 及之后「一次只问一个问题」，不许改 `skill/flows/flow-08/SKILL.md`。
      接口：不读取前两片的句子。图节点改名时，声明节点的那一行和所有指向它的边用同一个新标签，避免图里留下旧终点。本切片只追加测试方法。
      并行边界：本文件没有别的切片写入。测试文件阻塞于 1.2。
      步骤：先添加 `test_bounded_design_does_not_start_implementation`。方法读取 `skill/superpowers/brainstorming/SKILL.md` 与 `framework-rules.md`，按这个顺序断言：

      ```python
      self.assertNotIn('Implement via normal workflow', skill)
      self.assertNotIn('Each sub-project gets its own spec → plan → implementation cycle.', skill)
      self.assertIn('批准之后收尾指向活动 flow', skill)
      self.assertIn('要改行为、接口或验收就等 flow 进入规格', skill)
      self.assertIn('探针停在建议', skill)
      self.assertIn('本技能不按有界路径直接写实现', skill)
      self.assertIn('每个子项目单独做一轮设计对话', skill)
      self.assertIn('本技能不替它启动 spec、plan、implementation', skill)
      self.assertIn('flow-08 不创建 OpenSpec change', skill)
      self.assertIn('收尾指向活动 flow 的下一项', skill)
      self.assertIn('下一项只由活动中的 flow 正文宣布。', rules)
      self.assertIn('不按有界路径直接写实现。', rules)
      ```

      `rules` 那些句子是现成的，用来证明本切片没有改 `framework-rules.md`。只跑这个方法。RED 必须是 `assertNotIn('Implement via normal workflow', skill)` 失败，因为旧英文仍在。然后改 `SKILL.md` 的四处副本，再跑同一条，预期通过。图里两处节点标签和约 `:134` 的边目标一起换，旧字符串不留在边的标签上。约 `:167` 只换最后一句 “Each sub-project gets its own spec → plan → implementation cycle.”，前面「先帮用户把独立片段拆开」留下。不提交，不勾选。
      检索：在 `skill/superpowers/brainstorming/SKILL.md` 搜索 `Implement via normal workflow` 与 `spec → plan → implementation`，零处。搜索「不按有界路径直接写实现」，有界清单第 5 步、图终点和 Bounded 句都命中。`framework-rules.md` 与改前一致。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_bounded_design_does_not_start_implementation`。改正文前失败，失败原因是 “Implement via normal workflow” 仍在。改正文后同一条通过。

- [x] 1.4 当前任务里的窄整理仍在实现步做完
      做什么：读者在红到绿的整理步看到一个下一步：不夹带设计级重构；当前任务里的重复、命名和辅助函数就在这一步做完；改 seam、模块职责或接口放到评审里讨论；真要改源码，回到 `tdd`。决定 7 在 `SKILL.md:38` 和 `discipline.md:90-93` 的两处副本一起改完，不再用「两句都对」并立。
      阻塞于：1.3
      覆盖：WR-36，Scenario 窄整理留在实现步；Scenario 活动 flow 与三个未归档 change 不动
      验收：两处都写成「红到绿不夹带设计级重构；当前任务里的重复、命名和辅助函数仍在本技能的整理步做完；改 seam、模块职责或接口放到评审里讨论；真要改源码，回到 tdd。」`discipline.md:80-86` 的范围内、范围外清单原文仍在。1.1 留下的变绿句、`:88` 与完成清单仍在。“Both are true” 与 “Refactoring is not part of the loop.” 不再作为指令出现。`:18` 的 `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST` 仍在。
      模块与文件：框架分发库，单模块。允许改 `skill/matt-pocock/tdd/SKILL.md` 的 `:38`，以及 `skill/matt-pocock/tdd/discipline.md` 的 `:90-93`。允许在 `tests/test_flow_routers.py` 末尾新增一个方法。不许改 `discipline.md:80-86`，不许改 1.1 已写的 `:70`、`:88`、`:140`，不许改 `:18` 和「这些动作不算修复」。
      接口：消费 1.1 留下的三处变绿句子，本切片不改它们。`:80-86` 已经写明的范围是本切片要对齐的对象，不是要重写的对象。本切片只追加测试方法。
      并行边界：与 1.1 共享 `discipline.md`，所以排在 1.1 之后；测试文件阻塞于 1.3，从而也排在 1.1 之后。
      步骤：先添加 `test_narrow_cleanup_stays_with_implementation`。方法读取两份 tdd 文件，按这个顺序断言：

      ```python
      self.assertNotIn('Refactoring is not part of the loop.', skill)
      self.assertNotIn('Both are true here', discipline)
      self.assertIn('红到绿不夹带设计级重构', skill)
      self.assertIn('当前任务里的重复、命名和辅助函数仍在本技能的整理步做完', skill)
      self.assertIn('改 seam、模块职责或接口放到评审里讨论', skill)
      self.assertIn('真要改源码，回到 tdd', skill)
      self.assertIn('红到绿不夹带设计级重构', discipline)
      self.assertIn('In scope here:', discipline)
      self.assertIn('Out of scope here:', discipline)
      self.assertIn('这一轮变绿只看刚写的那条测试，以及这轮结束后的关联局部快测', discipline)
      self.assertIn('NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST', discipline)
      ```

      只跑这个方法。RED 必须是 `assertNotIn` 失败，因为 “Both are true here” 和 “Refactoring is not part of the loop.” 仍在。然后把 `:38` 与 `:90-93` 改成验收里的那一句。`:90-93` 不再写 “SKILL.md says refactoring is not part of the red-to-green loop”。再跑同一条，预期通过。不提交，不勾选。
      检索：在这两份文件搜索 `Both are true` 与 `Refactoring is not part of the loop`，零处。搜索「窄整理」对应的那句唯一下一步，`SKILL.md:38` 与 `discipline.md` 整理段都命中，且 `:80-86` 的范围内清单还在。变绿句仍只有 1.1 的那一个下一步。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_narrow_cleanup_stays_with_implementation`。改正文前失败，失败原因是旧英文仍在。改正文后同一条通过。

- [x] 1.5 规格就是活动 change，按风险决定是否派只读上下文
      做什么：读者做 code-review 时，规格就是活动 OpenSpec change；找不到就在报告里写无可用规格。低风险不派独立上下文；高风险只在已有授权的只读子代理时派；没有时报告标明自审。评审不改业务源码。决定 8 与决定 9 同在 `SKILL.md` 的描述行里，所以放在同一条里改完。气味清单的 “how to fix” 不改。
      阻塞于：1.4
      覆盖：WR-36，Scenario 规格就是活动 change；Scenario 低风险不派两个子代理；Scenario 路由测试锁改到新的唯一下一步（本切片负责 `code-review/SKILL.md` 里的 `setup-matt-pocock-skills` 与 “Issue both sub-agent calls”）；Scenario 活动 flow 与三个未归档 change 不动
      验收：`SKILL.md` 的描述行约 `:3`、`:13`、`:27-32` 把规格写成活动 OpenSpec change，找不到就写无可用规格，不再要求运行 `setup-matt-pocock-skills`，也不再把 `docs/`、`specs/`、`.scratch/` 写成查找顺序。`:9-10` 两轴的问题定义原文仍在。`:34-56` 气味基线和气味清单原文仍在，包括每条 “how to fix”。`:3`、`:11`、`:23`、`:58-60` 不再命令每次都派两个并行子代理。`:62-74` 的 brief 内容留下，但只在已经决定派授权只读子代理时使用；低风险不发这些 brief。`framework-rules.md` 只改约 `:55-56` 那一句并行子代理，改为同一条派发规则。`:7-40`、`:81`、`:87-89` 原文仍在。
      模块与文件：框架分发库，单模块。允许改 `skill/matt-pocock/code-review/SKILL.md` 的 `:3`、`:11`、`:13`、`:23`、`:27-32`、`:58-60`，以及必要时 `:62` 之前补一句「低风险不派这些 brief」。允许改 `skill/matt-pocock/code-review/framework-rules.md` 的 `:55-56` 第一句。允许在 `tests/test_flow_routers.py` 末尾新增一个方法。不许改 `:9-10`、`:34-56`、`framework-rules.md:7-40`、`:81`、`:87-89`。
      接口：不读取前面切片的句子。`:3` 一行里同时有决定 8 的 “originating issue/spec” 和决定 9 的 “Runs both reviews in parallel sub-agents”，这一行一次改完。本切片只追加测试方法。`framework-rules.md:7` 里已有的 “do not ask the user to run a setup skill” 留下，测试不要对整个 `framework-rules.md` 做 `setup-matt-pocock-skills` 的 `assertNotIn`。
      并行边界：这两份评审文件没有别的切片写入。测试文件阻塞于 1.4。
      步骤：先添加 `test_review_uses_the_active_change_and_conditional_context`。方法读取 `SKILL.md` 与 `framework-rules.md`，按这个顺序断言：

      ```python
      self.assertNotIn('setup-matt-pocock-skills', skill)
      self.assertNotIn('Issue both sub-agent calls', skill)
      self.assertNotIn('A spec file under', skill)
      self.assertNotIn('runs Standards and Spec as parallel sub-agents', rules)
      self.assertIn('规格就是活动 OpenSpec change', skill)
      self.assertIn('不把 docs/、specs/ 或 .scratch/ 写成规格来源', skill)
      self.assertIn('无可用规格', skill)
      self.assertIn('低风险不派独立上下文', skill)
      self.assertIn('高风险只在已有授权的只读子代理时派', skill)
      self.assertIn('没有时报告标明自审', skill)
      self.assertIn('评审不改业务源码', skill)
      self.assertIn('does the code conform to this repo', skill)
      self.assertIn('how to fix', skill)
      self.assertIn('低风险不派独立上下文', rules)
      self.assertIn('评审不改业务源码，不往 tasks.md 追加切片。发现写入交付报告。', rules)
      self.assertIn('走轻量核对，不要求独立只读上下文。', rules)
      self.assertIn('没有已授权的只读子代理时，报告标明自审。', rules)
      ```

      `assertNotIn('setup-matt-pocock-skills', skill)` 只针对 `SKILL.md`。`framework-rules.md:7` 里已有的禁止句要留下，不要对那份文件做同样的 `assertNotIn`。只跑这个方法。RED 必须是 `assertNotIn('Issue both sub-agent calls', skill)` 或 `assertNotIn('setup-matt-pocock-skills', skill)` 失败，因为旧英文仍在 `SKILL.md`。然后改正文，再跑同一条，预期通过。`:23` 仍先确认 `git rev-parse` 和 diff 非空，只是不再把失败地点写成「否则就进两个并行子代理」。不提交，不勾选。
      检索：在 `skill/matt-pocock/code-review/SKILL.md` 搜索 `setup-matt-pocock-skills`、`Issue both sub-agent calls`、`A spec file under`，零处。搜索「规格就是活动 OpenSpec change」与「低风险不派独立上下文」，描述行、查找节和派发节都命中。「不把 docs/、specs/ 或 .scratch/ 写成规格来源」可以留下，它是禁止，不是查找顺序。`framework-rules.md` 搜索 `runs Standards and Spec as parallel sub-agents`，零处；`:81` 与 `:87-89` 仍在。气味清单的 “how to fix” 仍在。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_review_uses_the_active_change_and_conditional_context`。改正文前失败，失败原因是旧英文仍在。改正文后同一条通过。

- [x] 1.6 被委派的实现者不提交，评审用 code-review
      做什么：读者读 `subagent-driven-development` 时只看到一个下一步。写进 `SKILL.md` 的句子是：「被委派者仍用 tdd，实现者不提交；不派上游任务评审，评审用 code-review；本技能结束时不自己提示下一个技能。提交仍等用户当次选择。」这句里面不要出现 `finishing-a-development-branch` 或 `task-reviewer-prompt`。决定 10 在图、正文和文末示例里的副本一起改完。`task-reviewer-prompt.md` 文件留在磁盘上，`SKILL.md` 不再提到它。
      阻塞于：1.5
      覆盖：WR-36，Scenario 实现者不提交也不派任务评审；Scenario 路由测试锁改到新的唯一下一步（本切片负责 `task-reviewer-prompt` 不再出现在这份 `SKILL.md`）；Scenario 活动 flow 与三个未归档 change 不动
      验收：图中约 `:70`、`:71`、`:91`、`:96-99`、`:120`，正文约 `:266`、`:290`、`:324`、`:345`、`:352`、`:469`、`:487`，示例约 `:525`、`:527`、`:540`、`:542`、`:567`，都换成「做什么」里那句落盘句子。节点改名后，指向旧节点的边一起改。这些位置改成删掉旧指令，不要改成「不要调用 finishing-a-development-branch」或「不要打开 task-reviewer-prompt」，否则整份 `SKILL.md` 仍能检索到这两串字符。约 `:55` 的 “Fresh subagent per task” 仍在。约 `:494` 的 “Controller fixes pollute your context” 仍在。`framework-rules.md` 不改，所以其中 “Do not dispatch the upstream `task-reviewer-prompt.md`.” 与 “The implementer does not commit.” 仍在。`task-reviewer-prompt.md` 文件仍在，内容不改。
      模块与文件：框架分发库，单模块。允许改 `skill/superpowers/subagent-driven-development/SKILL.md` 上列各处。允许在 `tests/test_flow_routers.py` 末尾新增一个方法。不许改同目录 `framework-rules.md`，不许改 `task-reviewer-prompt.md`，不许改约 `:55` 与约 `:494`。本技能不另写一套委派时机。
      接口：不读取前面切片的句子。同目录 `framework-rules.md:46-47` 已经是 “implements, tests, reports, self-reviews”，本切片不改那份文件，只把 `SKILL.md` 里仍写着 commits 的指令改成与它同一句。本切片只追加测试方法。
      并行边界：这份 `SKILL.md` 没有别的切片写入。测试文件阻塞于 1.5。
      步骤：先添加 `test_delegated_implementer_does_not_commit`。方法读取 `SKILL.md` 与 `framework-rules.md`，并确认 `task-reviewer-prompt.md` 仍能读到。按这个顺序断言：

      ```python
      self.assertNotIn('task-reviewer-prompt', skill)
      self.assertNotIn('finishing-a-development-branch', skill)
      self.assertNotIn('implements, tests, commits, self-reviews', skill)
      self.assertIn('被委派者仍用 tdd', skill)
      self.assertIn('实现者不提交', skill)
      self.assertIn('评审用 code-review', skill)
      self.assertIn('本技能结束时不自己提示下一个技能', skill)
      self.assertIn('提交仍等用户当次选择', skill)
      self.assertIn('Fresh subagent per task', skill)
      self.assertIn('Controller fixes pollute your context', skill)
      self.assertIn('The implementer does not commit.', rules)
      self.assertIn('Do not dispatch the upstream `task-reviewer-prompt.md`.', rules)
      self.assertTrue((ROOT / 'skill/superpowers/subagent-driven-development/task-reviewer-prompt.md').is_file())
      ```

      测试不要对 `framework-rules.md` 做 `task-reviewer-prompt` 的 `assertNotIn`，那份文件里的禁止句要留下。只跑这个方法。RED 必须是 `assertNotIn('task-reviewer-prompt', skill)` 失败，因为 `SKILL.md` 仍把它写成要执行的指令。然后改 `SKILL.md` 的全部点名副本，再跑同一条，预期通过。示例里的 “Committed” 改成实现者报告改动和测试结果、不提交。不提交，不勾选。
      检索：在 `skill/superpowers/subagent-driven-development/SKILL.md` 搜索 `task-reviewer-prompt`、`finishing-a-development-branch`、`implements, tests, commits`，零处。搜索「实现者不提交」与「评审用 code-review」，图、正文和示例都命中。`framework-rules.md` 与 `task-reviewer-prompt.md` 的字节与改前一致。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_delegated_implementer_does_not_commit`。改正文前失败，失败原因是 `task-reviewer-prompt` 仍在 `SKILL.md`。改正文后同一条通过。

- [x] 1.7 切片只写入当前 change，批准后不在这里选择执行方式
      做什么：读者用 to-tickets 时，切片正文只写入当前 change 的 `tasks.md`。不写 `.scratch`，不要求安装命令，不发到外部 tracker。计划批准之后，不再提供子代理执行或当轮执行的选择，也不在这里把 `- [ ]` 改成 `- [x]`。勾选仍等该切片 `TASK_VERIFIED`。下一项由活动 flow 宣布。决定 11 与决定 12 在这一条里一起改完，改完用整份路由测试确认前六条切片的断言仍在。
      阻塞于：1.6
      覆盖：WR-36，Scenario 切片只写入当前 change；Scenario Execution handoff 不选择执行方式；Scenario 路由测试锁改到新的唯一下一步（本切片负责 `to-tickets/SKILL.md` 里的 `setup-matt-pocock-skills`，并在整份测试通过时让该 Scenario 的 THEN 一起成立）；Scenario 活动 flow 与三个未归档 change 不动
      验收：`skill/matt-pocock/to-tickets/SKILL.md` 的描述行约 `:3`、`:10`、`:57-62` 都是「切片正文只写入当前 change 的 tasks.md；不写 .scratch，不要求安装命令，不发到外部 tracker。」约 `:28-39` 的垂直切片、阻塞边和 expand–contract 原文仍在。`:69` 之后的模板若还把票发到 `.scratch` 或外部 tracker，改成字段形状可以参考、落点只有当前 change 的 `tasks.md`；模板若本来就只描述字段，则留下。`plan-format.md:173-182` 换成：「不再提供子代理执行或当轮执行的选择，也不在这里把 `- [ ]` 改成 `- [x]`。勾选仍等该切片 TASK_VERIFIED。下一项由活动 flow 宣布。」`:19-21`、`:39` 起的切片字段、`:155-169` 的自检原文仍在。`tests/test_flow_routers.py:67`、`:713`、`:726` 仍锁着 flow 正文里的「Execution handoff 不是下一项」，那些断言和 flow 正文都不改。
      模块与文件：框架分发库，单模块。允许改 `skill/matt-pocock/to-tickets/SKILL.md` 的 `:3`、`:10`、`:57-62`，以及 `:69` 之后仍在指示外发的模板句子。允许改 `skill/matt-pocock/to-tickets/plan-format.md` 的 `:173-182`。允许在 `tests/test_flow_routers.py` 末尾新增一个方法。不许改 `:28-39`、`plan-format.md:19-21`、`:39` 起的字段表、`:155-169`。不许改 `skill/flows/` 与 `docs/framework/development-workflow.md`。
      接口：消费 1.1 到 1.6 已经加进 `tests/test_flow_routers.py` 的断言。本切片不改那些方法，也不改它们锁住的技能句子。整份测试通过，才表示路由测试锁的 THEN 全部成立。
      并行边界：to-tickets 的两个文件没有别的切片写入。测试文件阻塞于 1.6。这一条不能与前面的切片并行，否则整份测试还看不到它们的断言。
      步骤：先添加 `test_slices_land_in_tasks_and_handoff_does_not_choose`。方法读取这两份文件，按这个顺序断言：

      ```python
      self.assertNotIn('setup-matt-pocock-skills', skill)
      self.assertNotIn('.scratch/<feature-slug>', skill)
      self.assertNotIn('offer the execution choice', plan)
      self.assertNotIn('Subagent-driven (recommended)', plan)
      self.assertNotIn('Inline execution', plan)
      self.assertIn('切片正文只写入当前 change 的 tasks.md', skill)
      self.assertIn('不写 .scratch，不要求安装命令，不发到外部 tracker', skill)
      self.assertIn('Each slice cuts a narrow but COMPLETE path', skill)
      self.assertIn('不再提供子代理执行或当轮执行的选择', plan)
      self.assertIn('勾选仍等该切片 TASK_VERIFIED', plan)
      self.assertIn('下一项由活动 flow 宣布', plan)
      self.assertIn("Write them into the current OpenSpec", plan)
      self.assertIn('Spec coverage', plan)
      ```

      只跑这个方法。RED 必须是 `assertNotIn('setup-matt-pocock-skills', skill)` 或 `assertNotIn('offer the execution choice', plan)` 失败，因为旧英文仍在。然后改这两处正文，再跑同一条，预期通过。这条通过之后，才跑整份文件：

      `python3 -m unittest tests.test_flow_routers`

      预期整份通过。其中 `:67`、`:713`、`:726` 继续锁定 flow 里的「Execution handoff 不是下一项」。整份若失败在前面切片的断言上，回到那一条切片修，不在本切片改别的决定的句子。不提交，不勾选。
      检索：在 `skill/matt-pocock/to-tickets/SKILL.md` 搜索 `setup-matt-pocock-skills` 与 `.scratch`，零处。搜索「当前 change 的 tasks.md」，描述行和发布节都命中，垂直切片规则仍在。在 `plan-format.md` 搜索 `offer the execution choice`、`Subagent-driven (recommended)`、`Inline execution`，零处。搜索「下一项由活动 flow 宣布」，只命中 Execution handoff 那一节。`:19-21` 与自检仍在。
      测试：先 `python3 -m unittest tests.test_flow_routers.RouterContractTests.test_slices_land_in_tasks_and_handoff_does_not_choose`。改正文前失败，失败原因是旧英文仍在。改正文后同一条通过。然后 `python3 -m unittest tests.test_flow_routers`，预期整份通过。

## 规格覆盖

| Scenario | 切片 |
|---|---|
| 变绿只看刚写的测试和局部快测 | 1.1 |
| 诊断记下症状是为了核对根因 | 1.2 |
| 诊断技能不试三次修复 | 1.2 |
| 根因分层不新建概念页 | 1.2 |
| 有界批准后不直接实现 | 1.3 |
| 子项目不自启实现循环 | 1.3 |
| 窄整理留在实现步 | 1.4 |
| 规格就是活动 change | 1.5 |
| 低风险不派两个子代理 | 1.5 |
| 实现者不提交也不派任务评审 | 1.6 |
| 切片只写入当前 change | 1.7 |
| Execution handoff 不选择执行方式 | 1.7 |
| 路由测试锁改到新的唯一下一步 | 1.1 改现有方法；1.3、1.5、1.6、1.7 各自锁自己的旧字符串；1.7 的整份测试通过时 THEN 一起成立 |
| 活动 flow 与三个未归档 change 不动 | 1.1 至 1.7 的不许改路径；1.7 的整份测试不改 flow 断言 |

阻塞边只因为 `tests/test_flow_routers.py` 单写入者，以及 1.4 与 1.1 共享 `discipline.md`。技能正文除这两处外互不依赖，但测试文件不能并行写。没有未覆盖的 Scenario。

## 2. 知识回执

- [ ] 2.1 回执与主规格同步留到知识步骤，本次不写
      做什么：回执与主规格同步留到知识步骤，本次不写。
      阻塞于：1.7
      覆盖：无。本次不写 `knowledge-receipt.json`，不同步主规格，不归档。
      验收：本条保持未勾。不把回执或主规格同步写成已经完成。
      模块与文件：不改文件。
      接口：无。勾选全部任务会让 `check-changes` 把本 change 当成做完并要求回执。
      测试：不跑。
