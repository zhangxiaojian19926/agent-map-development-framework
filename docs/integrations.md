# 技能及工具集成

## 发布能力

skill/openspec 保存 6 个工作流，skill/super-powers 保存 14 个工作流，skill/llm-wiki 保存知识管理入口及本地辅助脚本。
skill/project-bootstrap 提供接入、刷新与地图 schema 参考；合计 22 个技能入口。
不重复创建竞争版本：一次任务确定一个技能来源，先完整读取该入口及其必需引用。
框架文件不能替代系统/宿主权限；附带技能示例中的自动提交、全局配置或委派建议，仅在当前用户授权且宿主支持时适用。

## 运行依赖

- 公共检查与 llm-wiki 辅助脚本：Python 3.9+ 标准库；Shell 入口使用 Bash。无第三方 pip 依赖。
- Git 工作区及集成：Git CLI。worktree 只在需要隔离且授权时使用。
- OpenSpec 技能：另需兼容的 OpenSpec CLI。来源 https://github.com/Fission-AI/OpenSpec 。使用前检查版本及实际 help/status/instructions，不假定所有版本均支持 store。
- Superpowers 的 JS 可视化及审查辅助：Node.js；Graphviz 渲染示例另需 dot。只有选中相关流程时才检查和使用。
- CodeGraph：可选。已有索引优先；无索引默认 rg。接入 CLI 在当次 index 授权下可初始化/同步，适配及排除范围见 [bootstrap](bootstrap.md)。
- 设备、provider、部署：目标工程提供，公共包不含凭据、服务配置或驱动。

本版不自动安装依赖，不修改机器级插件/技能目录，也不承诺离线运行模型。

## 宿主发现与调用

通用可移植方式：在目标工程入口登记本包位置和明确 SKILL.md 路径，Agent 按阶段读取所选技能后执行其步骤。
如果宿主要求专门的技能目录或插件 manifest，使用该宿主实际支持的项目级方式，经授权配置；本仓库不是可直接安装到所有宿主的插件。
Codex / Claude Code / 其他宿主的工具、委派和权限模型各不相同，实际可用工具优先于附带参考中的旧 API 示例。未完成真实宿主接入测试不能标记已认证。

## 知识入口

所有命令在目标工程内执行；不在框架分发目录推断业务工程。非 Git 工程可使用 framework-project.json 标记根；必要时通过 FRAMEWORK_PROJECT_ROOT 显式指定包含当前目录的根。
注册表是项目内 llm-wiki-aliases.json，alias 值为相对注册表根的目录，禁止 alias 逃逸。独立子仓库不自动越界寻找父工程；跨仓库编排从已确认的编排根进行，或显式指定根。
命令中 KB 的显式路径代表用户选择的目标，仍须核对模块关联、主题和权限。

```bash
bash skill/llm-wiki/scripts/query.sh --all "topic"
bash skill/llm-wiki/scripts/common.sh resolve module-a
bash skill/llm-wiki/scripts/lint.sh module-a --strict
```

建库、注册和 raw 准备是写操作：当前用户授权后，仅为该次命令设置 WIKI_WRITE_CONFIRM=yes。这个参数是误操作防护，不是认证或安全沙箱。
完整步骤与各命令的真实作用见 [llm-wiki](../skill/llm-wiki/SKILL.md)。
