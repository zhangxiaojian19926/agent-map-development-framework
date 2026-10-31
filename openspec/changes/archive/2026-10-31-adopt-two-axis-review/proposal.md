## Why

完整开发流程的 REVIEW 阶段已经写着"先检查需求符合性，再检查实现质量、回归和跨模块接口"——**这就是两轴评审**。但仓库里没有任何方法论支撑这句话：

- `superpowers:requesting-code-review` 提供的是**派发机制与节奏**（何时必须评审、怎么派 reviewer 子代理、用哪个模板），不是评审方法本身。它是单轴的，评审者拿到的指令里规格与规范混在一起。
- 缺少一条可判定的**规范基线**：现在评审"实现质量"只能凭评审者的个人口味。
- 缺少对**跨模块**的评审维度：框架的公共协作规则要求记录接口责任、版本组合和集成场景，但评审环节没有对应动作。
- 缺少对**自查与独立评审**的区分落地：框架 §10 要求"自查不得冒充独立评审"，但没有规定结论怎么写才不越界。

## What Changes

- 引入 `matt-pocock/code-review` 作为评审方法：两轴并行评审（规范轴与规格轴），规范轴带固定的气味基线，两轴结果分开汇报、不得互相掩盖或合并排序。
- 把规格来源从 issue tracker 改为**当前 OpenSpec change**，并规定没有 change 时如实报告"无可用规格"，不得用提交信息或 diff 自述替代需求。
- 增加**集成轴**：跨模块变更需按声明的版本组合评审跨边界正确性，单模块变更显式说明跳过原因。
- 规定结论必须绑定实际评审范围（diff 区间、规格版本、支撑命令），范围变动后需重评或标注失效。
- 规定重要问题闭合后重跑受影响检查，驳回需记录理由；自查必须标注为自查，不得表述为独立批准。

## Capabilities

### New Capabilities

- `code-review-discipline`: 规定评审阶段的方法纪律，包括两轴分离、规格来源、气味基线、集成轴、结论绑定、问题闭合与自查标注。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 新增 `skill/matt-pocock/code-review/`：上游原文一份（SKILL.md）与本框架适配层一份（framework-rules.md）。
- `superpowers:requesting-code-review` 保留：它提供评审的节奏与派发机制；新增指向两轴方法的引用。
- 更新 `AGENTS.md` 阶段路由的评审阶段、`docs/framework/development-workflow.md` 的评审阶段步骤。
- 更新 `framework-manifest.json` 的技能分组计数与文件指纹，`THIRD_PARTY_NOTICES.md` 增加来源说明，`docs/integrations.md` 与 `README.md` 的技能构成说明。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
