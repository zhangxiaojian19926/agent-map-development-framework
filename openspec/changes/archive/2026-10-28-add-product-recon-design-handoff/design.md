## Context

第一阶段 `product_recon.py` 负责草案校验、确定性私有产物与脱敏公开逆向摘要；`design-input.md` 则由普通项目资料与人工设计审批使用。第二阶段需要复用这两条既有边界，不能引入另一套需求状态，也不能通过通用 `accept-docs` 隐式批准产品观察。当前工作树仍有 `add-completion-summaries` 改动，入口和文档只能最小增量。

## Goals / Non-Goals

**Goals:**

- 以单个显式命令完成“只读证据核验 → 公开设计草案 → 待确认交接”。
- 让草案具备确定性、来源指纹、人工修改冲突检测和 dry-run 零写入。
- 复用标准库、现有私有自动逆向目录、原子写入与普通设计审批，不增加 provider 或依赖。
- 用指南和测试固定目录责任、后续 OpenSpec 门禁以及失败恢复方式。

**Non-Goals:**

- 不自动将 S/F/C/E 转换成 Req/Scenario，不推断业务名称、页面文案或数据字段语义。
- 不重新执行观察、访问网络、启动浏览器、读取原始证据正文或生成业务模块。
- 不改变第一阶段 `product-recon/v1` 格式、哈希或生成行为，不实现第三阶段 parity、视觉 diff、品牌扫描。
- 不在本变更中自动批准 `design-input.md`，不处理多逆向 ID 合并。

## Decisions

### D1 独立显式入口，交接与观察解耦

在现有 `reverse` 动作增加 `--design-handoff <reverse-id>`，与 `--request`、`--scope`、`--product-recon` 等互斥。dry-run 无需写权限；正式交接只新增 `write` 授权，不沿用工具安装、网络、浏览器或设备权限。这样产品设计交接可以在观察完成后单独审阅和重试，也不会重放目标。

备选方案是在第一阶段生成产品视图时自动写设计输入，或扩张 `accept-docs` 接受私有产品视图；前者违反显式交接，后者会混淆产品观察和人工 dossier，均不采用。

### D2 复用产品 schema 校验并补充持久化证据核验

新增标准库交接模块，以只读安全路径加载指定 ID 的 `request.json`、计划、`behavior-contract.json`、`product-recon.json` 和观察记录。复用产品模块的白名单、预算和证据检查；再核对：

- 产品与请求 ID、计划哈希一致，计划文件及其哈希匹配；
- `behavior_contract_sha256` 与当前契约一致，契约 schema/ID/计划正确；
- 产品结构与公开渲染所需的字段、状态和排除项合法；
- 事实观察存在、状态成功、计划与 provenance 相符，推断无观察引用；
- 本地目标当前 SHA-256 与计划一致；`RAW_RETAINED` 的原证据文件及哈希存在，`RAW_DISCARDED` 不读取正文；URL 快照按既有加载器验证。

只验证交接所需的持久化证据，不因工具后来卸载而否定已固定证据。错误分为 `PRODUCT_HANDOFF_STALE`、`PRODUCT_HANDOFF_INTEGRITY` 和输入/预算错误。

### D3 公开草案使用固定白名单渲染，私有内容只留原处

公开 `docs/project/design-input.md` 由固定标题、交接说明、来源 ID/哈希、S/F/C/E 元数据、未观察状态、排除分类、后续门禁组成。渲染器只读取 ID、数组状态字符串、provenance、confidence 和排除 kind；不接收 name、purpose、goal、steps、fields、relationships、reason 或观察原文。

状态字符串虽来自草案，仍按第一阶段文本预算校验；公开输出只允许安全枚举式 token，拒绝 URL、空白、控制字符和超长自由文本。完整产品语义由当前 Agent 在获得授权的私有工作区核对，公开草案不是完整产品规格。

私有交接记录 `.framework/local-state/reverse/auto/<id>/design-handoff.json` 保存 schema、来源/草案/文档哈希、`NEEDS_DESIGN_APPROVAL` 和固定否定状态，不复制产品自由文本。

### D4 单来源受管文档与冲突保护

首版一个设计输入只对应一个逆向 ID。不存在目标文件时创建；已有文件必须同时具有本能力受管标记、同一来源 ID、有效交接记录及匹配的文件哈希，才能幂等或更新。无标记文件、其他来源、记录缺失/不匹配或交接后人工编辑均返回 `PRODUCT_HANDOFF_CONFLICT`，不做三方合并。

正式写入前完成全部读取、验证和渲染；使用同目录临时文件和原子替换更新公开草案，再原子写入私有交接记录。写入失败不得留下半文件或删除旧版本；若第二份文件写入失败，恢复旧公开草案并报告失败，不以部分成功交付。

### D5 预览与结果复用原 JSON 边界

dry-run 返回 `DRY_RUN`、`NEEDS_DESIGN_APPROVAL`、来源和预计草案 SHA-256、固定路径及 `write=NOT_RUN`，不落盘。正式结果区分 `RECORDED`、`UNCHANGED`、`UPDATED`，包含 `product_sha256`、`design_input_sha256` 和固定否定门禁。未显式启用时不增加其他命令的 JSON 字段；`--summary` 的既有未提交行为不由本变更扩张。

### D6 指南回到普通开发，不建立逆向专用实现通道

更新逆向技能、逆向工具说明和目录指南，流程固定为：

```text
授权观察 → product-recon/v1 → 显式设计交接 → NEEDS_DESIGN_APPROVAL
→ 人工确认设计 → DISCOVERY / OpenSpec SPEC → PLAN → TDD → REVIEW → VERIFY
```

业务代码仍写 `modules/`，公开项目事实写 `docs/project/`，原始证据与派生私有视图留在 `.framework/local-state/reverse/`。只有产品观察交接不改变模块结构，不触发源码关系地图发布。

### D7 离线契约测试覆盖失败恢复

使用临时目录构造有效第一阶段请求、计划、契约、观察和含秘密的产品视图，覆盖有效交接、dry-run、重复/更新、人工冲突、篡改、过期、原始证据缺失、脱敏、预算、CLI 互斥和普通流程兼容。真实网页、浏览器、设备、业务代码生成和部署保持 `NOT_RUN`。

## Risks / Trade-offs

- [公开草案只有结构化 ID，业务可读性有限] → 保持严格脱敏，由当前 Agent 在私有证据范围内辅助设计讨论；不为了提高可读性复制秘密。
- [已有 `design-input.md` 不能自动合并] → 首版明确冲突并保留人工内容，后续如确需多来源再独立设计合并协议。
- [证据固定后目标继续变化] → 本地目标当前指纹参与核验；过期时返回重新观察提示，不沿用旧草案。
- [双产物写入存在中途失败窗口] → 预先完成校验，原子写入并恢复旧公开草案；测试注入失败验证恢复。
- [共享 CLI 与完成摘要改动相邻] → 最小增量、分别保留测试，不提交或覆盖其他 change。

## Migration Plan

无既有数据迁移。旧产品观察不会自动产生设计输入；用户需要时显式执行交接。未使用的项目没有新文件。回退可移除入口和交接模块，已有产品观察与普通设计审批不变；已生成的公开草案可按人工文档处理，不自动删除。
