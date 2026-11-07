## Context

参见 [提案](proposal.md) 与 [增量规格](specs/agent-persona/spec.md)。宿主自动注入的是业务项目根 `AGENTS.md` 的 `FRAMEWORK_ENTRY` 托管段，不是 `.agent-framework/AGENTS.md`。框架仓库 `AGENTS.md` 会被整份复制成运行包入口。提示词来源钉在 `66.agent_prompt@7099de8`，只复制短协议并加壳绑定，不把提示词仓库做成子模块。

## Goals / Non-Goals

**Goals**

- 人格只有一份正文，生成托管段与框架入口都读它，测试比较标记内外，避免两份文案漂移。
- 阶段表、doctor、知识库规则继续承担开发过程；人格只补结果与证据协议和壳绑定。
- Claude 与 CodeBuddy 安装同一份三个只读子代理；其余宿主本期只得到人格。

**Non-Goals**

- 不建技能、不把八个 UAP 角色登记成子代理、不另开自动系统。
- 不改 Qwen 模板、doctor 状态词典、知识库实现、提示词仓库。
- 不把换模型效果、真实项目闭环或知识回流标成已完成。

## Decisions

1. **唯一正文放在 `docs/framework/agent-persona.md`。** 内容为 `7099de8` 的短协议全文，加上与阶段表冲突的壳绑定。`generation.py` 从分发包读取该文件，拼上现有英文操作句后写入 `FRAMEWORK_ENTRY`。框架 `AGENTS.md` 用 HTML 注释 `<!-- AGENT_PERSONA_START -->` / `<!-- AGENT_PERSONA_END -->` 包住同一正文，阶段表留在后面。备选是直接把人格写进 `generation.py` 字符串，那样无法与框架入口对拍。

2. **托管段禁止自改，升级仍走哈希归属。** 已有完整且哈希匹配的区块可被 prepare 替换为含人格的新正文；残缺或人工改写继续 `RULE_CONFLICT`。不把人格标记写进托管段，避免与 `FRAMEWORK_ENTRY` 两套标记混用。

3. **子代理共享模板，不写 `CODEBUDDY.md`。** 模板在 `templates/host/agents/`。Claude 复制到 `.claude/agents/`，CodeBuddy 复制到 `.codebuddy/agents/`。CodeBuddy 在没有 `CODEBUDDY.md` 时才会把根 `AGENTS.md` 当项目记忆。适配器增加 `requires_hooks`：Claude 与 Qwen 为真，CodeBuddy 为假。investigator/challenger 去掉 `Bash`；verifier 保留 `Bash`。本期不实现宿主安装的代码归属本设计，实施落在宿主适配切片。

4. **doctor 词表与人格验收态分家。** 人格里的通过、部分完成、失败、阻断只描述这一次交付。不把它们登记进 `docs/guide/framework-model.md`。doctor 的 `READY` / `PARTIAL` / `BLOCKED` 继续只描述工程接入。

## Risks / Trade-offs

- 托管段里的人格使用仓库根路径（如 `docs/framework/knowledge-policy.md`），在业务项目根上不是运行包路径。→ 英文操作句首先要求读取 `.agent-framework/AGENTS.md`，运行包内相对路径仍然成立。
- 已接入工程的托管段哈希会因人格注入而变化。→ 仅当旧区块仍被归属记录认领时才替换；人工改写不覆盖。
- 子代理安装与人格注入并行。→ 规格先把安装合同写清；未安装时主 Agent 自己做并写明未委派。

## Migration Plan

新 prepare 的工程直接得到含人格的托管段。已有工程在下次成功的 prepare 中，若托管段未被人工改写则升级为含人格正文。撤回时恢复上一份受管区块即可，不删用户正文。
