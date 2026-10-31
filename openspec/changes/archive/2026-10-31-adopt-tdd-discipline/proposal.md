## Why

工程壳的 IMPLEMENT 阶段只绑定 `superpowers:test-driven-development`。那个技能在**行为合规**上很强（Iron Law、十二行合理化对照表、红旗清单），但在**测试工程技艺**上有三处空白：

1. **没有 seam 概念。** 公共协作规则规定模块接口双方、输入输出和错误模式，但没有任何一步要求"先确认在哪个 seam 测"。于是测试写在实现内部还是接口上，全凭 Agent 临场判断。
2. **没有识别同义反复的断言。** `expect(add(a, b)).toBe(a + b)` 这类断言按构造就永远通过，不可能与代码分歧；期望值必须来自独立真值源（已知字面值、算例或规格）。现有技能不覆盖这一类失败。
3. **没有禁止水平切片。** "先写全部测试再写全部实现"验证的是想象中的行为，必须一测一实现地垂直推进。

同时，superpowers 的 TDD 技能内部散落着对本仓库不成立的假设：示例全是 TypeScript/Jest，重构被放在红绿循环内（与本框架 §8 的五步循环冲突），且不说明重构与实现阶段的边界。

## What Changes

- 引入 `matt-pocock/tdd` 作为实现阶段的主技能：seam 预确认（未经确认的 seam 不写测试）、好测试的判据、垂直切片推进、独立真值源、独立于循环的重构，以及配套的测试示例与 mock 边界参考。
- 把 superpowers TDD 的合规强度保留为同目录的本地附录：Iron Law、合理化对照表、红旗清单、完成核对表，并补入本框架自有的 seam 确认要求与重构归属约定。
- 下线 `superpowers:test-driven-development`，更新引擎内部的交叉引用、阶段路由表、完整开发流程和技能计数。
- 明确重构的归属：实现阶段的重构步只做当前任务必要的整理，设计级重构归入评审阶段讨论。

## Capabilities

### New Capabilities

- `tdd-practice`: 规定实现阶段的测试驱动纪律，包括 seam 确认、好测试判据、垂直切片、合规层与重构归属。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- `skill/matt-pocock/tdd/`：上游原文三份（SKILL.md、tests.md、mocking.md）加一份本地合规附录。
- 删除 `skill/super-powers/test-driven-development/`。
- 更新 `skill/super-powers/` 内部四处交叉引用（systematic-debugging、writing-skills 及其测试说明、hermes-tools 参考）。
- 更新 `AGENTS.md` 阶段路由、`docs/framework/development-workflow.md` 实现阶段与 `docs/guide/daily-development.md`。
- 更新 `framework-manifest.json` 的技能分组计数与文件指纹，`THIRD_PARTY_NOTICES.md` 说明两个来源在本次变更后的归属。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
