## 1. 引入上游技能文件

- [x] 1.1 放入 `skill/matt-pocock/diagnosing-bugs/SKILL.md` 与 `scripts/hitl-loop.template.sh`，与上游 blob sha1 逐字节核对
- [x] 1.2 确认脚本通过 `bash -n` 语法检查

## 2. 本地纪律层与随迁材料

- [x] 2.1 写 `discipline.md`：Iron Law、合理化对照表、红旗清单、人类纠正信号表、三次失败升级判据
- [x] 2.2 补入本框架自有的环境故障规则（INFRA_ERROR 不是 RED 也不是 PASS）与证据绑定规则
- [x] 2.3 迁移三份技法参考：根因回溯、纵深防御校验、条件等待，附来源声明并修正路径引用
- [x] 2.4 迁移二分定位脚本与条件等待示例，用目标语言的注释声明来源
- [x] 2.5 迁移四份验证材料与上游创作史，修正旧路径引用

## 3. 下线旧技能并更新引用

- [x] 3.1 删除 `skill/super-powers/systematic-debugging/`
- [x] 3.2 更新 `using-superpowers/SKILL.md` 的技能引用
- [x] 3.3 更新 `writing-skills/SKILL.md` 的引用示例
- [x] 3.4 全仓搜索确认无残留的旧技能引用（历史归档与历史创作记录除外）

## 4. 工作流与计数

- [x] 4.1 `AGENTS.md` 阶段路由与异常回流改为新技能
- [x] 4.2 `docs/framework/development-workflow.md` 的排障技能与异常回流表更新
- [x] 4.3 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.4 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.5 `THIRD_PARTY_NOTICES.md` 说明两个来源在本次变更后的归属

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
