# 旧 OpenSpec change 证据对账

> 维护者对账记录，不改变旧 change 的任务状态，也不是同步、归档或发布结论。对账日期：2026-10-26，规格库补齐与归档决定：2026-10-31（见文末）。

## 对账口径

- 旧任务是否完成只由其最终工作树、适用环境和专属场景证据决定；本目录整理变更的测试不能替代旧任务验收。
- 2026-10-26 的对账只读核对两个旧 change 的任务文件、历史验收和已有提交/CI 记录；没有勾选旧任务，没有执行规格同步或归档。2026-10-31 按文末决定补齐了这 8 个能力的规格同步，两个 change 仍不归档、任务状态未改写。
- 历史计划已迁至 `docs/archive/plans/`，历史验收已迁至 `docs/archive/`。旧任务正文中的原路径是历史记录，不再作为现行导航入口。
- 可核实的公共提交为 `84a5caae73e4cb60f773245127e0d1a37693bda6`（`fix: harden project initialization checks`）。CI run `40249970950` 在该提交上完成 Ubuntu 与 macOS 的 `tools/check-framework` 和完整单元测试，结论均为 success；它不证明真实宿主、私有认证、设备、部署或当前未提交工作树。

## add-project-bootstrap-and-maps

最终专属证据状态：**未完成，不归档**。

| 项目 | 可核实记录 | 对账结论 |
|---|---|---|
| 已勾任务 1.1–6.3、6.5 | 旧任务文件和历史验收记录了实现、离线回归、真实 Codex/CodeGraph 与评审证据 | 本次不重写历史结论，也不把旧快照扩展为当前版本证明 |
| 6.4 | 历史记录为 macOS/Linux 各 58 项离线测试及 macOS 真实外部工具联调；Linux 真实外部工具联调未完成，且证据未绑定最终工作树 | 保持未勾；最终版本全场景证据不足 |
| Linux 真实 CodeGraph/Codex | 历史记录未执行 | NOT_RUN |
| 集成、推送、发布、归档 | 历史记录未执行；本次也未执行 | NOT_RUN，需独立授权和正常门禁 |

历史证据：[Bootstrap 0.2.0 本地验收](../archive/verification/bootstrap-0.2.0.md)。上述 CI 只能补充说明对应提交的离线检查状态，不能勾补 6.4 的最终全场景验收。

## agent-led-project-intake

最终专属证据状态：**未完成，不归档**。

| 任务 | 当前状态与证据缺口 |
|---|---|
| 2.3 | 保持未勾；启动区绑定、快照、秘密日志与旧状态授权需按 IN-04 对最终版本逐项核对 |
| 3.1–3.4 | 保持未勾；默认 ref、逐模块获取、真实认证失败及恢复场景不能用离线实现或其他测试替代 |
| 4.3–4.4 | 保持未勾；人工入口、分层诊断虽有回归，仍需完成 HN-03 的最终语义验收 |
| 5.1、5.3 | 保持未勾；D9 文档对照、私有输入隔离和兼容性需按最终 diff 核对 |
| 6.1 | 保持未勾；`84a5caa` 的双平台 CI 不覆盖旧任务全部场景，也不是当前工作树证据 |
| 6.2 | 保持未勾；历史真实 Codex 双路线记录早于后续修复，需最终版本重验 |
| 6.3 | NOT_RUN；没有真实非 Codex 双路线证据 |
| 6.4 | NOT_RUN；没有真实跨宿主中断恢复证据 |
| 6.5 | 保持未勾；历史评审和修复不等于最终全量规格符合性复核 |
| 6.6 | NOT_RUN；提交、推送和归档需届时独立授权 |
| 7.4 | 保持未勾；真实双宿主、两类跨宿主恢复和最终源码/HEAD 探针不足 |
| 7.5 | 保持未勾；最终工作树离线回归、完整规格评审和集成边界未闭合 |

已勾任务和历史真实 Codex 结果仅按原记录保留，不在本次对账中升级其证明范围。历史证据：[发布验收与证据边界](../archive/acceptance.md)。

## 后续门禁

1. 每个旧 change 分别确认最终提交或工作树，逐任务重验适用场景并记录环境。
2. 真实非 Codex、跨宿主恢复、私有认证、设备或部署没有证据时继续标记 NOT_RUN，不以“代码存在”代替。
3. 全部适用门禁完成后，先走规格同步并核对，再按正常归档流程处理；归档前取得用户明确授权。
4. 本次目录变更未摄入任何知识内容，也未对旧 change 做状态改写。

## 2026-10-31 规格库补齐与归档决定

### 审计发现

2026-10-31 对全部活跃 change 与规格库做交叉核对，发现**规格库缺失 8 个能力**，而它们的实现都已存在且在用：

| 能力 | 声明来源 | 实现证据 |
|---|---|---|
| `project-bootstrap` | add-project-bootstrap-and-maps | `skill/project-bootstrap/SKILL.md`、`BOOTSTRAP.md` |
| `agent-project-maps` | add-project-bootstrap-and-maps | `tools/framework_core/maps.py`、`map` 子命令 |
| `module-lifecycle` | add-project-bootstrap-and-maps | `docs/guide/module-lifecycle.md` |
| `project-readiness` | add-project-bootstrap-and-maps | `tools/framework_core/readiness.py`、doctor 分层状态 |
| `codegraph-maintenance` | add-project-bootstrap-and-maps | `tools/framework_core/adapters.py`、`refresh --index` |
| `project-intake` | agent-led-project-intake | `tools/framework_core/intake.py`、`intake` 子命令 |
| `named-module-acquisition` | agent-led-project-intake | `tools/framework_core/acquisition.py`、模块 clone/add |
| `host-neutral-onboarding` | agent-led-project-intake | `docs/project-intake.md`、BOOTSTRAP 通用入口 |

缺失原因是这两个 change 从未归档：归档门禁要求真实宿主与跨宿主恢复证据，本环境无法提供，于是规格库长期只反映 2026-10-26 之后新增的能力。规格库因此**低估了工程壳自身的能力**——只读规格的人会以为初始化、关系地图、模块获取这些核心能力不存在。

### 决定

1. **同步这 8 个能力规格到 `openspec/specs/`**，走规格同步流程，不绕过 change。规格同步与归档是两个独立操作：同步声明“这些是正式能力规格”，归档声明“实现已完成并留有证据”。
2. **两个 change 继续留在 `openspec/changes/`，不归档。** 未勾选任务仍缺真实宿主、跨宿主恢复、私有认证与远端 CI 证据，按本文件上方门禁第 2、3 条，这些门禁在本环境无法完成，因此不满足归档条件。
3. **未勾选任务仍是未验证部分的唯一权威记录。** 规格库记录要求，不记录实现完成度；完成度只看 change 的任务与验证证据。

### 后续影响

- `openspec validate --all --strict` 覆盖 20 个能力规格与 2 个活跃 change，全部通过。
- 新增的 CI 门禁 `openspec validate --archived` 会拒绝任何带未完成任务归档的 change，为上述决定提供机器校验。
- 若将来取得真实宿主与跨宿主证据，先按正常流程重验适用场景并逐项记录，再同步核对，最后归档；在此之前两个 change 的状态保持未完成。
