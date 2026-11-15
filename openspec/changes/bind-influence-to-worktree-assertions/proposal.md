## Why

`knowledge-receipt/v2` 的 `influenced[]` 现在对得上回执里的页和 `tasks.md` 里的 task，对不上工作树里的真实断言。`tools/framework_core/closure.py` 的 `influenced_errors` 只做两件事：页路径必须在同一张回执的页面清单里，`task_id` 必须出现在该 change 的 `tasks.md` 里。它不读 `file`，也不读 `assertion`。`tests/test_check_changes.py` 的 `test_a_v2_receipt_with_matching_influence_is_accepted` 用一条并不存在的 `src/a.py` / `test_a` 通过了这道核对；剩下的欠账是「仍未归档」，不是「文件对不上」。

用户给定的文章主张（腾讯技术工程《不只是Memory：Ontology如何让Coding Agent越用越懂项目？》，2026-11-13）是：经验的使用，应能追踪到它改变了哪项判断，哪段实现或哪项验证。只靠召回不能证明经验生效。这道缺口已经被现有完成检查看见，不必等第一张概念页。`docs/framework/knowledge-policy.md` §11.5 与 §11.12 已经允许规格同步后的需求页、以及 `conclusion` 为 `pass` 的问题页，在 flow-02 归档前写入 alias `project`。`influenced` 可以对上这两类已经授权的页。

## What Changes

- 收紧既有能力 `knowledge-influence-tracking` 的 KI-02。一条 `influenced` 列表项里的 `file` 与 `assertion` 必须出现在该完成检查所看的工作树文件里，并且该文件的文本里同时出现这条记录的知识页路径。页仍须在回执清单里，task 仍须在 `tasks.md` 里。对不上时，沿用 `outstanding_changes` 里已有的「knowledge receipt is not acceptable」欠账，并指出对不上的是哪一条。不新开回流，不新开入口。
- 页路径写在现有 TDD 步里、写断言的那个文件上。`skill/matt-pocock/tdd/SKILL.md` 今天的正文没有这句；flow-02 已经把 tdd 放在回执之前。归档前的那一次回执只做核对，不另起一次写入。
- `influenced` 为 `{status: not_applicable, reason: ...}` 时仍然放行。没有理由的不适用声明、空的 `influenced`、以及未声明 `knowledge-receipt/v2` 的回执，维持现在的判定：前者报出，后者不追溯。
- 校验落在 `tools/framework_core/closure.py` 的 `influenced_errors` 一类现有 Python 检查。文件路径留在完成检查已经收到的项目根内；越出该根与今天其他回执路径一样，算对不上。
- 概念页仍属 §11.12 的「其他种类」：术语已确定，且扩展语义已获本次授权，才可以写入。不得为了填 `influenced` 去写未授权的概念页。没有可引用的已授权页时，用带理由的 `not_applicable`，不另造一页。
- `skill/llm-wiki/scripts/wiki.py` 的 `find_matches` 按标题与正文打分，不读页面状态，不按 `superseded` 丢页。本 change 不改查询。

## Capabilities

### New Capabilities

- 无。把生效记录对上工作树里的断言，是收紧已归档的 `knowledge-influence-tracking`，不引入新 capability。

### Modified Capabilities

- `knowledge-influence-tracking`（`openspec/specs/knowledge-influence-tracking/spec.md`）：KI-02 今天要求页在回执清单里、task 在任务清单里，并拒绝不存在的页或不存在的 task。本 change 为列表项补上工作树核对：`file` 与 `assertion` 必须出现在该文件中，且该文件引用了这条知识页路径。KI-01 的 `not_applicable` 加理由、以及未声明 v2 的回执不追溯，保持不变。KI-03 与 KI-04 不在本 change 里改。
- `completion-knowledge-ingest`（`openspec/specs/completion-knowledge-ingest/spec.md`）：要求「回执证明已经写入」里的场景「第二版回执带生效记录」今天把「页在清单里、task 在任务清单里」接受为「既写了也起了作用」。这句话要收成与 KI-02 同一条更严的核对，避免两份规格各说各的。这是同一条规则的复述，不是第二项能力。

## Impact

- 将来修改 `tools/framework_core/closure.py` 的 `influenced_errors`。`knowledge_receipt_detail` 已经把该函数的第一条错误交给 `outstanding_changes`；入口保持这一条。
- 将来改 `tests/test_check_changes.py`：`test_a_v2_receipt_with_matching_influence_is_accepted` 今天接受不存在的 `src/a.py` / `test_a`。成功时，完成检查拒绝这种虚构路径；带理由的 `not_applicable` 仍不产生生效错误。页不在清单、task 不在 `tasks.md` 的现有失败保持。
- `docs/framework/knowledge-policy.md` §11.5 今天只写「页路径在回执清单里、task 在任务清单里」。规格落地时把工作树核对写进同一段。§11.5 与 §11.12 的授权表不放宽：需求页和已验证问题页仍是规格同步后直接写入；概念页仍要本次授权。
- 十五条 flow 的 `description` 不变。flow-01 到 flow-15 的前置说明保持现在的触发句。回执仍是 flow-02 正文里规格同步之后、`openspec-archive-change` 之前的那一次，不新增 flow，也不在别的 flow 再做一次生效核对。
- 已点名宿主的公共面是文件和现有 Python 校验。WR-10 与 `tools/framework_core/hosts/roster.json` 的十三个宿主是：`cursor`、`claude-code`、`codex`、`gemini-cli`、`copilot-cli`、`github-copilot`、`windsurf`、`grok`、`qwen-code`、`codebuddy`、`trae`、`lingma`、`deepseek-harness`。本 change 不使用记忆 API、钩子或子代理，也不写入这些宿主的发现目录或拦截载体。
- 这是收紧，不是追溯。`outstanding_changes` 不进入 `openspec/changes/archive/`。未声明 v2 的回执仍不要求生效记录。此后一张 v2 回执若 `file` 或 `assertion` 对不上工作树，完成检查把它留成欠账。
- 成功时：完成检查拒绝虚构的文件或断言，也拒绝文件里没有这条知识页路径的记录；`not_applicable` 加理由仍可通过。

## Non-goals

上一轮若只再提取一批，做的就是这一件。下面四项不放进本 change。

1. 证据种类分列（接口成功不等于业务验收）。那是把「验证通过」拆成不同证据种类，挂在 `verification-before-completion`。本 change 只核对回执里已经写下的文件与断言是否出现在工作树文本中，不改验证技能如何判通过。
2. 撤回后的技能与测试待复核清单。那是页面进入撤回之后的只读 doctor 清单。本 change 不改页面状态机，也不改任何技能的触发条件。
3. 查询结果带上适用条件，并在能够判断时停止。那是 flow-05 与 `wiki.py` 的查询行为。`find_matches` 今天不按作废状态丢页；本 change 保持这一点，不把 `superseded` 变成丢页条件。
4. 三层互索引、图数据库、Chat Memory、meta-skill、新的自动入口、概念页免授权自动写入、抽取策略自改进、效果评测。`docs/plans/2026-11-14-knowledge-concept-pages.md` 的「明确不做」已经写明：不建本体目录，不引 OWL 2 / SHACL / 图数据库，不把术语表搬进知识库，不拿文章里的 58%→65% 当验收。时间切分评测另立项。

## Risks

- 这道核对只证明知识页路径和断言字符串同时出现在同一份工作树文件里。它不证明对照实验里行为变了，也不能代替效果评测。
- 不得因此放宽概念页授权。填不满 `influenced` 时走带理由的 `not_applicable`，不自动写概念页。
- 不得改查询的丢页行为。`find_matches` 继续返回正文匹配到的页，包括作废页。
