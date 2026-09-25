# Changelog

## 0.2.0 — 2026-09-25

- 新增 tools/framework：init/new/module clone/add/sync/refresh/doctor/resume，显式能力授权、无写预览、文件归属与中断恢复。
- 模块、仓库、索引分离；CodeGraph 1.6.0 精确范围适配、hooks 共存；Codex CLI 0.151.0 静态分析、证据校验及设计/实际地图分离。
- 新增 project-bootstrap 技能、完整使用教程和 opt-in tools/verify-live；现有知识脚本与写入授权保持兼容。
- macOS/Linux 离线测试与真实模型集成分开；初始化 READY 不代表业务运行验证或生产就绪。

## 0.1.0 — 2026-09-25

- 从项目工作区提取独立公共规则、21 个技能入口及支持资源，不携带项目历史和业务内容。
- 补充接入/集成/验收文档、项目及模块模板、交接与证据模板。
- 公共 llm-wiki 适配为 Python 标准库辅助实现：项目边界内 alias、明确写入确认、无自动注册、拒绝覆盖、批量部分失败可见。
- query/status/lint/graph 只读；delete/digest/crystallize 输出计划，ingest 只准备 raw，Agent 负责知识编译及验证。
- 原有本地脚本接口的行为差异以 SKILL.md 和 integrations 为准；这不是上游原版的无差异镜像。
