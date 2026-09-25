## Context

当前发布基线是公共框架 0.1.0：规则、21 个技能、模板、知识脚本和分发校验，尚无工程生成器。动机见 [proposal](proposal.md)。本设计是待审阅的行为变更，不表示命令已经存在。
当前公共工作树已建立自己的 OpenSpec 根，避免 CLI 向上命中无关项目；这次初始化仅创建规划结构，没有配置宿主技能或全局工具。
初次只读预检发现本机 Codex CLI 启动失败（底层二进制缺失，ENOENT）。后续用户单独授权修复，CLI 已统一到 0.151.0 并通过真实模型/Shell 只读任务；这解决了启动环境问题，不替代本变更的多模块适配验收。安装修复不随公共包自动执行。

## Goals / Non-Goals

**Goals:**

- 一条入口命令接入工程，统一显示计划和权限后执行，用户无需手工复制模板或逐模块 init。
- 支持 init（已有工程）和 new（全新需求），让 Agent 主动建立并维护可追踪地图。
- 骨架、导航、代码实现和业务验证分别记录，不把部分成功包装成完整就绪。
- 不改变原有知识辅助脚本的授权语义，保留第三方来源及用户已有数据。

**Non-Goals:**

- 不自动创建远程仓库、公开源码、部署或连接设备。
- 不承诺所有宿主、Windows、所有语言或所有 hook 管理器首版即兼容。
- 不在 Git 钩子运行 LLM 或业务脚本；不增加全局 watcher。
- 不根据需求自由选择未经确认的业务技术栈，不自动“实现整款产品”。
- 不把 JSON 授权字段、AGENTS.md 或进程内白名单当操作系统安全沙箱。

## Decisions

### 1. 统一入口及两种生命周期

采用 Python 3.9+ 标准库作为确定性编排层，薄入口 tools/framework，内部模块按配置、事务、模块发现、适配器、地图、检查拆分。相比 shell 拼接，便于结构化校验、路径处理和可恢复状态；相比纯 Agent 执行，文件生成和错误语义更可复现。

以下为拟实现接口：

| 命令 | 用户提供 | 结果 |
|---|---|---|
| init --target PATH | 目标路径；交互选择宿主、发现根和能力 | 已有工程接入、分析及检查 |
| new --target PATH | 需求或批准的设计引用 | 未批准先规划；批准后生成工程骨架 |
| module clone --target PATH --url URL --path REL | 来源及工程内路径，可指定 ref | 下载后进入 add 同一状态机 |
| module add --target PATH --path REL | 已有或解压目录 | 确认身份、登记、索引、建图 |
| module sync --target PATH | 已登记发现范围 | 仅更新客观目录、标记地图过期；不隐式执行 Agent |
| doctor --target PATH | 目标路径 | 默认只读诊断与下一步 |
| resume --target PATH | 未完成 run 的选择与当前权限 | 重验输入后恢复，不盲目重放 |

init/new 支持 --config、--dry-run、--yes。--yes 仅确认显式计划里的动作，不补默认全局安装、源码发送或业务执行权限。未指定 agent 时交互列已检测候选，非交互缺值报错。

new 分为需求草案、设计批准、计划批准、生成四段。尚无工程时先在对话完成需求设计；用户要求保存时只创建明确的规划产物。保存草案不等于批准；自动调度的 Agent 不得自己批准自己的设计。带批准设计和计划的输入可直接从生成阶段开始。
init 的预检可给出模块候选；模块身份确认后才开展索引和语义分析。

### 2. 状态机、预算和退出码

执行链：
```text
PREFLIGHT -> PLAN -> CONFIRMED -> FRAMEWORK_READY
 -> MODULES_DISCOVERED -> INDEXES_CHECKED -> AGENT_ANALYZED
 -> MAPS_VALIDATED -> READINESS_REPORTED
```

失败在原步骤记录原因和恢复点。系统状态用 READY/PARTIAL/WAITING_AGENT/BLOCKED；new 的需求门禁另用 NEEDS_DESIGN_APPROVAL/NEEDS_PLAN_APPROVAL。导航与 runtime 两个独立维度；EMPTY/PLANNED 不冒充实际图。
CLI 退出码：0 完成本次命令声明范围（如成功预览不代表工程 READY）；2 无效输入；3 需要用户确认或冲突；4 依赖/执行失败或超时；5 部分完成或等待 Agent。JSON 同时返回 phase、各能力状态、诊断和 next_actions，不只返回布尔 success。
交互等待不计执行时限。外部操作逐项限时，取消要终止本次拥有的进程组并保留状态；索引默认串行，避免多大仓库同时耗尽资源。不得停止其他会话进程。

### 3. 文件组织与单源

目标工程中：
```text
AGENTS.md
framework-project.json
.agent-framework/                 # 固定版本公共包，保留内部相对链接
.framework/local-state/           # 本机计划、事务、锁和工具信息，不随包授权他机
docs/project/
  overview.md
  architecture.md                 # 人工批准的设计
  collaboration.md
  constraints.md
  resources.md                    # 引用登记源，不复制另一份权威路径表
  module-map.generated.md
  relationships.generated.json   # 经校验的实际观察
  relationships.generated.md     # JSON 派生视图
module-catalog.generated.json
llm-wiki-aliases.json              # 仅在用户选择时配置
<module-root>/AGENTS.md            # 或项目侧 docs/project/modules/<id>.md
```

framework-project.json 声明稳定项目 ID、模块声明、发现根、适配选择和期望自动化范围；不含密钥或机器绝对路径。机器能力授权由当前可信调用/交互提供，克隆配置不能自授权。
模板初次实例化后属于用户；只能更新显式受管段或派生文件。公共包更新与项目事实更新分开。copy 公共包须排除其 .git、源码工程实例及本机状态，保留技能支持资源和许可证。
只索引业务源码范围，排除复制的公共技能、测试 fixture、生成地图和外层嵌套独立仓库，避免循环自分析及重复成本。

### 4. 安全写入与恢复

计划包含规范化路径、文件前置指纹、预期动作和能力；应用时重新校验路径、符号链接和内容指纹，输入变化使计划失效。
受管文件用同目录临时文件原子替换。事务日志记录逐文件动作；多仓库不声称原子事务。失败恢复只处理本次创建且指纹未变的文件，不删除目标根；人工新增或修改时输出冲突。
每工程/工作树加锁；并发初始化拒绝重复写，等待有界。工具路径与参数以数组调用，不执行 shell 字符串。仓库 URL 含凭据拒绝或脱敏，日志不保存秘密；Git clone 不递归拉子模块，不启用下载模块的 hook 或安装脚本。

### 5. 模块身份和发现

将 module-id、repo-id、index-id 分开。新模块的路径推导 ID 只作初次建议；后续路径变化用稳定描述符或显式移动映射维持身份，不凭相似名称自动合并。
只扫描确认根和深度，默认跳过 .git、依赖、构建、缓存和公共包目录。无 Git 下载目录经 add 确认生成项目侧描述，不要求用户自己写描述符；普通 sync 只列候选，不越权修改模块。
独立仓库检查自己的 git root、HEAD 与 dirty fingerprint。Git submodule 和嵌套重叠范围需显式选择。目录缺失标 missing、关系标 stale，保留历史。新代码模块达到可索引条件后才创建实际索引。

### 6. CodeGraph 与 hook 适配

按经测试版本识别 help/status/init/sync，既有版本兼容时复用；缺失时显示固定版本、来源、校验和安装位置的计划。项目内安装仅使用已验证方式，不默认全局安装，不使用 curl | sh。显式禁止启动器隐式下载；是否可这样控制由实际版本检查。
init 的潜在副作用必须先审计：若工具会额外写 AGENTS、全局配置、hook 或守护进程，适配器必须限制到授权范围，不能只依据命令名字宣称安全；没有可控方式则阻塞该能力。不依赖没有公开支持的参数。
按 index-id 去重；先看状态，再初始化/同步并代表性查询。记录源码指纹，不仅记录 HEAD，因为未提交改动也影响地图。
首版支持无既有 hook 的受管接入和本框架自己安装的 hook 更新；任意其他 hook 不尝试文本拼接，报告冲突。core.hooksPath 外置或多 worktree 共享需要覆盖该范围的明确授权。
post-commit/post-merge/post-checkout 只调用轻量 dispatcher 标脏，事件按工作树合并；同步按支持情况异步安排。已有 CodeGraph watcher 可用时复用，任务入口与结束检查兜底。默认不放阻断型 pre-commit，也不在 hook 中启动 Agent。

### 7. Agent 适配与新技能

新增 project-bootstrap 技能，负责需求接入、模块分析、证据整理、待确认项和文档交接；与已有 OpenSpec/Superpowers 技能协调，不复制独立完成状态。
首个真实适配目标为 Codex CLI，采用实际 help 和本地实现核实后的参数，不在规格里捏造 CLI 调用。工具存在检测、进程启动、认证、实际响应、受管输出验收是不同阶段。
在源码读取/发送范围获确认后，生成最小上下文包。默认 Agent 分析仅只读源码、输出结构化结果；由确定性生成器写受管文件。可用宿主沙箱实际限制写入；没有该能力的适配不宣称隔离安全。模块文档和模型输出不得扩展执行权限。
若用户本来就在兼容 Coding Agent 会话中，可按技能直接完成交接，不再递归启动另一个 Agent。普通 shell 初始化走适配器；缺损或未认证返回 WAITING_AGENT。桌面 App 的可用性不能冒充 CLI 适配已验证。
无需用户手动说明所有模块，但对影响架构的疑问集中确认。凭模板或生成了一封提示词不能标 AGENT_ANALYZED。

### 8. 关系模型和地图生成

每条关系至少包含 edge-id、from/to module-id、kind、interface/protocol、evidence（相对路径、定位锚点和内容指纹）、provenance、runtime_validation、checked_at。kind 区分 contains/build-dependency/runtime-call/data-exchange；provenance 使用 DECLARED/STATIC_SUPPORTED/INFERRED；运行状态单列 NOT_RUN/VERIFIED/FAILED。
设计关系保存在人工批准资料，观察关系保存在 generated JSON，不以置信分数代替证据。连接两端证据不足时保留候选，不根据同名接口直接认定连接。
校验器拒绝不存在模块、越界证据、过期指纹和任意输出路径；静态证据不可升级为 runtime VERIFIED。Markdown 图从 JSON 派生。源码变化只标记/重算受影响边，无法确定范围时明确降级全模块复核并说明成本。
模块 AGENTS 要链接上级流程、真实源码与验证入口；第三方入口不允许写时使用项目侧文档并更新路由。

### 9. 新库开发与完成定义

new 从需求、验收、设计、计划到骨架，模块初始是 PLANNED/SCAFFOLDED；骨架创建不自动安装业务依赖或开始实现。开发先选最小端到端场景，由批准的 change/plan 驱动 TDD。
有源码后首次建立实际图，任务收尾更新相关关系。代码与设计冲突报告，不通过改设计掩盖。真实服务、硬件及发布仍分别授权。
doctor 默认只读，报告工具、规划根、模块、索引、Agent、地图、更新机制及 runtime；不自动“修复”。索引状态命令若可能隐式下载/同步须用无副作用证据替代，不悄悄启动它。
发布验收包含现有回归、macOS/Linux 合成端到端、真实 CodeGraph 小项目和真实 Agent 小项目。受控 CLI stub 验证编排，不冒充工具真实集成。

## Risks / Trade-offs

- [其他机器宿主 CLI 缺失或损坏] → 记录 WAITING_AGENT；仅在授权范围内修复或配置可用路径，真实联调前不宣称全链路完成。
- [Agent 访问源码可能涉及外发与费用] → 一次展示明确范围与工具调用；未经确认不启动，预算与超时有界。
- [仅写 AGENTS 不能保证每个宿主自动执行] → 已支持适配验证入口触发，其他宿主明确手动交接；不宣称通用强制执行。
- [扫描或索引大工程耗时] → 有界发现、按需索引、去重、取消与进度；默认不并行初始化全部大仓库。
- [hook 与现有工具冲突] → 首版少量明确支持，其他保留并入口兜底，不牺牲原 hook。
- [全新需求随讨论变化] → 绑定审批产物指纹；批准之后变化使受影响审批失效，而不是阻塞无关步骤。
- [自动地图被误当事实] → 证据等级、双层地图与 runtime 状态必填，测试伪证据和旧指纹拒绝路径。

## Migration Plan

1. 本变更先形成书面规格和宏观任务，经审阅后生成可执行微步骤计划，再获批实施。
2. 在公共包新增工具及技能；同步公共入口、知识/协作/技能规则、接入说明、模板、版本与清单，保留旧命令兼容。
3. 将 CLI 示例从“拟议”改成“已实现”必须有对应行为测试和真实集成证据；未完成能力继续如实标注。
4. 公共分发校验需纳入自身 OpenSpec 资料，区分可分发文件与目标工程实例；未完成规划不发布成已实现版本。
5. 用户已有工程仅显式接入，不自动迁移原业务工作区。模块人工文档和知识数据不覆盖。
6. 运行失败按事务恢复；框架升级回退仅恢复受管文件，hook 只解除可验证属于本次安装且未被再修改的部分。
7. commit、push 和发布按当次用户授权处理，本次仅本地规划，不新增远程分支。
