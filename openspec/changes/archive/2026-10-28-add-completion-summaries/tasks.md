## 1. 测试契约与有效失败

- [x] 1.1 新增 `tests/test_completion_summary.py`，覆盖SUM-01默认JSON兼容、显式摘要退出码及不支持组合拒绝；先在旧实现运行并取得因缺少 `--summary` 而失败的有效RED，同时确认默认JSON用例通过。
- [x] 1.2 为SUM-02编写全新无源码COMPLETE、已有源码、PARTIAL和幂等只读摘要测试，断言六段标题、当前产物措辞、条件性缺项、分层状态和唯一下一步；先在旧实现确认对应能力缺失。
- [x] 1.3 为SUM-03/04/05编写自动逆向RECORDED、PLAN_APPROVAL_REQUIRED、PROVIDER_MISSING、NOT_AUTHORIZED、秘密正文和doctor零副作用测试；注入秘密只写入私有fixture，断言摘要不包含秘密且不伪称行为契约完成。

## 2. 摘要实现与CLI接入

- [x] 2.1 新增标准库 `tools/framework_core/completion_summary.py`，按D2-D5实现固定路径、存在性检查、六段式普通/自动逆向渲染及单一优先级下一步；运行1.2/1.3对应单元测试达到GREEN，不读取私有正文。
- [x] 2.2 修改 `tools/framework_core/cli.py`，仅给doctor和自动reverse接入 `--summary`，复用原报告和退出码；其他组合在业务动作前拒绝。运行SUM-01及既有 `test_reverse_interfaces.py`、初始化CLI测试，验证默认JSON与授权语义不回归。
- [x] 2.3 自查产物与状态边界，修复把当前存在误述为本次新建、把可选缺项当成失败、把工具READY误述为观察完成或下一步竞争的问题；每项修复由对应测试或新增边界测试证明。

## 3. 文档与分发

- [x] 3.1 更新 `BOOTSTRAP.md`、`docs/bootstrap.md` 和 `skill/reverse-engineer/SKILL.md`，说明显式摘要、六段含义、默认JSON兼容、支持范围及隐私边界；运行文档布局和运行时链接检查。
- [x] 3.2 运行 `python3 -B tools/update-manifest` 同步新增/修改运行文件，检查 `framework-manifest.json` 只含预期差异；运行 `python3 tools/check-framework` 和分发测试，确认新增模块进入运行包且测试/私有证据不进入。

## 4. 评审与最终验证

- [x] 4.1 按SUM-01至SUM-05逐项审查最终diff和实际stdout，核对普通与逆向隔离、退出码、条件性缺项、脱敏和唯一下一步；记录自查发现及修复，不能把自查标成独立评审。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-completion-summaries --strict` 和 `git diff --check`，保存最终工作树的真实结果；未经另行授权不提交、推送或归档。
