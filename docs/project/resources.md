# 资源

| 项 | 值 |
|---|---|
| module-id | `wechat_fenxi` |
| module-root | `modules/wechat_fenxi` |
| 声明 | 仓库根 [framework-project.json](../../framework-project.json) |
| 小程序入口 | `modules/wechat_fenxi/miniprogram/app.json` |
| 后端入口 | `modules/wechat_fenxi/backend/src/server.js` |
| 模块规则 | [AGENTS.md](../../modules/wechat_fenxi/AGENTS.md) |
| Git | 外层仓库，模块内无独立远程 |
| KB alias | 无。NOT_CONFIGURED。未创建 `llm-wiki-aliases.json` |
| 证据 | 后端 `npm test`；源码在模块目录。微信客户端未测 |

技能来源是本仓库 `skill/`（OpenSpec、Superpowers、llm-wiki、project-bootstrap）。查询知识库前先看本表：没有 alias 就不要猜路径或建库。

`module-catalog.generated.json` 与 `.agent-framework/` 尚未生成。分发根不能作为 `init` 的 target。观察目录和 doctor 的 COMPLETE 状态因此还没有。
