## ADDED Requirements

### Requirement: WR-30 根因要解释为什么以前不出现

`diagnosing-bugs` 的根因陈述 MUST 同时写出因果链和代码位置，并且 MUST 能解释全部现象，包括为什么以前不出现、为什么只在某些输入或环境下出现。查过历史时 MUST 写引入提交的短哈希；没查历史时 MUST 写未验证，MUST NOT 凭提交说明下结论。该技能 MUST NOT 因此写回归测试，也 MUST NOT 改生产代码。修复 MUST 仍只在活动路由把 `tdd` 写成下一项时由 `tdd` 做。这句 MUST 出现在 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 的 Phase 5，以及同目录 `discipline.md`。

#### Scenario: 根因陈述解释以前不出现

- **WHEN** 读取 `diagnosing-bugs` 的 Phase 5 与同目录 `discipline.md`
- **THEN** 两处都要求根因陈述包含因果链、代码位置、为什么以前不出现、为什么只在某些输入或环境下出现；查过历史写引入提交的短哈希，没查写未验证，并且不凭提交说明下结论；Phase 5 仍不写回归测试，也不改生产代码

### Requirement: WR-31 二分放在临时 worktree

提交多、范围看不出时，`diagnosing-bugs` MUST 用 `git worktree add --detach` 在临时目录里 `git bisect run`。复现材料还没提交的，MUST 用新文件名拷进去。结束时 MUST 只 `git worktree remove` 这个临时目录。当前分支、工作区和暂存区 MUST 保持不动。构建失败的版本 MUST 用退出码 125 跳过。新 worktree 要装依赖或联网时 MUST 先问。这句 MUST 出现在 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 与同目录 `discipline.md`。`flow-02` 的卫生清单 MUST 仍不执行 `git worktree remove`。进入 `finishing-a-development-branch` 之前的只读事实 MUST 仍不执行 `git worktree remove`。本技能 MUST NOT 改生产代码。

#### Scenario: 二分不碰当前工作区

- **WHEN** 读取 `diagnosing-bugs` 的二分句，以及 `flow-02` 的卫生清单和进入 finishing 之前的只读事实
- **THEN** 二分使用临时目录里的 `git worktree add --detach` 与 `git bisect run`，结束只移除该临时目录，当前分支、工作区和暂存区不动，构建失败用退出码 125 跳过，装依赖或联网前先问；卫生清单和收尾前的只读事实仍不执行 `git worktree remove`

### Requirement: WR-32 这些动作不算修复

说不清坏值从哪来，就在报错处加空值判断、try/catch、重试、sleep 或加大超时；只对报告的那一个输入写特判；放宽、跳过或删除失败测试；一次改好几处却说不清是哪一处起作用。这些动作 MUST NOT 算作修好。兜底如果还要，MUST 单独写明，MUST NOT 把它当成根因修复。入口校验如果就是坏数据第一次产生的地方，空值判断 MUST 仍然算修复。这句 MUST 写在 `skill/matt-pocock/tdd/discipline.md` 写修复时的判定，以及 `skill/matt-pocock/code-review/framework-rules.md` 已有「是否改在坏数据第一次产生的位置」旁边。`diagnosing-bugs` 的 `discipline.md` 已有「报错消失但没解释原因不算修复」的英文原句时，MUST 只补这份否定清单，MUST NOT 重写那句，并且 MUST 仍不改产品代码。

#### Scenario: 兜底和特判不算根因修复

- **WHEN** 读取 `tdd` 的 `discipline.md`、`code-review` 的 `framework-rules.md`，以及 `diagnosing-bugs` 的 `discipline.md`
- **THEN** 三处都把空值判断、try/catch、重试、sleep、加大超时、单输入特判、放宽或删除失败测试、以及说不清哪一处起作用的多处修改排除在修好之外；兜底单独写明；入口处的空值判断仍然算修复；诊断纪律的英文原句保持不变，诊断仍不改产品代码

### Requirement: WR-33 规格里写成已经有的路径先核对

`openspec-propose` 与 `openspec-update-change` 写 design 时，proposal 或 design 里写成已经有的文件路径、可复用符号和测试命令，MUST 在落盘前于仓库里核对。对不上时 MUST 改这句或标成待确认。将要新建的文件 MUST NOT 被要求事先存在。MUST NOT 另写 `docs/` 规格，也 MUST NOT 另建任务契约。核对通过 MUST NOT 等于 Requirement 已被认可。这两份技能是 `generatedBy` 的上游生成物，且没有本地层。核对句 MUST 写在 `flow-02` 点名 `openspec-propose` 或 `openspec-update-change` 并写出 design 的句子上，包括新行为、下一项和既有规格修复三处。MUST NOT 把这句只写进会被下次导入覆盖的 `SKILL.md` 而路由句没有同样的约束。

#### Scenario: 路由句保住路径核对

- **WHEN** 读取渲染后的 `flow-02` 里点名 `openspec-propose` 或 `openspec-update-change` 并写出 design 的句子
- **THEN** 新行为、下一项和既有规格修复三处都要求落盘前核对已经有的文件路径、可复用符号和测试命令，对不上就改这句或标成待确认，将要新建的文件不要求事先存在，不另写 `docs/` 规格，不另建任务契约，并且核对通过不等于 Requirement 已被认可

### Requirement: WR-34 别人的结论对不上就不往下传

测试被删除、skip 或放宽 MUST NOT 当成通过。对方说基线本来就失败时，MUST 在主干上跑同一条命令，MUST NOT 为了证明无关而 stash 或 reset 当前改动。`verification-before-completion` 已有的不信外部自报句子 MUST 保持原样，MUST NOT 再写一句重复它。这些新句子 MUST 写在 `skill/superpowers/verification-before-completion/SKILL.md`。独立只读上下文返回的每条问题，MUST 回读对应代码后才写入交付报告；读不出依据的 MUST 标成待确认或剔除，MUST NOT 交给 `tdd`。审完 MUST 看到 `git status` 没有变化。只 mock 自证、没有业务断言、靠固定长 sleep 的测试，MUST 同样只记进报告。自审 MUST 标明自审。`flow-04` 与 `flow-09` MUST 仍只写报告，MUST NOT 把修改交回 `tdd`，这两条路由的入口 MUST NOT 改。主干对照 MUST NOT 用来声称全量验证已过。评审侧的新句子 MUST 写在 `skill/matt-pocock/code-review/framework-rules.md`。

#### Scenario: 对不上的结论停在报告

- **WHEN** 读取 `verification-before-completion` 的 `SKILL.md` 与 `code-review` 的 `framework-rules.md`
- **THEN** 删除、skip 或放宽的测试不能当成通过；基线声称失败时在主干上跑同一条命令，并且不为了证明无关而 stash 或 reset；已有的不信外部自报句子仍在且不重复；独立只读上下文的问题回读对应代码后才写入报告，读不出依据的标待确认或剔除并且不交给 `tdd`；审完 `git status` 没有变化；只 mock 自证、没有业务断言或靠固定长 sleep 的测试只记进报告；自审标明自审；`flow-04` 与 `flow-09` 仍只写报告；主干对照不能用来声称全量验证已过

### Requirement: WR-35 收尾前的只读事实再补判断

`flow-02` 进入 `finishing-a-development-branch` 之前的已有只读事实 MUST 保留，并 MUST 追加判断，且这一步 MUST NOT 清理。对还没进主干、且要用户决定或仍在进行的分支，MUST 读改动最多的一两个文件，用一句人话写改了什么，并给一条建议和理由。建议合并前 MUST 用 `git merge-tree --write-tree --name-only` 看冲突文件，这条命令 MUST NOT 改分支，也 MUST NOT 改工作目录。云端分支已删除 MUST NOT 单独当成可清理。只看是不是主干祖先 MUST 被写成会漏掉 squash，也会把还没提交的新分支误判成已合入。squash 或 rebase 之后整体补丁已在主干且工作区干净时，MUST 可以标成可清理候选。推送、合并、删除 MUST 仍等用户当次选择。读不到 PR 时 MUST NOT 猜。MUST NOT 新做看板脚本。这句 MUST 同时出现在新行为与下一项两处已有只读事实之后。`flow-02` 正文 MUST 先改 `tools/framework_core/workflows/combinations.json` 再渲染，MUST NOT 手改出漂移。

#### Scenario: 只读事实补上判断并且不清理

- **WHEN** 读取 `flow-02` 新行为与下一项里进入 `finishing-a-development-branch` 之前的只读事实
- **THEN** 两处都保留原有的分支与工作树事实，并要求对未进主干且待决定或仍在进行的分支读改动最多的一两个文件、写一句人话和一条带理由的建议；合并前用 `git merge-tree --write-tree --name-only` 看冲突文件且该命令不改分支、不改工作目录；云端分支已删除不能单独当成可清理；只看主干祖先会漏掉 squash，也会误判未提交的新分支；squash 或 rebase 之后整体补丁已在主干且工作区干净可以标成可清理候选；推送、合并、删除仍等用户当次选择；读不到 PR 就不要猜；不新做看板脚本；仍不执行 `git worktree remove`
