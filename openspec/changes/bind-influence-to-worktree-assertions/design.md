## Context

动机见 `proposal.md` 的 Why。行为合同见本 change 的两份 delta：`knowledge-influence-tracking` 的 KI-02，以及 `completion-knowledge-ingest` 里「回执证明已经写入」的场景「第二版回执带生效记录」。

本次核对的源码事实：

- `tools/framework_core/closure.py` 的 `influenced_errors` 在 `schema` 不是 `knowledge-receipt/v2` 时返回空。`influenced` 为带 `status: not_applicable` 且带 `reason` 的对象时返回空；无理由则报出。列表为空或不存在时报出未记录是否生效。列表项只核对页路径是否在回执页面清单、`task_id` 是否在该 change 的 `tasks.md`。函数不读 `file`，也不读 `assertion`。
- `knowledge_receipt_detail` 把 `influenced_errors` 的第一条错误交给 `outstanding_changes`。问题文案是 `knowledge receipt is not acceptable`。`outstanding_changes` 只扫 `openspec/changes/` 的直接子目录，不进入 `archive/`。
- `tests/test_check_changes.py` 的 `test_a_v2_receipt_with_matching_influence_is_accepted` 使用并不存在的 `src/a.py` / `test_a`。该用例的剩余发现是 `still active`，说明生效核对已放行。
- `skill/matt-pocock/tdd/SKILL.md` 的正文没有知识页路径。flow-02 已把 tdd 放在规格同步与回执之前；回执在 `openspec-archive-change` 之前做一次。
- `skill/llm-wiki/scripts/wiki.py` 的 `find_matches` 按标题与正文打分，不读页面状态。
- `docs/framework/knowledge-policy.md` §11.5 与 §11.12：需求页和 `conclusion` 为 `pass` 的问题页在规格同步后写入 alias `project`。概念页属于其他种类，扩展语义要有本次授权。

## Goals / Non-Goals

**Goals:**

- 只扩 KI-02。列表项的 `file` 与 `assertion` 必须出现在完成检查所看的项目根内的该文件文本中，且该文件文本同时包含这条记录的知识页路径。页与 task 的现有核对保留。
- 对不上时沿用现有完成检查欠账，指出是哪一条。不新开入口。
- 页路径写在现有 TDD 写断言的那个文件上。归档前仍是 flow-02 那一次回执，回执只核对。
- `completion-knowledge-ingest` 的「第二版回执带生效记录」收成同一条更严的接受条件。不新开能力。
- 带理由的 `not_applicable` 仍放行。未声明 v2 的回执不追溯。

**Non-Goals:**

- 证据种类分列（接口成功与业务验收分开）。那一批挂在 `verification-before-completion`。
- 撤回后的技能与测试待复核清单。那是只读 doctor 清单，且不改技能触发。
- 查询结果带上适用条件，并在能够判断时停止。`find_matches` 不按 `superseded` 丢页，本 change 不改查询。
- 三层互索引、图数据库、Chat Memory、meta-skill、新的自动入口、概念页免授权自动写入、抽取策略自改进、效果评测。不拿文章里的 58%→65% 当验收。时间切分另立项。
- 不改 KI-03、KI-04（`knowledge-influence-tracking` 的投入产出核算），不改 flow-01 到 flow-15 的 `description`，不新增 flow。
- 十三个已点名宿主不使用记忆 API、钩子或子代理。

## Decisions

1. **核对落在现有 `influenced_errors`，不新开函数入口。** `knowledge_receipt_detail` 继续取第一条错误。已考虑在 doctor 或 flow-05 另做一次生效检查。完成检查已经是归档前的欠账口，再开一口会变成第二套入口，故不另开。

2. **`file` 与 `assertion` 按工作树文件的文本出现来判定。** 路径留在完成检查已经收到的项目根内；越出该根算这条记录对不上。文件文本必须同时含断言字符串和该条的知识页路径。已考虑解析测试 AST，或要求对照实验证明行为变了。前者绑死语言，后者属于效果评测。本 change 只证明两个字符串同在一个文件里。

3. **引用写在现有 TDD 写断言那一步。** flow-02 已有这个顺序：tdd，然后评审与验证，规格同步，留下回执，然后归档。回执不负责把页路径写进文件。已考虑在归档前再插入一次「补引用」步骤。那会变成新的流程入口，十五条 `description` 也不该为此改写，故不插入。

4. **`not_applicable` 加理由在读列表之前放行。** 这是当前函数的顺序。没有可引用的已授权页时用它，不为此写概念页。概念页授权停留在 §11.12：术语已确定且扩展语义已获本次授权。已考虑把概念页改成可自动写入以填满 `influenced`。授权表不放宽，故不做。

5. **`completion-knowledge-ingest` 只改场景「第二版回执带生效记录」的 WHEN。** 同一要求的其余场景原样保留，包括概念页来源受限、缺生效记录被报出、第一版不追溯、没有回执留为欠账。已考虑把工作树核对写成第三份能力。它是 KI-02 的复述，故并进既有要求。

6. **已点名宿主的公共面是文件和现有 Python 校验。** WR-10 与 `tools/framework_core/hosts/roster.json` 的十三个宿主是 `cursor`、`claude-code`、`codex`、`gemini-cli`、`copilot-cli`、`github-copilot`、`windsurf`、`grok`、`qwen-code`、`codebuddy`、`trae`、`lingma`、`deepseek-harness`。不写发现目录，不写拦截载体。已考虑用宿主钩子在写文件时拦截缺引用。名册里的钩子能力并不都是可阻断，且本 change 不需要运行时拦截，故不用。

## Risks / Trade-offs

- [只证明页路径和断言字符串同在一个文件里] → 不把这当成对照实验里行为变了，也不用 58%→65% 或时间切分当验收。效果评测留在本 change 之外。
- [有人用未授权概念页填 `influenced`] → 概念页授权不放宽。没有可引用的已授权页时使用带理由的 `not_applicable`。
- [查询被顺手改成丢掉作废页] → `find_matches` 不在本 change 的修改面上。作废页继续按正文匹配返回。
- [归档里已有的 v2 回执对不上新规则] → `outstanding_changes` 不进入 `archive/`。未声明 v2 的回执仍不要求生效记录。新规则只约束此后仍被完成检查看到的 v2 回执。
- [十五条路由的触发句被改写] → flow-01 到 flow-15 的 `description` 保持现状。回执仍是 flow-02 归档前那一次。

## Migration Plan

- 无数据迁移。不重写 `openspec/changes/archive/` 里的回执，不改 `openspec/specs/` 下的主规格；主规格留到该 change 归档时同步。
- 实现时改 `influenced_errors`，并让 `test_a_v2_receipt_with_matching_influence_is_accepted` 不再接受不存在的 `src/a.py` / `test_a`。带理由的 `not_applicable`、页不在清单、task 不在 `tasks.md`、未声明 v2，保持现在的判定。
- `docs/framework/knowledge-policy.md` §11.5 在同一段补上工作树核对。授权表不动。
- 回滚时去掉列表项的工作树核对，KI-02 回到只核对页与 task。
