## Context

现有自动逆向在获批计划后生成观察记录、`behavior-contract.json` 和脱敏公开摘要。行为契约中的 capability name、constraint 和 inference 都是自由文本，不能可靠恢复屏幕、流程或组件结构；原始 HTML、DOM、截图和网络记录则只能留在私有证据区。当前工作树另有完成摘要增量，本设计必须在其现有接口上追加固定产物展示，不覆盖或回退该工作。

## Goals / Non-Goals

**Goals:**

- 用单独、显式的草案契约承载产品语义，框架负责校验而不是猜测产品结构。
- 复用现有自动逆向计划、观察记录、私有目录和公开摘要，不建立第二套事实或完成状态。
- 输出确定性、可复核、可原子更新的私有 JSON，以及不含草案自由文本的公开统计摘要。
- dry-run、默认调用、旧接口和非逆向流程保持兼容，全部验证可离线完成。

**Non-Goals:**

- 不自动解析截图、DOM、JavaScript 或 HAR 来识别屏幕和流程。
- 不引入 `replica/`、`features.csv`、功能完成分数、OpenSpec 自动写入或业务代码生成。
- 不改变 `reverse-request/v1`、`toolchain-plan/v1` 的计划哈希、授权集合或工具安装决策。
- 不实现第二阶段开发指南或第三阶段功能 parity、视觉 diff 和品牌扫描。

## Decisions

### D1 独立草案契约，避免扩张 reverse-request/v1

新增 `product-recon-draft/v1` 作为自动逆向命令的可选本地 JSON 输入，字段为 `schema`、`id`、`plan_sha256`、`screens`、`flows`、`components`、`entities`、`exclusions`。草案由当前 Agent 根据已授权私有证据整理；框架不读取原始证据来“自动理解”产品。

输出采用独立的 `product-recon/v1`，在草案内容上增加 `behavior_contract_sha256`、规范化后的 `draft_sha256` 以及固定的 `runtime_validation=NOT_RUN`、`source_map_evidence=False`、`implementation_approved=False`。输入与输出分离可避免自引用哈希和把派生元数据交给调用方伪造。

备选方案是给 `reverse-request/v1` 增加产品字段或从 capability name 猜测 S/F；前者破坏严格字段兼容，后者产生无证据事实，均不采用。

### D2 复用自动 reverse 命令，以显式选项启用

增加 `--product-recon <draft.json>`，只允许与 `reverse --request` 组合。dry-run 在既有计划生成后只读校验草案并返回单独的 `product_recon` 预览信息；该信息不进入 `toolchain-plan/v1`，所以计划批准语义和哈希不变。正式执行在行为契约和观察记录完成后校验动态证据，再生成产品视图。

旧 scope、v2、设备动作及其他命令携带该选项时，在业务执行前返回 `INVALID_INPUT`。默认未传选项的分支不读取草案、不增加结果字段，现有 `--summary` 和 JSON 行为保持原样。

### D3 采用白名单 schema 和引用完整性校验

每个屏幕、流程、组件和实体使用统一 `evidence` 对象：`provenance`、`observations`、`confidence`。ID 分别匹配 `S`、`F`、`C`、`E` 后接至少两位十进制数字，并在各自集合内唯一。屏幕引用组件，流程引用屏幕；所有引用必须先声明后校验，不能依赖数组位置。

屏幕和组件分别记录 `states_observed` 与 `states_unobserved`，同一状态不得同时出现。推断实体的字段和关系保留在私有 JSON，但只继承实体级证据与置信度，不声称逐字段独立验证。排除项使用固定分类枚举和私有 `reason`，可关联已声明 ID。

未知字段一律拒绝，避免前向兼容被误认为已验证。空集合合法；没有可靠产品结构的任务不应启用该能力。

### D4 最终证据以实际观察记录为准

dry-run 能检查草案引用的观察 ID 是否在当前请求中声明、动作类型是否与声明 provenance 相容；正式生成还必须确认记录存在、`status=RECORDED`、属于当前计划且实际 provenance 完全匹配。`INFERRED` 必须没有 observations，事实条目必须有至少一个有效观察。

证据校验失败使用可区分的 `PRODUCT_RECON_EVIDENCE`，结构、预算和计划绑定错误使用输入类错误。失败不会删除已完成的原始观察，但也不能生成公开产品摘要或更新旧产品视图。

### D5 私有完整视图与无自由文本公开区块分离

完整产物固定写入 `.framework/local-state/reverse/auto/<id>/product-recon.json`。公开 `docs/project/reverse/<id>.md` 增加一个产品观察受管区块，仅渲染：

- 各类型条目数量；
- S/F/C/E ID、provenance 和 confidence；
- 已观察及未观察状态计数；
- 排除项固定分类与数量；
- 产物 SHA-256 和固定交接状态。

公开区块不渲染草案中的 name、purpose、description、steps、fields、relationship、notes 或 reason，也不渲染 URL、目标路径和观察原文。这样脱敏不依赖不可靠的秘密正则；秘密扫描仅作为测试中的反向断言，不作为公开渲染的主要防线。

### D6 规范化、幂等和原子更新

草案在读取原始 JSON 后先做字节和深度预算检查，再做 schema 校验；规范化草案使用排序键和稳定数组顺序计算 SHA-256。输出 JSON 使用 UTF-8、排序键、固定缩进和结尾换行，不写生成时间或随机值。

同一输入重复生成得到相同文件哈希。不同草案只有在全部校验成功后通过同目录临时文件和原子替换更新 `product-recon.json` 与公开摘要；任一失败保留旧文件。派生视图不是原始证据，因此允许更新，但历史观察记录和行为契约不被改写。

### D7 预算、文档和现有摘要增量兼容

初版集中定义预算：草案最大 1 MiB、嵌套深度最大 32、每类最多 250 项且总计最多 1000 项；字符串、状态和观察引用另设固定上限。 malformed JSON、递归过深和超限均转化为受控错误。

更新 `skill/reverse-engineer/SKILL.md`、`docs/framework/reverse-tools.md`、`docs/guide/project-layout.md`，并新增一份空白草案模板。完成摘要仅在产品视图实际存在且本次显式启用时增加固定相对路径，不把存在文件解释为业务完成。新增/修改运行文件按既有流程同步 `framework-manifest.json`。

### D8 测试以契约场景为主，不运行上游或真实目标

新增独立标准库测试模块，先验证旧实现缺少选项和生成能力形成有效 RED，再覆盖有效生成、推断、非法引用、未授权观察、敏感文本、幂等、更新回滚、dry-run 零写入、预算、默认 JSON 和非逆向隔离。所有 fixture 使用本地临时目录和假观察记录，真实网页、浏览器、登录态、设备和部署保持 `NOT_RUN`。

## Risks / Trade-offs

- [Agent 草案本身可能整理错误] → 框架只能保证证据引用和契约一致，不能证明语义绝对正确；provenance、confidence 和未观察状态必须保留，后续 OpenSpec 仍需审批。
- [独立草案增加一次结构化整理成本] → 比扩张现有请求或不可靠自动猜测更透明；模板和 dry-run 降低使用成本。
- [公开摘要仅 ID 和统计不够直观] → 这是避免自由文本泄漏的刻意取舍；完整内容可在本机私有产物查看，公开文档不冒充完整 recon。
- [更新派生视图可能改变后续设计输入] → 绑定计划和契约哈希、记录新产物哈希并原子更新；下游仍需绑定自己使用的版本，不自动更新已批准规格。
- [与未提交完成摘要同时修改相邻代码] → 先读取最终工作树并做最小增量，分别保留既有测试；不提交、不归档或覆盖其他 change。

## Migration Plan

本变更无既有数据迁移。未使用新选项的项目无需修改。发布后旧自动逆向结果没有 `product-recon.json`，保持 `NOT_GENERATED` 而不是错误；用户需要时按同一已批准计划补充草案。回退可移除可选参数和派生模块，既有请求、行为契约和观察记录无需回滚；已生成私有派生文件可保留但不参与旧流程。
