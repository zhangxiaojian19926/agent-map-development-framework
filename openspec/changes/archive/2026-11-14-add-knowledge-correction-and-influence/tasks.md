## 0. 批准记录

- [x] 0.1 用户批准了 `docs/plans/2026-11-14-knowledge-concept-pages.md` 与随后的目标流程展示，并指示"开始执行"。本 change 的 delta spec 是那份计划的正式化：能力划分（`knowledge-correction`、`knowledge-influence-tracking`）、三个新状态码、回执 v2 结构、归因五层与分期均来自已批准的计划。**批准范围未覆盖场景措辞的逐条评审**，评审时以本 change 的 delta spec 为准。结构有效由 `openspec validate --all --strict --no-interactive` 单独确认，与本条分开记录。

## 1. 状态机与状态词典

- [x] 1.1 先写会失败的测试：状态为被取代但缺 `superseded_by` 或目标页不存在被报出、状态为撤回但缺撤回理由被报出、作废的页仍被某页的 `applies_when` 引用被报出（KC-02）
- [x] 1.2 在 `tools/framework_core/closure.py` 实现知识页状态校验，让 1.1 的测试转绿；验证代码里真的发出被取代、撤回、待复核三个状态字面量（KC-01、KC-02）
- [x] 1.3 扩知识库 schema 的状态集合（`skill/llm-wiki/templates/schema-template.md` 与 `knowledge/project/.wiki-schema.md`）：加入被取代、撤回、待复核三个状态与 `retraction_reason` 字段；**页面状态不进对外指南的框架状态词典**（那本词典只收框架自身的大写状态码，两者同名不同义）；加一条机器检查比对 schema 声明的集合与代码接受的集合，验证两者不漂移（KC-04）
- [x] 1.4 实现"引用它的下游能被列出"：一张进入待复核的页能列出引用它的断言、摘要与技能条目；验证原始事件保留而不再作为已确认规则被引用（KC-03）

## 2. 回执 v2 与生效记录

- [x] 2.1 先写会失败的测试：声明 v2 的回执缺 `influenced` 且未标不适用被报出、`influenced` 的页路径不在页面清单里被报出、task 标识不在该 change 的任务清单里被报出、v1 回执仍按老规则通过（KI-01、KI-02）
- [x] 2.2 在 `tools/framework_core/closure.py` 的 `knowledge_receipt_detail()` 实现 v2 分支，让 2.1 的测试转绿；验证 v1 回执的判定结果与引入前一致（KI-01、KI-02）
- [x] 2.3 同步改 `docs/framework/knowledge-policy.md`，写明回执的 v2 结构与 `influenced` 的内容与校验规则；验证政策与实现一致（KI-01）

## 3. 失败归因与成本账

- [x] 3.1 扩 `skill/matt-pocock/diagnosing-bugs/discipline.md`，新增失败归因一节：内容层、访问层、验证层、流程层、方法层，各自写明该动什么、落到哪；验证该文件仍以本地层声明开头并被 `flow-02` 既有路径点名（KI-03）
- [x] 3.2 扩 doctor 的 knowledge 维度：每个知识页的引用次数与从未被引用的页清单；验证这两项以报告字段出现而没有变成新的状态码（KI-04）
- [x] 3.3 运行 `python3 tools/check-framework`，验证本地层登记、活文档链接与状态词典仍然一致（KI-03、KI-04）

## 4. 本 change 自身

- [x] 4.1 把 `knowledge-correction` 与 `knowledge-influence-tracking` 同步进 `openspec/specs/`，并按 `completion-knowledge-ingest` 修改 `KI-04`；**不修改 `guide-learning-path`**（页面状态不进框架状态词典）；验证 `openspec validate --all --strict --no-interactive` 通过（KC-01、KC-02、KC-03、KC-04、KI-01、KI-02、KI-03、KI-04）
- [x] 4.2 写入本 change 的需求页与知识回执，再归档；验证 `python3 tools/check-changes` 不再报本 change 的欠账（KI-01）

## 5. 验证证据

- 变异检验：把 lint 的适用条件与状态校验、回执的适用条件/概念页/状态机/v2 回执校验逐条关掉后，`tests.test_knowledge` 与 `tests.test_check_changes` 共 14 项失败；恢复后 68 项全过。测试确实在测行为，不是在测文件存在。
- 全量回归：`python3 -m unittest discover -s tests` —— 486 项通过（基线 454，新增 32）。
- 六道门禁：`check-framework` PASS（596 文件 / 42 技能）、`openspec validate --all --strict` 43 项通过、`openspec validate --archived` 31 项通过、`check-changes` PASS、`git diff --check` 无输出。
- 回执判定：对两个 change 显式调用 `knowledge_receipt_detail`，均返回空——页面齐备、来源可核对、状态一致。
- 一处实现期修正：原计划让三个新状态进入对外指南的框架状态词典。实现时发现 `check-framework` 的状态词典校验用 `STATUS_TOKEN` 只扫大写 token，而知识页状态是小写且本来就不在那本词典里，写进去既不构成双向校验，又会让两套同名不同义的词汇混在一张表里。改为由知识库 schema 声明状态集合，另加一条机器检查比对 schema 与代码接受的集合。
