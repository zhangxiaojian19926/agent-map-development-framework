## Why

知识层现在只能表达"一条结论是什么"，不能表达"它在什么条件下成立"。具体三个缺口：

1. **适用条件没有落点**。知识页 frontmatter 只有 `type`/`artifact_kind`/`created`/`confidence`/`status`/`module_ids`/`source_path`/`source_sha256`/`problem_id`/`sources`。一条只适用于旧协议的经验，没有地方写"只适用于 v2"，条件只能藏在正文最深处——而摘要层会把它当普适规则读走。

2. **术语与概念没有可核对的分工**。`docs/framework/knowledge-policy.md` §11.12 末段和 `skill/matt-pocock/domain-modeling/framework-rules.md` 两处独立明文把术语表挡在知识库之外。理由本身成立：术语表是当前词汇，不是已验证经验。但代价是项目里**唯一一处表达"概念"的地方没有来源、没有置信度、没有机器校验**。术语页要写"这个概念在什么条件下成立、和谁容易混、约束了哪些代码、怎么验证"，只能写在没有校验的散文里。

3. **第三层经验层至今是空的**。`knowledge/project/` 里 5 篇页面全是需求规格的镜像，`problems/`、`entities/modules/`、`synthesis/decisions/`、`sources/verifications/`、`topics/constraints/` 全部只剩 `.gitkeep`。

本 change 只做一件事：让知识层能表达适用条件，并让"概念"这种语义有可核对的落点。

## What Changes

- **概念页成为可摄入的知识页种类**（`artifact_kind: concept`，目录 `wiki/topics/concepts/`）。概念页只放**扩展语义**——适用条件、易混淆对象、状态作用域、工程映射、关键约束、验证入口。
- **术语的"定义"仍留在 `docs/project/GLOSSARY.md`**。概念页不复制定义，只用 `source_path` + `source_sha256` 指向术语表并锚住当时的文件哈希。两边各管一处，不产生第二真相源。
- **知识页新增适用条件字段**：`applies_when`、`not_applicable_when`，另有 `preconditions`、`confusable_with`、`supersedes`、`superseded_by`、`derived_from`、`affects`。`problem` 与 `concept` 类的 `applies_when` 必填，`problem` 类的 `not_applicable_when` 必填；`requirement` 类不强制。
- **新规则只对新对象生效**。现有 5 篇 requirement 页一个字段都没有，加字段不能让它们一夜之间变成非法页；`requirement` 类页面只在有值时校验格式。
- 知识回执的页面种类白名单加入 `concept`，其来源必须是术语表或已同步规格。

**不做**：不新建本体层，不引入 OWL 2 / SHACL / 图数据库，不新增技能，不新增流程，不把术语表搬进知识库。

## Capabilities

### New Capabilities

- `concept-pages`: 概念作为可摄入、可核对的知识页形态，与术语表分工而不重叠。
- `knowledge-applicability`: 知识页声明适用条件与不适用条件，并对特定页面种类强校验。

### Modified Capabilities

- `completion-knowledge-ingest`: 问题页必须带适用条件；知识回执可以记录概念页，并约束概念页的来源。

## Impact

- `skill/llm-wiki/scripts/wiki.py`：`SHELL_DIRS` 加入概念目录；lint 的 strict 模式新增适用条件与状态枚举校验。
- `skill/llm-wiki/templates/`：`schema-template.md`、`engineering-template.md`、`index-template.md`。
- `knowledge/project/.wiki-schema.md`：与 schema 模板保持一致。
- `docs/framework/knowledge-policy.md`：§11.12 允许清单加入概念页；末段"术语表不属于知识库"改写为"定义留术语表、扩展语义入库并双向锚定"。
- `skill/matt-pocock/domain-modeling/framework-rules.md`：与政策同步改写同一处边界。
- `tools/framework_core/closure.py`：回执页面种类白名单加入概念页并补来源约束。
- 不新建知识库，不改 alias 注册表，不推送。新增目录在 `knowledge/` 之内，不触发分发清单的顶层目录白名单。

## 边界

概念页属于"其他种类"，按 §11.5 仍需逐次授权：先列出内容、来源、目标 alias 并获本次确认。需求页与已验证问题页的长期授权不因本 change 扩展到概念页。
