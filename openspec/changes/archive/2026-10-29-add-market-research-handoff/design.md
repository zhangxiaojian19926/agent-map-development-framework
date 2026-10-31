## Context

现有产品观察交接读取私有证据并写入 `docs/project/design-input.md`，4A 候选则使用独立请求和双产物回执。4B 的输入是当前 Agent 已完成的公开研究声明，不是新的网页采集器，因此需要独立的公开研究路径，不能复用私有观察加载器或覆盖既有设计入口。

## Goals / Non-Goals

**Goals:**

- 用固定 schema 保留公开来源、事实、推断、局限及引用关系。
- 用一份受管报告同时承载研究摘要和待确认设计草案，减少状态分叉。
- 复用安全路径、哈希、原子写入、CLI 授权和离线测试模式。

**Non-Goals:**

- 不联网、不抓网页、不验证 URL 可访问性、不保存或抓取来源正文。
- 不判断市场结论是否真实，不自动产生需求、OpenSpec、业务代码或发布证据。
- 不修改既有 design-input、4A 报告和私有逆向资料，不实现 4C。

## Decisions

### D1 新增独立 `research --request`，只增加 `write` 授权

请求采用 `market-research-request/v1`，固定包含 `schema`、`id`、`question`、`sources`、`facts`、`inferences`、`limitations`、`design`。dry-run 只读，正式生成仅要求 `write`；与其他动作、额外 grant 和 `--summary` 互斥。请求由当前 Agent 在已完成相应公开研究后提供，CLI 不代替研究过程。

备选方案是扩张 reverse 或 design-handoff；前者会混淆私有观察和公开研究，后者会覆盖既有设计产物，因此不采用。

### D2 来源只作公开声明绑定，不伪造外部核验

source 固定包含 `id`、`url`、`accessed_at`、`content_sha256`。URL 仅允许 HTTP/HTTPS，解析后禁止用户名密码、空 host、控制字符和本地文件形式；日期采用 `YYYY-MM-DD` 并用标准库校验真实日期，哈希为 SHA-256。报告固定 `source_verification=NOT_RUN`，说明哈希绑定的是研究责任方声明的内容，不由工具在线复核。

source ID、fact ID、inference ID 使用安全 token 且全局分类内唯一。fact 包含 `id`、`statement`、`source_ids`；inference 包含 `id`、`statement`、`fact_ids`、`confidence`（HIGH/MEDIUM/LOW）；所有 statement、question、limitations 为受限公开文本，引用必须非空且存在。首版不读取来源正文，也不提供附件字段，从结构上阻断私有文件输入。

### D3 设计草案只引用研究，不成为规格状态

`design` 固定包含 `summary`、`opportunities`、`constraints`，均为公开文本或文本数组。公开报告 `docs/project/market-research/<id>.md` 依次包含研究问题、来源、事实、推断、局限、设计草案和固定 `design_status=NEEDS_DESIGN_APPROVAL`、`source_verification=NOT_RUN`、`execution=NOT_RUN`。不修改 `docs/project/design-input.md`，不调用 OpenSpec。

备选方案是分别生成研究文件和 design-input；双公开文件更容易产生覆盖与状态不一致，因此首版合并。

### D4 固定双产物与确定性渲染

私有回执为 `.framework/local-state/market-research/<id>.json`，保存规范化请求哈希、报告路径及哈希和上述 NOT_RUN 状态，不保存额外正文。报告包含受管首尾标记、请求哈希和稳定排序/请求声明顺序；公开 URL 是研究契约的一部分，不能按逆向脱敏规则删除。

全部校验和渲染在写入前完成。dry-run 返回报告路径和预计哈希但不创建文件；正式重复输入 UNCHANGED，同 ID 合法变化 UPDATED；人工修改、缺一份产物或回执不匹配均 CONFLICT。

### D5 双写入恢复与最小文档接入

先原子写公开报告再写私有回执，第二次失败恢复旧公开报告，首次失败清理本能力新报告。测试覆盖有效交接、日期/URL/哈希/引用错误、私有路径、公开字段边界、dry-run、幂等、冲突、第二次写入恢复、CLI 授权与既有设计/4A 回归。文档在普通开发指南增加可选入口，不改变初始化或逆向必经步骤。

## Risks / Trade-offs

- [研究责任方可能错误陈述来源或事实] → 明示工具只做内部一致性校验，外部真实性仍需人工核对。
- [公开 URL 可能含敏感查询参数] → 禁止凭据并限制公开文本；请求者须审查 URL 公开性，不声称通用秘密扫描。
- [事实与推断仍可能被后续误用] → 报告分区且设计固定待确认，不直接生成规格或验证证据。
- [一份报告包含研究和草案增加篇幅] → 避免双文件覆盖冲突，引用 ID 保持可追踪。

## Migration Plan

无旧数据迁移。未运行 `research` 的项目不产生新路径，既有 design-input 和私有观察不变。回退可移除研究入口和派生模块，不删除既有研究人工资料或修改 OpenSpec。
