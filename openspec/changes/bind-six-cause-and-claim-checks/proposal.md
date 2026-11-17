## Why

诊断、评审和收尾已经能停住，但六种会把结论传错的做法还没写进原文。根因可以不解释以前为什么不出现；二分可以动到当前工作区；说不清来源的兜底可以被当成修好；规格里的「已经有」可以不核对；别人的结论可以直接当成通过；收尾前的只读事实还不会判断一条还没进主干的分支。

## What Changes

- 根因陈述除了因果链和代码位置，还要能解释全部现象，包括为什么以前不出现、为什么只在某些输入或环境下出现。查过历史就写引入提交的短哈希；没查就写未验证，不凭提交说明下结论。仍不写回归测试，不改生产代码。修复仍只在活动路由把 `tdd` 写成下一项时由 `tdd` 做。落在 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 Phase 5，以及 `discipline.md` 的证据绑定旁。
- 提交多、范围看不出时，二分用 `git worktree add --detach` 在临时目录里 `git bisect run`。复现材料还没提交的，用新文件名拷进去。结束只 `git worktree remove` 这个临时目录。当前分支、工作区和暂存区不动。构建失败的版本用退出码 125 跳过。新 worktree 要装依赖或联网时先问。卫生清单和进入 finishing 前的只读事实仍不执行 `git worktree remove`。落在 `diagnosing-bugs` 的 `SKILL.md` 与 `discipline.md`。
- 说不清坏值从哪来就在报错处加空值判断、try/catch、重试、sleep 或加大超时；只对报告的那一个输入写特判；放宽、跳过或删除失败测试；一次改好几处却说不清是哪一处起作用。这些都不算修好。兜底如果还要，单独写明，不把它当成根因修复。入口校验如果就是坏数据第一次产生的地方，空值判断仍然算修复。落在 `tdd` 写修复时的 `discipline.md`，以及 `code-review` 的 `framework-rules.md` 里「是否改在坏数据第一次产生的位置」旁边。`diagnosing-bugs` 的 `discipline.md` 已有「报错消失但没解释原因不算修复」的英文原句，只补这份否定清单，不重写那句，仍不改产品代码。
- `openspec-propose` 与 `openspec-update-change` 写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，落盘前在仓库里核对。对不上就改这句或标成待确认。将要新建的文件不要求事先存在。不另写 `docs/` 规格，不另建任务契约。核对通过不等于 Requirement 已被认可。这两份技能是 `generatedBy` 的上游生成物，且没有本地层。核对句只写进 `flow-02` 点名 propose/update 的那一句，不改这两份 `SKILL.md`，避免下次导入把唯一的句子覆盖掉。
- 测试被删除、skip 或放宽不能当成通过。对方说基线本来就失败时，在主干上跑同一条命令，不要为了证明无关而 stash 或 reset 当前改动。`verification-before-completion` 已有的「不信外部自报」不重复。独立只读上下文返回的每条问题，回读对应代码后才写入交付报告；读不出依据的标待确认或剔除，不交给 `tdd`。审完看 `git status` 没有变化。只 mock 自证、没有业务断言、靠固定长 sleep 的测试，同样只记进报告。自审必须标明自审。`flow-04` 与 `flow-09` 仍只写报告，不把修改交回 `tdd`。主干对照不能用来声称全量验证已过。落在 `verification-before-completion` 的 `SKILL.md` 与 `code-review` 的 `framework-rules.md`。
- 在 `flow-02` 进入 `finishing-a-development-branch` 之前那段已有只读事实上追加判断，仍不清理。对还没进主干、且要用户决定或仍在进行的分支，读改动最多的一两个文件，用一句人话写改了什么，并给一条建议和理由。建议合并前用 `git merge-tree --write-tree --name-only` 看冲突文件。云端分支已删除不能单独当成可清理。只看是不是主干祖先会漏掉 squash，也会把还没提交的新分支误判成已合入。squash 或 rebase 之后整体补丁已在主干且工作区干净，可以标成可清理候选。推送、合并、删除仍等用户当次选择。读不到 PR 就不要猜。不新做看板脚本。`flow-02` 正文只改 `combinations.json` 再渲染。

不写进来：诊断自己写复现测试再自己修；五维深审整包和外部 CLI 审查；重写 `AGENTS.md` 或新增 oil-dev 小节；把工作树迁出 `.worktrees/` 或只复审改过的几行。不改 `openspec/changes/bind-skill-endings-to-active-flow` 与 `openspec/changes/absorb-five-flow-02-practices`。不改人格标记。不提交，不 push，不归档，不写知识库，不同步主规格。

## Capabilities

### New Capabilities

### Modified Capabilities

- `agent-workflow-routers`：新增六条行为约束，写明各自落在哪一份技能或 `flow-02` 的哪一句。不改 WR-01 至 WR-22 的已有正文，不改 `flow-04` 与 `flow-09` 的入口。

## Impact

- `skill/matt-pocock/diagnosing-bugs/SKILL.md`
- `skill/matt-pocock/diagnosing-bugs/discipline.md`
- `skill/matt-pocock/tdd/discipline.md`
- `skill/matt-pocock/code-review/framework-rules.md`
- `skill/superpowers/verification-before-completion/SKILL.md`
- `tools/framework_core/workflows/combinations.json` 的 `flow-02`，再渲染 `skill/flows/flow-02/SKILL.md`
- `tests/test_flow_routers.py`
- 不改 `openspec-propose` 与 `openspec-update-change` 的 `SKILL.md`
- 不改 `AGENTS.md`、`docs/framework/development-workflow.md`、`flow-04`、`flow-09`
- 不改 `finishing-a-development-branch` 里用户选择之后的清理步骤；进入该技能之前的只读事实仍不执行 `git worktree remove`
