## Why

工程壳的异常回流只绑定 `superpowers:systematic-debugging`。那个技能在**流程编排**上很强（四阶段、根因优先、三次失败质疑架构），但它的第一阶段只要求"能复现就收集更多数据，不要猜"，缺少一条可判定的门槛：

- 什么算一个**合法的红色信号**？本地技能写的是"Reproduce Consistently … If not reproducible → gather more data, don't guess"，这是软要求。
- 本框架的公共开发流程已经有一条硬规则——"环境故障记 INFRA_ERROR，不是 RED"——但它只写在流程文档里，没有变成诊断过程里的判据。
- 假设阶段本地技能要求"Form **Single** Hypothesis"，而多条排序且各自可证伪的假设是更可靠的排查方法。

## What Changes

- 引入 `matt-pocock/diagnosing-bugs` 作为排障阶段的主技能：先建立能对该 bug 变红的反馈回路并按可勾选的判据收紧它，再排序多个可证伪假设，逐项对应预测地插桩，最小修复后按正确 seam 写回归测试，最后清理插桩与临时产物。
- 把 superpowers 调试纪律保留为同目录的本地改编：Iron Law、合理化对照表、红旗清单、人类纠正信号表，以及"三次修复失败即质疑架构"的升级判据。
- 保留并迁移三份技法参考：根因回溯、纵深防御校验、条件等待（替代固定超时），附二分定位脚本与条件等待示例。
- 保留四份纪律验证材料与上游创作史，随纪律层一起迁移。
- 把本框架的环境故障规则与证据绑定规则写进本地纪律层：环境故障不是 RED，也不是 PASS；结论必须绑定到实际检查的工作树或提交。

## Capabilities

### New Capabilities

- `debugging-discipline`: 规定排障阶段的诊断纪律，包括合法红色信号的判据、反馈回路的收紧、假设排序与可证伪预测、插桩与清理、回归测试的 seam 选择、三次失败升级，以及环境故障与证据绑定的边界。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- `skill/matt-pocock/diagnosing-bugs/`：上游原文两份（SKILL.md、scripts/hitl-loop.template.sh）加本地改编的纪律层与随迁材料。
- 删除 `skill/super-powers/systematic-debugging/`。
- 更新 `using-superpowers` 与 `writing-skills` 的技能引用，以及阶段路由表、完整开发流程的异常回流表。
- 更新 `framework-manifest.json` 的技能分组计数与文件指纹，`THIRD_PARTY_NOTICES.md` 说明两个来源在本次变更后的归属。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
