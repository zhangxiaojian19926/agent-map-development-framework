# 验证与追踪矩阵

日期：2026-10-26。范围：`organize-framework-and-project-layout` 当前未提交工作树。本文件记录场景走查与自动证据，不把文档存在单独视为流程通过。

## 最终检查

| 检查 | 结果 | 证据与边界 |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | PASS，155 项 | 覆盖生成、清理、恢复、文档布局和既有完整回归；默认不调用真实模型、私有仓库、设备或部署 |
| `python3 tools/check-framework` | PASS，210 个登记文件、23 个技能 | 清单指纹、大小写敏感相对链接和脚本语法通过 |
| `openspec validate --all --strict --no-interactive` | PASS，3/3 | 三个活跃 change 均通过严格结构校验，不改变旧任务状态 |
| `git diff --check` | PASS | 无空白错误 |
| 规格符合性与代码质量评审 | 自查完成 | 当前会话禁止子 Agent，未伪称独立评审；发现运行时链接、后续同步误删和模板源链接问题后均已修复并重跑受影响测试 |
| 最终工作树 Ubuntu/macOS CI | NOT_RUN | 当前改动未提交、未推送；历史 run `40249970950` 不属于本最终工作树 |
| 真实宿主、私有认证、设备、部署 | NOT_RUN | 不属于本目录治理变更的新增验收证据 |

## Requirement / Scenario 追踪

| Requirement / Scenario | 任务 | 场景走查与自动证据 |
|---|---|---|
| Audience-specific navigation / First-time user | 1.2、1.3、2.4 | 从 README 仅沿 BOOTSTRAP、启动单和 `docs/guide/` 即可完成初始化及后续开发导航；`test_readme_separates_user_and_maintainer_paths` 与完整链接检查通过 |
| Audience-specific navigation / Maintainer finds guidance | 1.4 | README 的公共壳维护入口分别定位布局、验证和发布；说明明确不是业务初始化前置；文档布局测试通过 |
| Audience-specific navigation / Historical document encountered | 4.1、4.2 | 四份历史计划/验收均在 `docs/archive/`，首页有集中索引，文首有“历史、不是现行操作说明”；`test_archive_is_linked_and_every_document_is_marked_historical` 通过 |
| Runtime allowlist / New project receives only runtime content | 3.1、3.2、5.1 | 先取得维护资料被复制的 RED，再以白名单转 GREEN；`test_prepare_copies_only_runtime_payload` 检查必需和禁止路径，`test_runtime_markdown_links_stay_inside_payload` 检查所有运行时 Markdown 链接 |
| Runtime allowlist / Existing project upgraded | 3.3–3.5 | 重复 prepare 后人工 AGENTS、项目事实、模块规则、源码、知识和活跃 change 前后 SHA256 一致；旧受管残留分别验证未修改删除、人工修改冲突、未知归属冲突和目录外同名保留 |
| Runtime allowlist / Payload incomplete | 3.2、5.1 | 空清单合成测试得到 `RUNTIME_PAYLOAD_INCOMPLETE: AGENTS.md`；`test_runtime_payload_missing_required_file_reports_path` 通过 |
| Directory ownership / Contributor classifies artifact | 2.1、2.2 | 项目布局表逐项核对声明、生成目录、公共包、本机状态、事实、规格、模块、验证、知识和构建产物的唯一位置、责任方和提交规则 |
| Directory ownership / Generated file edited | 2.2、2.4、3.5 | 指南规定人工正文和受管区块边界；生成器冲突回归与人工内容指纹比较通过，未强制覆盖 |
| Directory ownership / Local state reviewed for commit | 2.2 | `.framework/`、私有启动输入、凭据、缓存和 `dist/` 均有本机/忽略边界；未把这些内容写入公共事实或知识库 |
| Module placement / Existing source tree onboarded | 2.3、3.5 | 既有 `src/app.py` 保持原路径和指纹；既有散落源码发现回归继续通过 |
| Module placement / Planned module has no implementation | 2.3 | 指南明确拟议模块只存在于设计/规格，不创建空目录；未改变模块数据模型或新增拟议模块目录 |
| Module placement / Cross-module change delivered | 2.3、2.4 | 模块生命周期、任务交接和验证报告关联共享 Scenario、双方模块、局部/集成验证和版本组合；未以单元测试替代集成门禁 |
| Historical lifecycle / Legacy change unchecked | 4.3、4.4 | `docs/maintainer/legacy-change-status.md` 逐项列出旧任务、环境和证据缺口；两个旧 change 未勾任务保持未勾，未执行项保留 NOT_RUN |
| Historical lifecycle / Completed change archived | 4.4 | 本变更没有达到归档门禁的旧 change，因此实际归档为 N/A；报告明确后续须独立授权、先同步核对再正常归档，未自动同步或归档 |
| Layout validation / Distribution drift detected | 5.1、5.2 | 白名单禁止内容、必要文件缺失、历史标识、源文档和生成文档链接均有失败定位；完整单元测试和公共检查通过，CI 配置继续运行同一检查 |
| Usable delivery / Standard development flow | 1.3、2.4、5.3 | 日常开发、模块生命周期、测试交付和框架升级均走查输入、写入范围、授权、证据和完成状态；任务仍分查询、文档、缺陷和新行为，没有统一成无差别全量流程 |

## 评审记录与未执行边界

- 有效 RED：运行时禁止文件、旧残留删除/冲突、目标公共包失效链接均先复现，再最小修复。
- 回归中发现后续 `sync_catalog` 会受通用删除推导影响，已改为只有生成流程显式传入的候选才可删除，避免其他 `owned_changes` 调用清理公共包。
- 删除事务支持预检、幂等和恢复；目录外文件不属于清理范围，未使用递归清空。
- 当前工作树尚未提交或推送，所以 5.4 的最终双平台 CI 和 5.5 的集成/同步/归档不能宣称完成。
- 未摄入知识内容；可复用经验和目标知识库须在交付时单独取得明确授权。
