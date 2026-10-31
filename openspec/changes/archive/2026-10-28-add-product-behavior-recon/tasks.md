## 1. 测试契约与有效失败

- [x] 1.1 新增 `tests/test_product_recon.py`，为“显式启用与既有接口兼容”编写默认自动逆向、旧 scope/v2 拒绝和非逆向隔离测试；先在旧实现确认 `--product-recon` 缺失导致有效 RED，同时确认默认 JSON 用例通过。
- [x] 1.2 为“版本化产品观察结构与稳定标识”“证据绑定与事实推断分离”编写有效 S/F/C/E、交叉引用、未知字段、重复 ID、非法枚举、悬空引用、推断、未授权/缺 provider/失败/跨计划观察测试；先在旧实现确认生成能力缺失，再逐组达到 GREEN。
- [x] 1.3 为“已观察与未观察范围”“确定性生成与失败恢复”编写状态重叠、排除分类、同输入哈希稳定、合法更新原子替换、非法更新保留旧产物和公开区块不重复测试；用临时目录中的文件哈希和行为契约/观察记录哈希验证恢复边界。
- [x] 1.4 为“私有产物与公开摘要隔离”“只读预览和资源边界”“设计交接不等于实现或验证批准”编写秘密自由文本、dry-run 零写入、malformed/超限/深嵌套、固定交接状态及后续规格门禁测试；断言公开摘要无秘密且真实网页、浏览器、设备和部署保持 NOT_RUN。

## 2. 产品观察实现与 CLI 接入

- [x] 2.1 新增标准库 `tools/framework_core/product_recon.py`，按 D1/D3/D7 实现 `product-recon-draft/v1` 白名单、预算、ID/引用、状态和排除项校验及规范化；运行 1.2、1.4 对应纯校验测试达到 GREEN，不读取原始证据或引入依赖。
- [x] 2.2 在同一模块按 D4-D6 实现实际观察证据校验、`product-recon/v1` 确定性输出、契约/草案哈希、原子更新和无自由文本公开区块；运行 1.2-1.4 对应生成、脱敏、幂等及失败恢复测试。
- [x] 2.3 增量修改 `tools/framework_core/cli.py` 和现有自动逆向编排，仅给 `reverse --request` 接入 `--product-recon`，dry-run 返回独立预览且不改计划哈希，正式执行在行为契约后生成视图；运行 1.1 及既有 `test_reverse_interfaces.py`、`test_reverse_auto.py`，验证授权、退出码和默认输出不回归。
- [x] 2.4 在保留 `add-completion-summaries` 现有改动的前提下增量更新完成摘要，只在本次显式启用且产物有效时展示固定相对路径和派生状态；运行 `tests/test_completion_summary.py` 与产品观察摘要测试，确认不把文件存在或工具 READY 写成业务完成。

## 3. 模板、文档与分发

- [x] 3.1 新增 `templates/product-recon-draft.json` 空白契约，并更新 `skill/reverse-engineer/SKILL.md`、`docs/framework/reverse-tools.md`、`docs/guide/project-layout.md`，说明 Agent 草案责任、显式命令、证据/置信度、私有/公开边界、更新语义和 OpenSpec 门禁；运行文档链接、目录责任和示例校验。
- [x] 3.2 运行 `python3 -B tools/update-manifest` 同步新增/修改运行文件，检查 `framework-manifest.json` 仅包含本变更及既有未提交工作的预期差异；运行 `python3 tools/check-framework` 和分发测试，确认模板/运行模块可用且测试、草案实例和私有证据不进入公开运行包。

## 4. 评审与最终验证

- [x] 4.1 按八个 Requirement 逐项审查最终 diff、CLI stdout 和产物，核对普通/逆向隔离、请求与计划兼容、证据分层、公开无自由文本、失败恢复及未提交改动保护；记录自查发现和修复，不把自查冒充独立评审。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-product-behavior-recon --strict` 和 `git diff --check`，保存最终工作树的新鲜结果并逐项更新任务；未经另行授权不提交、推送、同步正式 specs 或归档。
