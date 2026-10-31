# domain-vocabulary Specification

## Purpose

规定项目术语表的落点、维护方式与使用要求，并明确它与知识库、决策记录的边界。目的��让多模块工程用同一套词说话，同时避免为同一事实建立第二处来源。

## Requirements

### Requirement: 术语表落在项目文档

系统 SHALL 把项目术语表落在 `docs/project/GLOSSARY.md`；存在多个语境时使用 `docs/project/GLOSSARY-MAP.md` 指向各语境的术语表。系统 SHALL 把术语表作为人工正文维护，SHALL NOT 由框架生成。系统 SHALL 在首个术语确定时才建立术语表，SHALL NOT 建立空文件。

#### Scenario: 首个术语确定

- **WHEN** 项目中第一个领域术语被确定
- **THEN** 建立 `docs/project/GLOSSARY.md` 并写入该术语及其应避免的同义词

#### Scenario: 尚无术语

- **WHEN** 项目还没有任何确定的领域术语
- **THEN** 不建立空的术语表文件

#### Scenario: 多个语境

- **WHEN** 项目存在多个语境且术语不通用
- **THEN** 使用 `docs/project/GLOSSARY-MAP.md` 指向各语境的术语表，并说明语境之间的关系

### Requirement: 词汇冲突当场处理

系统 SHALL 在用户使用的词与术语表冲突时立即指出并询问以哪个含义为准。系统 SHALL 在一个词承载多个含义时给出规范术语并记录应避免的同义词。系统 SHALL 用具体场景压测概念边界，并在用户的说法与代码不一致时把矛盾提出来。

#### Scenario: 用词与术语表冲突

- **WHEN** 用户使用的词与术语表中的定义冲突
- **THEN** Agent 指出冲突并询问以哪个含义为准，不默认其中一种

#### Scenario: 说法与代码矛盾

- **WHEN** 用户描述的行为与代码实际行为不一致
- **THEN** Agent 指出矛盾，而不是同时接受两种说法

#### Scenario: 术语表不含实现细节

- **WHEN** 写入术语定义
- **THEN** 定义说明概念是什么，不说明它怎么实现

### Requirement: 术语表与决策记录不进知识库

系统 SHALL NOT 把术语表或决策记录摄入知识库。系统 SHALL 把术语表视为项目当前词汇，落在项目文档；系统 SHALL 把决策记录落在 OpenSpec change 的设计产物、项目架构与约束文档，或模块局部规则。

#### Scenario: 知识库不收术语表

- **WHEN** 有人提议把术语表摄入知识库
- **THEN** Agent 拒绝并说明：知识库存的是已验证且以后仍值得复用的经验，不是项目当前的词汇

#### Scenario: 决策记录不另立一套

- **WHEN** 出现一个难以逆转的架构决策
- **THEN** Agent 不建立独立的决策记录集合，而是把它落到对应的 change 设计产物、项目架构与约束文档，或模块局部规则

### Requirement: 术语确定后被实际使用

系统 SHALL 要求确定的术语在代码命名、项目文档与知识页中使用同一套词。系统 SHALL 在某个 change 确定了术语时同步更新术语表。

#### Scenario: 术语进入代码

- **WHEN** 某术语被确定
- **THEN** 模块、类型、函数与文件命名使用该术语，不使用同义词

#### Scenario: change 解决术语后同步

- **WHEN** 某个 change 确定或修正了一个术语
- **THEN** 该 change 的工作同时包含对术语表的更新

### Requirement: 技能替换与引用一致

系统 SHALL 引入词汇参考技能并登记来源与适配说明，SHALL 在上游原文与本框架适配层冲突时以适配层为准。

#### Scenario: 上游原文保持不变

- **WHEN** 核对引入的上游文件
- **THEN** 每份文件与上游固定提交的字节一致，适配内容单独成文并声明来源

#### Scenario: 适配层优先

- **WHEN** 上游技能正文与本框架的落点约定冲突
- **THEN** 以适配层为准，例如术语表位置与决策记录的去处
