# 工作流路由规格

变更：`add-agent-workflow-routers`。状态：规划规格，尚未实现。可校验要求在 `specs/` 的 delta 中，编号 `WR-01` 至 `WR-20`，以及 `skill-routing`、`invocation-forms`、`native-workflow-gates` 的增量。本文件把这些要求收成一份通读文本。与 delta 冲突时以 delta 为准。

## 1. 目的

十五条工作流各有一个可自动选中的路由技能。路由按固定组合点名成员技能和改编层，并在每个步骤完成后写明下一项。成员技能不各自提示下一个技能。发现投影和写入拦截只使用已证实的宿主载体。

`retro` 不进入任何自动组合。不改 `FRAMEWORK_ENTRY` 托管段，不改 doctor 状态词典，不删除用户主目录里的全局 OpenSpec 技能。

## 2. 怎样选定工作流

宿主发现目录里只有 `flow-01` 至 `flow-15` 十五条路由描述。任意两条描述的触发词不相交，一条请求只命中一个入口。命中后读取该路由正文。

工作流 2 只有 `flow-02` 一条描述。只读审计、纯文档、既有规格修复和新行为写在正文内部。文档若改变公开接口或验收，正文要求改走新行为。

写入门禁不选择工作流。它只在流程判定不是 `READY` 且不是 `NOT_APPLICABLE` 时拒绝业务写入，并在理由中写明应读取的 `flow-*` 和缺失步骤。读文件放行。

当前已经运行的 `catalog.py` `route()` 仍按请求 JSON 分类。本规格的描述匹配在路由生成并投影之后才生效。

## 3. 每条工作流点名的技能

| 工作流 | 技能 |
|---|---|
| 1 初始化 | `project-bootstrap`。失败再读 `diagnosing-bugs` 与 `discipline.md`。设计未批准时停止，不进入工作流 2 |
| 2 日常开发 | 见第 4 节 |
| 3 模块生命周期 | 接口或 seam 读 `codebase-design`。术语或 ADR 读 `domain-modeling`。同一次只读一条。二者不产生完成状态 |
| 4 公共壳升级 | 评审受管 diff 时读 `code-review` 与 `framework-rules.md`。有人工改动冲突时停止 |
| 5 知识 | 只读 `llm-wiki`。查询可进行。写入须先列出内容、目标和 alias，并获得本次授权 |
| 6 逆向观察 | 明确要求逆向时，读 `reverse-engineer` 的取证部分 |
| 7 产品行为观察 | `reverse-engineer` 的证据归并部分。触发词与工作流 6 不同 |
| 8 设计交接 | `reverse-engineer` 的交接部分，然后 `brainstorming` 的架构路径。产物保持未批准 |
| 9 差距追踪 | 规格已批准且实现之后，读 `code-review` 与 `framework-rules.md`。找不到 change 时报告无可用规格 |
| 10 市场研究 | 无成员技能。绑定既有研究命令。工具不联网 |
| 11 发布候选 | 无成员技能。工作流 13 未登记产物时停止 |
| 12 渠道适配 | 无成员技能。候选未 `READY` 时停止 |
| 13 产物登记 | 无成员技能。它是工作流 11 的前置 |
| 14 壳验证 | 改技能读 `writing-skills`。改 Agent 所读文档读 `writing-for-agents`。失败读 `diagnosing-bugs` 与 `discipline.md`。三种模式同属这一条路由 |
| 15 壳发布 | `verification-before-completion`。进入前必须已有工作流 14 的验证证据。触发词与工作流 14 不同 |

## 4. 工作流 2

进入时先读根 `AGENTS.md`、当前 handoff 和只读 doctor。只要求读到当前步骤。

| 路径 | 技能 |
|---|---|
| 只读审计 | 不点名实现技能，不写文件 |
| 纯文档 | `writing-for-agents` |
| 既有规格修复 | `diagnosing-bugs` 与 `discipline.md`，然后 `tdd` 与 `discipline.md`，然后 `code-review` 与 `framework-rules.md`。结果写回原 change |
| 新行为 | 见下表。故障时先加 `diagnosing-bugs` 与 `discipline.md` |

新行为的顺序：

1. 已有规格上下文读 `openspec-explore`。新设计读 `brainstorming`。
2. `openspec-propose` 或 `openspec-update-change`。
3. `to-tickets` 与 `plan-format.md`。切片只写入当前 change 的 `tasks.md`。
4. 需要隔离读 `using-git-worktrees`。顺序执行读 `executing-plans`。另有委派授权才读 `subagent-driven-development` 与 `framework-rules.md`，或 `dispatching-parallel-agents`。
5. `openspec-apply-change` 只装载 status、instructions 和 contextFiles。
6. `tdd` 与 `discipline.md`。
7. `code-review` 与 `framework-rules.md`。派发或接收反馈再读 `requesting-code-review`、`receiving-code-review`。
8. `verification-before-completion`。
9. `finishing-a-development-branch`。提交、推送、合并等待用户当次选择。
10. `openspec-sync-specs`，然后 `openspec-archive-change`。
11. 询问是否摄入。授权后才读 `llm-wiki` 的写入步骤。

## 5. 完成后的下一项

下一项由路由正文写明。成员技能结束时不各自提示下一个技能。成员技能的收尾若指向别处，以路由写明的下一项为准。新行为只写当前步骤的下一项。

| 刚完成 | 下一项 |
|---|---|
| `diagnosing-bugs` | 已有规格上下文：`openspec-explore`。新设计：`brainstorming` |
| `openspec-explore` 或 `brainstorming` | `openspec-propose` 或 `openspec-update-change` |
| 规格提案 | `to-tickets` 与 `plan-format.md` |
| `to-tickets` 且计划已批准 | 需要隔离：`using-git-worktrees`。顺序执行：`executing-plans`。另有委派授权才写子代理技能 |
| 工作区就绪 | `openspec-apply-change`，只装载上下文 |
| 上下文装载完成 | `tdd` 与 `discipline.md` |
| `tdd` 到达 `TASK_VERIFIED` | `code-review` 与 `framework-rules.md`。派发或接收反馈再写评审往返技能 |
| 评审闭合 | `verification-before-completion` |
| 验证通过 | `finishing-a-development-branch` |
| 用户选定集成方式 | `openspec-sync-specs`，然后 `openspec-archive-change` |
| 归档完成 | 询问是否摄入。授权后才是 `llm-wiki` 的写入步骤 |

其他工作流：

- 工作流 1 失败时，下一项是 `diagnosing-bugs` 与 `discipline.md`。设计未批准时没有下一项技能。
- 工作流 8 在逆向交接完成后，下一项是 `brainstorming` 的架构路径。
- 工作流 14 的三种模式各自结束，不把另一种模式写成下一项。
- 工作流 15 不把工作流 14 写成完成后的下一项。工作流 14 的证据是进入条件。
- 工作流 10 至 13 完成后不点名下一个技能。

路由同时暂停这些成员收尾：改变行为、接口或验收的有界设计仍进入规格和 `to-tickets`，探针停在建议。`openspec-propose` 收尾里的直接 apply 暂停。`openspec-apply-change` 不直接改业务源码，也不在 `TASK_VERIFIED` 之前勾选任务。`to-tickets` 不写 `.scratch`，也不要求本包不存在的安装命令。

## 6. 路由技能形态

每条路由省略 `disable-model-invocation`，Codex 侧也不声明 `allow_implicit_invocation: false`。描述用第三人称，同时写明用途和触发条件，不超过 1024 字符。正文不超过 500 行。必读文件从正文直接链接，只跳一层。

规范正文生成在 `skill/flows/flow-01` 至 `flow-15`。成员技能留在原目录，不复制到发现目录。`brainstorming` 增加一份改编层并登记进 `skill/local-layers.json`。`discipline.md`、`plan-format.md`、`framework-rules.md` 继续由路由点名。

组合清单是路由正文、工作流目录技能字段和对外指南技能列的共同事实源。`docs/framework/skill-policy.md` 改为：`diagnosing-bugs`、`to-tickets`、`tdd`、`code-review` 是工作流 2 对应路径的必读；`codebase-design`、`domain-modeling`、`writing-for-agents`、`retro` 仍按条件读取。

## 7. 宿主名册

档案字段是发现目录、拦截载体、能力类、证据等级。证据等级只允许 `DOCUMENTED`、`RECORDED`、`CARRIER_UNKNOWN`。名册外宿主安装失败且不写文件。

国际：

| 宿主 | 发现目录 | 拦截 | 能力类 |
|---|---|---|---|
| `cursor` | `.cursor/skills/`，`DOCUMENTED` | `.cursor/hooks.json` 的 `preToolUse` | 可阻断。失败即关闭 |
| `claude-code` | `CARRIER_UNKNOWN` | `.claude/settings.json` 的 `PreToolUse`，`RECORDED` | 可阻断 |
| `codex` | `CARRIER_UNKNOWN`。`~/.agents/skills/` 不是安装目标 | `.codex/hooks.json`，`RECORDED` | 可阻断 |
| `gemini-cli` | `CARRIER_UNKNOWN`。用户级技能目录不是安装目标 | `.gemini/settings.json` 的 `BeforeTool`，`RECORDED` | 可阻断 |
| `copilot-cli` | `CARRIER_UNKNOWN` | `CARRIER_UNKNOWN` | 只建议 |
| `github-copilot` | `CARRIER_UNKNOWN` | `CARRIER_UNKNOWN` | 只建议 |
| `windsurf` | `CARRIER_UNKNOWN` | `CARRIER_UNKNOWN` | 只建议 |
| `grok` | `CARRIER_UNKNOWN` | 项目载体 `CARRIER_UNKNOWN` | 只建议 |

国内：

| 宿主 | 发现目录 | 拦截 | 能力类 |
|---|---|---|---|
| `qwen-code` | `CARRIER_UNKNOWN` | `.qwen/settings.json`，`RECORDED` | 可阻断 |
| `codebuddy` | `CARRIER_UNKNOWN` | 无 | 只建议。不写 `CODEBUDDY.md`，不装钩子 |
| `trae` | `CARRIER_UNKNOWN` | `CARRIER_UNKNOWN` | 只建议 |
| `lingma` | `CARRIER_UNKNOWN` | `CARRIER_UNKNOWN` | 只建议。与 `qwen-code` 分开 |
| `deepseek-harness` | Git 根 `.dsh/skills/` 的直接子项，`DOCUMENTED` | `.dsh/hooks.json`。仅当 profile 的 `configPath` 指向它 | 未挂载或配置读失败时按只建议 |

会自动收到路由投影的只有 `cursor` 和 `deepseek-harness`。DeepSeek 不写 `.agents/skills`，不改 `~/.dsh`。省略 `disable-model-invocation` 时，DeepSeek 本地提供方把路由视为模型可调用。其钩子桥在进程启动时读一次配置；读失败则不跑钩子，该次启动不记为已阻断。退出码 2 且目标文件未变，才记为已拦截。工具名未经真实事件确认前，该入口未覆盖。

`claude-code` 与 `qwen-code` 沿用既有钩子，只把拒绝理由改为指向当前路由，不新建技能目录。`codex` 与 `gemini-cli` 可以写入已记录的钩子载体；没有真实会话时执行轴是 `NOT_RUN`。

文件安装通过不等于现场已拦截。账号、模型或 CLI 缺失记为 `NOT_RUN` 或 `INFRA_ERROR`。

## 8. 检查

分发结构检查必须能因下列偏差失败：路由缺失、两条路由共用触发词、成员技能被投影、`CARRIER_UNKNOWN` 却有安装路径、名册缺宿主。
