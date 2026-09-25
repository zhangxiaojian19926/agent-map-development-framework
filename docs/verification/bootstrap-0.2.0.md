# Bootstrap 0.2.0 本地验收

日期：2026-09-25。此记录区分离线回归、真实工具验收和发布状态；不是生产认证。

## 已取得的证据

| 层级 | 环境与结果 |
|---|---|
| 公共包 | manifest 校验、相对链接和脚本语法通过；22 个技能 |
| 离线回归 | macOS / Python 3.9：58 项通过，包含原有 22 项 |
| Linux 回归 | 官方 python:3.9-slim 容器，Python 3.9.25、Git 2.47.3：58 项通过；源码只读挂载；未挂载宿主凭据 |
| 真实源码接入 | CodeGraph 1.6.0 + Codex CLI 0.151.0：三个模块分别建索引、产生证据地图；同名但无关模块没有被误连 |
| 重复执行 | 无源码变化的 refresh 保持原始 Agent 结果不变，不再次请求模型 |
| 新需求 | 未批准先返回 3 且不建目录；确认三份产物指纹后生成工程；无源码时等待 Agent，不虚报完成 |
| 真实开发 | 独立 Codex CLI workspace-write 会话实现 taskcli/domain/storage，先 RED 后 GREEN；8 个跨进程测试通过 |
| 独立业务验收 | 固定黑盒探针额外验证 add/list/done、单调 ID、缺失数据库及错误不改写；CONTRACT_PASS |
| 开发后导航 | 三个真实索引 READY，Codex 关系地图 READY，无设计依赖缺失；从工程自带入口运行 doctor 也通过 |
| 规格 | OpenSpec 1.11.0 严格校验公共 change 和 demo-task-cli |

Linux 镜像摘要：`sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b`。Git/Bash 仅安装在自动删除的验证容器中，不是框架自动安装行为。Linux 本轮没有真实模型或 CodeGraph 联调；真实外部工具联调在 macOS 完成。

真实验收由 `tools/verify-live --target <new-directory> --allow-live` 执行。独立保留的验收根包含 `existing/`、`new-project/`、`evidence/` 和 `report.json`。该批报告为 PASS，报告绑定的分发 manifest SHA256 是 `5b9a53793a05ddae173f405fda02bb90a76764266bc5a951b18e8cfe66c5bec8`，新工程源码摘要为 `f00216b76c4b98926b60a9c130c2f5846ea8ecdce9c2e5e4e1ce755e7ba4e42b`。随后仅补充本验收说明和任务记录，不能把旧 manifest 摘要当成最终分发摘要。

该批长运行开始后才将固定黑盒探针接入 verify-live，所以其 report.steps 尚无 independent-contract；探针已在同一新工程上单独执行通过。后续运行会自动包含该步骤，不把补验伪称为原报告的一部分。

## 场景到证据

| Scenario | 主要检查 |
|---|---|
| BOOT-01-INIT、BOOT-03-CONSENT | test_bootstrap_config、test_bootstrap_boundaries：零写预览、能力缺失、下载配置不能自授权 |
| BOOT-01-NEW、BOOT-02-ROOT | 审批拒绝测试、上级 OpenSpec 根拒绝；真实 new-unapproved-gate/new-scaffold |
| BOOT-03-CHANGED、BOOT-04-RETRY | test_bootstrap_storage、test_bootstrap_boundaries：人工变更、互斥、幂等、中断恢复 |
| MOD-01-IMPORT、MOD-01-ESCAPE | 本地真实 clone 全流程、危险 URL 拒绝、有界发现、链接越界拒绝 |
| MOD-02-IDENTITY、MOD-03-EMPTY、MOD-03-MOVE | 同仓索引共享；真实空工程；module add 移动及 missing 历史 |
| CG-01-INDEX、CG-01-TOOL | 真实 status/query；缺失工具和无节点回显不得 READY |
| CG-02-HOOK、CG-02-EVENT | 原 hook 保留、共享 worktree 拒绝、真实 dispatcher 执行、dirty 合并 |
| CG-03-STALE | 源码摘要与 dirty 检查；新候选发现；真实重复执行不重调 Agent |
| MAP-01-AGENT、MAP-01-MISSING | 真实 CLI 建图；手动宿主 WAITING_AGENT；超时进程回归 |
| MAP-02-RELATION、MAP-02-DESIGN | 证据摘要/锚点校验、陈旧证据拒绝；真实设计与观察比较 |
| MAP-03-DOCS、MAP-04-UNTRUSTED | 人工 AGENTS 不覆盖、模块摘要完整性、静态不能宣称运行通过；技能正向/无技能对照评估 |
| READY-01-REPORT、READY-01-NO_CODE、READY-02-READONLY | doctor 只读与分层结果；删除索引/分发文件不得缓存 READY |
| READY-02-RELEASE | 本节 macOS/Linux 离线回归及 macOS 真实工具验收；远程发布仍需集成决定 |

该表是证据索引，不代表穷尽所有输入组合或平台。参考型 project-bootstrap 技能做了无技能对照和正向测试，不把既有安全默认能力归功于新技能。

## 评审修复

独立代码复审提出并复核关闭六类重要问题：全操作锁保护、恢复权限重验、实际文件/数据库就绪检查、模块摘要覆盖校验、真实查询节点校验、索引范围默认拒绝。最后一项另外做了真实实验：索引完成后新增未批准目录并 sync，查询不到该目录的符号，批准模块仍可查询。

## 明确边界

- 静态 doctor 的 runtime=NOT_RUN 是刻意设计；业务实际通过由独立运行报告证明。
- 不隐式安装宿主工具、初始化 Git、建立远程仓库、推送、烧录或摄入知识库。
- init/new 是受控工程初始化，不是绕过需求确认的无限自主开发。完整真实示范另由 verify-live 显式启动。
- 人工 AGENTS、CodeGraph 配置或共享 hooks 冲突需处理后重试，不承诺无条件覆盖式一键成功。
- 所有微任务未逐一 commit，不能把本地实现说成已发布版本。集成、OpenSpec sync/archive 和知识回流仍保留各自门禁。
- GitHub 新版本 CI、Linux 真实外部工具联调、Windows、硬件和生产服务验收不在本轮已通过证据内。
