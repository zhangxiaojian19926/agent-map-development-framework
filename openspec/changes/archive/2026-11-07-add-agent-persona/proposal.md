## Why

工程壳已有阶段表、doctor 和知识库，但主 Agent 每次会话缺少一份常驻、可复查的结果与证据协议。提示词仓库 `7099de8` 的短协议需要接到现有入口上，而不是另开技能或把八个角色登记成子代理。

## What Changes

- 新增能力 `agent-persona`：把 Universal Agent Protocol v4.0 写成唯一人格正文，注入项目根 `AGENTS.md` 的 `FRAMEWORK_ENTRY` 托管段，并放在框架 `AGENTS.md` / `.agent-framework/AGENTS.md` 开头。
- 托管段禁止主 Agent 自行改写；人格、阶段表和子代理只通过评审过的 OpenSpec 变更修改。现有 `RULE_CONFLICT` 继续生效。
- Claude Code 与 CodeBuddy 只安装三个命名只读子代理：`uap-investigator`、`uap-challenger`、`uap-verifier`。不注册其余 UAP 角色，不新建技能，不写 `CODEBUDDY.md`。
- doctor 状态词典不增加人格里的通过 / 部分完成 / 失败 / 阻断四态。不改 `openspec/specs/skill-routing/spec.md`。

## Capabilities

### New Capabilities

- `agent-persona`：规定人格正文的唯一来源、托管段注入与禁止自改、运行包 `AGENTS.md` 与阶段表共存、Claude/CodeBuddy 三个只读子代理、禁止 `CODEBUDDY.md`、以及 doctor 词表边界。

### Modified Capabilities

无。不改 `skill-routing` 或其他已归档能力的验收含义。

## Impact

- 新增 `docs/framework/agent-persona.md`；框架根 `AGENTS.md` 用标记包住同一正文；`tools/framework_core/generation.py` 生成托管段时读取该文件并保留现有英文操作句。
- Claude 与 CodeBuddy 宿主安装改为复制三个共享子代理模板；CodeBuddy 不要求 hooks。
- 测试覆盖托管段含人格与自改禁令、既有 `RULE_CONFLICT`、以及两处人格正文一致。
- 不改 `skill/`、Qwen 模板、doctor 状态词典正文、知识库实现和提示词仓库。
