## Purpose

规定知识页声明适用条件与不适用条件：一条经验必须能说清"在什么前提下成立"和"什么情况下不能用它"，并对问题页与概念页强校验、对需求页不强制，保证新规则只对新对象生效。

## ADDED Requirements

### Requirement: KA-01 知识页可以声明适用条件

系统 SHALL 让知识页的 frontmatter 声明 `applies_when` 与 `not_applicable_when`，两者都是自由文本。系统 SHALL 让知识页另外可以声明 `preconditions`、`confusable_with`、`supersedes`、`superseded_by`、`derived_from` 与 `affects`。系统 MUST NOT 要求任何页面声明这八个字段之外的集合。

#### Scenario: 经验能写明成立前提

- **WHEN** 一张知识页声明 `applies_when` 为"请求走了 X 分支且 Y 为空"
- **THEN** 该前提在页面的前置字段里可被读到，不必翻到正文深处

#### Scenario: 能写明不适用情形

- **WHEN** 一张知识页声明 `not_applicable_when` 为"仅 v2 协议"
- **THEN** 该不适用情形与适用条件同样出现在前置字段里

#### Scenario: 附加字段可承载扩展语义

- **WHEN** 一张概念页用 `confusable_with` 指向易混淆对象、用 `affects` 指向受约束的代码位置
- **THEN** 这些关系在页面前置字段里可被读到

### Requirement: KA-02 适用条件对问题页与概念页必填

系统 SHALL 要求 `artifact_kind` 为 `problem` 的页面声明非空的 `applies_when`。系统 SHALL 要求 `artifact_kind` 为 `concept` 的页面声明非空的 `applies_when`。系统 SHALL 要求 `artifact_kind` 为 `problem` 的页面声明非空的 `not_applicable_when`。系统 SHALL 让结构校验按页面种类分别判定必填字段。系统 MUST NOT 让 `requirement` 类的页面因缺少这些字段而被判为不合格。

#### Scenario: 问题页缺适用条件被报出

- **WHEN** 一张问题页没有 `applies_when` 或它为空
- **THEN** 结构校验报出这张页面缺少适用条件

#### Scenario: 问题页缺不适用条件被报出

- **WHEN** 一张问题页有 `applies_when` 但没有 `not_applicable_when`
- **THEN** 结构校验报出这张页面缺少不适用条件

#### Scenario: 概念页缺适用条件被报出

- **WHEN** 一张概念页没有 `applies_when`
- **THEN** 结构校验报出这张页面缺少适用条件

#### Scenario: 需求页不受影响

- **WHEN** 一张需求页没有这些字段
- **THEN** 结构校验不把它报为不合格；这些字段有值时其格式仍被校验

### Requirement: KA-03 新规则只对新对象生效

系统 SHALL 让新增的适用条件字段在引入之后写入的页面上生效。系统 MUST NOT 让引入之前已经存在的知识页因缺少这些字段而失效。系统 SHALL 让既有页面的回归校验保持通过。

#### Scenario: 既有需求页仍然合格

- **WHEN** 一个知识库里已有若干 `requirement` 页且它们没有适用条件字段
- **THEN** 结构校验对它们不出错，页面内容不需要重写

#### Scenario: 引入前的归档不回溯

- **WHEN** 归档目录里存在引入之前写入的知识页
- **THEN** 本能力不对它们提出要求，也不修改它们
