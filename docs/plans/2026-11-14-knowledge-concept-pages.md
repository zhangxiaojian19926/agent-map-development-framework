# 实施计划：知识层的概念语义与可纠正性

> 配套维护者 [roadmap 第 8 批](../maintainer/roadmap.md)。
> **配套的 OpenSpec change 尚未创建**——按本计划 Phase 0，字段最终定稿并获评审后才建 change，任务状态只在该 change 的 `tasks.md` 里。
> 本文件只写文件、字段、命令与判据，不重复任务状态。

## 目标

把知识层的"概念语义"和"可纠正性"落成**可校验的字段与状态**，让一条经验能说明"在什么条件下成立、什么条件下不能用"，让一条被推翻的结论能作废而不是继续被召回。

做法是**只扩字段、不加机制**：概念页是知识页的一种形态，术语接缝挂在既有本地层，可纠正性落在既有回执校验里。不新增技能、不新增流程、不建本体层、不引形式化本体工具。

## 为什么不是"再加一层本体"

工程壳已经是三层结构，本体落在第二层（项目语义）与第三层（错误与经验）：

| 层 | 工程壳实体 | 现状 |
|---|---|---|
| 第一层 工程事实 | `framework-manifest.json` 580 条指纹、关系地图、CodeGraph | 满 |
| 第二层 项目语义 | [`openspec/specs/`](../../openspec/specs/) 39 规格 / 234 Requirement / 519 Scenario、`knowledge/project/` | 规格满，知识层薄 |
| 第三层 错误与经验 | `wiki/topics/problems/`、`verified-problem.json`、`knowledge-receipt.json` | 空壳 |

**第三层从未被填过**：知识库 5 篇页面全是需求规格的镜像，`problems/`、`entities/modules/`、`synthesis/decisions/`、`sources/verifications/`、`topics/constraints/` 全部只剩 `.gitkeep`。补第三层的收益远大于新造一层。

## 现状证据

以下均为逐文件读取所得，行号对应本仓库当前状态：

| 事实 | 出处 |
|---|---|
| 知识页 frontmatter 只有 `type`/`artifact_kind`/`created`/`confidence`/`status`/`module_ids`/`source_path`/`source_sha256`/`problem_id`/`sources` | [`engineering-template.md`](../../skill/llm-wiki/templates/engineering-template.md) |
| `status` 枚举只有 `approved`/`verified`/`temporary-workaround` | [`.wiki-schema.md`](../../knowledge/project/.wiki-schema.md) |
| lint 的 frontmatter 校验只查 `type` 与 `created` 非空 | `skill/llm-wiki/scripts/wiki.py:248-252` |
| KB 目录清单在 `SHELL_DIRS` 常量里 | `skill/llm-wiki/scripts/wiki.py:15-21` |
| 回执页种类白名单只有 `requirement` 与 `problem` | `tools/framework_core/closure.py:70` |
| 回执校验逻辑在 `knowledge_receipt_detail()` | `tools/framework_core/closure.py:96-140` |
| 状态词典是**双向校验**的：文档写的状态码必须在 `tools/` 或 `skill/` 的 `.py`/`SKILL.md` 里真的出现 | `tools/check-framework:347` `status_dictionary_errors` |
| 术语表被**两处独立明文**排除在知识库外 | [`knowledge-policy.md`](../framework/knowledge-policy.md) §11.12 末段；[`domain-modeling/framework-rules.md`](../../skill/matt-pocock/domain-modeling/framework-rules.md) |
| 15 条工作流的 `SKILL.md` 是 `combinations.json` 的生成物 | `tools/framework_core/workflows/routers.py` |

## 数据模型

### 知识页 frontmatter 扩展

全部为**可选字段**，只对特定 `artifact_kind` 强校验。这是向后兼容的关键——现有 5 篇 requirement 页一个字段都没有，加字段不能让它们一夜之间变成非法页。

| 字段 | 类型 | 含义 | 约束 |
|---|---|---|---|
| `applies_when` | string | 适用条件：这条结论在什么前提下成立 | 必填（`problem`/`concept`） |
| `not_applicable_when` | string | 不适用条件：什么情况下不能用它 | 必填（`problem`） |
| `preconditions` | list | 前置条件清单 | 可选 |
| `confusable_with` | list | 易混淆对象的 concept 页路径 | 可选，建议 `concept` 填 |
| `supersedes` | string | 本页取代的旧页路径 | 可选 |
| `superseded_by` | string | 取代本页的新页路径 | `status: superseded` 时必填 |
| `derived_from` | list | 支撑本页的事件页路径 | 可选 |
| `affects` | list | 本页约束的工程位置：文件、断言、动作前检查 | 可选 |

### 状态机

保留现有三个状态，新增三个：

| 状态 | 含义 | 处置 |
|---|---|---|
| `approved` | 已批准，可用 | 保留，语义不变 |
| `verified` | 经验证通过，可用 | 保留，语义不变 |
| `temporary-workaround` | 根因未消除，不算已解决 | 保留不变 |
| `superseded` | 被新页取代，旧页保留但不作数 | 新增 |
| `retracted` | 结论不成立，撤回 | 新增 |
| `needs-review` | 结论被质疑，等复核，不得继续当规则用 | 新增 |

三条硬规则：

1. `superseded` 必须有 `superseded_by` 指向一个真实存在的页。
2. `retracted` 必须写撤回理由，且不再被任何页的 `applies_when` 引用。
3. 进入 `needs-review` 时，引用它的测试断言与 Skill 必须一并进待复核。

### 事件与经验

一次事件不等于一条经验。用 `derived_from` 表达"这条经验由哪些事件支撑"，一条经验可由多个事件支撑，一个事件也可支持多条经验。两者共用 `artifact_kind: problem`，靠 `type` 与 `derived_from` 区分。

### 术语表接缝

**定义只留一处**：

- 术语的**定义**留在 `docs/project/GLOSSARY.md`（人工维护，位置不动）。
- concept 页只放**扩展语义**：适用条件、易混淆对象、状态作用域、工程映射、关键约束、验证入口。
- 双向锚定：concept 页的 `source_path` 指向 `docs/project/GLOSSARY.md`，`source_sha256` 记录当时的文件哈希。术语改了而 concept 页没改，哈希失配即报出。

两边都不复制对方的正文，因此不产生第二真相源——这与"不建独立 ADR 集合"是同一条原则。

## 文件清单

| 文件 | 动作 | 说明 |
|---|---|---|
| `skill/llm-wiki/scripts/wiki.py:15-21` | 改 | `SHELL_DIRS` 加 `wiki/topics/concepts` |
| `skill/llm-wiki/scripts/wiki.py:248-252` | 改 | lint 的 strict 模式增：`problem`/`concept` 的 `applies_when` 非空、`status` 在允许枚举内 |
| `skill/llm-wiki/templates/schema-template.md:8-10` | 改 | 目录表加 concepts；`artifact_kind` 枚举加 `concept`；`status` 枚举扩三项；frontmatter 字段行重写 |
| `skill/llm-wiki/templates/engineering-template.md:1-13` | 改 | frontmatter 增 8 个可选字段；正文"记录"段增触发条件、被排除的解释、不适用条件三行 |
| `skill/llm-wiki/templates/index-template.md:5` | 改 | 空目录说明补 `topics/concepts` |
| `skill/llm-wiki/SKILL.md` | 改 | 说明 lint 现在校验什么、concept 页的来源要求；规则本身仍只写在 knowledge-policy |
| `knowledge/project/.wiki-schema.md:8-10` | 改 | 与 schema-template 保持一致 |
| `docs/framework/knowledge-policy.md:150-160` | 改 | §11.12 允许清单加 `concept` 一行，目录 `wiki/topics/concepts/` |
| `docs/framework/knowledge-policy.md:162` | 改 | 改写"术语表不属于知识库"那句：定义仍留 GLOSSARY，扩展语义以 concept 页入库并带来源哈希 |
| `skill/matt-pocock/domain-modeling/framework-rules.md:8-26` | 改 | 同步改写为"定义 / 扩展语义 / 双向锚定"三段 |
| `skill/matt-pocock/diagnosing-bugs/discipline.md` | 改 | 新增"归因"一节：五层表 |
| `tools/framework_core/closure.py:70` | 改 | kind 白名单加 `concept`；给 concept 补来源约束 |
| `tools/framework_core/closure.py:96-140` | 改 | 新增 v2 回执分支校验 `influenced[]`；v1 回执按老规则放行 |
| `docs/guide/framework-model.md:161-168` | 改 | §7.4 状态词典新增三项 |
| `framework-manifest.json` | 改 | 全部改完后由 `tools/update-manifest` 重算，不手改 |

## 失败归因五层

`diagnosing-bugs/discipline.md` 新增一节，把"这次失败该改哪一层"写清楚：

| 层 | 含义 | 该动什么 | 落到哪 |
|---|---|---|---|
| 内容层 | 概念缺失或混淆 | 补概念、拆概念 | concept 页 |
| 访问层 | 知识在但检索不到、条件不匹配 | 索引与适用性过滤 | 字段与查询 |
| 验证层 | 已知约束却没执行检查 | 工作流与验证工具 | 流程与断言 |
| 流程层 | 步骤顺序、授权、门禁错 | 流程契约 | `development-workflow.md` |
| 方法层 | 抽取策略系统性漏 | 改抽取方法 | 需跨任务验证 |

这五层与 [`knowledge-policy.md`](../framework/knowledge-policy.md) §11.9 的多模块归属是两件事：归属决定写到哪个库，归因决定该改哪一层。

## 知识生效追踪

回执升级为带版本的形式，只有 v2 才校验生效记录，v1 回执按老规则放行：

```json
{
  "schema": "knowledge-receipt/v2",
  "change": "<change-id>",
  "alias": "project",
  "pages": [],
  "influenced": [
    { "page": "wiki/topics/problems/x.md", "task_id": "T3", "file": "src/a.py", "assertion": "test_x" }
  ],
  "problem": { "status": "not_applicable", "reason": "..." }
}
```

校验：`influenced[].page` 必须在 `pages` 里；`influenced[].task_id` 必须在该 change 的 `tasks.md` 里存在。

## 分期

每期独立交付、独立归档，不必等五期全完。闭环判据一律是门禁通过，不是"看起来做完了"。

### Phase 0 · 规格与字段设计

产出两个 change，字段表、状态机、关系设计逐条落进 `proposal.md` 与 `design.md`，切片写入各自 `tasks.md`。

- Change A `add-concept-pages-and-applicability`：capability `concept-pages`、`knowledge-applicability`
- Change B `add-knowledge-correction-and-influence`：capability `knowledge-correction`、`knowledge-influence-tracking`

判据：`openspec validate --all --strict --no-interactive` 结构有效；用户认可与 schema 校验分别记录。**Phase 2 涉及改既定规则，这一期就要过评审，不能拖到实现期。**

### Phase 1 · 字段能填

扩模板、扩 schema、加目录。**此时不强制、不校验，只提供形态。**

判据：初始化出的空 KB 含 `wiki/topics/concepts/`；一张 concept 页能过 `lint --strict`；现有 5 篇 requirement 页不受影响、lint 仍 PASS；`check-framework` PASS。

### Phase 2 · 字段必填 + 术语接缝

lint 增校验；改 `knowledge-policy.md:162` 与 `domain-modeling/framework-rules.md:8-26` 两处既定规则。**这是全方案风险最高的一期。**

判据：缺 `applies_when` 的 problem 页被报出；术语表条目指向 concept 页，concept 页的 `source_sha256` 与 GLOSSARY 实文件匹配；GLOSSARY 改了而 concept 页未改则失配被报出；概念页与术语表不重复存定义（评审检查项）。

### Phase 3 · 结论能撤回

加三个状态，把状态机变成代码。**这是唯一需要写逻辑而不只是改字段的一期。**

判据：`superseded` 页缺 `superseded_by` 被报出；`retracted` 页仍被某页的 `applies_when` 引用被报出；状态词典的三个码在 `closure.py` 里真的被发出；撤回一页时引用它的下游被列出而不是静默保留。

### Phase 4 · 生效可追踪 + 失败有归属

回执加 `influenced[]`；调试纪律加归因五层；doctor 的 `knowledge` 维度加引用计数与"从未被引用"清单（加字段，不加状态码）。

判据：缺 `influenced` 的 v2 回执被报出；`influenced[].task_id` 不在 `tasks.md` 里被报出；归因表能覆盖五层。

## 门禁影响矩阵

| 门禁 | 为什么碰到 | 怎么过 | 触发期 |
|---|---|---|---|
| `check-framework` 指纹比对 | 改任何文件后 sha256 与磁盘不符 | 改完跑 `tools/update-manifest` 重算，不手改 | 每期收尾 |
| `check-framework` `status_dictionary_errors` | §7.4 新增三个状态码 | 代码里必须真的发出，`closure.py` 同步实现状态校验 | Phase 3 |
| `check-framework` `local_layer_errors` | 改 `domain-modeling/framework-rules.md` 正文 | 该文件已在 `skill/local-layers.json` 登记且已在 AGENTS.md 被提及，无需新增登记 | Phase 2 |
| `check-framework` `skill_routing_errors` | 不触发 | 不新增技能即不触发 | — |
| `check-framework` `unexpected file` | 不触发 | 不新增顶层目录 | — |
| `check-changes` | 回执格式加 `influenced` | v2 才校验，v1 按老规则放行 | Phase 4 |
| `openspec validate --strict` | 新增两个 change 与四个 capability | delta spec 写全 Requirement 与 Scenario | Phase 0 起每期 |
| `unittest` | lint 规则、closure 规则、状态机有新行为 | 先写会失败的测试再实现，新增用例挂在既有测试文件 | Phase 1/3/4 |

**没有一条需要新增门禁。** 这是"只扩字段、不加机制"的直接收益。

## 迁移与兼容

原则：**新规则只对新对象生效，旧对象不追溯。** 每期可独立上线，不需要数据迁移窗口。

| 现有对象 | 会不会被打到 | 处理 |
|---|---|---|
| `knowledge/project/wiki/topics/requirements/` 5 篇 | 会——没有新字段 | `requirement` 类不做必填校验，lint 只在有值时校验格式。回归基线必须保持 PASS |
| 31 个已归档 change | 不会 | 归档产物不可变，本计划不触碰 |
| 2 个活跃 change | 可能——回执格式变化 | 回执加 `schema: knowledge-receipt/v2`，只有 v2 才校验 `influenced`。两个 change 当前任务未全勾，暂不触发 |
| 39 个能力规格 | 不会 | 规格不动。新增四个 capability 作为 delta spec 独立存在 |
| 采用方项目的 `docs/project/GLOSSARY.md` | 会——概念页要指向它 | 按 concept 页的 `source_sha256` 自动锚定，无需人工改 |
| 采用方已有的知识页 | 可能——schema 枚举变了 | 旧页因为不强校验不会立刻变红 |

## 风险

| 风险 | 缓解 |
|---|---|
| 状态词典改了、代码没改，CI 报"documents status X which the shipped code never emits" | Phase 3 第一个切片就是改代码而不是改文档；文档切片依赖代码切片，写进 `tasks.md` 的阻塞关系 |
| 两处规则改动只改一处，造出"政策说 A、本地层说 B"的矛盾 | 机器门禁查不出来。把"两处措辞一致"做成一条可机器检查的测试，而不是靠评审记忆 |
| 概念页变成"看着语义、无法核对" | concept 页必须有 `source_path` + `source_sha256` + `confidence`；`closure.py` 校验来源指向 GLOSSARY 或已同步规格，不指向就报出 |
| 评审否掉术语接缝 | Phase 0 带备选方案 B：只加链接不动政策。退回成本约半天 |
| 字段太多，摄入变慢 | 只有两个字段必填且只对 problem/concept 生效。Phase 1 先只提供不强制，用真实摄入体验决定要不要收紧 |
| 第三层仍然没人填 | Phase 4 的 `influenced` 让"知识改变了什么"可见，doctor 暴露从未被引用的页。但真正的解法是有人真的开始写 concept 页——不能用"机制已具备"冒充"经验层已启动" |

## 工期

估算，未经 spike 验证，按熟悉本仓库的人加 AI 辅助计，流程开销已计入。

| 期 | 人日 |
|---|---|
| Phase 0 规格与字段设计 | 0.5–1 |
| Phase 1 字段能填 | 1–1.5 |
| Phase 2 字段必填 + 术语接缝 | 1–2 |
| Phase 3 结论能撤回 | 1.5–2 |
| Phase 4 生效可追踪 + 失败有归属 | 2–2.5 |
| 合计 | **6–9** |

效果评测（时间切分双组）不在本计划内，另立项。

**推荐先做 Phase 0 + Phase 1（1.5–2.5 人日）。** 它只扩形态不强制，风险最低，而且能让人真写几页，看清 8 个字段里哪几个真被用、哪几个永远空着。字段设计就是呈现位设计，定错了后面全要返工。

## 明确不做

- 不建 `ontology/` 目录，不加"本体引擎"：文章自己反对"再搭一层"，而工程壳已是三层结构。
- 不引入 OWL 2 / SHACL / 图数据库：工程实践不必一开始就使用完整的形式化语言；版本化的概念定义、关系类型和规则文件足以承担这些职责。
- 不把术语表搬进知识库：那是推翻既定规则而不是集成。正确做法是术语表指向知识库，知识库成为扩展语义的权威副本。
- 不拿文章里的 58%→65% 当本工程的验收标准：该数字无样本量、无置信区间、无分层对照、成本未披露，只能当方向性信号。

## 证据分级

- **已确认**：所有带文件路径与行号的现状描述，均为逐文件读取所得。仓库现状由实跑 `tools/check-framework` 与 `tools/check-changes` 确认（均 PASS）。
- **设计**：字段清单、状态机、门禁影响矩阵、回执 v2 结构、归因五层、分期切法是设计产物，尚未实现，可被评审推翻。
- **未验证**：工期未经 spike；状态词典双向校验在真实改动下的具体报错行为未实测；采用方项目的迁移表现未验证；概念页的实际写作成本与认知负担未测。
