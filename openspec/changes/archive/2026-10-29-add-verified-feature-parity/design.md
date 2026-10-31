## Context

前两个阶段提供有效 `product-recon/v1` 与待确认设计输入；OpenSpec 管理 Req/Scenario/task，`docs/verification/` 目前只有 Markdown 报告模板。现有格式没有机器可核验的测试证据记录，也没有产品 ID 到规格的映射，因此不能直接通过“文件存在”或 Agent 自报状态生成可信 parity。当前工作树仍有 `add-completion-summaries`，新增入口和清单必须保留这些改动。

## Goals / Non-Goals

**Goals:**

- 用显式、固定 schema 的请求连接产品目标、已批准 change、task 和验证证据，最终状态全部由当前输入推导。
- 支持一个 change 的多个 capability spec，发现未映射目标和 Scenario，而不是仅检查请求中列出的项目。
- 以哈希、安全路径、固定预算和白名单渲染保证来源新鲜、输出确定性与公开隐私。
- 复用第二阶段只读产品证据核验、原子写入和双产物恢复，不引入依赖或执行行为。

**Non-Goals:**

- 不自动运行测试、截图比较、可访问性扫描、品牌扫描、浏览器、网络或部署。
- 不解析产品私有名称来猜测需求，不自动创建/批准/勾选 OpenSpec，不生成业务代码。
- 不引入 `features.csv`、完成百分比、综合分数或跨 change 汇总；首版一次报告只绑定一个逆向 ID 和一个 change。
- 不实现第四阶段市场研究、产品化或发布能力。

## Decisions

### D1 新增独立 `parity --request`，只增加 `write` 授权

CLI 新增 `parity` 动作，请求文件由当前 Agent 在用户批准规格和映射后提供。dry-run 只读；正式生成只要求 `write`，不要求 `reverse`、安装、网络、浏览器或设备授权。`--scope`、`--product-recon`、`--design-handoff`、计划批准和完成摘要等互斥组合在读取业务输入前拒绝。

备选方案是扩张 `reverse --design-handoff` 或 `doctor`；前者会混淆设计与验证，后者会把只读环境检查变成业务报告写入，均不采用。

### D2 显式请求绑定一个 change 和选定产品集合

新增 `feature-parity-request/v1`，固定字段包括：

- `schema`、`id`、`change`、`product_collections`；
- `specs[{path,sha256}]`、`tasks{path,sha256}`、`evidence[{path,sha256}]`；
- `items`、`product_exclusions`、`scenario_exclusions`、`severity_policy`。

规格与任务路径必须属于 `openspec/changes/<change>/`，证据路径必须属于该 change 在 `docs/verification/` 的公开证据区。`product_collections` 显式选择本次纳入的 screens/flows/components/entities；被选集合中的所有产品 ID 必须映射或排除，避免只报告调用方挑出的成功项。

每个 item 包含安全 token ID、可选 `product_id`、priority、Requirement/Scenario 标题和 task ID。没有 `product_id` 表示仅有已批准需求目标，目标证据为 NOT_OBSERVED；产品排除映射为 SKIP。Scenario 排除只允许 SHOULD/COULD 等明确非必须分类，MUST 不得通过排除绕过门禁。未知或重复引用是输入错误，遗漏引用是报告差距。

不自动推断“已批准”：请求记录用户已批准的精确规格和映射版本，文件存在本身仍不是批准证明。工具只保证所处理的版本与声明一致。

### D3 用受限 Markdown 解析读取规格和任务，不发明第二套状态

规格解析只接受 `### Requirement:` 和 `#### Scenario:` 标题，保留其公开标题并形成 `requirement + scenario` 键；重复键、空标题和孤立 Scenario 拒绝。任务解析只接受 `- [ ] <id>` 与 `- [x] <id>`，重复 ID 拒绝，其他正文不修改也不作为状态。

实现状态由 item 关联 task 推导：无 task 或全部未勾选为 DECLARED，部分勾选为 PARTIAL，至少一个且全部勾选为 IMPLEMENTED。工具不写 tasks，也不把 `[x]` 当作验证证据。

备选方案是要求调用方填写 IMPLEMENTED 或解析任意 Markdown；前者允许自报完成，后者脆弱且容易误读，均不采用。

### D4 新增结构化验证证据，功能与诊断记录分类

`verification-evidence/v1` 绑定 change，包含 records 和 findings。每条 record 固定包含 ID、Requirement、Scenario、task、test、environment、result、category、artifact 和可选原因：

- result 为 PASS、FAIL、NOT_RUN、INFRA_ERROR、N/A；N/A 和环境异常必须给出公开原因分类。
- category 为 FUNCTION、VISUAL、ACCESSIBILITY、BRAND；只有 FUNCTION 可支持功能 VERIFIED。
- PASS 必须有项目内、非符号链接、哈希匹配的 artifact；其他结果也可附 artifact，但不能因文件存在升级为 PASS。
- finding 包含 ID、S1–S4、OPEN/CLOSED、category 和 evidence_id；请求显式给出各级 BLOCK/REPORT 策略，未声明级别不默认放行。

同一 item 的每个 MUST Scenario 至少有一条匹配 task 的有效 FUNCTION/PASS，且没有匹配 FAIL，才可 VERIFIED。存在匹配 FAIL 为 FAILED；其余为 NOT_RUN，并在差距中保留 INFRA_ERROR/N/A 等原因。视觉、可访问性和品牌记录只形成诊断及 findings，不参与功能状态推导。

结构化记录只能证明“所声明证据存在且未篡改”，不能独立证明历史上确实执行过测试；验证责任方仍须按开发流程提供真实执行证据，工具不得把 schema 校验宣传为业务运行成功。

### D5 复用有效产品来源并计算三维状态和门禁

复用 `load_valid_source` 校验请求、计划、契约、观察、目标与产品视图，避免另写一套产品证据规则。产品 ID 的 provenance 映射为 OBSERVED 或 INFERRED；无产品 ID 的声明目标为 NOT_OBSERVED；合法产品排除为 SKIP。

整体只使用 PASS、GAPS_OPEN、FAILED：任一匹配功能 FAIL 为 FAILED；否则，只要 MUST 项未 IMPLEMENTED/VERIFIED、存在未映射必须 Scenario/产品目标或 BLOCK 开放问题，即为 GAPS_OPEN；其余为 PASS。非 MUST 差距和 REPORT 诊断仍展示，不由总分抵消。命令生成报告后按整体结果返回相应退出码，输入完整性错误在写入前失败。

### D6 固定白名单公开报告和私有回执

公开输出为 `docs/verification/<change>-parity.md`，包含受管标记、来源哈希、逐项三维状态、差距代码、严重问题策略和公开证据 ID/路径。渲染器不接收产品 name/purpose/goal/steps/fields/relationships/reason 或原始观察正文，不输出 URL、Cookie、Authorization 和账号数据。

私有回执为 `.framework/local-state/parity/<change>.json`，保存请求规范化哈希、所有输入哈希、公开报告哈希和固定 `execution=NOT_RUN`。首版同一 change 只有一个受管报告；已有报告与回执必须同来源且哈希匹配，人工修改、跨 change 或记录篡改均冲突保留。

### D7 确定性双产物写入与离线契约测试

全部校验和渲染完成后先原子写公开报告，再原子写私有回执；第二份失败恢复旧公开报告，首次失败清理本能力新产物。dry-run 返回相同整体结果、差距和预计报告哈希，但不创建目录或文件。重复输入 UNCHANGED，合法来源变化 UPDATED。

测试使用本地临时产品证据、多个 spec、tasks、证据 JSON 和假 artifact，覆盖有效通过、缺失映射、状态推导、非法/重复 ID、哈希过期、严重问题、诊断隔离、秘密、预算、dry-run、幂等、人工冲突和第二份写入恢复。真实业务测试、网页、浏览器、设备、视觉/品牌扫描和部署保持 NOT_RUN。

## Risks / Trade-offs

- [结构化证据仍可能由责任方错误填写] → 强制绑定 Scenario/task/artifact/hash，并明确工具不证明历史执行；保留人工评审与最终验证门禁。
- [严格标题解析依赖 OpenSpec 格式] → 只支持公开约定的标题和任务复选框，格式不明确时受控失败，不猜测语义。
- [一次只绑定一个 change 和逆向 ID] → 保持追踪简单；跨 change 或多来源合并后续另行设计，不在首版隐式拼接。
- [公开证据可能自身含秘密] → 报告只索引白名单路径和 ID，不复制 artifact 正文；公开证据的脱敏仍由验证责任方审查。
- [完整映射增加准备成本] → dry-run 和固定错误/差距代码帮助定位，不能以减少 Scenario 或降低优先级来换取 PASS。
- [共享 CLI 和清单包含其他未提交工作] → 最小增量并保留相关测试，第三阶段不提交、推送或归档其他 change。

## Migration Plan

无旧数据迁移。未使用 `parity` 的项目没有新目录或文件；既有 Markdown 验证报告不自动转为证据，需由验证责任方按真实记录补建 `verification-evidence/v1`。回退可移除入口和派生报告模块，产品观察、OpenSpec 和原证据不变；已生成报告按人工资料处理，不自动删除。
