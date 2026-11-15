## Context

见 `proposal.md` 的前提与结论。框架根 `AGENTS.md` 的人格由 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 包住，阶段表在标记之后。`persona_text()` 只读 `docs/framework/agent-persona.md`，用来拼业务项目根的 `FRAMEWORK_ENTRY`。生成器不把人格标记写回框架根 `AGENTS.md`。运行包 `.agent-framework/AGENTS.md` 是框架根该文件的整份复制。

## Goals / Non-Goals

**Goals:**

- 在第 48 行 `<!-- AGENT_PERSONA_END -->` 与第 50 行第二个一级标题之间写入 proposal 给出的两段正文。当前这一位置是空的第 49 行。
- 标记内正文继续与 `docs/framework/agent-persona.md` 相同，阶段表仍在标记之后。
- 实施时在 `GenerationTests` 增加位置测试，并在改源文件后运行 `python3 tools/update-manifest`。

**Non-Goals:**

- 不改人格正文，不同步 `docs/framework/agent-persona.md`。
- 不改阶段表各行，不改 doctor 词，不改「简单任务直接完成」，不改委派句，不改第 47 行自改禁令。
- 不改 `generation.py`，不把这段话写入业务根 `FRAMEWORK_ENTRY`。
- 不改十五条 flow 正文，不改 `agent-workflow-routers`。
- 本次不实施，不刷新 manifest。

## Decisions

1. **只插入第 48 行与第 50 行之间。** 正文以 proposal 为准，不改写。备选是把阅读顺序写进人格，或把两段合成一节。写进人格会经 `persona_text()` 进入业务根 `FRAMEWORK_ENTRY`，而那段没有 §0/§1。合成一节会改变标记内正文或把阶段表移出「标记之后」。

2. **生成器不负责这段话。** 框架根 `AGENTS.md` 的人格标记以源文件为准，生成器不写回该文件。业务根 `FRAMEWORK_ENTRY` 仍只含 `agent-persona.md` 加现有英文操作句，因此不含这段接缝。运行包整份复制框架根 `AGENTS.md`，接缝会出现在 `.agent-framework/AGENTS.md`。

3. **位置测试放在 `GenerationTests`。** 断言固定句「标记内先读约束，再读交付姿态，再读工程壳闸门」在 `AGENT_PERSONA_END` 之后、`| 1. DISCOVERY |` 之前；该句不在两个标记之间；`docs/framework/agent-persona.md` 不含该句。现有的标记一致和阶段表在标记之后的测试保持不动。改完 `AGENTS.md` 后刷新 `framework-manifest.json` 的指纹，否则按清单复制会报哈希不符。

## Risks / Trade-offs

- [第 49 行会随插入变成正文，其后行号后移] → 验收用标记和 `| 1. DISCOVERY |` 的相对位置，不把「第 49 行」当作长期断言。
- [`tools/update-manifest` 会重算全部指纹] → 实施时只核对本次 `AGENTS.md` 的指纹差异，不把工作区里无关改动算进这次刷新的意图。
- [业务根读不到这段接缝] → 业务根英文操作句已经指向 `.agent-framework/AGENTS.md`；接缝只存在于被整份复制的那份文件。

## Migration Plan

1. 先改框架根 `AGENTS.md` 第 48 与第 50 行之间，再添加 `GenerationTests` 的位置测试。
2. 测试通过后运行 `python3 tools/update-manifest`，检查指纹 diff。
3. 回退时删掉这两段，恢复第 49 行为空行，并再次刷新指纹。不改人格来源，因此不需要回退 `FRAMEWORK_ENTRY` 的生成结果。

## Open Questions

无。
