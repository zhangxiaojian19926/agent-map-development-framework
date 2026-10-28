## 1. 契约测试与有效失败

- [x] 1.1 新增 `tests/test_product_design_handoff.py`，覆盖显式交接、默认流程兼容和 CLI 互斥；先在旧实现确认 `--design-handoff` 缺失形成有效 RED，同时运行既有逆向与完成摘要测试证明基线可用。
- [x] 1.2 为来源绑定与证据新鲜度编写有效证据链、产品/契约/计划篡改、目标过期、观察失败、跨计划和保留原文缺失测试；验证失败时公开草案及旧交接记录保持不变。
- [x] 1.3 为脱敏设计输入、状态/推断/排除范围、固定交接门禁编写测试；断言所有私有自由文本和秘密不进入公开草案，且 `NEEDS_DESIGN_APPROVAL`、`NOT_RUN` 和否定批准状态准确保留。
- [x] 1.4 为确定性、重复/更新、人工修改/来源冲突、dry-run 零写入、malformed/超限/深嵌套/符号链接和双产物写入恢复编写测试；用文件哈希证明无部分成功及旧版本保护。

## 2. 只读核验与公开草案

- [x] 2.1 新增标准库 `tools/framework_core/product_design_handoff.py`，实现受限 JSON 读取、产品结构与计划/契约/观察/目标/原始证据核验；运行 1.2 和资源边界测试，不读取原文正文、不执行工具或网络。
- [x] 2.2 在同一模块实现固定白名单公开草案渲染和私有交接元数据，保留稳定 ID、证据分层、未观察/排除边界及来源指纹；运行 1.3 测试并核对私有字段不出现在公开内容。
- [x] 2.3 实现单来源人工冲突检测、确定性 `RECORDED`/`UNCHANGED`/`UPDATED`、原子更新与第二份写入失败恢复；运行 1.4 测试，验证原始观察和上一份有效草案不被损坏。

## 3. CLI、指南与分发

- [x] 3.1 增量修改 `tools/framework_core/cli.py`，仅给独立 `reverse --design-handoff <id>` 接入只读预览和需 `write` 的正式交接；拒绝与 request/scope/product-recon 等互斥组合，运行 1.1 及既有 CLI 回归并保留完成摘要改动。
- [x] 3.2 更新 `skill/reverse-engineer/SKILL.md`、`docs/framework/reverse-tools.md` 和 `docs/guide/project-layout.md`，给出观察→交接→人工设计批准→OpenSpec→TDD→验证流程及公开/私有目录责任；运行文档链接、目录归属和示例校验。
- [x] 3.3 运行 `python3 -B tools/update-manifest` 同步运行文件与新增规格/测试，检查清单只包含本变更和既有未提交工作的预期差异；运行 `python3 tools/check-framework` 与分发测试，确认私有证据不进入公开运行包。

## 4. 评审与最终验证

- [x] 4.1 按七个 Requirement 逐项审查最终 diff、CLI stdout、公开草案和交接记录，核对普通/逆向隔离、证据新鲜度、公开无自由文本、人工冲突及失败恢复；记录并修复自查发现，不把自查冒充独立评审。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-product-recon-design-handoff --strict` 和 `git diff --check`，保存最终工作树的新鲜结果并逐项更新任务；真实网页、浏览器、设备、业务实现和部署保持 NOT_RUN，未经另行授权不提交、推送、同步正式 specs 或归档。
