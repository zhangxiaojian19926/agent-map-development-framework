## Why

公共工程壳自己会犯错，但它没有复盘自己的机制。三轮技能替换加 CI 门禁升级的会话里，**两个自己造成的 CI 红**（空白检查范围错、清单指纹过期）都是靠远端 CI 才发现的，本地没有留下任何记录，也没有机制把它们变成"下次不会再犯"的改进。

框架里已有"知识回流"（把解决过的问题记进知识库），但那是**向后**的——记录已知问题的解法。缺的是**向前**的：让 agent 复盘"这次为什么会绕远路、为什么会误判、哪些指令其实是空转"，并把结论变成可执行的改动。

## What Changes

- 引入 `matt-pocock/retro` 作为会话复盘技能：按导航缺口、自动化检查缺失、编码规范、steering 文件、工具经济、空转指令、信息获取七个类别产出候选，按严重度排序。
- 规定候选必须**绑定会话证据**；无法绑定证据的猜测直接丢弃，不记入清单。
- 规定复盘结果落到 `docs/maintainer/retro-findings.md`，逐条标明"已做 / 已排期 / 待决定"，使后续改动可追踪。
- 规定本框架的证据来源与检查入口：git 历史、CI 运行记录、change 的任务清单、对账记录，以及 `tools/check-framework`、`tools/pre-commit-check`、`openspec validate` 这套检查。
- 引入 `agents/openai.yaml` 与 `disable-model-invocation` 两种形态的组合——这是本框架第一个用户调用型技能，作为调用形态机制的前向试点。

## Capabilities

### New Capabilities

- `session-retrospective`: 规定会话复盘的纪律，包括按需调用的形态、候选的证据要求、七类检查范围的本地映射、结果的记录位置与状态标注。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 新增 `skill/matt-pocock/retro/`：上游原文一份（SKILL.md）、其用户调用形态声明（agents/openai.yaml）与本框架适配层一份（framework-rules.md）。
- 新增 `docs/maintainer/retro-findings.md`，记录本仓库的复盘结果。
- 更新 `AGENTS.md` 与 `docs/framework/skill-policy.md` 说明该技能的可用形态与取用条件。
- 更新 `framework-manifest.json` 的技能分组计数与文件指纹，`THIRD_PARTY_NOTICES.md` 增加来源说明，`docs/integrations.md` 与 `README.md` 的技能构成说明。
- 不引入运行时依赖，不改变 CLI、初始化、逆向与发布流程。
