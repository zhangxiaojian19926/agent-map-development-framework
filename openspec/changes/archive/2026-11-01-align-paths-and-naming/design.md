## Context

技能组目录与调用前缀是**两套名字**，各自有用途：目录决定文件在哪，前缀决定 Agent 怎么称呼它。两者不一致时，搜一个找不到另一个。

| 组 | 目录 | 调用前缀 | 一致？ |
|---|---|---|---|
| superpowers | `skill/super-powers/` | `superpowers:` | ✗ |
| openspec | `skill/openspec/` | `openspec-` | ✓ |
| matt-pocock | `skill/matt-pocock/` | `matt-pocock:` | ✓ |
| llm-wiki | `skill/llm-wiki/` | `llm-wiki` | ✓ |

计划文档的位置同理：计划技能迁到 `matt-pocock` 组后，`docs/superpowers/plans/` 这个名字已经指向一个不存在的目录。

## Decisions

**改目录名，不改调用前缀。**
前缀 `superpowers:` 是上游在 Claude Code 插件里的命名空间，框架的 AGENTS.md 也已声明了这个约定；目录名则是本框架自己的选择。改目录成本低（一次 git mv），改前缀要动所有技能间的互引和阶段路由表。

**计划文档位置改为 `docs/plans/`。**
去掉已退役技能的名字。它是公共工程壳自身的目录，不进入目标项目公共包，所以不影响业务项目的目录所有权。

**运行时排除清单同步更新，并清掉失效项。**
`RUNTIME_EXCLUDED_DOCS` 决定哪些文档的**链接**在运行时载荷里被剥掉。目录改名后不更新它，计划文档的链接就会指向目标项目里不存在的位置。同时，`docs/verification/` 这一条早已失效——该目录在 2026-10-26 已迁到 `docs/archive/verification/`。

**cron 避开整点。**
GitHub 官方说明调度工作流在整点高峰会延迟，并建议避开整点。实测唯一一次定时运行落在 07:34 UTC，比计划的 02:00 晚了 5.5 小时。

**两处技能内的示例路径改成中性表述。**
`requesting-code-review` 和 `subagent-driven-development` 的示例里写死了 `docs/superpowers/plans/xxx.md`。它们是占位示例，但会强化"计划文档就在这个具体路径"的错觉。改成"本变更的计划文档"更准确。

**历史记录不改。**
已归档 change 的正文里出现的旧路径是历史事实，不追溯修改。`docs/maintainer/retro-findings.md` 是活文档，其条目状态要更新。

## Risks

- 目录改名会影响所有引用该路径的文档。本批已全仓搜索确认无遗留引用；归档 change 与两个未完成 change 的历史正文按原则保留。
- `docs/plans/` 成为一个新目录约定。它只属于公共工程壳自身，已加入维护者目录归属表并标记为不进入目标项目公共包。
- 改 cron 后第一次定时运行的时刻会变。这是预期内的。

## Migration

不涉及技能入口数量、运行时依赖、CLI、初始化、逆向与发布流程的语义。
