# 协作

当前只有一个顶层模块。小程序是调用方，后端是 HTTP 与摘要的提供方。共享契约是 `miniprogram/utils/limits.js`、同意字段，以及 `/api/policy` 返回的阈值。

| 项 | 说明 |
|---|---|
| 主负责模块 | `wechat_fenxi` |
| 受影响模块 | 无其他产品模块 |
| 接口提供方 | `backend` |
| 接口消费方 | `miniprogram` |
| 集成顺序 | 先保持 limits 与解析/同意行为，再改页面或模型调用 |
| 局部入口 | [modules/wechat_fenxi/AGENTS.md](../../modules/wechat_fenxi/AGENTS.md) |
| 交接 | [handoff.md](handoff.md) |

公共技能和知识规则只从 [开发流程](../framework/development-workflow.md) 进入，不在这里复制。

集成验证：`cd modules/wechat_fenxi/backend && npm test` 会加载小程序的 limits、导入策略和部分页面源码。这不是微信开发者工具或真机上的集成。该客户端路径标 NOT_RUN。

框架分发的既有 OpenSpec 变更（`openspec/changes/`）记录的是框架本身，不是本产品的需求。产品的新行为要单独建 change，并在变更里写明模块 ID `wechat_fenxi`。
