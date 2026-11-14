## Why

知识层存下来的东西无法作废，也无法证明它起了作用。

**作废不了**：`status` 枚举只有 `approved` / `verified` / `temporary-workaround`。一条结论被推翻之后，没有"待复核"和"被取代"的说法，只能继续被召回并继续当已确认规则用。文章的原话是"一条错误经验被更稳定地召回，反而可能让错误重复得更稳定"。

**证明不了生效**：知识回执 `knowledge-receipt.json` 只列页路径、种类、来源路径与来源哈希——它证明"写了哪页"，不证明"这页知识改变了哪段实现或哪条断言"。回执能挡住"没写知识页就宣称完成"，挡不住"写了知识页却没改变任何行为"。

**失败没有归属**：调试纪律能产出"我改好了"，但产不出"下次该改哪一层"。同一个失败可能来自概念混淆、检索不适用、已知约束未执行检查、流程跳步或抽取策略系统性遗漏——这几种修法完全不同，笼统记成"补一条经验"就等于每种失败都加同一句提醒。

## What Changes

- **新增三个知识页状态**：`superseded`（被新页取代）、`retracted`（结论不成立，撤回）、`needs-review`（结论被质疑，等复核，不得继续当规则用）。现有三个状态语义不变。
- **状态转移成为可校验规则**：`superseded` 必须有 `superseded_by` 指向真实存在的页；`retracted` 必须写明撤回理由；两者都不得再被任何页的 `applies_when` 引用。
- **撤回传播**：进入 `needs-review` 时，引用它的测试断言与 Skill 必须一并进待复核；原事件保留，但不再以已确认规则指导新任务。
- **知识回执升级为 v2**，新增 `influenced[]`：记录这页知识改变了哪条断言、哪个文件、哪个 task。v1 回执按老规则放行，不追溯。
- **诊断纪律补失败归因五层**：内容层、访问层、验证层、流程层、方法层，各自写明该动什么、落到哪。归因与"多模块归属"是两件事，分别记录。
- **doctor 的 knowledge 维度暴露引用计数与从未被引用的页**，让知识的投入产出可核算。

## Capabilities

### New Capabilities

- `knowledge-correction`: 结论可以被取代、撤回与待复核，状态转移有可核对的规则。
- `knowledge-influence-tracking`: 知识回执能证明它改变了哪条断言，诊断失败能归属到具体改进层。

### Modified Capabilities

- `completion-knowledge-ingest`: 知识回执升级到 v2 并记录生效证据；v1 回执不被追溯。

`guide-learning-path` 的状态词典**不修改**：那本词典收的是框架自身的大写状态码，知识页状态是另一套小写词汇，混进去既是同名不同义，也让那道双向校验对页面状态失效。页面状态的声明处是知识库 schema，另有一条机器检查守住 schema 与代码不漂移。

## Impact

- `tools/framework_core/closure.py`：回执 v2 分支、`influenced[]` 校验、知识页状态机校验。
- `docs/guide/framework-model.md` §7.4：状态词典新增三项。**状态词典是双向校验的**——新码必须在 `tools/` 或 `skill/` 的代码里真的出现，否则 `check-framework` 直接失败。
- `skill/matt-pocock/diagnosing-bugs/discipline.md`：新增失败归因五层。
- doctor 的 knowledge 维度：引用计数与从未被引用的页。加字段，不加状态码。
- `docs/framework/knowledge-policy.md`：回执结构变化需要在政策里同步。
- 不新增技能、不新增流程、不新增门禁、不改 15 条路由的组合。

## 边界

三个新状态只对**新写入或此后修改**的知识页生效；引入之前已存在的页面不追溯改状态。回执 v1 与 v2 并存：只有带 `schema: knowledge-receipt/v2` 的回执才校验 `influenced[]`。

效果评测（时间切分双组、冻结组 vs 吸收新经验组）不在本 change 内，属于效果研究，另立项。
