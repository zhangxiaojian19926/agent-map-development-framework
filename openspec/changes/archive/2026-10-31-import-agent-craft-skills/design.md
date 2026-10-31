## Context

mattpocock/skills 是一个按“用户调用 / 模型调用”分层的开源技能库（MIT）。它与本框架的 OpenSpec、superpowers 不在同一层：OpenSpec 管需求与完成状态，superpowers 管流程骨架，mattpocock 管工程技艺。因此引入它不会产生第二套规格来源。

本次只取两个纯参考型技能，理由是它们改造量最低且直接补空白：

| 技能 | 上游路径 | 依赖 | 缺口 |
|---|---|---|---|
| writing-for-agents | skills/productivity/writing-for-agents | 无外部依赖，仅自身子文档 | 仓库缺“给 agent 写文档”的方法论 |
| codebase-design | skills/engineering/codebase-design | 无外部依赖，仅自身子文档 | 协作规则只管模块间，缺模块内接口语言 |

## Decisions

**放在独立分组 `skill/matt-pocock/`，不并入 superpowers。**
两个上游是 MIT 许可的第三方内容，与 superpowers（也是第三方）保持同等地位。并入会让上游归属变得不可追溯，也会让清单的分组计数失去意义。

**只复制原文，不改写方法论。**
两个技能是纯参考文档，没有 issue tracker、领域词汇表或宿主能力依赖，因此不需要适配。改写会让“本地适配”与上游原文的边界模糊，后续升级无法比对。

**不带入 `agents/openai.yaml`。**
上游用该文件区分“用户调用 / 模型调用”两种调用形态。本框架当前所有技能都是模型调用形态，引入该机制需要同时改造现有 23 个入口并新增一致性断言，属于独立变更，不在本次范围内。本次保持形态一致。

**不带入上游其余技能。**
上游的 `to-spec` / `to-tickets` / `implement` / `implement-spec` / `wayfinder` 构成一条与 OpenSpec 竞争的规格体系；`triage` / `setup-matt-pocock-skills` 是 issue tracker 运维；`misc/` 上游自述冻结；`in-progress/` 上游自述未稳定。这些都不引入，理由随本次记录保留。

**工作流接线为“参考”而非“步骤”。**
两个技能不进入 AGENTS.md 的阶段路由表作为必做步骤，而是挂在相应阶段的“可用参考”位置：写作参考属于技能与 AGENTS.md 的编写工作，不属于产品开发的 11 个阶段；接口设计参考挂在 DISCOVERY 与 PLAN 的设计讨论环节。

## Risks

- 上游后续变更需要比对升级。清单登记上游固定提交与技能文件指纹，沿用 superpowers 与 OpenSpec 的既有做法。
- 引入后技能总数增加，描述常驻上下文的负担随之增加。这由 writing-for-agents 自身的指针纪律约束，不在本次引入范围内治理。

## Migration

无破坏性变更。技能计数从 23 变为 25，清单与文档同步更新。不涉及初始化、CLI、逆向与发布流程。
