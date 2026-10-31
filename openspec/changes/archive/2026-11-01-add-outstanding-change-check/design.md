## Context

change 的生命周期有三个环节：写 change（`openspec/changes/<name>/`）→ 同步能力规格到 `openspec/specs/` → 归档到 `openspec/changes/archive/`。

现有两道 OpenSpec 校验各管一头：

| 校验 | 覆盖 |
|---|---|
| `openspec validate --all --strict` | 活动 change 的 delta 规格结构 + 正式规格结构 |
| `openspec validate --archived` | 已归档 change 的任务是否全部完成 |

**缺口在中间**：一个任务全部完成、还在活动区的 change，两道都看不见。它声明的能力不在规格库里，而规格库没有别的机制会提醒这件事。

## Decisions

**做成独立的只读工具，而不是塞进 `tools/check-framework`。**
`check-framework` 校验的是**分发内容**（指纹、链接、技能计数、形态声明）。change 生命周期是这个仓库自身的 OpenSpec 状态，两者是不同关注点；而且 `check-framework` 会随包分发到目标工程，而目标工程不接收 `openspec/changes/`，把仓库自身的生命周期检查塞进去会让那个工具在目标工程上做无意义的事。

**只读，不代替同步与归档。**
工具报出"哪个 change 完成了、缺哪些能力的同步、该走归档流程了"，但它不移动目录、不合并规格。同步是智能合并（上游 `openspec-sync-specs` 明确要求 Agent 读 delta 与 main 后合并，不是覆盖），归档也要走正常流程。一个会自己改文件的检查会绕过这两道需要判断的步骤。

**区分两种未完成形态。**
"能力规格没同步"和"已同步但没归档"是两种不同的欠账，处理方式不同。工具分别报出，避免维护者以为只要同步就够了。

**判定"完成"只看任务清单。**
`tasks.md` 里没有未勾选的项就算完成。没有 `tasks.md` 的 change 不判定——没有证据就不报。`skip_specs` 的 change 没有 delta 规格，因此它只需要归档。

**接入三处而不是一处。**
- `tools/pre-commit-check`：本地序列。它是 CI 门禁的本地镜像，本地不跑就等于把问题留给远端。
- `validate.yml`：每次推送与拉取请求。完成了却没归档的 change 进不了正式规格库，这个门禁要在合并前就拦住。
- `release.yml`：打 tag 前。发布出去的版本规格库必须是完整的。

**先在真实历史里验证过这个缺口存在。**
2026-10-31 审计发现六个 100% 完成却未归档的 change（当时为 `add-completion-summaries` 等，已在同日人工同步并归档）。这不是假想场景，是已经付过代价的场景。

## Risks

- 拉取请求可能因为自己完成了某个 change 而被这道门禁拦下。这是正确提示——该 change 本来就该同步并归档——但对贡献者是新负担，错误信息里直接给出下一步。
- 判定"完成"只认任务清单，不看规格是否满足。若一个 change 的任务勾了但规格没写完，本检查发现不了；那属于规格评审的职责，不是归档检查的职责。
- 工具只覆盖本仓库的顶层 `openspec/changes/`，不覆盖多仓场景里的其他仓库。

## Migration

不涉及技能入口数量、运行时依赖、CLI、初始化、逆向与发布流程的语义。
