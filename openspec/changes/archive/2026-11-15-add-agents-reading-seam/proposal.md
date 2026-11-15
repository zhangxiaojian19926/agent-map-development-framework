## Why

框架根 `AGENTS.md` 在同一文件里先后出现两段标题：第 2 行 `# Universal Agent Protocol v4.0 — 结果与证据优先` 在标记内，第 50 行 `# AGENTS.md — 公共开发流程入口` 在标记外。第 48 行是 `<!-- AGENT_PERSONA_END -->`，第 49 行是空行。文件没有一句写明：这两段是同一次任务的前后半，以及读完人格之后下一步进入哪一节。

下面用本次读到的规格、生成代码和测试，按前提、排除、结论确定可以写这句话的位置。不改标记内正文，不改阶段表各行。

### 前提

1. 标记内正文必须与 `docs/framework/agent-persona.md` 逐字相同。`openspec/specs/agent-persona/spec.md` 第 30 行：框架仓库 `AGENTS.md` 用 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 包住与 `docs/framework/agent-persona.md` 相同的人格正文。第 35 行 Scenario「标记内正文与唯一来源一致」的 THEN 是「两处正文相同」。本次命令对标记内正文和 `agent-persona.md` 做 `strip()` 后比较：相等，两边长度都是 2321，SHA-256 都是 `612448e364e7dcc3738e8f634fd61451f8b8e342d5b2398219ba99378c07abb2`。同一命令确认 `agent-persona.md` 不含 `## 0.`，也不含 `## 1.`。

2. 阶段表必须留在标记之后。同一 Requirement 第 30 行：复制后的文件 MUST 以同一份人格开头，MUST 仍包含现有阶段路由表。第 40 行 Scenario「运行包保留阶段表」的 THEN：该文件以人格正文开头，并且仍含有 DISCOVERY 到 KNOWLEDGE 的阶段路由表。现有表在 `AGENTS.md` 第 91–103 行；第 93 行是 `| 1. DISCOVERY |`，第 103 行是 `| 11. KNOWLEDGE |`。

3. `FRAMEWORK_ENTRY` 由 `agent-persona.md` 生成，不含 §0/§1。`tools/framework_core/generation.py` 的 `persona_text`（第 127–133 行）只读 `docs/framework/agent-persona.md`，返回 `strip()` 后的正文加换行。`generation_changes` 第 68–80 行把这个返回值拼上固定英文操作句，得到 `agent`。英文操作句是「Read public workflow」、只读 doctor、地图发布条件、已批准 OpenSpec/TDD，以及完成后写入初始化知识库；其中没有「§0」或「§1」。`prepare` 为真时，第 85–86 行用 `<!-- FRAMEWORK_ENTRY_START -->` / `<!-- FRAMEWORK_ENTRY_END -->` 包住 `agent`。规格第 11 行要求托管段写入的就是这份人格正文加上这些英文操作句。框架根的 `## 0. 先读谁` 在第 54 行，`## 1. 按任务选路径` 在第 72 行，都在第 48 行标记之后，不在 `persona_text` 的输入里。

4. 运行包是框架根 `AGENTS.md` 的整份复制。规格第 30 行：把该文件整份复制为业务工程的 `.agent-framework/AGENTS.md`。`generation_changes` 第 14 行把 `AGENTS.md` 列入 `RUNTIME_ROOT_FILES`；第 49–65 行按清单读取分发包中的该文件，markdown 经 `runtime_markdown`（第 24–36 行，只改写部分链接）后写入 `outputs['.agent-framework/' + rel]`。这不是只复制标记内。第 103 行 `outputs['AGENTS.md'] = agent` 是 `prepare` 为假时的另一条路径，内容只有人格加英文操作句，不是运行包。

### 排除

1. 把两段合成一节。把第 91–103 行的阶段表放进第 1–48 行的标记，标记内就不再是 `agent-persona.md`。该文件没有阶段表，也不含 `## 0.` / `## 1.`。这违反规格第 30 行和第 35 行。去掉标记，或让人格不再处于文件开头，违反第 30 行「用 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 包住」以及第 40 行「以人格正文开头」。`tests/test_bootstrap_generation.py` 第 211 行要求 `| 1. DISCOVERY |` 出现在 `PERSONA_END` 之后，合成进标记内就不再满足这个断言。

2. 把阅读顺序写进人格。只改 `AGENTS.md` 第 2–47 行会使标记内正文与 `agent-persona.md` 不等，`tests/test_bootstrap_generation.py` 第 210 行和 `tests/test_flow_routers.py` 第 89 行的 `assertEqual` 失败。两处一起改，则 `persona_text`（第 127–133 行）把新正文交给第 68 行，再由第 86 行写入 `FRAMEWORK_ENTRY`。将写入的句子含「§0」「§1」。这两节只在框架根第 54、72 行，不在 `persona_text` 的来源里，也不在第 68–80 行的英文操作句里。业务根托管段因此会含它自己没有的节。规格第 11 行要求托管段含的是人格正文和列出的英文操作句，不是框架文件的 §0/§1。`openspec/specs/agent-workflow-routers/spec.md` 第 302 行 WR-16 写明系统 SHALL NOT 改写 `FRAMEWORK_ENTRY` 托管段。本 change 不修改该能力。人格来源一旦变化，哈希相符的 prepare 会按 `generation.py` 第 91–94 行替换托管段。

3. 改阶段表各行。规格第 30 行要求 MUST 仍包含现有阶段路由表，第 40 行要求仍含有 DISCOVERY 到 KNOWLEDGE。现有表就是第 91–103 行。改其中一行，复制结果就不再是这张表。第 211 行和第 230 行还锁定 `| 1. DISCOVERY |` 仍在。

4. 改 doctor 词。规格第 5 行 Purpose 写明不改 doctor 词表。Requirement「doctor 词表不增加验收四态」第 70–72 行：不得把通过、部分完成、失败、阻断写入状态词典；`READY`、`PARTIAL`、`BLOCKED` MUST 继续只描述工程接入；人格 MUST NOT 把 doctor 的工程接入状态当成单次交付结论。`AGENTS.md` 第 44 行已经把这两套词分开。WR-16 第 302 行同时禁止把新的验收状态写入 `docs/guide/framework-model.md` 的状态词典。`test_persona_block_matches_source_and_status_dictionary_stays_put` 第 92–95 行锁定 `<!-- status-dictionary:start -->` 之后的片段与 `HEAD` 相同。

5. 改「简单任务直接完成」。该句在标记内：`AGENTS.md` 第 12 行，`agent-persona.md` 第 11 行。第 42 行（`agent-persona.md` 第 41 行）写明不能用这句跳过已批准的规格、实现、评审和验证。改这句会使标记内正文不再与来源相同，违反规格第 30、35 行。

6. 改委派句。`AGENTS.md` 第 31–35 行在标记内，改它们同样违反第 30、35 行的逐字相同。第 96 行「委派需授权」属于第 91–103 行的现有阶段表，改它违反第 30、40 行。

7. 改第 47 行自改禁令。该行在标记内，原文是「不得修改 `FRAMEWORK_ENTRY` 托管段。人格、阶段表和子代理只通过评审过的 OpenSpec 变更修改。现有 `RULE_CONFLICT` 继续生效。」`agent-persona.md` 第 46 行是同一句。规格第 11 行要求人格正文禁止主 Agent 修改该托管段；第 21 行 THEN 要求正文写明不得修改 `FRAMEWORK_ENTRY` 托管段。`test_prepare_managed_block_includes_persona_and_forbids_self_edit` 第 223 行断言托管段含 `SELF_EDIT_BAN`。

### 结论

满足上面四条前提的改动不能进入第 1–48 行，也不能改第 91–103 行。

第 48 行与第 50 行之间只有第 49 行，本次命令读到该行是空字符串。这是 `AGENT_PERSONA_END` 之后、第二个一级标题之前的唯一一行。

四条前提单独还不排除第 51–90 行，也不排除第 104 行之后：那些位置同样在标记外，不改阶段表各行，也不会进入 `persona_text`。收窄到第 49 行用的是将写入句子的指称，不是另一条 Requirement。该句把「标记后的流程入口」指到第 50 行的标题，并写「出标记后进入 §0」；§0 在第 54 行。句子若放在第 50 行或第 54 行之后，读到它时所指的标题或 §0 已经过去。在第 50 行之前、又在标记外的行，只有第 49 行。

将写入第 49 行的正文是：

```
一次任务只读这一份文件。标记内的人格和标记后的流程入口是同一次任务的前后半，不是两份任务。

阅读顺序：标记内先读约束，再读交付姿态，再读工程壳闸门；出标记后进入 §0，再按 §1 分流；需要走阶段表时只进入命中的一条 flow，下一项以该 flow 正文为准。收尾时 doctor 的工程接入词和这一次交付的成败词分开写。
```

这句不改第 12、31–35、44、47、91–103 行。它不列出 15 条 flow 的名字；第 89 行已经写明入口是 `flow-01` 到 `flow-15`，一条请求只命中其中一个，下一项以该路由正文为准。这句里的「一条 flow」和「下一项以该 flow 正文为准」与第 89 行一致。它不新增 doctor 状态码，只重述第 44 行已经分开的两套词。文件里的节名是第 40 行「工程壳绑定」，不是「工程壳闸门」；「约束」「交付姿态」也不是现有标题。规格没有禁止在标记外用这两个称呼指标记内已有段落，因此正文不替换。

### 反例

若把上面这段话放进标记内，并且为了通过第 35 行的「两处正文相同」而同步 `agent-persona.md`，调用关系是：

`persona_text(distribution)` 读取 `docs/framework/agent-persona.md`（`generation.py` 第 127–133 行）→ `generation_changes` 第 68 行把它与英文操作句拼成 `agent` → 第 86 行 `block = begin + '\n' + agent + end`，其中 `begin` / `end` 是 `FRAMEWORK_ENTRY` 标记（第 85 行）→ 哈希相符时第 94 行用这个 block 替换业务根 `AGENTS.md` 里的旧托管段。

替换后的业务根托管段会含「§0」「§1」。业务根的托管段来源只有 `agent-persona.md` 和要求 3 里的英文操作句，没有第 54 行和第 72 行。运行包里的 §0/§1 来自整份复制（第 49–65 行），不来自 `persona_text`。

## What Changes

- 将来只在框架根 `AGENTS.md` 第 49 行写入上一节给出的两段话。第 1–48 行、第 50 行标题、第 91–103 行阶段表保持不动。
- 行为变化落在已有能力 `agent-persona`：Requirement「运行包 AGENTS 以同一人格开头并保留阶段表」增加一个 Scenario，要求这段话位于 `AGENT_PERSONA_END` 之后、第二个一级标题之前，且标记内正文仍与 `agent-persona.md` 相同。
- 不修改 Requirement「托管段含人格且禁止自行改写」。不把 `agent-workflow-routers` 放进本 change 的 delta。WR-16 只作为上面第 2 项排除的依据。
- 将来补一条位置测试。现有三条测试继续锁住标记内一致、阶段表在标记之后、托管段含人格和自改禁令、状态词典片段不变。
- 本次不实施上述源文件修改。

## Capabilities

### New Capabilities

- 无。阅读顺序是运行包入口上的一句位置约束，不引入新 capability。

### Modified Capabilities

- `agent-persona`（`openspec/specs/agent-persona/spec.md`）：Requirement「运行包 AGENTS 以同一人格开头并保留阶段表」增加 Scenario。标记结束后、第二个一级标题之前 MUST 有指定的阅读顺序；`AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间的正文 MUST 仍与 `docs/framework/agent-persona.md` 相同；阶段路由表 MUST 仍在标记之后。不改「托管段含人格且禁止自行改写」，不改「doctor 词表不增加验收四态」。

## Impact

- 实施阶段才会改框架根 `AGENTS.md` 的第 49 行。运行包 `.agent-framework/AGENTS.md` 因第 49–65 行的整份复制，会在之后的 prepare 里带上这段话。`runtime_markdown` 不改写这段纯文本。
- 业务根 `FRAMEWORK_ENTRY` 不变。`persona_text` 的来源文件不改，第 68–80 行的英文操作句不改。
- 现有测试仍然适用：`GenerationTests.test_framework_agents_persona_matches_source`（第 205–211 行）锁标记内相等，并锁 `| 1. DISCOVERY |` 在 `PERSONA_END` 之后。`GenerationTests.test_prepare_managed_block_includes_persona_and_forbids_self_edit`（第 213–230 行）锁托管段含人格来源、`SELF_EDIT_BAN`、公共工作流英文句和「initialized knowledge base」，且运行包以 `AGENT_PERSONA_START` 开头并含 `| 1. DISCOVERY |`。`RouterContractTests.test_persona_block_matches_source_and_status_dictionary_stays_put`（第 83–95 行）锁标记内相等、含「写入初始化知识库」、不含「询问是否摄入」，并锁状态词典片段与 `HEAD` 相同。
- 这三条都不断言第 49 行存在阅读顺序。还缺一条位置测试，断言是：固定句「标记内先读约束，再读交付姿态，再读工程壳闸门」出现在 `AGENT_PERSONA_END` 之后、`| 1. DISCOVERY |` 之前；该句不出现在两个标记之间；`docs/framework/agent-persona.md` 不含该句。
- 非目标：本次不改 `AGENTS.md`，不同步 `agent-persona.md`，不改 `generation.py`，不刷新 `framework-manifest.json`，不改 `skill/flows/flow-01` 到 `flow-15` 的正文，不改第 12、31–35、44、47、91–103 行。清单指纹是实施阶段的事。
