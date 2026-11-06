# 总结报告：add-native-workflow-gates

日期：2026-11-06。变更已同步并归档：能力规格见 [openspec/specs/native-workflow-gates/spec.md](../../openspec/specs/native-workflow-gates/spec.md)，变更原文见 [归档目录](../../openspec/changes/archive/2026-11-06-add-native-workflow-gates/proposal.md)，原生验收证据见 [验收记录](add-native-workflow-gates-native/README.md)。

## 一句话结论

提案的四个动作全部落地：**三条完全交付**，第三条（两个试点宿主）按约定交付为"Claude Code 有真实拦截证据、Qwen Code 原生验收显式延后且覆盖如实记 `NOT_RUN`"。本期交付资格按提案本身声明为 `NOT_RUN`。

## 逐条对账

| 提案动作 | 状态 | 证据 |
|---|---|---|
| 登记十五条工作流并提供只读任务路由，区分主流程／条件流程／不适用／待确认；流程 ID 与教程表逐行对应 | ✅ | `tools/framework_core/workflows/catalog.json`（15 条，`flow-01`–`flow-15`）、`catalog.py`；目录与教程表的一致性由 `test_workflow_routes.py` 反向校验，漂移即失败 |
| 首批为日常开发的新行为路径校验规格、计划、批准和相关版本 | ✅ | `workflows/engine.py`、`workflows/evidence.py`；WF-02 的三个场景各有对应用例 |
| 支持经授权的任务记录及跨会话恢复 | ✅ | `workflows/records.py`（项目锁 + 文件事务 + 幂等 + 并发 `CONFLICT`）；WF-04 两个场景 |
| 试点 Claude Code CLI 与 Qwen Code CLI，保留原生入口，按版本／工具入口／故障行为报告覆盖 | ⚠️ 按约定收口 | `hosts/claude_code.py`、`hosts/qwen_code.py` + 两份项目级模板；Claude Code 有真实拦截证据，Qwen Code 原生验收显式延后、五个故障类 `NOT_RUN` |
| 判定证据不足时要求宿主阻断，不默认放行 | ✅ | WF-05/WF-06；宿主执行轴区分"已阻断／已放行／未覆盖／未知" |
| 流程判定、宿主执行与交付资格三轴分别记录，只使用已发布状态词典的状态码 | ✅ | WF-07；规格引用的 15 个状态码逐个核对，均在随包代码中真实产生 |
| 本期交付资格为 `NOT_RUN` | ✅ | 交付资格轴固定 `NOT_RUN`，不写成 `PASS` |
| 受保护 CI 与其余工作流的新增可执行门禁留给后续变更 | ✅（按范围未做） | 本期未触碰受保护 CI |

## 交付物

**代码**（新增约 2100 行）

- `tools/framework_core/workflows/`：`catalog.py` / `catalog.json`（十五条目录 + 四类开发路由）、`engine.py`（阶段判定）、`evidence.py`（信任来源与验签）、`records.py`（私有任务记录）。
- `tools/framework_core/hosts/`：`base.py`（适配接口 + 事件归一化 + 覆盖矩阵）、`claude_code.py`、`qwen_code.py`。
- `templates/host/{claude-code,qwen-code}/settings.json`：项目级 hook 模板。
- `tools/framework_core/cli.py`：新增 `flow`（route/check/record/report）与 `host`（preview/apply/verify/coverage/record）两个动作；原有 22 个动作一字未改、顺序不变、退出码兼容。

**测试**（新增 58 条用例，6 个文件）

| 文件 | 用例 | 覆盖 |
|---|---|---|
| `test_workflow_routes.py` | 17 | 十五条路由、角色与冲突、意图不足、目录与教程表漂移、指南与路由一致性 |
| `test_workflow_evidence.py` | 11 | 批准缺失／过期／有效、越界、伪造、跨项目重放 |
| `test_workflow_records.py` | 7 | 幂等重试、并发冲突、恢复时重新判定、写入授权 |
| `test_workflow_trust.py` | 6 | 信任来源可改写则阻断、受保护则放行、路径不可被请求或环境改指 |
| `test_host_claude_code.py` | 10 | 安装/冲突/校验、缺任务与缺批准都阻断、有效批准放行、未认证工具如实报告 |
| `test_host_qwen_code.py` | 7 | 跨宿主同事实同判定、Shell 与未知工具为覆盖缺口、故障矩阵 |

**文档**：`docs/guide/daily-development.md`（分流表加路由列、任务路由与批准核验、信任来源配置三行）、`openspec/specs/native-workflow-gates/spec.md`（8 条要求 / 20 个场景）。

## 验证

- 全量单元测试 **418 项通过**。
- **变异检查 22 次全部被捕获**（每个切片逐条确认测试确实能失败；其中 M4「apply 不看授权」首轮漏过，补测守卫后复检通过）。
- `openspec validate --all --strict`：38 项全过。
- `python3 tools/check-changes`：PASS（无已完成未同步的变更）。
- `python3 tools/check-framework`：仅剩 5 个 `docs/plans/dsh-plugin/` 报告——那是另一件事的未跟踪本地资料，与本变更无关，清单生成时已刻意排除。

## 过程中发现并修掉的问题

**门禁拦得住编辑，但拦不住代理自己找授权。** 原生验收里，Claude Code 被门禁拦下后依次读了门禁源码、算规格指纹、写 `~/.config/framework/approvals/`、`ssh-keygen` 生成自己的密钥准备自签批准——只因 Anthropic 侧 429 配额中断才没成。根因是信任锚点放在用户 home 下、路径写在随包源码里，代理读得到也写得进去。

据此新增 WF-08 与切片 1.7：信任来源改为固定系统路径 `/etc/framework/workflow-trust.allowed_signers`，且文件与所在目录必须对当前用户不可写，否则判定 `NOT_VERIFIED` 并阻断。签名私钥是否可被代理读取无法机械校验，改为在报告与指南中如实声明。

## 尚需人工完成

```bash
sudo mkdir -p /etc/framework
sudo install -m 0444 -o root approver.pub /etc/framework/workflow-trust.allowed_signers
sudo chmod 0555 /etc/framework
```

未完成前，所有需要批准的动作一律 `NOT_VERIFIED` 并阻断——这是严格口径的预期行为。

## 后续可做（不在本期范围）

- **Codex 适配**：协议与 Claude Code 同构（`.codex/hooks.json` 同 schema），适配器约 70 行加一份模板；本机 Codex 需改用自定义 provider 配置（`~/.codex/config.deepseek.toml` / `config_doubao.toml`）才能跑，ChatGPT 登录配 OpenAI 模型名会被服务端拒绝。
- **Gemini 适配**：官方 `gemini hooks migrate --from-claude` 可直接生成项目级配置，只差把本机账号配置好。
- **Grok**：项目级 hook 载体尚未探明，用户级 `~/.grok/hooks/` 不在本设计范围内（全局宿主配置是非目标）。
