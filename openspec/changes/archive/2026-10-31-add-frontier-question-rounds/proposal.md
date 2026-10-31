## Why

DISCOVERY 阶段绑定 `superpowers:brainstorming`。那个技能对**一条线索**的提问纪律很好——一次一问、优先多选、聚焦目的/约束/成功标准——但它明确写死"Only one question per message"，并且把"需要更多探索就拆成多个问题"当成解决办法。

真实的设计讨论常常有**互相独立的多个决策**：命名、边界、数据模型、错误处理、兼容策略。这些问题互不依赖，一次问一个会让用户等七八轮。

同时，"事实是你的活"这条纪律在本地技能里没有：本地技能会说"检查项目当前状态"，但没说**当某个问题需要环境才能回答时，应该自己去查而不是问用户**。

## What Changes

- 在 `superpowers:brainstorming` 的提问环节增加**多分支决策的整轮提问**：当若干开放决策互相独立时，一次问完整个前沿——编号、每问附推荐答案、等这一轮答完再问依赖它们的问题。
- 明确**依赖未决答案的问题属于下一轮**，不能塞进当前这一轮。
- 明确**事实由 Agent 自己查**：前沿问题里需要环境才能回答的部分，Agent 自己去查，不把查证工作转给用户。
- 保留"一次一问"作为单线追问的默认规则，不改变现有路径。

## Capabilities

### New Capabilities

- `discovery-questioning`: 规定设计讨论阶段的提问纪律，包括单线追问、互相独立的多个决策的整轮提问、问题与依赖的轮次归属，以及事实由 Agent 自查的分工。

### Modified Capabilities

无。本次不改变 OpenSpec 的需求事实源地位，也不改变任何既有能力的验收含义。

## Impact

- 修改 `skill/super-powers/brainstorming/SKILL.md`：在提问环节增加整轮提问小节，并声明该技法改编自 mattpocock/skills 的 `grilling`。
- 更新 `AGENTS.md` 与 `docs/framework/development-workflow.md` 的设计阶段说明。
- 更新 `THIRD_PARTY_NOTICES.md`：说明该技法改编的来源与归属。
- 技能入口总数不变（27），不引入新技能，不改变运行时依赖、CLI、初始化、逆向与发布流程。
