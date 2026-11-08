# 2026-11-08 工作流路由实现验证

变更：`add-agent-workflow-routers`。本页只记录这次命令看到的结果。文件安装通过不等于宿主已经拦截写入。

## 安装轴

已确认：

- `python3 tools/check-framework` 输出 `PASS: 542 inventoried files, 42 skills`。十五条路由在 `skill/flows/flow-01` 至 `flow-15`，与组合清单一致。
- `python3 -m unittest discover -s tests -q` 跑完 447 项，退出码 0。其中 `tests/test_flow_routers.py` 覆盖路由正文、下一项、触发词、技能约束、人格托管段和状态词典；人为偏差（共用触发词、缺路由、指南多写 `retro`、成员技能被投影、为 `trae` 写入发现路径）使检查以退出码 1 结束。
- `tests/test_host_routers.py` 在临时目录里投影 Cursor 与 DeepSeek harness，写入 Codex、Gemini CLI 的已记录钩子载体，并确认名册外宿主、`CARRIER_UNKNOWN` 发现目录和 CodeBuddy 不新增文件。
- `openspec validate --all --strict`：40 项通过，0 项失败。

这些结果说明路由文件、目录字段、指南技能列和安装函数与清单一致。它们不说明某个 Coding Agent 的真实会话已经拒绝过写入。

## 宿主执行轴

没有真实会话。下列宿主的执行轴都是 `NOT_RUN`，不是已拦截：

| 宿主 | 这次看到的事实 |
|---|---|
| Cursor | 临时目录里的钩子文件含 `failClosed: true`。单元测试调用已认证的 `Write` 时，判定拒绝并指向 `skill/flows/flow-02/SKILL.md` 与缺失的 `tdd`，目标文件哈希不变。没有真实 `preToolUse` 事件。`StrReplace` 仍是未覆盖 |
| Claude Code、Qwen Code | 已认证工具名未改。拒绝理由增加了 `flow-02` 和缺失的 `tdd`。没有新的 CLI 会话 |
| Codex、Gemini CLI | 只写入已记录的项目钩子载体。没有会话 |
| DeepSeek harness | 临时 Git 根下有扁平的 `.dsh/skills/flow-*` 和 `.dsh/hooks.json`。没有 profile 把 `configPath` 指向该文件，执行轴是 `NOT_RUN`，测试断言它不是已拦截 |
| CodeBuddy、Trae、通义灵码、GitHub Copilot、Windsurf、Grok、Copilot CLI | 不创建技能发现目录，也不新增钩子。CodeBuddy 不新增 `CODEBUDDY.md` |

`docs/guide/framework-model.md` 的状态词典相对本次改动前的 `HEAD` 没有新增状态码。`AGENTS.md` 的 `AGENT_PERSONA` 托管段字节与 `HEAD` 一致。

## 规格落点

任务全部勾完之后，CI 的 `tools/check-changes` 要求能力规格进入 `openspec/specs/`，并把变更移入归档。因此 `agent-workflow-routers` 已写入主规格，`skill-routing`、`invocation-forms`、`native-workflow-gates` 已并入原规格，变更目录为 `openspec/changes/archive/2026-11-08-add-agent-workflow-routers/`。

任务清单勾完和规格归档只表示安装轴上的检查已经跑过，不表示现场拦截已经验证。

本仓库 doctor（`python3 tools/framework doctor --target . --summary`）退出码 5：`initialization=PARTIAL`，`documentation=MISSING`，`coverage=MISSING`，`handoff=BLOCKED`，`runtime=NOT_RUN`。这是分发壳当前的接入状态，不是上述宿主的执行轴。

当前仍由 `tools/framework_core/workflows/catalog.py` 的 `route()` 按请求 JSON 选择工作流。描述匹配要等宿主读到投影后的 `flow-*` 才会发生。
