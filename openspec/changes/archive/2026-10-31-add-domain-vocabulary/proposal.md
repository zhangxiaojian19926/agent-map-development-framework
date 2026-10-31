## Why

多模块工程里最常见的协作损耗不是接口不一致，而是**词不一致**：同一个概念在产品、模块 A、模块 B 里各有一个名字。于是接口文档要逐个翻译，评审要反复确认"你说的那个 X 是不是我说的那个 Y"。

本框架有 llm-wiki，但知识库存的是"已验证且以后仍值得复用的经验"，**不是项目当前的词汇**。把术语表放进知识库会变成两套来源。

同时，上游的 domain-modeling 技能还提供 ADR（架构决策记录）。但本框架**已经有决策记录机制**：OpenSpec change 的 design 产物（随变更归档）和 `docs/project/architecture.md`。再建一套 `docs/adr/` 就是同一事实的第二个来源，与公共规则冲突。

所以这项能力要分两半处理：**词汇的部分引入，决策记录的部分明确不引入**。

## What Changes

- 引入 `matt-pocock/domain-modeling` 的词汇部分：挑战与词汇表冲突的用词、锐化含糊表达、用具体场景压测概念边界、拿代码与人的说法互相核对。
- 规定术语表落在 `docs/project/GLOSSARY.md`（多上下文时用 `docs/project/GLOSSARY-MAP.md`），人工维护、首个术语确定时才建立，不由框架生成。
- 明确**术语表与决策记录都不进知识库**：术语表是项目当前词汇，决策记录在 OpenSpec change 与项目架构文档里；知识库只存已验证且可复用的经验。
- 明确**本框架不另建 ADR 集合**，并说明决策按性质分别落在 change 的 design、项目架构与约束文档、模块局部规则。
- 规定术语确定后必须在代码、项目文档与知识页中使用同一套词，避免词汇分裂。

## Capabilities

### New Capabilities

- `domain-vocabulary`: 规定项目术语表的落点、维护方式、与知识库和决策记录的边界，以及术语确定后的使用要求。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 新增 `skill/matt-pocock/domain-modeling/`：上游原文三份（SKILL.md、GLOSSARY-FORMAT.md、ADR-FORMAT.md）与调用形态声明一份，加本框架适配层一份。
- 更新 `docs/framework/knowledge-policy.md`：写明术语表与决策记录不进知识库及其原因。
- 更新 `docs/guide/project-layout.md`：新增术语表的目录归属行。
- 更新 `framework-manifest.json` 的技能分组计数与文件指纹，`THIRD_PARTY_NOTICES.md` 增加来源与适配说明，`docs/integrations.md` 与 `README.md` 的技能构成说明。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
