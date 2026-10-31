## 1. 引入上游技能文件

- [x] 1.1 放入 `skill/matt-pocock/tdd/SKILL.md`、`tests.md`、`mocking.md`，与上游 blob sha1 逐字节核对
- [x] 1.2 确认三个文件的内部相对链接在分发仓库内可解析

## 2. 编写本地合规附录

- [x] 2.1 迁入 Iron Law 与"先看它失败"的强制要求
- [x] 2.2 迁入合理化对照表、红旗清单与完成核对表
- [x] 2.3 补入本框架自有的 seam 预确认要求
- [x] 2.4 写明重构归属：实现阶段仅任务内整理，设计级重构归评审阶段
- [x] 2.5 合入上游 `writing-good-tests.md` 的测试判据，并在文件头声明来源与改编范围

## 3. 下线旧技能并更新引用

- [x] 3.1 删除 `skill/super-powers/test-driven-development/`
- [x] 3.2 更新 `systematic-debugging/SKILL.md` 的技能引用
- [x] 3.3 更新 `writing-skills/SKILL.md` 与 `testing-skills-with-subagents.md` 的引用与示例
- [x] 3.4 更新 `using-superpowers/references/hermes-tools.md` 的示例命令
- [x] 3.5 全仓搜索确认无残留的旧技能引用（历史创作记录除外）

## 4. 工作流与计数

- [x] 4.1 `AGENTS.md` 阶段路由的 IMPLEMENT 行改为新技能
- [x] 4.2 `docs/framework/development-workflow.md` 实现阶段更新技能与重构归属表述
- [x] 4.3 `docs/guide/daily-development.md` 的主流程表述保持一致（仅用通用表述，无需改动）
- [x] 4.4 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.5 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.6 `THIRD_PARTY_NOTICES.md` 说明两个来源在本次变更后的归属

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过（345 文件 / 25 技能）
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
