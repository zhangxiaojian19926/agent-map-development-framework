## Why

十五条工作流的技能组合写在阶段表里，但常见 Coding Agent 的自动调用只认各自发现目录中的技能描述。成员技能要么不在发现面上，要么被全局 OpenSpec 技能单独命中后跳过计划与测试。现在需要一份宿主中立的路由契约，让每条工作流按组合被读到，并按各宿主真实能力安装发现投影和写入拦截。

## What Changes

- 新增十五条工作流路由技能。每条路由是该工作流的自动入口，正文按组合点名成员技能和同目录改编层。
- 新增组合清单作为路由正文、目录技能字段和指南技能列的共同事实源。工作流 2 保持一个入口，内部再分只读、文档、既有规格修复和新行为。
- 成员技能仍留在原目录。不把它们第二份投影到宿主发现目录，避免与路由抢触发。
- 为常用国内外 Coding Agent 建立封闭名册和能力档案。只有档案里已记载的项目级发现目录才接收路由投影；只有已记载的拦截载体才安装写入门禁。
- 载体未知的宿主仍必须出现在名册和缺口报告中。安装不得猜测路径，也不得改写用户主目录里的全局技能。
- 路由正文暂停三处会拆开组合的收尾：有界设计直接实现、提案结束后直接 apply、apply 在任务验证前勾选任务。每个已完成步骤的下一项由路由正文写明，不由成员技能各自提示。
- **BREAKING**：阶段的自主到达改为「工作流路由可被模型选中，并由它点名成员技能」。不再要求每个成员技能各自占一条自动描述。

## Capabilities

### New Capabilities

- `agent-workflow-routers`：十五条路由、技能组合、宿主名册、发现投影、写入拦截和收尾暂停。

### Modified Capabilities

- `skill-routing`：每条工作流有且只有一个路由落点；相邻路由的触发词不得混用；组合清单与阶段表、指南技能列一致。
- `invocation-forms`：模型必须能自主到达的是工作流路由；成员技能由路由在同一次任务中点名读取；`retro` 仍只在用户点名时出现。
- `native-workflow-gates`：宿主档案区分可阻断、只建议和载体未知；文件投影通过不得写成现场拦截已验证。

## Impact

- 新增组合清单与路由生成，产物进入 `skill/flows/`，并只向已证实的项目发现目录投影。
- Cursor 获得 `.cursor/skills/flow-*` 与 `.cursor/hooks.json`。DeepSeek harness 在 Git 根的 `.dsh/skills/flow-*` 获得同一份扁平路由；钩子配置写入 `.dsh/hooks.json`，只有 profile 的 `configPath` 指向它时才拦截。Claude Code、Qwen Code 沿用现有项目钩子并让拒绝理由指向路由。Codex、Gemini CLI 只使用验证记录里已写明的钩子载体。
- CodeBuddy 继续不安装钩子、不写 `CODEBUDDY.md`。
- `tools/check-framework` 增加路由、触发词和宿主档案检查。
- `docs/framework/skill-policy.md` 中与阶段必读冲突的那一句改为跟随组合清单。
- 不改 `FRAMEWORK_ENTRY` 托管段，不改 doctor 状态词典，不删除用户全局 OpenSpec 技能。
