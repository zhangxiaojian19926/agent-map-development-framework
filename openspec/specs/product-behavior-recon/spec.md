# product-behavior-recon Specification

## Purpose

为已授权的产品或 UI 逆向观察提供证据绑定的结构化派生视图，使屏幕、流程、组件、推断实体和排除范围能够安全地交接给后续设计，而不混淆事实、推断、实现与验证状态。

## Requirements

### Requirement: 显式启用与既有接口兼容

系统 SHALL 仅在调用方为自动 `reverse --request` 显式提供产品行为观察草案时生成产品观察视图。系统 MUST 保持未提供该选项时的 `reverse-request/v1` 字段、计划哈希、默认 JSON、退出码、工具链和普通开发行为不变，且 MUST NOT 为旧 scope、`reverse-scope/v2` 或设备动作隐式启用该能力。

#### Scenario: 默认自动逆向保持兼容

- **WHEN** 调用方执行不含产品观察选项的既有自动逆向请求
- **THEN** 系统按原契约执行，不读取或生成产品观察文件，原请求校验、计划和结果保持兼容

#### Scenario: 不支持的逆向接口

- **WHEN** 调用方为旧 scope、`reverse-scope/v2` 或设备动作提供产品观察选项
- **THEN** 系统在目标执行前返回明确输入错误，不运行工具、不写入产品观察产物

#### Scenario: 普通开发无逆向请求

- **WHEN** 用户执行初始化、地图、资料、打包或其他非逆向流程
- **THEN** 系统不读取产品观察草案、不生成产品观察视图，也不增加网络、安装或第三方依赖

### Requirement: 版本化产品观察结构与稳定标识

系统 SHALL 支持版本化产品观察草案和 `product-recon/v1` 产物，包含屏幕、流程、组件、实体和排除项。屏幕、流程、组件和实体 MUST 分别使用唯一的 S-ID、F-ID、C-ID 和 E-ID，交叉引用 MUST 指向同视图内已声明的 ID；未知字段、非法枚举、重复标识和悬空引用 MUST 被拒绝。

#### Scenario: 完整产品观察草案

- **WHEN** 草案包含相互引用的屏幕、流程、组件、实体和排除项且字段符合版本化契约
- **THEN** 系统接受草案并生成保留稳定 ID 和引用关系的机器产物

#### Scenario: 非法结构或引用

- **WHEN** 草案包含未知字段、错误 ID 格式、重复 ID、非法 provenance 或不存在的屏幕/组件引用
- **THEN** 系统返回可区分的校验错误，不生成或覆盖产品观察产物

#### Scenario: 非产品目标没有 UI 观察

- **WHEN** 二进制、固件或其他非 UI 目标没有可靠屏幕和流程证据
- **THEN** 调用方保持对应集合为空或不启用本能力，系统不要求伪造 UI 条目

### Requirement: 证据绑定与事实推断分离

系统 SHALL 将每个产品观察条目绑定到当前计划和适用的成功观察记录。`STATIC_SUPPORTED` 与 `DYNAMIC_OBSERVED` 条目 MUST 引用状态为 `RECORDED` 且 provenance 相符的观察；`INFERRED` 条目 MUST 明确标记推断和置信度，不得伪装成已观察事实。未完成、未授权、缺 provider、失败或不属于当前计划的观察 MUST NOT 支撑事实条目。

#### Scenario: 静态或动态事实引用有效观察

- **WHEN** 产品条目引用的观察已记录成功且 provenance 与条目一致
- **THEN** 系统保留该证据关系并允许生成对应事实条目

#### Scenario: 推断没有直接观察证据

- **WHEN** 数据实体或产品行为仅属于模型推断
- **THEN** 系统将其标记为 `INFERRED` 并保留置信度，不增加观察引用或运行验证通过声明

#### Scenario: 引用不可用观察

- **WHEN** 产品条目引用 `NOT_AUTHORIZED`、`PROVIDER_MISSING`、失败、未知或其他计划的观察
- **THEN** 系统拒绝该草案并保留已有观察与产品产物，不将其汇总为成功

### Requirement: 已观察与未观察范围

系统 SHALL 区分屏幕和组件的已观察状态、明确未观察状态及排除范围。未观察内容 MUST 保持 `NOT_OBSERVED` 语义，排除项 MUST 有分类和私有原因；系统 MUST NOT 将未观察、排除或推断内容标记为已经实现或验证。

#### Scenario: 部分屏幕状态未观察

- **WHEN** 已观察屏幕仅覆盖正常状态，错误、权限不足或移动状态没有证据
- **THEN** 产物记录已观察状态并将其余状态保持为未观察，不自动补齐事实

#### Scenario: 明确不可复制或不在范围内

- **WHEN** 草案包含许可内容、网络效应、私有数据、合作资源、硬件、监管或其他排除项
- **THEN** 系统保存分类和私有原因，公开摘要仅展示安全分类和数量

### Requirement: 确定性生成与失败恢复

系统 SHALL 对同一计划、行为契约和草案生成确定性产品观察产物；相同输入重复执行 MUST 幂等，更新草案 MUST 在完整校验通过后原子替换派生产物。校验或写入失败 MUST NOT 损坏已有行为契约、观察记录或上一份有效产品观察产物。

#### Scenario: 相同草案重复生成

- **WHEN** 同一逆向 ID 使用相同计划、行为契约和草案再次执行
- **THEN** 产品观察 JSON 的语义内容和 SHA-256 保持稳定，不重复追加公开摘要区块

#### Scenario: 合法草案更新

- **WHEN** 同一计划下提交内容不同且校验通过的新草案
- **THEN** 系统原子更新派生视图和公开受管摘要并报告更新，不改写原始观察证据

#### Scenario: 新草案校验失败

- **WHEN** 已存在有效产品观察产物后提交非法新草案
- **THEN** 系统返回失败并保留上一份有效产物及其哈希，不留下部分写入文件

### Requirement: 私有产物与公开摘要隔离

系统 SHALL 将完整产品观察 JSON 保存在既有 `.framework/local-state/reverse/auto/<id>/` 私有目录，并仅在既有 `docs/project/reverse/<id>.md` 中维护一个受管脱敏区块。公开区块 MUST 只包含固定结构、稳定 ID、数量、provenance、confidence、观察/未观察状态和安全排除分类，不得复制草案自由文本或原始证据正文。

#### Scenario: 草案包含敏感自由文本

- **WHEN** 私有草案的名称、目的、步骤、字段或排除原因包含账号名称、Cookie、Authorization、私有端点或原始页面片段
- **THEN** 私有产物按证据边界保存，公开摘要不包含这些字符串且仍保留可核对的 ID 和统计

#### Scenario: 重复执行公开摘要生成

- **WHEN** 产品观察视图被重复生成或更新
- **THEN** 系统替换同一个受管区块，不产生重复区块，不影响摘要中的既有逆向内容

### Requirement: 只读预览和资源边界

系统 SHALL 在 dry-run 中只读校验草案的结构、计划绑定和可静态检查的证据引用，不写入任何产品产物。系统 MUST 限制草案字节数、条目数、文本长度和嵌套深度，超限或 malformed JSON MUST 返回受控错误而非 traceback 或不受控资源消耗。

#### Scenario: dry-run 产品观察预览

- **WHEN** 调用方在自动逆向 dry-run 中提供有效产品观察草案
- **THEN** 系统报告草案校验结果和草案指纹，不联网、不执行工具、不写 `.framework` 或公开摘要

#### Scenario: 非法或超限草案

- **WHEN** 草案为 malformed JSON、超过声明预算或嵌套过深
- **THEN** 系统在业务执行前返回明确输入错误，不崩溃、不执行目标且不写入产物

### Requirement: 设计交接不等于实现或验证批准

系统 SHALL 将产品观察视图作为后续 DISCOVERY 和 OpenSpec 的可选输入，并保持 `runtime_validation=NOT_RUN`、`source_map_evidence=False`、`implementation_approved=False`。系统 MUST NOT 自动创建或批准 Req/Scenario、修改业务模块、更新任务完成状态或声明发布就绪。

#### Scenario: 产品观察生成完成

- **WHEN** 系统成功生成包含事实和推断的产品观察视图
- **THEN** 结果仅表示派生观察已记录，运行验证、源码地图证据和实现批准仍保持原有否定或未执行状态

#### Scenario: 后续产品重建

- **WHEN** 用户决定根据产品观察结果重建功能
- **THEN** 后续工作仍从设计、规格校验与批准、计划、TDD 和验证门禁进入，不沿用产品观察作为完成证明
