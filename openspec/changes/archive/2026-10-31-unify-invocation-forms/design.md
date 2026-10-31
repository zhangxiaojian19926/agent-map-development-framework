## Context

形态声明分散在两个宿主各自的约定里：

| 宿主 | 读哪里 | 缺省 |
|---|---|---|
| Claude Code | 技能 frontmatter 的 `disable-model-invocation: true` | 模型调用型 |
| Codex | `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` | 模型调用型 |

两边都默认"模型调用型"，所以**漏写声明通常不改变行为**——直到有人把一个技能声明为用户调用型而只写一侧。

## Decisions

**检查规则做成双向的，而不是"必须有 agents/openai.yaml"。**
如果要求每个技能都必须带 `agents/openai.yaml`，就得给二十多个技能补文件，其中大部分是无意义的重复声明。更有价值的是**只在声明存在时校验两侧一致**：
- frontmatter 写了 `disable-model-invocation: true` → 必须有 `agents/openai.yaml` 且写 `allow_implicit_invocation: false`
- `agents/openai.yaml` 写了 `allow_implicit_invocation: false` → 必须有 frontmatter 的 `disable-model-invocation: true`
- 两侧都不写 → 都是模型调用型，通过

这样新技能不必被强制写声明，而**真正会出问题的单侧声明会被抓住**。

**`to-tickets` 改为模型调用型，这是有意的本地改编。**
上游把它做成用户调用型，因为上游的 `to-spec` / `implement` 是配套的编排入口，用户一次只调一个。本框架没有那套编排，计划阶段是**流程里的一个阶段**，Agent 必须能自主到达。所以：
- frontmatter 去掉 `disable-model-invocation`
- `agents/openai.yaml` 的 `allow_implicit_invocation` 改为 true
- 第三方声明里写明这是本地改编

`retro` 保持用户调用型——复盘是人主动要求的，让 Agent 每次会话结束就自己开复盘是噪声。

**阶段路由点名的技能必须是模型调用型。**
这条规则写进 `skill-policy.md`：阶段由 Agent 按流程推进，用户不需要、也不应该知道每个阶段的技能名。参考型技能（写作参考、接口设计参考）与编排型技能（复盘）可以声明为用户调用型。

**补齐其余技能的上游声明。**
五个漏带的 `agents/openai.yaml` 按上游字节恢复，附带 Codex 的 `display_name` 与 `short_description`。这些元数据本身也有用——它们是 Codex 技能选择器里显示的名字。

## Risks

- 形态检查只覆盖随包分发的技能，不覆盖使用者自己写的技能。这是有意的边界：本仓库只管自己分发的内容。
- 检查用文本匹配 frontmatter 的固定写法。非常规写法会被漏掉，但技能 frontmatter 本身就是固定格式，不构成实际风险。
- 把 `to-tickets` 改成模型调用型后，它在 Codex 侧会常驻于发现面。这是阶段技能的必然代价。

## Migration

技能入口总数不变（28）。形态改变只影响 `to-tickets` 一个技能。不涉及初始化、CLI、逆向与发布流程。
