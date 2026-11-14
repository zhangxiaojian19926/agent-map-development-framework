## Context

知识回执的判定集中在 `tools/framework_core/closure.py` 的 `knowledge_receipt_detail()` 与 `_page_detail()`；`tools/check-changes` 用它报出欠账，`tools/check-project` 报同一份清单。知识页的 `status` 枚举定义在 `skill/llm-wiki/templates/schema-template.md` 与 `knowledge/project/.wiki-schema.md`，页面上真正可选的值目前只有三个。

状态词典在 `docs/guide/framework-model.md` 的 `<!-- status-dictionary:start -->` 与 `<!-- status-dictionary:end -->` 之间，按域分组。`tools/check-framework` 的 `status_dictionary_errors` 会扫这段里的每个状态码，要求它在 `tools/` 与 `skill/` 的 `.py` 与 `SKILL.md` 里真的出现——这是双向的：文档写了但代码没发出，直接 FAIL。

调试纪律在 `skill/matt-pocock/diagnosing-bugs/discipline.md`，已登记在 `skill/local-layers.json`，并由 `flow-02` 的既有规格修复路径点名。

## Goals / Non-Goals

**Goals:**

- 结论被推翻时能标待复核、被取代或撤回，且这些状态有可核对的规则。
- 撤回时引用它的下游能被列出，而不是静默保留。
- 知识回执能证明"写了并且起了作用"，而不是只证明"写了"。
- 诊断失败能归属到内容、访问、验证、流程或方法某一层。
- 新状态码在文档与代码两侧都真实存在。

**Non-Goals:**

- 不做效果评测，不建评测集，不做时间切分双组实验。
- 不回溯改写引入之前已存在的知识页状态。
- 不改 `requirement` 与 `problem` 之外的页面种类的必填规则。
- 不新增技能、不新增流程、不新增门禁。
- 不删除原始事件——作废靠状态与引用，不靠删除。

## Decisions

1. **加三个状态，不加第四个。** `temporary-workaround` 继续表示"根因未消除，不算已解决"，不再造近义词。枚举越少越不容易漂移，状态词典的校验面也越小。

2. **页面状态不进框架状态词典,改用 schema 与代码的比对。** 实现时发现原计划的一处错位：`tools/check-framework` 的状态词典校验用 `STATUS_TOKEN = "`([A-Z][A-Z0-9_]*(?:/[A-Z]+)?)`"` 扫描 `docs/guide/framework-model.md`，**只认大写 token**；而知识页的 `status` 是小写（`approved`/`verified`/`temporary-workaround`），本来就从未出现在那本词典里。把小写的页面状态写进去既扫不到、也不构成双向校验，还会让框架状态码与页面状态变成同名不同义的两套词汇混在一张表里。

   改为：页面状态的**唯一声明处是知识库 schema**（`skill/llm-wiki/templates/schema-template.md` 与 `knowledge/project/.wiki-schema.md`），代码里的接受集合与它比对，一条机器检查守住不漂移。框架状态词典保持只收框架自身的状态码，不动。这比原计划更严——原计划依赖的那道双向校验对页面状态本来就不生效。

3. **状态机做成校验规则，不做运行时引擎。** 没有新的常驻组件。`closure.py` 在判定回执与欠账时顺带校验知识页的状态：被判为 `superseded` 的页必须有 `superseded_by` 指向真实存在的页；被判为 `retracted` 的页必须有撤回理由；两者都不得再被任何页的 `applies_when` 引用。

4. **撤回靠状态与传播，不靠删除。** 原事件保留在库里，但状态改成 `superseded` 或 `retracted`，不再作为已确认规则被引用。传播规则是"引用它的断言与 Skill 必须一并进待复核"，落点是列出受影响的引用者，而不是自动去改别人的断言。

5. **回执升级为 v2，v1 继续放行。** 回执加 `schema: knowledge-receipt/v2`。只有 v2 才校验 `influenced[]`；v1 回执按老规则判定通过。不追溯——引入之前写的回执不补字段。

6. **`influenced[]` 只校验"能对上"，不校验"真的起了作用"。** 每条记录含页路径、task id、文件与断言。校验规则是页路径必须在回执的 `pages` 里、task id 必须在该 change 的 `tasks.md` 里存在。它能证明"声明了影响并可被追溯"，不能证明语义上确实正确——后者仍是评审的判断。

7. **归因五层加在调试纪律层，不加新技能。** 内容层、访问层、验证层、流程层、方法层，各自写明该动什么、落到哪。归因与"多模块归属"是两件事：归属决定写到哪个知识库，归因决定该改哪一层。两者分别记录，不能互相替代。

8. **doctor 加字段不加状态码。** knowledge 维度增加引用计数与"从未被引用的页"清单。这两个是报告内容，不是新的状态分类，因此不进入状态词典，避开双向校验。

## Risks / Trade-offs

- [状态词典改了但代码没改，CI 报"documents status X which the shipped code never emits"] → 第一个实现切片就是改 `closure.py`，文档切片依赖代码切片，写进 `tasks.md` 的阻塞关系。
- [引入新的状态让枚举变大，误用变多] → 只加三个且各有明确触发场景；`temporary-workaround` 保持原义不造近义词。
- [撤回传播靠人执行，漏了就等于没传播] → 校验规则先能"列出受影响的引用者"，把传播从看不见变成看得见；自动改别人的断言不做。
- [`influenced[]` 变成填表任务] → 只校验能对上，不要求条数；`influenced` 为空时必须显式标 `not_applicable` 并给理由，不允许静默省略。
- [回执结构变化让旧回执失效] → v1/v2 并存，v1 按老规则放行。

## Migration Plan

1. 先加状态校验与三个新状态码，同批改状态词典。
2. 再加回执 v2 与 `influenced[]` 校验，v1 分支保持原判定。
3. 最后加归因五层与 doctor 的引用计数。
4. 回退时撤掉新状态与 v2 分支，已写入的字段保留。

## Open Questions

无。效果评测单独立项，不在本 change 的判据内。
