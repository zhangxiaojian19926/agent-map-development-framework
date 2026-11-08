## Context

见 proposal.md 的 Why。当前自动调用依赖宿主发现目录里的 `description`，仓库 `skill/` 不在 Cursor 的发现面上；Claude Code 与 Qwen Code 已有项目级 PreToolUse，Codex 与 Gemini CLI 只在 2026-11-06 的验证记录里留下钩子载体，现场会话为 `NOT_RUN`。CodeBuddy 没有钩子，也不能写 `CODEBUDDY.md`。用户主目录里的 OpenSpec 技能会单独命中并跳过计划与测试。

规范行为见本变更的 delta specs。本文只记录实现选择。

## Goals / Non-Goals

**Goals:**

- 用一份组合清单生成十五条路由，并让目录、指南和路由正文使用同一组技能。
- 只把路由投影到档案里证据等级不是 `CARRIER_UNKNOWN` 的项目发现目录。当前是 Cursor 与 DeepSeek harness。
- 可阻断宿主的拒绝理由指向 `flow-*`，读文件放行。
- 名册内载体未知的宿主得到明确缺口，不得到猜测出来的目录。

**Non-Goals:**

- 不在本变更里跑通十三个宿主的真实会话。
- 不改 `FRAMEWORK_ENTRY`，不改 doctor 状态词典。
- 不把成员技能复制进发现目录，不修改 `~/.agents/skills`。
- 不为名册外的宿主发明载体。

## Decisions

### 1. 规范路由放在 `skill/flows/`，发现目录只做投影

组合清单生成 `skill/flows/flow-01` 至 `flow-15` 的 `SKILL.md`。这是所有宿主都能按路径读取的正文。Cursor 安装时把同一正文写入 `.cursor/skills/flow-*`。其他宿主的项目发现目录仍是 `CARRIER_UNKNOWN`，所以不投影。

备选是给每个宿主各写一份路由。那会让触发词和组合分叉，因此不采用。

### 2. 工作流 2 保持一个描述、四条内部路径，下一项写在路由里

只读、文档、修复和新行为共用 `flow-02` 的描述。路径判断写在正文里。每个已完成步骤的下一项也写在同一份正文里，成员技能结束时不再各自提示下一个技能。这样「改文档」和「做功能」不会抢两个自动入口。

### 3. 宿主名册按证据等级安装

| 宿主 | 区域 | 安装动作 |
|---|---|---|
| `cursor` | 国际 | 投影十五条路由；新增 `.cursor/hooks.json`，`preToolUse` 失败即关闭 |
| `deepseek-harness` | 国内 | 把同一正文扁平投影到 Git 根 `.dsh/skills/flow-*`；另写 `.dsh/hooks.json`。不写 `.agents/skills`，不改 `~/.dsh`。桥未把 `configPath` 指向该文件时，执行轴不是已阻断 |
| `claude-code` | 国际 | 沿用 `.claude/settings.json`，拒绝理由增加路由路径；不新建技能目录 |
| `qwen-code` | 国内 | 沿用 `.qwen/settings.json`，同样只更新拒绝理由 |
| `codex` | 国际 | 可写入已记录的 `.codex/hooks.json`；执行轴保持 `NOT_RUN`，直到真实会话 |
| `gemini-cli` | 国际 | 可写入已记录的 `.gemini/settings.json` BeforeTool；执行轴同样保持 `NOT_RUN` |
| `codebuddy` | 国内 | 不增加文件。到达方式仍是项目 `AGENTS.md` |
| `copilot-cli`、`github-copilot`、`windsurf`、`grok`、`trae`、`lingma` | 国际或国内 | 只写缺口报告 |

DeepSeek 的发现规则来自本机检出的 `deepseek-ai/deepseek-harness`，提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`，文档 `docs/subsystems/skills.md`。项目根是最近的含 `.git` 祖先。发现根只认直接子项，所以路由必须是 `.dsh/skills/flow-01/SKILL.md` 这种一层目录。省略 `disable-model-invocation` 时，本地提供方默认模型可调用。

钩子来自同一次检出的 `packages/experimental/hooks-claude-code/README.md`。`configPath` 在进程启动时读一次；读失败则不跑钩子，Agent 继续。项目级自动发现仍是上游 TODO，所以只放文件不能当成已经拦住写入。退出码 2 才是阻断。

用户级目录一律不写。`lingma` 与 `qwen-code` 分属 IDE 与 CLI，不合并档案。

备选是把 `.agents/skills` 当作所有国际宿主的项目发现目录。仓库只证实它是用户级共享别名，没有证实项目级会被扫描，因此不投影。

### 4. 门禁复用现有流程判定

钩子调用现有 `framework flow` 的批准检查。判定不是 `READY` 且不是 `NOT_APPLICABLE` 时拒绝写入。理由包含路由路径和缺失步骤。已认证工具名保持各适配器的现有列表。Cursor 第一次实现先记录真实事件里的工具名；未出现在认证列表里的名字记为未覆盖。

公共壳用 `tools/framework`，业务项目用 `.agent-framework/tools/framework`，钩子选择目标项目里实际存在的那个入口。

### 5. 三处跳步写进路由和一份新改编层

`brainstorming` 增加 `framework-rules.md` 并登记到 `skill/local-layers.json`。路由正文同时写明：改变行为的有界设计仍进规格和 `to-tickets`；提案之后先计划批准；apply 只装载上下文；任务勾选发生在 `TASK_VERIFIED` 之后；切片只进 `tasks.md`。

`docs/framework/skill-policy.md` 的一刀切句子改成组合清单的必读与参考之分。阶段表在托管段之外增加指向 `skill/flows/flow-*` 的一行，不改托管段字节。

### 6. 检查从清单推导

`tools/check-framework` 增加四类失败：路由缺失、触发词相交、成员技能被投影、`CARRIER_UNKNOWN` 却有安装路径。测试用人为偏差证明这些检查会失败。

## Risks / Trade-offs

- [描述匹配仍可能先读到全局 OpenSpec] → 可阻断宿主拒绝业务写入，理由指回 `flow-02`。只建议宿主把这个缺口写进报告。
- [Cursor 写工具名可能不只 `Write`] → 未认证名字保持未覆盖，不把安装成功写成已经拦住所有编辑。
- [Codex 与 Gemini 的钩子载体来自既往记录，本机当时没有跑通会话] → 允许安装载体文件，执行轴保持 `NOT_RUN`。
- [十五条描述常驻提示词] → 每条描述限制在 1024 字符以内，成员技能不进发现目录。
- [名册里六个宿主没有载体] → 覆盖义务是档案和缺口，不是假钩子。补载体必须先改档案证据等级。
- [DeepSeek 的钩子桥默认不读取项目文件] → 安装 `.dsh/hooks.json`，档案写明必须由 profile 指向它。未挂载时按只建议报告。

## Migration Plan

1. 先落组合清单和 `skill/flows/`，结构检查通过后再投影 Cursor。
2. 更新 Claude Code 与 Qwen Code 的拒绝理由，保持原工具名。
3. Codex 与 Gemini 的钩子文件单独提交，报告里写明执行轴 `NOT_RUN`。
4. 回滚时删除 `skill/flows/`、Cursor 投影和新增钩子字段；已有 Claude、Qwen、CodeBuddy 适配器回到变更前的模板。不触碰用户主目录。

## Open Questions

Cursor 里除 `Write` 以外的精确改写工具名，等第一次 `preToolUse` 事件再写入认证列表。这不改变路由组合、名册或「未认证即未覆盖」的判定。
