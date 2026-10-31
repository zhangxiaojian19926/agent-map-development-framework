## Why

公共工程壳本身是一个“给 agent 写文档”的分发包：它发布顶层 AGENTS.md、23 个技能入口和 docs/framework 下的公共规则。但仓库里没有任何“如何写好这些文档”的方法论，也没有模块内部接口设计的共享词汇。

两个具体后果已经在使用中暴露：

- 技能 description 是典型的弱指针：多个近义触发分支写在一个 description 里，还有永久触发的入口（例如“任何对话开始时”），模型发现面被稀释。
- 公共协作规则只管模块之间（接口双方、集成顺序、版本组合），模块内部的 seam 位置、接口深度和替换策略没有任何共享语言，评审时只能各说各话。

## What Changes

- 引入 `writing-for-agents` 参考技能，覆盖 context pointer、context/cognitive 双预算、渐进披露、co-location、leading word、negation 失效和 no-op 指令检测，并附带技能调用形态的说明。它是纯参考文档，不依赖 issue tracker、领域词汇表或任何宿主能力。
- 引入 `codebase-design` 参考技能，规定 module / interface / seam / adapter / depth / leverage / locality 的用词与设计原则，附带依赖分类、seam 纪律和“替换而非叠加”的测试策略。
- 两个技能都以独立分组随包分发，登记来源、版本与许可归属；技能计数与清单保持一致。
- 公共规则与工作流文档指向这两个参考：写或改技能、AGENTS.md、CLAUDE.md 以及任何被指针引用的文档时读取写作参考；设计或重构模块接口、决定 seam 位置、判断可测试性时读取接口设计参考。

## Capabilities

### New Capabilities

- `agent-craft-skills`: 规定面向 agent 的文档写作参考与模块内部接口设计参考的引入、归属、分发和工作流接线。

### Modified Capabilities

无。本次不改变既有能力的验收含义，也不新增运行期依赖。

## Impact

- 新增 `skill/matt-pocock/` 分组：`writing-for-agents/`、`codebase-design/` 及其子文档，以及该分组的 LICENSE。
- 更新 `THIRD_PARTY_NOTICES.md`，按既有三段结构增加第四个第三方来源声明。
- 更新 `framework-manifest.json`：来源列表增加该上游及其固定提交，技能计数分组增加对应条目，文件指纹整体刷新。
- 更新 `AGENTS.md` 阶段路由、`docs/framework/development-workflow.md` 与 `docs/integrations.md` 的技能说明和计数。
- 不引入运行时依赖、不新增 CLI 子命令、不改变初始化与逆向流程。
