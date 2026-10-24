# 架构

一个顶层模块 `wechat_fenxi`，路径 `modules/wechat_fenxi`。内部两个子系统，不另建顶层模块：

| 子系统 | 路径 | 角色 |
|---|---|---|
| 小程序 | `modules/wechat_fenxi/miniprogram` | 引导、同意、粘贴/选文件、轮询、结果、删除 |
| 后端 | `modules/wechat_fenxi/backend` | 解析、体积分流、内容安全、摘要任务、删除 |

运行调用：小程序 `utils/api.js` → 本机 HTTP（默认 `http://127.0.0.1:8787`）→ `backend/src/create-app.js`。后端 `require('../../miniprogram/utils/limits')` 共用阈值，所以两个子系统必须保持为同一模块根下的兄弟目录。

数据流：

1. 用户在导入页同时勾选隐私同意和他人发言授权。
2. UTF-8 字节长度 ≤ 64KiB 时，`POST /api/jobs` 携带文本。超过则预签名直传或 multipart，任务体不含原文。
3. 后端识别 UTF-8 或 GBK/GB18030，解析 txt/json/md。
4. 本地关键词内容安全通过后，mock 或 MiniMax 生成固定 schema 摘要。
5. 小程序轮询 `GET /api/jobs/:id`。删除单条或删除账号数据后，原文和结果不可再读。任务在进程内存中，默认 24 小时过期。

Git 边界：整个模块属于外层仓库，没有嵌套 `.git`。框架工具、技能和 `openspec/` 仍是分发内容，不是这个产品的运行依赖。

关系证据来自源码中的 `require` 与页面调用。这些调用的运行验证只覆盖 Node 测试里启动的 HTTP 服务，不覆盖微信客户端。provenance 记为源码可见；runtime 对微信端为 NOT_RUN。
