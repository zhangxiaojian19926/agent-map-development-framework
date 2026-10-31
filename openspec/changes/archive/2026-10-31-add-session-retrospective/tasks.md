## 1. 引入上游技能文件

- [x] 1.1 放入 `skill/matt-pocock/retro/SKILL.md` 与 `agents/openai.yaml`，与上游 blob sha1 逐字节核对
- [x] 1.2 确认用户调用形态的两种声明同时存在

## 2. 本框架适配层

- [x] 2.1 写 `framework-rules.md`：本框架的证据来源、规范所在、检查入口
- [x] 2.2 写机械规则与判断项的边界在本框架的落法
- [x] 2.3 写候选的呈现要求：证据、动作、成本

## 3. 复盘记录

- [x] 3.1 建立 `docs/maintainer/retro-findings.md`
- [x] 3.2 记录 2026-10-31 会话的候选，逐条标注证据与状态

## 4. 接线与计数

- [x] 4.1 `AGENTS.md` 与 `docs/framework/skill-policy.md` 说明该技能的可用形态
- [x] 4.2 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.3 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.4 `THIRD_PARTY_NOTICES.md` 增加该技能的来源与形态说明

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
