# wechat-fenxi

项目稳定标识：`wechat-fenxi`（见仓库根 `framework-project.json`）。目录名与模块 ID 是 `wechat_fenxi`。

目标：在微信小程序里导入已经导出的聊天文本（粘贴或选择文件），由 Node 后端解析并生成要点摘要。默认不调用外网模型；配置 MiniMax 环境变量后走 MiniMax 的 OpenAI 兼容接口。

非目标：不自动读取微信聊天，不自动同步会话，不解密 PC 微信数据库，不在本仓库保存 API 密钥或微信应用密钥，不把框架分发清单改成业务发布包。

当前状态：源码在 `modules/wechat_fenxi`。后端 `npm test` 是已执行的 Host 检查。微信开发者工具、真机、提审和线上内容安全接口未执行。

本仓库同时是 Agent Map 框架的分发根。`python3 tools/framework init --target .` 会因目标包含分发目录而拒绝。产品资料在本目录，不写入 `framework-manifest.json`。

来源：接入前的产品代码与说明在工程外的只读副本；本仓库中的模块树是继续开发的位置。
