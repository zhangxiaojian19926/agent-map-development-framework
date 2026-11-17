## 1. 六条结论约束

- [x] 1.1 根因陈述解释为什么以前不出现
      做什么：读者读完诊断的根因陈述，能看到因果链和代码位置，也能看到为什么以前不出现、为什么只在某些输入或环境下出现。查过历史就有引入提交的短哈希；没查就写未验证，不凭提交说明下结论。仍不写回归测试，不改生产代码。
      阻塞于：无
      覆盖：WR-30，Scenario 根因陈述解释以前不出现
      验收：`diagnosing-bugs` 的 Phase 5 与 `discipline.md` 都含上述句子。已有的「不应用修复，也不写生产代码」和「回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做」保持原句。
      模块与文件：框架分发库。`skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 Phase 5，`skill/matt-pocock/diagnosing-bugs/discipline.md` 的证据绑定旁。断言加在 `tests/test_flow_routers.py`。
      接口：本切片不改生产代码，不写回归测试。后续切片沿用同一份 Phase 5 停点。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_root_cause_explains_why_it_was_absent`。改正文前失败，因为现文没有「为什么以前不出现」。

- [x] 1.2 提交多时把二分放进临时 worktree
      做什么：提交多、范围看不出时，读者在临时目录里用 `git worktree add --detach` 跑 `git bisect run`。未提交的复现材料用新文件名拷进去。结束只移除这个临时目录。当前分支、工作区和暂存区不动。构建失败用退出码 125 跳过。要装依赖或联网时先问。卫生清单和进入 finishing 前的只读事实仍不执行 `git worktree remove`。
      阻塞于：1.1
      覆盖：WR-31，Scenario 二分不碰当前工作区
      验收：`diagnosing-bugs` 的 `SKILL.md` 与 `discipline.md` 都含上述二分句。`flow-02` 卫生清单仍含「不执行 git worktree remove」。进入 finishing 前的只读事实含「仍不执行 git worktree remove」。
      模块与文件：同一诊断技能的 `SKILL.md` 与 `discipline.md`。`flow-02` 的卫生句已在，不改卫生清单去执行移除。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.1 留下的「不改生产代码」。本切片不把 `git worktree remove` 写进卫生清单或收尾前的清理动作。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_bisect_runs_in_a_temporary_worktree`。改正文前失败，因为现文没有「git worktree add --detach」。

- [x] 1.3 说不清来源的兜底不算修好
      做什么：写修复的人看到一份否定清单：说不清坏值从哪来，就在报错处加空值判断、try/catch、重试、sleep 或加大超时；只对报告的那一个输入写特判；放宽、跳过或删除失败测试；一次改好几处却说不清是哪一处起作用。这些都不算修好。兜底单独写明。入口校验如果就是坏数据第一次产生的地方，空值判断仍然算修复。
      阻塞于：1.2
      覆盖：WR-32，Scenario 兜底和特判不算根因修复
      验收：`tdd` 的 `discipline.md` 在写修复的判定里有这份清单。`code-review` 的 `framework-rules.md` 在「缺陷修复再核对改动是否在坏数据第一次产生的位置」旁边有同一份清单。`diagnosing-bugs` 的 `discipline.md` 只追加清单，英文原句「A fix that makes the error message go away without explaining why the error happened is not a fix」保持不变，并仍写明不改产品代码。
      模块与文件：`skill/matt-pocock/tdd/discipline.md`，`skill/matt-pocock/code-review/framework-rules.md`，`skill/matt-pocock/diagnosing-bugs/discipline.md`。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.2 已经写过的诊断纪律。本切片不把评审改回改业务源码，也不改 `flow-04` 与 `flow-09`。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_symptom_patches_do_not_count_as_the_fix`。改正文前失败，因为现文没有「这些动作不算修复」。

- [x] 1.4 写成已经有的路径先在仓库里核对
      做什么：`openspec-propose` 与 `openspec-update-change` 写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，落盘前在仓库里核对。对不上就改这句或标成待确认。将要新建的文件不要求事先存在。不另写 `docs/` 规格，不另建任务契约。核对通过不等于 Requirement 已被认可。
      阻塞于：无
      覆盖：WR-33，Scenario 路由句保住路径核对
      验收：渲染后的 `flow-02` 在新行为、下一项、既有规格修复三处点名 propose/update 并写出 design 的句子上都有同一句核对。这两份 `SKILL.md` 仍带 `generatedBy`。路由句在，不把唯一的句子只留在会被导入覆盖的 `SKILL.md`。
      模块与文件：`tools/framework_core/workflows/combinations.json` 里 `id` 为 `flow-02` 的三处 `lines`，再用 `render_skill` 写出 `skill/flows/flow-02/SKILL.md`。不改 `skill/openspec/openspec-propose/SKILL.md` 与 `skill/openspec/openspec-update-change/SKILL.md`。断言加在 `tests/test_flow_routers.py`。
      接口：不改 `flow-02` 的 `mentions`、名称、触发词和目的。其他 flow 对象不动。本切片交给 1.6 的是仍保留的「不创建 tasks.md」和进入 finishing 前的原有只读事实。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_existing_paths_are_checked_before_design_is_written`。改正文前失败，因为现文没有「落盘前在仓库里核对」。

- [x] 1.5 对不上的结论不往下传
      做什么：测试被删除、skip 或放宽不能当成通过。对方说基线本来就失败时，在主干上跑同一条命令，不要为了证明无关而 stash 或 reset 当前改动。独立只读上下文返回的每条问题，回读对应代码后才写入交付报告；读不出依据的标待确认或剔除，不交给 `tdd`。审完看 `git status` 没有变化。只 mock 自证、没有业务断言、靠固定长 sleep 的测试，同样只记进报告。自审必须标明自审。`flow-04` 与 `flow-09` 仍只写报告。主干对照不能用来声称全量验证已过。
      阻塞于：1.3
      覆盖：WR-34，Scenario 对不上的结论停在报告
      验收：`verification-before-completion` 的 `SKILL.md` 含删除、skip、放宽、主干同一条命令、stash、reset，以及主干对照不能声称全量验证已过。已有的 `Trusting agent success reports` 仍只出现一次。`framework-rules.md` 含回读、待确认、`git status` 没有变化、mock 自证和固定长 sleep。自审标明自审与 `flow-04`、`flow-09` 只写报告的原句仍在。
      模块与文件：`skill/superpowers/verification-before-completion/SKILL.md`，`skill/matt-pocock/code-review/framework-rules.md`。不改 `skill/flows/flow-04/SKILL.md` 与 `skill/flows/flow-09/SKILL.md`。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.3 留在 `framework-rules.md` 的「不改业务源码」和否定清单。本切片不把「修改交回 tdd」写进 `flow-04` 或 `flow-09`。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_unmatched_conclusions_are_not_forwarded`。改正文前失败，因为现文没有「不能当成通过」。

- [x] 1.6 收尾前的只读事实补上判断，仍不清理
      做什么：对还没进主干、且要用户决定或仍在进行的分支，读者读改动最多的一两个文件，用一句人话写改了什么，并给一条建议和理由。建议合并前用 `git merge-tree --write-tree --name-only` 看冲突文件，这条命令不改分支、不改工作目录。云端分支已删除不能单独当成可清理。只看是不是主干祖先会漏掉 squash，也会把还没提交的新分支误判成已合入。squash 或 rebase 之后整体补丁已在主干且工作区干净，可以标成可清理候选。推送、合并、删除仍等用户当次选择。读不到 PR 就不要猜。不新做看板脚本。
      阻塞于：1.4
      覆盖：WR-35，Scenario 只读事实补上判断并且不清理
      验收：`flow-02` 新行为与下一项两处都保留「先用只读事实说明每条分支和工作树在哪」，并追加上述判断，且含「仍不执行 git worktree remove」。渲染结果与 `render_skill` 一致。`AGENTS.md` 人格标记与 `finishing-a-development-branch` 的清理步骤不改。
      模块与文件：同一 `flow-02` 对象里进入 `finishing-a-development-branch` 之前的两句，先改 `combinations.json` 再渲染 `skill/flows/flow-02/SKILL.md`。不手改渲染结果。断言加在 `tests/test_flow_routers.py`。
      接口：依赖 1.4 已经渲染过的 propose/update 核对句。本切片不执行清理，不新做看板脚本。
      测试：`python3 -m unittest tests.test_flow_routers.RouterContractTests.test_branch_facts_add_a_judgment_before_finishing`。改正文前失败，因为现文没有「git merge-tree --write-tree --name-only」。全量验收再跑 `python3 -m unittest discover -s tests`、`python3 tools/check-framework`、`python3 tools/check-changes`、`openspec validate bind-six-cause-and-claim-checks --type change --strict --no-interactive`。指纹失败只跑 `python3 tools/update-manifest`。

## 2. 不写回执

- [ ] 2.1 把本 change 的需求页写入初始化知识库并留下 `knowledge-receipt.json`
      做什么：规格同步之后把需求页写入初始化知识库，并留下回执。
      阻塞于：1.1、1.2、1.3、1.4、1.5、1.6
      覆盖：无。本次没有回执授权。
      验收：未勾。没有回执授权，不写知识库，不同步主规格，不归档。全部勾完会要求 knowledge-receipt，所以本条留下。
      模块与文件：不改文件。
      接口：不依赖已实现切片去写知识页。
      测试：不跑。知识库状态为 NOT_CONFIGURED，不新建库。
