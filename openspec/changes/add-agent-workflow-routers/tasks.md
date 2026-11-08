## 1. 组合清单与十五条路由

- [x] 1.1 新增组合清单，写入 WR-05、WR-06、WR-07 的路径、技能、改编层和触发词，并验证 `flow-01` 至 `flow-15` 各有一条且 `flow-14` 与 `flow-15`、`flow-06` 与 `flow-07` 的触发词不相交
- [x] 1.2 由清单生成 `skill/flows/flow-01` 至 `flow-15` 的 `SKILL.md`，并验证每份都省略 `disable-model-invocation`、描述不超过 1024 字符、正文不超过 500 行、必读链接只跳一层，且每个已完成步骤按 WR-20 写明下一项
- [x] 1.3 为 `brainstorming` 增加 `framework-rules.md` 并登记到 `skill/local-layers.json`，并验证活文档同时点名该技能和该文件名，且路由写明有界行为变更仍进规格和 `to-tickets`

## 2. 目录、指南与技能约束

- [x] 2.1 回填工作流目录的技能字段和对外指南的技能列，使其与组合清单一致，并验证多写一个技能时结构检查失败
- [x] 2.2 更新 `docs/framework/skill-policy.md`：`diagnosing-bugs`、`to-tickets`、`tdd`、`code-review` 按 `flow-02` 路径必读，`retro` 仍非自动必读；验证旧的一刀切句子不再存在
- [x] 2.3 在 `AGENTS.md` 托管段之外增加指向 `skill/flows/flow-*` 的指针，并验证 `FRAMEWORK_ENTRY` 字节不变、`docs/guide/framework-model.md` 状态词典未新增状态码

## 3. 宿主档案与安装

- [x] 3.1 写入十三个宿主的档案：八个国际、五个国内，证据等级只取 `DOCUMENTED`、`RECORDED`、`CARRIER_UNKNOWN`；验证名册外宿主安装失败且不写文件
- [x] 3.2 为 `cursor` 投影十五条路由到目标项目 `.cursor/skills/`，并验证内容与 `skill/flows/` 一致、成员技能没有第二份、用户主目录无新增文件
- [x] 3.3 为 `deepseek-harness` 把十五条路由扁平投影到 Git 根 `.dsh/skills/flow-*`，并写入 `.dsh/hooks.json`；验证没有写入 `.agents/skills` 和 `~/.dsh`。profile 未把 `configPath` 指向该文件时，执行轴不是已阻断
- [x] 3.4 为 `cursor` 安装 `.cursor/hooks.json`，写工具在非 `READY` 且非 `NOT_APPLICABLE` 时拒绝并指向 `flow-*`，读文件放行，失败即关闭；验证未批准写入前后目标文件哈希不变。未在事件中出现的工具名保持未覆盖
- [x] 3.5 更新 `claude-code` 与 `qwen-code` 的既有拒绝理由，使其包含当前 `flow-*` 和缺失步骤，并验证原已认证工具名不变
- [x] 3.6 为 `codex` 与 `gemini-cli` 写入已记录的项目钩子载体，验证没有真实会话时宿主执行轴为 `NOT_RUN`
- [x] 3.7 验证 `codebuddy` 安装不新增 `CODEBUDDY.md` 和钩子；`trae`、`lingma`、`github-copilot`、`windsurf`、`grok`、`copilot-cli` 以及其余 `CARRIER_UNKNOWN` 发现目录不被创建

## 4. 可证伪检查

- [x] 4.1 在 `tools/check-framework` 中检查路由缺失、触发词相交、成员技能被投影、`CARRIER_UNKNOWN` 却有安装路径，并各写一个人为偏差测试证明检查非零退出
- [x] 4.2 运行 `openspec validate --all --strict` 与本变更相关的单元测试，确认新增要求可被解析且既有宿主测试仍通过

## 5. 证据边界

- [x] 5.1 记录安装轴与宿主执行轴。文件一致只说明安装通过；没有真实会话的宿主保持 `NOT_RUN`。不得把 Cursor、Codex、Gemini、Qwen、未挂载桥的 DeepSeek harness，或名册内只建议宿主写成已阻断
- [x] 5.2 同步 delta specs 与归档留到实现和适用验证完成之后。本任务清单勾完不等于现场拦截已验证
