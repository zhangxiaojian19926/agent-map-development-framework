# Changelog

## Unreleased — Agent 主导工程初始化

- 逆向只加在原有工作流之前：静态观察调用 `rea analyze`，`run` 和 `network` 不执行。没有校验值的工具不阻断观察，已安装工具不重复下载。没有逆向请求时，初始化、地图、规格和开发流程不变。
- 操作说明收成一套：初始化以 BOOTSTRAP.md 为准，知识内容以 knowledge-policy 11.12 为准。历史验收、实现计划和未归档 change 标明为历史记录。
- 工程初始化建立空知识库壳 `knowledge/project/` 和 alias `project`。工程页面按设计、规格、计划、问题、模块、验证和约束分类。内容仍需确认后摄入；lint 会标出没有知识页的 raw。
- 关系地图只在缺少地图或模块结构、模块间关系变化时更新。模块内部修改保持 CURRENT，不要求重新发布。
- 增加每周 GitHub Release：校验通过且 Unreleased 有内容时递增版本、打 tag 并发布源码说明。
- 关系地图不再调用或探测特定 Coding Agent CLI。任意能读写文件并执行 Python 的当前会话按 v2 协议建图。
- CodeGraph 接受主版本 1。CLI 缺失且当次授予 `index-install` 时，把锁定版本装进目标项目 `.framework/tools/codegraph`；不全局安装，不修改 Agent 配置。已有代码 `init`，已有索引用 `sync`；受管放行列表随源码变化更新。索引 READY 不代替关系地图。
- 增加v2有界分片、逐批可恢复接收和全批聚合；覆盖绑定源码/目录/框架，保留旧v1入口。
- 增加证据化项目/模块dossier、人工正文与受管区块保护、只读模块完整替代入口及开发handoff；doctor新增documentation/coverage/initialization分层状态，新设计待批准和模块变化不会冒充完成。
- 完整初始化入口由Agent补齐资料再交接；增强真实验收探针，分别核对remote、HEAD、源码hash及资料结构，不相信宿主自述。
- 修复大小写不敏感文件系统上的链接检查、完整新工程诊断退出码、设计批准路径绑定、旧克隆 Git 环境隔离，以及模块 ID 和路径大小写冲突检测。
- 用户提供模块名称与 URL 键值对或全新需求，由当前 Agent 通过 BOOTSTRAP 选择路线；基础 prepare 不要求先建仓库、选分支或批准业务实现。
- 新增私有启动单快照、输入和目标绑定、逐模块来源版本解析与获取状态；恢复保护已有目录、人工规则和初始化后新增的模块。
- 新增当前会话分析请求/结果接收，不依赖 Codex CLI；接入、理解、开发准备与业务运行分别报告。
- 增加真实宿主 opt-in 验收入口。当前非 Codex 真实执行、跨宿主恢复和最终发布验收仍未完成，详见验收文档；本节不是已发布版本声明。

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
