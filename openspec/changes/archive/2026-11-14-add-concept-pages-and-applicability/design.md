## Context

知识层的形态由三处共同定义：`skill/llm-wiki/templates/schema-template.md`（空库初始化时的 schema）、`knowledge/project/.wiki-schema.md`（本仓库已实例化的项目库）、`skill/llm-wiki/templates/engineering-template.md`（页面模板）。校验在 `skill/llm-wiki/scripts/wiki.py` 的 `lint()`，其中 strict 模式目前只检查 frontmatter 的 `type` 与 `created` 非空。回执判定在 `tools/framework_core/closure.py` 的 `_page_detail()`，页面种类白名单只有 `requirement` 与 `problem`。

术语表的归属写了两遍：`docs/framework/knowledge-policy.md` §11.12 末段说"术语表与决策记录不属于知识库内容……术语表是项目当前的词汇，落在 `docs/project/GLOSSARY.md`，人工维护"；`skill/matt-pocock/domain-modeling/framework-rules.md` 第 23–26 行说"The knowledge base does not hold it. … a glossary is current project vocabulary rather than a verified, reusable experience."两处今天措辞一致。

## Goals / Non-Goals

**Goals:**

- 知识页能声明"在什么条件下成立"和"什么条件下不成立"，并对问题页与概念页强校验。
- 概念这种语义有可核对的落点：带来源路径、来源哈希与置信度，能被机器校验。
- 术语定义只有一份，扩展语义只有一份，两者互相锚定，术语改动能被检出。
- 新规则只对新对象生效，旧页与旧回执不追溯。

**Non-Goals:**

- 不建本体层，不引形式化本体工具与图数据库。
- 不新增技能、不新增流程、不改 15 条路由的组合。
- 不把术语表搬进知识库，不改 `docs/project/GLOSSARY.md` 的位置与人工性质。
- 不实现结论撤回与知识生效追踪——那是 `add-knowledge-correction-and-influence` 的范围。
- 不回填 `knowledge/project/` 里已有的 5 篇需求页。

## Decisions

1. **概念页是知识页的一种形态，不是新的一层。** `artifact_kind` 加 `concept`，目录 `wiki/topics/concepts/`，模板仍是 `engineering-template.md`。不引入第二种页面模板，避免"同一套字段写两遍"。

2. **定义留术语表，扩展语义进知识库。** 概念页的 `source_path` 指向 `docs/project/GLOSSARY.md`，`source_sha256` 记录当时的文件哈希。术语表条目写定义，概念页写适用条件、易混淆对象、状态作用域、工程映射、关键约束、验证入口。两边都不复制对方的内容——如果两边都写定义，就是第二真相源，违反框架既有原则（与"不建独立 ADR 集合"同一条）。术语表改动后概念页哈希失配即报出。

3. **八个字段全部可选，只有两条强校验。** `applies_when` 与 `not_applicable_when` 是语义核心，必填范围限定在 `problem` 与 `concept` 类。`requirement` 类不强校验——现有 5 篇页面没有这些字段，强制会让它们立刻变成非法页。`preconditions`、`confusable_with`、`supersedes`、`superseded_by`、`derived_from`、`affects` 全部可选，为后续的撤回与生效追踪预留位置，但在本 change 里不校验。

4. **lint 的 strict 模式按页面种类分别校验。** 现有校验用正则找 `key: 非空`，扩展为：按 `artifact_kind` 取该种类的必填字段集合，缺失才报错。`requirement` 类不在必填集合里。

5. **概念页进入回执白名单，但只放宽白名单不加必填。** `_page_detail()` 的种类白名单加 `concept`，并给它一条来源约束：来源必须是 `docs/project/GLOSSARY.md` 或 `openspec/specs/` 下的已同步规格。回执里没有概念页不算缺陷——概念页是项目词汇，不是某个 change 的完成证明。

6. **两处规则同改，且加一条机器检查。** 政策与本地层今天各说一遍，改的时候必须同改。`local_layer_errors` 只查"登记项存在且被活文档提及"，查不出两处措辞不一致，所以本 change 额外加一条测试，比对两份文件里的同一组关键句。

7. **schema 与模板同步，实例库同步跟上。** `schema-template.md` 是空库初始化的来源，`knowledge/project/.wiki-schema.md` 是本仓库已实例化的库。两者今天内容一致，改一处必须改另一处，否则新初始化出来的库和本仓库的库形态不同。

8. **概念页的写入仍需逐次授权。** 概念页属 §11.5 的"其他种类"，先列内容、来源、目标 alias 获本次确认。需求页与已验证问题页的长期授权不扩展。

## Risks / Trade-offs

- [字段变多，摄入变慢] → 只有两条必填且只对问题页与概念页生效；`requirement` 类完全不受影响。第一版先把字段提供出来，不强制，用真实摄入体验决定要不要收紧。
- [概念页退化成"看着语义、无法核对"的事实源] → 概念页必须有 `source_path` + `source_sha256` + `confidence`；回执校验其来源必须指向术语表或已同步规格，不指向就报出。
- [概念页与术语表内容重复，形成第二真相源] → 定义只在术语表，概念页只放扩展语义；评审把"是否重复存定义"列为检查项，并由新增的一致性测试守住两处措辞。
- [政策与本地层只改一处] → 两条规则同改，并新增机器检查比对两份文件的关键句。
- [现有 5 篇需求页变成非法页] → `requirement` 类不做必填校验，回归基线必须保持 PASS。

## Migration Plan

1. 先扩 schema、模板、目录与白名单，只提供形态不强制。
2. 再开 lint 的适用条件校验，并同步改政策与本地层。
3. 回退时撤掉校验与字段声明。已写入的概念页保留，不删除。

## Open Questions

无。字段清单与分工见 `docs/plans/2026-11-14-knowledge-concept-pages.md` 的数据模型一节。
