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

- 目标提交：`NOT_RUN`
- 验证工作流运行 ID：`NOT_RUN`
- Ubuntu：`NOT_RUN`
- macOS：`NOT_RUN`
- checkout / setup-python 的 Node.js 20 弃用警告：`NOT_RUN`
- 发布工作流实测：`NOT_RUN`；本变更不主动触发发布。

## 最终范围

待线上验收后记录最终提交、工作树、其他活跃变更和未验证项。
