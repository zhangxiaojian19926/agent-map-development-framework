## 0. 批准记录

- [x] 0.1 用户批准了 `docs/plans/2026-11-14-knowledge-concept-pages.md` 与随后的目标流程展示，并指示"开始执行"。本 change 的 delta spec 是那份计划的正式化：能力划分（`concept-pages`、`knowledge-applicability`）、字段清单、分期与验收口径均来自已批准的计划。**批准范围未覆盖字段名与场景措辞的逐条评审**，评审时以本 change 的 delta spec 为准。结构有效由 `openspec validate --all --strict --no-interactive` 单独确认，与本条分开记录。

## 1. 页面形态与字段

- [x] 1.1 扩 `skill/llm-wiki/templates/schema-template.md` 与 `knowledge/project/.wiki-schema.md`：目录表加入 `wiki/topics/concepts`，`artifact_kind` 枚举加入 `concept`，frontmatter 字段行写明八个可选字段与"问题页/概念页必填 `applies_when`、问题页必填 `not_applicable_when`、需求页不强制"三条规则；验证两处内容一致且不出现两份定义（CP-01、KA-01、KA-02）
- [x] 1.2 扩 `skill/llm-wiki/templates/engineering-template.md`：frontmatter 增八个字段，正文"记录"段增触发条件、不适用条件、被排除的解释三行；验证按模板渲染出的概念页能通过结构校验（CP-01、KA-01）
- [x] 1.3 扩 `skill/llm-wiki/templates/index-template.md` 的空目录说明，把 `topics/concepts` 列进去；验证索引模板与 schema 模板描述的目录集合一致（CP-01）
- [x] 1.4 扩 `skill/llm-wiki/scripts/wiki.py` 的 `SHELL_DIRS`，加入 `wiki/topics/concepts`；验证初始化出的知识库含该目录且不改动其他目录（CP-01）

## 2. 结构校验

- [x] 2.1 先写会失败的测试：问题页缺 `applies_when` 被报出、问题页缺 `not_applicable_when` 被报出、概念页缺 `applies_when` 被报出、需求页缺这些字段不被报出、需求页有值时格式仍被校验（KA-02、KA-03）
- [x] 2.2 实现 `skill/llm-wiki/scripts/wiki.py` 中 lint 的按种类必填校验（当前 frontmatter 校验在第 248–252 行），让 2.1 的测试转绿；验证既有需求页的回归用例仍然通过（KA-02、KA-03）
- [x] 2.3 扩 `tools/framework_core/closure.py` 的 `_page_detail()`（当前种类白名单在第 70 行）：白名单加入 `concept`，并给它一条来源约束——来源必须是 `docs/project/GLOSSARY.md` 或 `openspec/specs/` 下的已同步规格；验证回执接受来源合规的概念页、报出来源缺失或不合规的概念页（CP-02、KI-04）
- [x] 2.4 扩 `tools/framework_core/closure.py` 的 `knowledge_receipt_detail()`：问题页缺适用条件或缺不适用条件时报出并指出缺哪一项（KI-02、KA-02）

## 3. 术语接缝

- [x] 3.1 改 `docs/framework/knowledge-policy.md` 的 §11.12：允许清单加入 `concept` 一行（目录 `wiki/topics/concepts/`，时机为术语已确定且概念页获本次授权）；把末段"术语表与决策记录不属于知识库内容"改写为"术语的定义留在 `docs/project/GLOSSARY.md` 并由人工维护，概念的扩展语义以概念页入库并带来源路径与来源哈希，两者互指但不互相复制"；验证政策里不再出现"知识库不收术语表"的表述（CP-03）
- [x] 3.2 同步改 `skill/matt-pocock/domain-modeling/framework-rules.md` 的第 8–26 行，把"The knowledge base does not hold it"改写为与 3.1 同一组关键句；验证该文件的本地层声明仍在开头且与上游原文的边界未被破坏（CP-03）
- [x] 3.3 加一条机器检查，比对 3.1 与 3.2 写入的同一组关键句；验证两处措辞被改动到不一致时该检查失败（CP-03）
- [x] 3.4 运行 `python3 tools/check-framework`，验证本地层登记、活文档链接与状态词典仍然一致（CP-03）

## 4. 本 change 自身

- [x] 4.1 把 `concept-pages` 与 `knowledge-applicability` 同步进 `openspec/specs/`，并按 `completion-knowledge-ingest` 修改 `KI-02` 与 `KI-04`；验证 `openspec validate --all --strict --no-interactive` 通过（CP-01、CP-02、CP-03、KA-01、KA-02、KA-03）
- [x] 4.2 写入本 change 的需求页与知识回执，再归档；验证 `python3 tools/check-changes` 不再报本 change 的欠账（KI-04）

## 5. 验证证据

- 变异检验：把 lint 的适用条件与状态校验、回执的适用条件/概念页/状态机/v2 回执校验逐条关掉后，`tests.test_knowledge` 与 `tests.test_check_changes` 共 14 项失败；恢复后 68 项全过。测试确实在测行为，不是在测文件存在。
- 全量回归：`python3 -m unittest discover -s tests` —— 486 项通过（基线 454，新增 32）。
- 六道门禁：`check-framework` PASS（596 文件 / 42 技能）、`openspec validate --all --strict` 43 项通过、`openspec validate --archived` 31 项通过、`check-changes` PASS、`git diff --check` 无输出。
- 回执判定：对两个 change 显式调用 `knowledge_receipt_detail`，均返回空——页面齐备、来源可核对、状态一致。
- 一处实现期修正：原计划让三个新状态进入对外指南的框架状态词典。实现时发现 `check-framework` 的状态词典校验用 `STATUS_TOKEN` 只扫大写 token，而知识页状态是小写且本来就不在那本词典里，写进去既不构成双向校验，又会让两套同名不同义的词汇混在一张表里。改为由知识库 schema 声明状态集合，另加一条机器检查比对 schema 与代码接受的集合。
