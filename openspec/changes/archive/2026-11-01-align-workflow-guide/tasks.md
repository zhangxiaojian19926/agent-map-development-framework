## 1. 补齐流程契约摘要行

- [x] 1.1 `docs/framework/development-workflow.md` 的完整行为变更路线摘要行补上 `REGRESSION`，使任务循环为 `TASK_SELECTED → RED → GREEN → REFACTOR → REGRESSION → TASK_VERIFIED`
  - 交付行为：摘要行与同文件 §8 分节声明的步骤集合完全一致
  - 关联：`workflow-guide-consistency` / 摘要行与分节一致
  - 验收：§8 的五个步骤全部出现在摘要行中；`tests/test_doc_contract.py` 的摘要行检查通过
  - 阻塞于：无

## 2. 修正对外指南的两处漂移

- [x] 2.1 `docs/guide/from-zero-to-one.md` 工作流 14 的流程行补齐全部六道门禁（`check-framework` / `unittest` / `openspec validate --all --strict` / `openspec validate --archived` / `check-changes` / `git diff --check`）
  - 交付行为：读者照流程行执行时，与 CI 实际跑的门禁集合相同
  - 关联：`workflow-guide-consistency` / 指南列出全部门禁
  - 验收：`tools/check-framework` 的门禁清单检查通过
  - 阻塞于：无

- [x] 2.2 `docs/guide/from-zero-to-one.md` 工作流 14 的提示词步骤同步补上 `openspec validate --archived` 与 `check-changes`，步骤重新编号
  - 交付行为：提示词里的步骤与流程行一一对应，不出现只在其中一处出现的门禁
  - 关联：`workflow-guide-consistency` / 指南列出全部门禁
  - 验收：提示词文本包含六道门禁全部命令
  - 阻塞于：2.1

- [x] 2.3 `docs/guide/from-zero-to-one.md` 工作流 15 的定时时刻改为与 `release.yml` 的 `17 2 * * 1` 一致（02:17 UTC / 10:17 北京时间）
  - 交付行为：指南给出的时刻与调度表达式表示同一时刻，UTC 与北京时间两个数字同时正确
  - 关联：`workflow-guide-consistency` / 活文档的时刻与调度一致
  - 验收：`tools/check-framework` 的调度时刻检查通过
  - 阻塞于：无

- [x] 2.4 `docs/maintainer/release.md` 的定时发布时刻同步改为 02:17 UTC（北京时间 10:17）
  - 交付行为：维护者发布文档给出的时刻与调度表达式一致
  - 关联：`workflow-guide-consistency` / 活文档的时刻与调度一致
  - 验收：全仓搜索无遗留的旧时刻表述
  - 阻塞于：2.3

- [x] 2.5 `README.md` 的定时发布时刻同步改为 02:17 UTC（北京时间 10:17）
  - 交付行为：README 给出的时刻与调度表达式一致
  - 关联：`workflow-guide-consistency` / 活文档的时刻与调度一致
  - 验收：全仓搜索无遗留的旧时刻表述
  - 阻塞于：2.3

## 3. 加自动检查，让漂移当场暴露

- [x] 3.1 `tools/check-framework` 新增 `doc_contract_errors(root, files)`，实现三项检查：实现阶段摘要行覆盖 §8 全步骤、指南工作流 14 覆盖 CI 实际门禁、所有陈述发布调度时刻的活文档与调度表达式一致
  - 交付行为：期望值从事实源推导（§8 分节 / `validate.yml` / `release.yml`），不是写死清单；扫描范围取自分发清单的活文档，排除记录历史的文档
  - 关联：`workflow-guide-consistency` / 三项检查各一条场景
  - 验收：函数在人为制造偏差时报出对应错误
  - 阻塞于：1.1、2.1、2.2、2.3、2.4、2.5

- [x] 3.2 `tools/check-framework` 的 `main()` 接入 `doc_contract_errors`
  - 交付行为：`python3 tools/check-framework` 会因文档漂移失败
  - 关联：`workflow-guide-consistency` / 自动检查接入
  - 验收：人为改坏指南后 `check-framework` 非零退出
  - 阻塞于：3.1

- [x] 3.3 新增 `tests/test_doc_contract.py`：三项检查各一组 RED 用例（制造偏差 → 检查报错）+ 一组 GREEN 用例（当前仓库文件通过）
  - 交付行为：检查的可证伪性有测试保障
  - 关联：`workflow-guide-consistency` / 自动检查接入
  - 验收：全量 `python3 -m unittest discover -s tests` 通过
  - 阻塞于：3.2

## 4. 配套更新

- [x] 4.1 `docs/maintainer/verification.md` 的基础检查清单补上文档契约检查
  - 交付行为：维护者文档说明这项检查查什么
  - 关联：`workflow-guide-consistency` / 自动检查接入
  - 验收：清单条目与 `check-framework` 实际行为一致
  - 阻塞于：3.2

- [x] 4.2 更新 `framework-manifest.json` 分发清单
  - 交付行为：清单包含新增测试文件，且所有改动文件哈希已刷新
  - 关联：无（分发完整性）
  - 验收：`python3 tools/check-framework` 通过
  - 阻塞于：3.3、4.1

- [x] 4.3 `CHANGELOG.md` 的 Unreleased 记录本次变更
  - 交付行为：变更可追溯
  - 关联：无
  - 验收：条目写明改了什么、为什么
  - 阻塞于：无

## 5. 验证与归档

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 `python3 -m unittest discover -s tests` 全量通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 `openspec validate --archived --no-interactive` 通过
- [x] 5.5 `python3 tools/check-changes` 无欠账
- [x] 5.6 提交后 `git diff --check HEAD^ HEAD` 无空白错误
- [x] 5.7 同步能力规格到 `openspec/specs/` 并归档本 change
