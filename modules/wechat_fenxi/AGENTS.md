# AGENTS.md — wechat_fenxi

> 模块 ID `wechat_fenxi`。模块根是本目录。Git 归属是外层仓库 `zhangxiaojian19926/agent-map-development-framework`，本目录不是独立 Git 根。
>
> 上级流程：[公共开发入口](../../AGENTS.md)、[开发流程](../../docs/framework/development-workflow.md)、[公共协作](../../docs/framework/collaboration-policy.md)、[知识规则](../../docs/framework/knowledge-policy.md)。
> 项目事实：[概览](../../docs/project/overview.md)、[架构](../../docs/project/architecture.md)、[协作](../../docs/project/collaboration.md)、[约束](../../docs/project/constraints.md)、[资源](../../docs/project/resources.md)、[交接](../../docs/project/handoff.md)。

## 用途与上级

负责：用户把已经导出的聊天文本粘贴或用 `wx.chooseMessageFile` 选进来，后端解析后做要点摘要。产品表面是微信小程序，不会自动拉取个人聊天。

不负责：框架分发、技能包、公共 OpenSpec 变更、知识库写入、微信提审、真机预览、设备调试。

目录父子：`miniprogram/` 与 `backend/` 是本模块内部子系统，调用关系见项目架构。不要把它们拆到 `modules/` 的两个顶层目录，后端用 `../../miniprogram/utils/limits` 与小程序共用阈值。

## 调用与接口

- 小程序入口：用微信开发者工具打开 `miniprogram/`（`project.config.json` 的 `miniprogramRoot` 为 `./`，`appid` 为 `touristappid`）。`app.js` 的 `apiBase` 默认 `http://127.0.0.1:8787`。
- 后端入口：工作目录 `backend/`，`npm start` 即 `node src/server.js`。监听 `127.0.0.1`，端口 `PORT` 或 8787。先读进程环境，再读 `backend/.env`（该文件不入库）。
- HTTP：`GET /api/health`、`GET /api/policy`、`POST /api/auth/session`、`POST /api/jobs`、`GET /api/jobs/:id`、`DELETE /api/jobs/:id`、`DELETE /api/me/data`、`POST /api/storage/presign`、`PUT /api/storage/objects/:id`、`POST /api/uploads`。任务状态为 `pending` → `parsing` → `summarizing` → `done` 或 `failed`。通知方式是轮询，不是订阅消息。
- 错误：缺同意 `403 CONSENT_REQUIRED`；空内容 `EMPTY_INPUT`；内联超过 64KiB `413 OVERSIZE_USE_STORAGE`；更大的 JSON 体 `PAYLOAD_TOO_LARGE`；无法解码 `BAD_ENCODING`；内容安全拦截 `CONTENT_BLOCKED`。
- 上游是小程序页面。下游是环境变量里的 MiniMax（OpenAI 兼容 chat completions）。未配置密钥时用进程内 mock，不访问网络。

## 内部协作

1. `miniprogram/pages/onboard` 说明导入已经整理好的文本，不读取微信会话、不自动同步。
2. `miniprogram/pages/privacy` 与 `pages/import`：必须同时同意隐私和「有权提交他人发言」。`utils/import-policy.js` 决定能否提交，以及走内联还是直传。
3. `utils/limits.js` 是前后端共用阈值：内联 64KiB，单文件 10MB，JSON 体上限 72KiB，保留 24 小时，允许后缀 `txt`/`json`/`md`，轮询 1500ms。
4. `utils/api.js` 调后端。`pages/job` 轮询，`pages/result` 展示 title、要点、待办、决策、开放问题，并提供删除这一次和删除我的数据。
5. `backend/src/parse.js` 与 `encoding.js`：UTF-8（含 BOM）优先，非法 UTF-8 再按 GB18030/GBK 解码。
6. `jobs.js` 分段（`chunk.js`）后先做内容安全（`safety.js` 的本地关键词规则），再调 `llm.js`。`LLM_PROVIDER=minimax` 且存在 `MINIMAX_API_KEY`（或 `LLM_API_KEY`）时请求 MiniMax；否则 mock。`CONTENT_SAFETY=composite` 或 `wechat` 且配置了微信凭据时才调用消息安全检查。
7. `store.js` 把任务和上传放在进程内存。删除单条或 `DELETE /api/me/data` 清掉该账号的原文和结果。

## 本模块开发流程

相对顶层只增加：改阈值必须同时改 `miniprogram/utils/limits.js`（后端直接 require 它）；改导入同意或体积分流时同时跑 `backend` 里引用小程序源码的测试。新行为仍走公共流程的规格、计划和 TDD，不在本文件另写一套完成状态。

## 命令与验证

| 命令 | 目录 | 前提 | 副作用 | 成功判据 |
|---|---|---|---|---|
| `npm test` | `modules/wechat_fenxi/backend` | Node.js >= 20。不需要 API 密钥。 | 无网络、无写盘业务数据。 | `node --test test/*.test.js` 退出码 0 |
| `npm start` | `modules/wechat_fenxi/backend` | 同上。真实摘要才需要本机 `.env`。 | 监听本机端口。 | 日志出现 `scheme A API listening` |

Host：`npm test` 覆盖解析、同意、64KiB 分流、GBK/UTF-8、本地内容安全、轮询状态、删除和 mock/MiniMax 构造。Cross-build：无。Target：微信开发者工具、真机、提审均未在本模块命令里执行，不能把 `npm test` 写成设备或审核通过。Integration：小程序与后端的共享阈值由测试读取同一 `limits.js` 和页面源码；没有在微信客户端里点过页面。

## 知识与完成标准

KB alias：未关联。项目没有 `llm-wiki-aliases.json`。状态 NOT_CONFIGURED。不要在未获本次内容和目标授权时建库或写入。

完成证据：后端 `npm test` 通过，加上本次改动的 diff。不把静态阅读或 mock 摘要当成 MiniMax 线上调用、微信 `msgSecCheck` 线上调用或提审通过。
