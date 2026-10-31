## 1. 引入上游文件

- [x] 1.1 放入 `skill/matt-pocock/domain-modeling/` 的 SKILL.md、GLOSSARY-FORMAT.md、ADR-FORMAT.md，与上游 blob sha1 逐字节核对
- [x] 1.2 放入调用形态声明 `agents/openai.yaml`
- [x] 1.3 确认上游 SKILL.md 指向 ADR-FORMAT.md 的链接可解析

## 2. 本框架适配层

- [x] 2.1 写 `framework-rules.md`：术语表落在 `docs/project/`，多上下文用 GLOSSARY-MAP
- [x] 2.2 写明术语表人工维护、懒创建，不由框架生成
- [x] 2.3 写明本框架不另建 ADR 集合，并给出决策的三种去处
- [x] 2.4 写明术语确定后必须在代码、项目文档与知识页中使用

## 3. 边界与归属

- [x] 3.1 `docs/framework/knowledge-policy.md` 写明术语表与决策记录不进知识库及其原因
- [x] 3.2 `docs/guide/project-layout.md` 新增术语表的目录归属行

## 4. 计数与文档

- [x] 4.1 `framework-manifest.json` 技能分组计数更新并刷新指纹
- [x] 4.2 `docs/integrations.md` 与 `README.md` 的技能构成说明更新
- [x] 4.3 `THIRD_PARTY_NOTICES.md` 增加来源与适配说明

## 5. 验证

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 全量单元测试通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 规格同步后归档本 change
