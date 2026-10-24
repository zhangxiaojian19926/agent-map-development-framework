# 约束

工具链：

- 后端：Node.js >= 20，仅用内置 `http` 与 `node:test`，`backend/package.json` 没有第三方依赖。
- 小程序：微信开发者工具打开 `miniprogram/`。`project.config.json` 的基础库字段为 `3.5.5`，`urlCheck` 为 true，appid 为 `touristappid`。
- 本仓库的框架检查仍是 `python3 tools/check-framework` 与 `python3 -m unittest discover -s tests -v`。产品文件不计入分发指纹。

运行与验证：

- `npm test` 不读取真实密钥，未设置 `LLM_PROVIDER=minimax` 时摘要是 mock。
- 真实 MiniMax 需要本机 `backend/.env` 中的 `LLM_PROVIDER=minimax` 与 `MINIMAX_API_KEY`。DeepSeek 只作为备用环境变量名，不是当前生效提供方。
- 微信消息安全检查默认关闭。打开需要 `CONTENT_SAFETY=composite` 或 `wechat`，以及微信 appid/secret。
- 密钥只放 `backend/.env`。仓库根 `.gitignore` 已忽略 `.env` 和 `.env.*`（保留 `.env.example`）。不要把密钥、Authorization 头的真实值写进提交、文档或 PR。

兼容：粘贴内联上限 64KiB（65536 字节），不是「8 万字」。超限走存储直传。编码是 UTF-8，非法 UTF-8 再试 GB18030。

外部动作：不在未获当次授权时安装全局工具、推送以外的远程、操作微信后台、访问设备或写入知识库。

设备：小程序预览、上传和真机调试需要微信开发者工具。自动化测试不能代替该步骤。没有已完成的设备验收。

恢复：后端状态在进程内存里。重启进程会丢掉任务和上传。代码恢复点是外层 Git 分支。
