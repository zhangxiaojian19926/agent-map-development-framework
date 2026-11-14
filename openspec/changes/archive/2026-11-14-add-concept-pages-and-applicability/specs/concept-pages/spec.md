## Purpose

规定概念作为一种可摄入、可核对的知识页形态：概念页承载适用条件与工程约束等扩展语义，术语的定义仍留在项目术语表，两者用来源路径与哈希双向锚定而不互相复制。

## ADDED Requirements

### Requirement: CP-01 概念是可摄入的知识页种类

系统 SHALL 把概念表达为知识页的一种种类，`artifact_kind` 为 `concept`，目录为 `wiki/topics/concepts/`。系统 MUST NOT 为概念另建一套页面模板或另一套字段定义；概念页 MUST 使用与工程页相同的 frontmatter 与页面模板。系统 SHALL 让知识库的初始化过程建立该目录。

#### Scenario: 初始化出的知识库含概念目录

- **WHEN** 初始化一个项目知识库
- **THEN** 知识库中存在 `wiki/topics/concepts/`，且概念页可使用与其他工程页相同的前置字段

#### Scenario: 概念页与其他知识页共用模板

- **WHEN** 比较概念页的字段声明与工程页的字段声明
- **THEN** 两者使用同一份模板与同一组前置字段，概念页没有独立的一套

### Requirement: CP-02 概念页必须带可核对的来源

系统 SHALL 要求每个概念页声明 `source_path` 与 `source_sha256`。`source_path` MUST 指向 `docs/project/GLOSSARY.md` 或 `openspec/specs/` 下的已同步规格。`source_sha256` MUST 是该来源在写入时刻的内容哈希。系统 MUST NOT 接受来源无法核对的概念页进入知识回执。系统 SHALL 让来源内容改变后能检出概念页的来源哈希失配。

#### Scenario: 概念页来源指向术语表

- **WHEN** 一个概念页的 `source_path` 是 `docs/project/GLOSSARY.md`，其 `source_sha256` 与该文件当前内容一致
- **THEN** 该概念页的来源可被核对，知识回执接受它

#### Scenario: 来源缺失或不可核对被报出

- **WHEN** 一个概念页没有 `source_path` 或 `source_sha256`，或 `source_path` 指向术语表与已同步规格之外的位置
- **THEN** 校验把它报出，不把它当作已核对的概念页

#### Scenario: 术语表改动后能检出失配

- **WHEN** 术语表的内容改变，而某个概念页的 `source_sha256` 仍是旧值
- **THEN** 校验能判定该概念页的来源已失配

### Requirement: CP-03 术语的定义与概念的扩展语义各有唯一归属

系统 SHALL 让术语的**定义**留在项目术语表，由人工维护。系统 SHALL 让概念页只承载扩展语义：适用条件、易混淆对象、状态作用域、工程映射、关键约束与验证入口。系统 MUST NOT 要求概念页复制定义；系统 MUST NOT 要求知识库另存一份术语定义。系统 SHALL 让两者互指：概念页指向术语表的来源路径，术语表条目可指向对应概念页。

#### Scenario: 概念页不复制定义

- **WHEN** 审阅一张概念页
- **THEN** 页面上没有术语的完整定义，定义在 `docs/project/GLOSSARY.md` 中，概念页通过来源路径指向它

#### Scenario: 知识库不是术语的第二份副本

- **WHEN** 检索知识库中的概念内容
- **THEN** 得到的是适用条件与工程约束，而不是一份与术语表重复的词汇表

#### Scenario: 两处可以互相找到

- **WHEN** 术语表中的一个术语已确定且已有对应概念页
- **THEN** 术语表条目能指向该概念页，概念页能通过 `source_path` 找到该术语在术语表中的位置
