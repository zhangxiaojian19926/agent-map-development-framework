# Changelog

## 0.1.0 — 2026-09-25

- 从项目工作区提取独立公共规则、21 个技能入口及支持资源，不携带项目历史和业务内容。
- 补充接入/集成/验收文档、项目及模块模板、交接与证据模板。
- 公共 llm-wiki 适配为 Python 标准库辅助实现：项目边界内 alias、明确写入确认、无自动注册、拒绝覆盖、批量部分失败可见。
- query/status/lint/graph 只读；delete/digest/crystallize 输出计划，ingest 只准备 raw，Agent 负责知识编译及验证。
- 原有本地脚本接口的行为差异以 SKILL.md 和 integrations 为准；这不是上游原版的无差异镜像。
