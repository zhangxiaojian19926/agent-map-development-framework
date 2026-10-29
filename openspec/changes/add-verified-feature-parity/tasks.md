## 1. 契约测试与有效失败

- [x] 1.1 新增 `tests/test_verified_feature_parity.py`，建立有效产品观察、多个 capability spec、tasks、结构化证据和 artifact fixture；先在旧实现确认 `parity` 动作缺失形成有效 RED，同时运行既有逆向、设计交接和完成摘要测试证明基线可用。
- [x] 1.2 为来源绑定和完整追踪编写有效证据链、规格/任务/证据哈希篡改、跨 change、缺失必须 Scenario、未映射产品目标、未知/重复 ID 和非法排除测试；验证输入失败时旧报告保持不变。
- [x] 1.3 为三维状态与门禁编写 DECLARED/PARTIAL/IMPLEMENTED、OBSERVED/INFERRED/NOT_OBSERVED/SKIP、VERIFIED/FAILED/NOT_RUN、PASS 无 artifact、INFRA_ERROR/N/A 及 S1–S4 BLOCK/REPORT 测试；断言 task 完成和诊断记录均不能替代功能验证。
- [x] 1.4 为公开隐私、确定性、dry-run、重复/更新、人工/跨来源冲突、malformed/超限/深嵌套/符号链接和第二份写入恢复编写测试；用文件哈希证明无自由文本泄漏、零预览写入及旧版本保护。

## 2. 只读核验与状态推导

- [x] 2.1 新增标准库 `tools/framework_core/verified_feature_parity.py`，实现受限请求/证据 JSON 读取、路径和哈希绑定、OpenSpec Requirement/Scenario 与 task 解析；运行 1.2 和资源边界测试，不执行测试、目标或网络。
- [x] 2.2 实现 `feature-parity-request/v1` 白名单校验、选定产品集合与 Scenario 全覆盖检查、合法排除及引用唯一性；运行缺失映射和无法追踪 ID 测试，区分输入错误与报告差距。
- [x] 2.3 实现 `verification-evidence/v1` 校验、FUNCTION 与 VISUAL/ACCESSIBILITY/BRAND 分类、artifact 完整性和 findings 策略；运行 1.3，确保 PASS 缺证据、失败、未运行和环境异常不被误判。
- [x] 2.4 复用第二阶段产品来源核验，实现三维状态、缺失差距和 PASS/GAPS_OPEN/FAILED 整体门禁；运行所有状态组合与严重问题测试，不引入完成分数或状态回写。

## 3. 报告、CLI、指南与分发

- [x] 3.1 实现固定白名单 Markdown 报告、私有回执、人工冲突检测、确定性 RECORDED/UNCHANGED/UPDATED 和双产物失败恢复；运行 1.4，验证原始规格、任务、产品观察和证据不被修改。
- [x] 3.2 增量修改 `tools/framework_core/cli.py`，仅给独立 `parity --request` 接入 dry-run 和需 `write` 的正式报告，按整体结果返回退出码并拒绝互斥组合；运行 1.1 及既有 CLI 回归，保留完成摘要改动。
- [x] 3.3 更新 `skill/reverse-engineer/SKILL.md`、`docs/framework/reverse-tools.md`、`docs/guide/testing-and-delivery.md`、`docs/guide/project-layout.md` 和验证报告模板，给出观察→规格→TDD→结构化证据→差距报告流程及公开/私有责任；运行文档链接和示例校验。
- [x] 3.4 运行 `python3 -B tools/update-manifest` 同步运行文件与新增规格/测试，检查清单只包含本变更和既有未提交工作的预期差异；运行 `python3 tools/check-framework` 与分发测试，确认私有产品文本不进入公开运行包。

## 4. 评审与最终验证

- [x] 4.1 按八个 Requirement 逐项审查最终 diff、CLI stdout、公开报告和私有回执，核对普通/逆向隔离、完整映射、状态推导、证据门禁、公开无自由文本及失败恢复；记录并修复自查发现，不把自查冒充独立评审。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-verified-feature-parity --strict` 和 `git diff --check`，保存最终工作树的新鲜结果并逐项更新任务；真实业务测试、网页、浏览器、设备、视觉/品牌扫描和部署保持 NOT_RUN，未经另行授权不提交、推送、同步正式 specs 或归档。
