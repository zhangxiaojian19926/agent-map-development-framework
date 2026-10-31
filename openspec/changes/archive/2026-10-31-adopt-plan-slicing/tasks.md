## 1. 引入上游技能文件

- [x] 1.1 放入 `skill/matt-pocock/to-tickets/SKILL.md`，与上游 blob sha1 逐字节核对

## 2. 本地计划格式层

- [x] 2.1 写 `plan-format.md`：切片落地位置、每条切片的必备字段、任务右尺寸、逐步粒度、文件结构映射、范围检查
- [x] 2.2 迁入跨模块字段：依赖顺序、接口责任、可并行边界、集成验收、恢复方式
- [x] 2.3 迁入计划文档头、任务块模板、占位符禁令与自查清单
- [x] 2.4 迁移计划评审模板并附来源声明

## 3. 下线旧技能并更新引用

- [x] 3.1 删除 `skill/super-powers/writing-plans/`
- [x] 3.2 更新 `brainstorming/SKILL.md` 的后续技能指向（正文、流程图与清单）
- [x] 3.3 全仓搜索确认无残留的旧技能引用（历史归档与历史 change 记录除外）

## 4. 工作流与计数

- [x] 4.1 `AGENTS.md` 阶段路由的计划阶段改为新技能
- [x] 4.2 `docs/framework/development-workflow.md` 计划阶段步骤改写为切片与阻塞边
- [x] 4.3 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.4 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.5 `THIRD_PARTY_NOTICES.md` 说明两个来源在本次变更后的归属

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
