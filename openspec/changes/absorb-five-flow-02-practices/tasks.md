## 1. flow-02 补上五条做法

- [x] 1.1 只读审计写出探索简报和卫生清单，结束仍停在只读审计
      做什么：读者走 `flow-02` 的只读审计时，能按熟悉度拿到简报，并在要看仓库卫生时只看到一份不改文件的清单。
      阻塞于：无
      覆盖：WR-06，Scenario 只读审计按熟悉度出简报，Scenario 只读切片只在已授权时切开，Scenario 只读审计停在简报，Scenario 卫生清单不改文件
      验收：`skill/flows/flow-02/SKILL.md` 的只读审计节同时含熟悉度分档、简报四项、只读切片条件、停点，以及卫生五项；纯文档两句保持原句；`openspec-explore`、`openspec-propose`、`to-tickets` 不被写成这一路径的下一项。
      模块与文件：框架分发库。改 `tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的「只读审计」`lines`，再用 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。断言加在 `tests/test_flow_routers.py`。
      接口：后续切片沿用同一 `flow-02` 对象和同一渲染结果。本切片不改 `mentions`，也不改其他 flow 对象。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_flow_02_readonly_audit_names_the_brief_and_hygiene_list`。改正文前失败，因为现文只有「不点名实现技能，不写文件。」

- [x] 1.2 `flow-02` 点名 `tdd` 时写出秒级检查和该轮局部快测，纪律只追加这一句
      做什么：写这一轮生产代码时，读者看到额外检查只跑编译和类型检查；这一轮写完后跑关联局部快测，失败就修并重跑同一条。切片自己的一次 RED 仍在。全量不在这一步用来声称验证通过。
      阻塞于：1.1
      覆盖：WR-24，Scenario 一轮写完后重跑同一条局部快测；WR-06 既有规格修复与新行为里点名 `tdd` 的句子；WR-20 的「`tdd` 进行中」
      验收：既有规格修复、新行为、下一项三处都有同一句检查节奏。`discipline.md` 第 52–68 行的 RED/GREEN 循环仍在，framework addition 追加限定「其他测试也要通过」的那一句。
      模块与文件：同一 `flow-02` 对象的「既有规格修复」「新行为」「下一项」，渲染 `skill/flows/flow-02/SKILL.md`。追加 `skill/matt-pocock/tdd/discipline.md` 已有的 framework addition。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.1 已经渲染过的 `flow-02` 正文。本切片交给 1.3 的是仍保留的「不往 tasks.md 追加切片」和「不创建 tasks.md」。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_flow_02_tdd_keeps_one_red_and_limits_the_round`。改正文前失败，因为现文没有「额外检查只跑编译、类型检查这类秒级检查」。

- [x] 1.3 `flow-02` 点名 `code-review` 时按风险分档核对范围，并亲自跑一次局部快测
      做什么：纯界面、文案、辅助脚本且没碰到高风险目录时，读者看到轻量核对，不要求独立只读上下文。高风险类别和已写明的禁改目录才需要独立只读上下文。没有已授权的只读子代理时，报告标明自审。评审核对活动 change 的三项，缺陷修复再看坏数据第一次产生的位置。审查人亲自跑一次相关局部快测，这次通过不能代替验证。发现仍只进交付报告。
      阻塞于：1.2
      覆盖：WR-23 的四个 Scenario；WR-22 Scenario 壳升级与差距评审不把风险问题交回实现；WR-20 的 `code-review` 与评审闭合两句
      验收：既有规格修复、新行为、下一项三处都有风险分档、三项核对、缺陷位置和一次局部快测。`framework-rules.md` 只追加这些分档句，不含「局部快测」，不删除「评审不改业务源码」。`flow-04` 与 `flow-09` 入口句不变，正文不出现「不往 tasks.md 追加切片」，也不出现这次局部快测。
      模块与文件：同一 `flow-02` 对象里点名 `code-review` 和 `verification-before-completion` 的句子，渲染 `skill/flows/flow-02/SKILL.md`。在 `skill/matt-pocock/code-review/framework-rules.md` 的 Closure rules 之后追加句子。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.2 留下的 `tdd` 句子。本切片不把「修改回到 tdd」写成 `flow-04` 与 `flow-09` 的义务。局部快测只出现在 `flow-02`。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_flow_02_review_uses_risk_tiers_and_one_local_check`。改正文前失败，因为现文没有「走轻量核对，不要求独立只读上下文」。

- [x] 1.4 进入收尾之前先写只读的分支与工作树事实
      做什么：验证已经通过、尚未点名 `finishing-a-development-branch` 时，读者先看到每条分支和工作树在哪、相对主干推没推、进没进主干、有没有未提交改动。没有独立提交或工作区不干净的，不标成可清理。推送、合并、删除和清理仍等用户当次选择。
      阻塞于：1.3
      覆盖：WR-24，Scenario 不干净的工作树不标成可清理；WR-20 Scenario 收尾前先写只读事实；WR-06 新行为里点名收尾之前的句子
      验收：新行为与下一项两处都有这组只读事实。卫生清单仍写「不执行 git worktree remove」。收尾技能原文不改。
      模块与文件：同一 `flow-02` 对象里点名 `finishing-a-development-branch` 之前的句子，渲染 `skill/flows/flow-02/SKILL.md`。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.3 留下的「局部快测通过不能代替这一步」。本切片不改 `skill/superpowers/finishing-a-development-branch/SKILL.md`。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_flow_02_states_branch_facts_before_finishing`。改正文前失败，因为现文是「验证通过后：下一项是 finishing-a-development-branch」，没有只读事实。

- [x] 1.5 阶段表第 6–9 行和流程正文写成同一条链
      做什么：阶段表的实现、评审、验证、收尾四行交接句，以及 `development-workflow.md` 的回归、评审、验证声称、进入收尾前的事实，与 `flow-02` 的新句子一致。三条切分线、人格标记、`FRAMEWORK_ENTRY`、第 80 行审计行保持不动。
      阻塞于：1.4
      覆盖：WR-21，Scenario 检查与评审的新句子进入同一条链
      验收：`AGENTS.md` 第 6–9 行交接句含秒级检查、风险分档、一次局部快测、验证声称和收尾前只读事实。`development-workflow.md` 第 8、10、11、12 节含同一组句子。人格标记仍在，托管段相对 HEAD 不变，第 91 行三条切分线仍在，第 80 行仍是「不修改文件」。
      模块与文件：`AGENTS.md` 阶段表第 6–9 行的交接句；`docs/framework/development-workflow.md` 第 8、10、11、12 节。断言加在 `tests/test_flow_routers.py`。
      接口：句子取自 1.2、1.3、1.4 已经写进 `flow-02` 的原文，不另起一套说法。不新增 `AGENTS.md` 小节。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_stage_table_and_workflow_match_the_five_practices`。改交接句前失败，因为第 6 行还没有「额外检查只跑编译、类型检查这类秒级检查」。

## 2. 验证与未授权的回执

- [x] 2.1 用整库命令复核这五条没有把其他路由或切分线带偏
      做什么：读者能看到整库测试、框架检查、活动 change 检查和本 change 的严格校验都通过；其他 flow 正文与改前一致；doctor 的既有退出码 5 被记录，不为此改工程。
      阻塞于：1.5
      覆盖：WR-01、WR-02、WR-05 的现有句子不被这次改写；WR-21 的托管段约束
      验收：`python3 -m unittest discover -s tests`、`python3 tools/check-framework`、`python3 tools/check-changes` 退出码为 0。`openspec validate absorb-five-flow-02-practices --type change --strict --no-interactive` 退出码为 0。`flow-01`、`flow-03` 至 `flow-15` 的 `SKILL.md` 与 HEAD 字节相同。指纹不一致时只跑 `python3 tools/update-manifest`。
      模块与文件：不新增行为。若指纹失败，只刷新 `framework-manifest.json` 的校验和。不改 `openspec/changes/bind-skill-endings-to-active-flow`。
      接口：依赖 1.1 至 1.5 的正文已经落在渲染结果和阶段表上。
      测试：上面四条命令，外加 `python3 tools/framework doctor --target . --summary`。doctor 退出码 5 记为分发库既有状态。

- [ ] 2.2 把本 change 的需求页写入初始化知识库并留下 `knowledge-receipt.json`
      做什么：规格同步之后，需求页和回执留在活动 change。
      阻塞于：2.1
      覆盖：WR-20 规格同步完成后的知识回执。本次没有单独授权，所以不执行。
      验收：活动 change 里出现可接受的 `knowledge-receipt.json`，并且主规格已同步。本次做不到。
      模块与文件：不写 `knowledge/project/`，不写 `knowledge-receipt.json`，不同步 `openspec/specs/`，不归档。
      接口：无。勾选全部任务会让 `check-changes` 把本 change 当成做完并要求回执。
      测试：不跑写入。未勾原因写在本条：没有回执授权。
