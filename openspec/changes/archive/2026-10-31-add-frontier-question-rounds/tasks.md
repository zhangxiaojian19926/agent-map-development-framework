## 1. 提问技法

- [x] 1.1 在 `brainstorming` 的提问环节增加多分支整轮提问小节
- [x] 1.2 写明依赖未决答案的问题属于下一轮
- [x] 1.3 写明事实由 Agent 自查，不转给用户
- [x] 1.4 声明该技法改编自 mattpocock/skills 的 `grilling`

## 2. 接线与归属

- [x] 2.1 `AGENTS.md` 设计阶段说明整轮提问的取用条件
- [x] 2.2 `docs/framework/development-workflow.md` 设计阶段步骤同步
- [x] 2.3 `THIRD_PARTY_NOTICES.md` 说明该技法改编的来源与归属

## 3. 验证

- [x] 3.1 `python3 tools/check-framework` 通过
- [x] 3.2 全量单元测试通过
- [x] 3.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 3.4 规格同步后归档本 change
