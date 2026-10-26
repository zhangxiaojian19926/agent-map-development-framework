## 离线验证

验证日期：2026-10-26。

| 命令 | 结果 |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_ci_workflows.py' -v`（升级前） | 退出状态 1；运行 10 项，8 项通过，仅两个 Action 版本测试失败，形成有效 RED |
| `git diff --check && git diff -- .github/workflows/validate.yml .github/workflows/release.yml` | 退出状态 0；两个工作流仅四处 Action 主版本引用变化 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_ci_workflows.py' -v`（升级后） | 退出状态 0；10 项全部通过，形成 GREEN |
| `python3 tools/update-manifest` | 退出状态 0；清单已同步 |
| `python3 tools/check-framework` | 退出状态 0；框架指纹、链接和脚本语法检查通过 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | 退出状态 0；198 项测试全部通过 |
| `openspec validate upgrade-ci-actions-runtime --strict` | 退出状态 0；严格规格校验通过 |

离线验证只证明仓库文本契约、框架完整性和本地测试通过，不能执行 GitHub Action 本身。此阶段升级后实际 CI 为 `NOT_RUN`，发布实测为 `NOT_RUN`。

## 线上验证

- 目标提交：`1187767b442c79b81c56dc435c2a3a5285b3763b`
- 验证工作流运行 ID：`40326687726`；状态 `completed`，结论 `success`，运行提交与目标提交一致
- Ubuntu：`success`；任务 `validate (ubuntu-latest)`，任务 ID `121585102282`
- macOS：`success`；任务 `validate (macos-latest)`，任务 ID `121585102589`
- checkout / setup-python 的 Node.js 20 弃用警告：两个任务的检查注解中均未出现，线上警告已消除
- Ubuntu 平台提示：`ubuntu-latest` 标签将迁移至 Ubuntu 26；不属于本变更的消除目标
- macOS 平台提示：arm64 runner 容量限制可能延长排队时间；不属于本变更的消除目标
- 发布工作流实测：`NOT_RUN`；本变更未主动触发发布。

## 最终范围

- 功能提交 `1187767b442c79b81c56dc435c2a3a5285b3763b` 已推送到 `origin/main`，两个工作流仍保持原有触发器、权限、并发、验证矩阵和发布条件。
- `add-project-bootstrap-and-maps` 与 `agent-led-project-intake` 在功能提交及后续工作树中均无改动。
- 已完成本地契约测试、完整测试、框架检查、严格规格校验及目标提交的 Ubuntu/macOS 实际 CI 验收。
- 未验证项仅为发布工作流实测，状态保持 `NOT_RUN`；平台 runner 迁移和容量提示不属于本变更缺陷。
