## 1. 政策

- [x] 1.1 在 `docs/framework/knowledge-policy.md` 写明需求页和已验证问题页在规格同步后直接写入 alias `project`，并验证文中不再要求这两类逐次询问
- [x] 1.2 在 `docs/framework/development-workflow.md` 把归档前的下一项改成写入回执，并验证「询问是否摄入」不再作为这两类完成的下一步

## 2. 路由

- [x] 2.1 更新 `tools/framework_core/workflows/combinations.json` 的 `flow-02` 下一项，重新生成 `skill/flows/flow-02/SKILL.md`，并验证正文是同步后写入需求页、适用时写入问题页、留下回执、然后归档
- [x] 2.2 运行 `python3 tools/check-framework`，验证路由清单与生成正文没有漂移

## 3. 人格

- [x] 3.1 同时修改 `docs/framework/agent-persona.md` 和根 `AGENTS.md` 的人格段，把操作句改为完成后写入初始化知识库，并验证两处人格正文仍然相同
- [x] 3.2 更新断言旧句的测试，运行相关测试，验证托管段要求的是写入而不是询问

## 4. 回执门禁

- [x] 4.1 扩展 `tools/framework_core/closure.py` 的 `outstanding_changes`，使任务完成且规格已同步但回执不合规时成为欠账，并验证 `tests/test_check_changes.py` 覆盖缺失回执、哈希不符和 `NOT_CONFIGURED` 且不创建知识库
- [x] 4.2 让 `tools/check-project` 的同一列表带上知识欠账，并验证默认退出 0、`--strict` 失败、欠账清单一致
- [x] 4.3 用夹具验证 `verified-problem.json` 的 `conclusion` 为 `pass` 时必须有问题页，没有该文件时允许 `not_applicable`

## 5. 本 change 自身

- [x] 5.1 在获得单独的初始化授权之前保持本任务未勾选；授权后写入本 change 的需求页和回执，再运行 `python3 tools/check-changes` 验证它不再因知识欠账失败
