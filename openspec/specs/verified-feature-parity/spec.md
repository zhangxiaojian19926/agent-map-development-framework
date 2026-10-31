# verified-feature-parity Specification

## Purpose

为产品重建和既有功能开发提供证据驱动的差距报告，把目标、已批准规格、实现任务与真实验证结果放在同一追踪链中，并明确阻断尚未满足验收条件的工作。

## Requirements

### Requirement: 显式报告与既有流程兼容

系统 SHALL 仅在调用方显式提供功能差距请求时读取产品观察、指定 OpenSpec change 和验证证据并生成报告。系统 MUST NOT 因规格、任务或验证文件存在而自动改变其状态，且 MUST 保持未使用该入口时的普通开发、初始化、逆向观察和默认输出不变。

#### Scenario: 显式生成差距报告

- **WHEN** 调用方提供有效差距请求并授予当前报告写入权限
- **THEN** 系统只读核验输入并生成公开差距报告，不运行目标、业务测试、浏览器、网络或部署

#### Scenario: 未请求差距报告

- **WHEN** 调用方执行既有普通开发或逆向命令
- **THEN** 系统不读取差距请求，不生成报告，也不修改 OpenSpec task 或验证证据

#### Scenario: 不支持的参数组合

- **WHEN** 调用方把差距报告入口与新逆向观察、设计交接、安装或其他互斥动作组合
- **THEN** 系统在业务执行和文件写入前返回明确输入错误

### Requirement: 来源绑定与证据新鲜度

系统 SHALL 验证产品观察证据链、请求 schema、规格/任务/验证证据路径及 SHA-256，并保证所有输入位于获准的项目边界内。输入缺失、篡改、跨 change、跨计划、过期、符号链接逃逸或超出资源预算时，系统 MUST 拒绝报告并保留旧产物。

#### Scenario: 当前来源完整一致

- **WHEN** 产品观察有效且所有声明的规格、任务和证据文件与当前内容指纹一致
- **THEN** 系统接受来源并在报告中记录可复核的来源指纹

#### Scenario: 来源被篡改或已经过期

- **WHEN** 任一声明文件的内容哈希、change、计划或证据绑定与请求不一致
- **THEN** 系统返回可区分的完整性或过期错误，不生成或覆盖报告

#### Scenario: 输入越过安全边界

- **WHEN** 输入包含越界路径、符号链接、malformed JSON、深嵌套或超过固定预算的集合与文本
- **THEN** 系统返回受控输入或预算错误，不读取证据正文到公开输出

### Requirement: 完整目标与规格追踪

系统 SHALL 要求请求将相关产品 S/F/C/E ID 和已批准规格中的 Scenario 映射到差距项或明确排除项。每个引用 MUST 唯一、存在且可追踪；未映射的必须 Scenario 或产品目标 MUST 形成差距，未知或重复引用 MUST 被拒绝。

#### Scenario: 完整映射目标与 Scenario

- **WHEN** 每个相关产品 ID 和规格 Scenario 都恰好属于一个差距项或合法排除项
- **THEN** 系统建立目标、Requirement、Scenario、task 和验证证据之间的追踪关系

#### Scenario: 必须 Scenario 缺失

- **WHEN** 已批准规格中的 Scenario 未映射且没有合法的非必须排除
- **THEN** 报告记录 `MISSING_SCENARIO`，整体结果不得为通过

#### Scenario: 引用无法追踪

- **WHEN** 请求引用不存在的产品 ID、Requirement、Scenario、task、证据 ID，或在多个差距项重复引用同一对象
- **THEN** 系统拒绝请求，不把未知 ID 当作未观察或跳过项

### Requirement: 分离推导目标实现与验证状态

系统 SHALL 分别报告 `target_evidence=OBSERVED|INFERRED|NOT_OBSERVED|SKIP`、`implementation=DECLARED|PARTIAL|IMPLEMENTED` 和 `verification=VERIFIED|FAILED|NOT_RUN`。实现状态 MUST 从当前 task 勾选推导，验证状态 MUST 从匹配 Scenario/task 的有效证据推导，调用方 MUST NOT 直接填写最终完成状态。

#### Scenario: 从任务推导实现状态

- **WHEN** 差距项没有已完成 task、部分 task 完成或全部关联 task 完成
- **THEN** 系统分别报告 DECLARED、PARTIAL 或 IMPLEMENTED，不把 task 完成等同于验证通过

#### Scenario: 从证据推导验证状态

- **WHEN** 每个必须 Scenario 都有匹配的有效 PASS 证据且没有关联失败证据
- **THEN** 系统将该项标记为 VERIFIED；证据失败时标记 FAILED，证据缺失或未运行时标记 NOT_RUN

#### Scenario: 目标未观察或明确跳过

- **WHEN** 差距项只有已批准需求目标而没有产品观察，或具有合法排除范围
- **THEN** 系统分别保留 NOT_OBSERVED 或 SKIP，不将其提升为 OBSERVED

### Requirement: 验证证据不可由声明替代

系统 SHALL 使用结构化 `verification-evidence/v1` 记录验证的 Scenario、task、测试、环境、结果和证据产物指纹。PASS 记录 MUST 绑定存在的证据产物；`VERIFIED` 缺少匹配证据、证据产物哈希不符或只有文件存在时 MUST NOT 被视为通过。

#### Scenario: 有效 PASS 证据

- **WHEN** PASS 记录关联当前 Scenario/task，并包含测试、环境和哈希匹配的本地证据产物
- **THEN** 系统允许该记录支持对应 Scenario 的验证状态

#### Scenario: 通过声明缺少证据

- **WHEN** PASS 或 VERIFIED 声明缺少测试、环境、匹配 Scenario/task 或有效证据产物
- **THEN** 系统拒绝该证据或保持 NOT_RUN，不生成虚假的通过结论

#### Scenario: 失败未运行与环境异常

- **WHEN** 证据结果为 FAIL、NOT_RUN、INFRA_ERROR 或 N/A
- **THEN** 系统保留对应结果和原因分类，且只有 FAIL 使该项验证状态为 FAILED，其余情况不得算 VERIFIED

### Requirement: 门禁与严重问题策略

系统 SHALL 按请求中显式批准的优先级和 S1–S4 开放问题策略计算整体结果。必须差距项只有在实现和必须 Scenario 验证均满足时才可通过；`NOT_RUN`、验证失败、缺失必须 Scenario 及策略为 BLOCK 的开放问题 MUST 阻断整体通过。

#### Scenario: 所有必须条件满足

- **WHEN** 所有 MUST 差距项均为 IMPLEMENTED 和 VERIFIED，没有缺失必须 Scenario 或阻断级开放问题
- **THEN** 系统允许整体结果为 PASS，同时保留非必须差距和诊断信息

#### Scenario: 未运行或验证失败

- **WHEN** 任一 MUST 差距项验证为 NOT_RUN 或 FAILED
- **THEN** 整体结果分别为 GAPS_OPEN 或 FAILED，不以其他通过项抵消

#### Scenario: 开放严重问题

- **WHEN** 有效证据包含 S1–S4 开放问题
- **THEN** 系统按请求中的显式策略报告；策略为 BLOCK 的 S1/S2 问题阻断整体通过，CLOSED 问题不按开放问题阻断

### Requirement: 公开报告隐私与诊断边界

系统 SHALL 在 `docs/verification/` 生成固定结构报告，包含稳定 ID、来源指纹、三维状态、差距、策略和证据索引。报告 MUST NOT 复制产品私有名称、目的、步骤、字段、关系、排除原因、原始观察、凭据或秘密，也 MUST NOT 使用总分或主观百分比替代门禁。

#### Scenario: 报告包含敏感产品草案

- **WHEN** 产品观察和验证输入含私有自由文本、URL、Cookie、Authorization 或账号数据
- **THEN** 公开报告只包含白名单 ID、状态、差距和公开证据索引，不包含这些敏感值

#### Scenario: 可选诊断证据

- **WHEN** 请求关联视觉、可访问性或品牌诊断记录
- **THEN** 系统将其作为独立诊断类别和可选问题来源，不据此推断功能已观察、已实现或已验证

### Requirement: 确定性预览更新与失败恢复

系统 SHALL 支持 dry-run 零写入、相同输入确定性幂等和合法来源更新的原子替换。已有报告存在人工修改、跨 change 来源或私有交接记录不一致时 MUST 冲突保留；任一输出写入失败 MUST 恢复旧版本，不宣称部分成功。

#### Scenario: 只读预览

- **WHEN** 调用方以 dry-run 请求有效差距报告
- **THEN** 系统返回预计整体结果、差距和报告指纹，公开报告与私有记录均不写入

#### Scenario: 重复与合法更新

- **WHEN** 相同输入重复生成或相同 change 的有效来源发生更新
- **THEN** 系统分别返回 UNCHANGED 或 UPDATED，并保持输出确定性和旧版本可恢复性

#### Scenario: 人工冲突与写入失败

- **WHEN** 既有报告被人工修改、属于其他来源，或公开报告与私有记录写入中途失败
- **THEN** 系统拒绝覆盖或恢复旧公开报告，原始规格、任务、产品观察和验证证据保持不变
