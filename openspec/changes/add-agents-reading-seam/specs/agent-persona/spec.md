## MODIFIED Requirements

### Requirement: 运行包 AGENTS 以同一人格开头并保留阶段表

系统 SHALL 让框架仓库 `AGENTS.md` 用 `AGENT_PERSONA_START` / `AGENT_PERSONA_END` 包住与 `docs/framework/agent-persona.md` 相同的人格正文，并把该文件整份复制为业务工程的 `.agent-framework/AGENTS.md`。复制后的文件 MUST 以同一份人格开头，MUST 仍包含现有阶段路由表。两处人格正文 MUST 一致。

框架仓库 `AGENTS.md` MUST 在 `AGENT_PERSONA_END` 之后、一级标题 `# AGENTS.md — 公共开发流程入口` 之前包含下面两段正文。这两段 MUST NOT 出现在 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间，也 MUST NOT 出现在 `docs/framework/agent-persona.md`。固定句「标记内先读约束，再读交付姿态，再读工程壳闸门」MUST 位于 `AGENT_PERSONA_END` 之后、`| 1. DISCOVERY |` 之前。

```
一次任务只读这一份文件。标记内的人格和标记后的流程入口是同一次任务的前后半，不是两份任务。

阅读顺序：标记内先读约束，再读交付姿态，再读工程壳闸门；出标记后进入 §0，再按 §1 分流；需要走阶段表时只进入命中的一条 flow，下一项以该 flow 正文为准。收尾时 doctor 的工程接入词和这一次交付的成败词分开写。
```

#### Scenario: 标记内正文与唯一来源一致

- **WHEN** 比较框架 `AGENTS.md` 中 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间的正文和 `docs/framework/agent-persona.md`
- **THEN** 两处正文相同

#### Scenario: 运行包保留阶段表

- **WHEN** 初始化把框架 `AGENTS.md` 复制到 `.agent-framework/AGENTS.md`
- **THEN** 该文件以人格正文开头，并且仍含有 DISCOVERY 到 KNOWLEDGE 的阶段路由表

#### Scenario: 阅读顺序位于标记之后且不进入人格来源

- **WHEN** 比较框架仓库根 `AGENTS.md` 与 `docs/framework/agent-persona.md`
- **THEN** 两标记之间的正文在去掉首尾空白后与 `docs/framework/agent-persona.md` 去掉首尾空白后相同，且 `| 1. DISCOVERY |` 仍出现在 `AGENT_PERSONA_END` 之后；固定句「标记内先读约束，再读交付姿态，再读工程壳闸门」出现在 `AGENT_PERSONA_END` 之后、`| 1. DISCOVERY |` 之前，并且不出现在 `AGENT_PERSONA_START` 与 `AGENT_PERSONA_END` 之间；`docs/framework/agent-persona.md` 不含该固定句；上面两段正文出现在 `AGENT_PERSONA_END` 之后、`# AGENTS.md — 公共开发流程入口` 之前
