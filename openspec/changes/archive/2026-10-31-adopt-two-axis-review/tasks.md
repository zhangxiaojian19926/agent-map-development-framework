## 1. 引入上游技能文件

- [x] 1.1 放入 `skill/matt-pocock/code-review/SKILL.md`，与上游 blob sha1 逐字节核对
- [x] 1.2 确认上游文件内部的相对链接在分发仓库内可解析

## 2. 编写本框架适配层

- [x] 2.1 写 `framework-rules.md`：规格来源改为 OpenSpec change、没有 change 时的处理
- [x] 2.2 写集成轴的触发条件与跳过说明
- [x] 2.3 写评审范围绑定、结论绑定、问题闭合与自查标注规则
- [x] 2.4 明确上游与本地层的冲突优先级，并覆盖上游的 issue tracker 提示

## 3. 接线

- [x] 3.1 `superpowers:requesting-code-review` 增加指向两轴方法的引用，说明两者的分工
- [x] 3.2 `AGENTS.md` 阶段路由的评审阶段更新
- [x] 3.3 `docs/framework/development-workflow.md` 评审阶段步骤更新

## 4. 计数与文档

- [x] 4.1 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.2 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.3 `THIRD_PARTY_NOTICES.md` 增加该技能的来源与适配说明

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
