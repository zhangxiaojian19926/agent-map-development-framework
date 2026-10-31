## 1. 引入技能文件

- [x] 1.1 建立 `skill/matt-pocock/` 分组，放入上游 LICENSE
- [x] 1.2 放入 `writing-for-agents/SKILL.md` 与 `SKILL-MECHANICS.md`
- [x] 1.3 放入 `codebase-design/SKILL.md`、`DEEPENING.md` 与 `DESIGN-IT-TWICE.md`
- [x] 1.4 核对子文档相对链接在分发仓库内可解析

## 2. 归属与清单

- [x] 2.1 `THIRD_PARTY_NOTICES.md` 增加第四个来源段，写明来源、许可、版权归属、上游固定提交与本地适配说明
- [x] 2.2 `framework-manifest.json` 的 `sources` 增加该上游及其固定提交
- [x] 2.3 `framework-manifest.json` 的 `skills` 增加对应分组计数，与实际技能入口数一致
- [x] 2.4 运行 `tools/update-manifest` 刷新文件指纹

## 3. 工作流接线

- [x] 3.1 `docs/integrations.md` 列出新分组并更新技能计数
- [x] 3.2 `README.md` 的技能构成说明补上新分组
- [x] 3.3 `AGENTS.md` 在阶段路由后说明两个参考技能的取用条件
- [x] 3.4 `docs/framework/development-workflow.md` 在设计环节说明可用的接口设计参考
- [x] 3.5 `docs/framework/skill-policy.md` 说明该分组属于参考型技能，不引入执行型义务

## 4. 验证

- [x] 4.1 `python3 tools/check-framework` 通过（326 文件 / 25 技能）
- [x] 4.2 全量单元测试通过
- [x] 4.3 `openspec validate --all --strict --no-interactive` 通过（14 项）
- [x] 4.4 引入文件与上游字节一致（git blob sha1 逐个核对）
- [x] 4.5 规格同步后归档本 change
