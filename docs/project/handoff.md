# 开发交接

资料不授予业务实现、安装、发布或知识写入权限。

## 已接入

- 模块 `wechat_fenxi` 在 `modules/wechat_fenxi`。
- 小程序 `miniprogram/`，后端 `backend/`。行为保持：粘贴与 `wx.chooseMessageFile`、双重同意、64KiB 内联上限、GBK/UTF-8、本地内容安全、轮询任务、删除、MiniMax 由环境变量开关（无密钥时 mock）。
- 密钥不在 Git 中。占位见 `modules/wechat_fenxi/backend/.env.example`。

## 未完成的框架接入

本仓库是框架分发根。`generation_changes` 在目标等于或包含分发目录时返回 `TARGET_CONTAINS_DISTRIBUTION`，因此没有安装 `.agent-framework/`，没有生成 `module-catalog.generated.json`，也没有 doctor 的 `initialization=COMPLETE`。不要为了跑 doctor 把分发目录复制进自身。

## 下一步

按 [开发流程](../framework/development-workflow.md) 继续产品开发，不要从头再初始化：

1. 新行为、接口或验收：在本仓库 OpenSpec 根另建 change，模块 ID 写 `wechat_fenxi`。先规格，再 `writing-plans`，批准后再 TDD。
2. 只改已有行为的缺陷：用 systematic-debugging，先有失败测试再改 `modules/wechat_fenxi`。
3. 每次改完在 `modules/wechat_fenxi/backend` 运行 `npm test`。微信开发者工具、真机和提审另计，不能写成已通过。
4. 问题解决后若要写入知识库，先确认内容和目标 alias。当前没有 KB，未授权不创建。

阻塞：无产品代码阻塞。框架 doctor 完整初始化被分发根与目标重合挡住，不影响在本模块里继续改代码和跑 `npm test`。
