# 日常开发流程

从业务项目根目录开始。普通使用者只需说明目标，例如“继续当前 change”或“修复某个已定义 Scenario”；Agent 负责读取规则和运行内部命令。

## 入口顺序

1. 读取根 `AGENTS.md`、`docs/project/handoff.md`、项目约束和目标模块规则。
2. 运行只读 doctor，读取当前 OpenSpec status、instructions 和 contextFiles。
3. 按项目资源登记做 KB-first；没有注册表时继续只读研究，不自动建库。
4. 核对每个受影响仓库的 HEAD、工作区和已有修改，再选择任务路径。

## 按任务分流

| 任务 | 路径 | 完成证据 |
|---|---|---|
| 查询、解释、审计 | 只读探索 → 事实/推断/限制 | 不修改文件，给出来源 |
| 纯文档 | 确认范围 → 精确修改 → 链接和 diff 校验 | 不制造代码 RED |
| 既有规格缺陷 | 调试复现 → 有效 RED → 最小修复 → 回归 | 关联原 change 和实际测试 |
| 新行为或接口 | DISCOVERY → SPEC → PLAN → APPLY → TDD → REVIEW → VERIFY | 已批准场景、实现和适用验证 |
| 知识摄入 | 查询 → 明确内容与目标授权 → 摄入和校验 | 真实知识页、索引和日志 |

## 可选：公开市场研究交接

需要把竞品或市场资料带入 DISCOVERY 时，先由当前 Agent 按用户授权完成公开研究，再整理 `market-research-request/v1` 请求。请求绑定研究 ID、问题、公开 HTTP/HTTPS 来源、访问日期、声明内容 SHA-256、来源事实、Agent 推断、局限和待确认设计草案；工具本身不联网、不抓网页，也不验证来源仍在线或内容真实。

```bash
python3 tools/framework research --target . --request path/to/research-request.json --dry-run
python3 tools/framework research --target . --request path/to/research-request.json --allow write
```

正式写入只生成 `docs/project/market-research/<id>.md` 和私有回执 `.framework/local-state/market-research/<id>.json`。报告分区展示来源事实与 Agent 推断，固定 `design_status=NEEDS_DESIGN_APPROVAL`、`source_verification=NOT_RUN` 和 `execution=NOT_RUN`；不覆盖 `docs/project/design-input.md`，不自动创建或批准 OpenSpec，不生成业务代码或发布证据。

重复输入返回 `UNCHANGED`，合法更新返回 `UPDATED`；人工修改或回执不匹配会形成冲突，不会被静默覆盖。未显式运行此入口时，普通初始化、开发、逆向和发布候选流程不增加研究文件、网络或授权步骤。

## 新行为主流程

```text
DISCOVERY
   --> SPEC_VALIDATED + SPEC_APPROVED
   --> PLAN_APPROVED
   --> WORKSPACE_READY
   --> APPLY_CONTEXT_LOADED
   --> (RED --> GREEN --> REFACTOR --> REGRESSION)*
   --> REVIEWED
   --> CHANGE_VERIFIED
   --> 用户选择提交、PR 或保留
   --> SPECS_SYNCED
   --> ARCHIVED
```

需求、接口或验收变化时回到规格更新；实现失败先定位根因；环境不可用记 INFRA_ERROR，不能当作有效 RED 或业务 PASS。

## 模块资料何时更新

- 新增、删除、移动模块，或改变对外职责、模块间关系、整体拆分时，交付前发布一次关系地图并重新 doctor。
- 仅模块内部实现变化时不重建地图；源码指纹变化仍可能需要核对项目资料。
- 只读任务不写地图，CodeGraph sync 也不等于发布地图。

## 流程卡

| 项目 | 约定 |
|---|---|
| 输入 | 当前任务、change、目标模块、已有修改和验证环境 |
| 写入范围 | 当前 change、获批计划涉及的模块和对应测试；公共包不手改 |
| 授权 | 实现、委派、外部写入、设备、部署、提交和推送分别按当前请求核对 |
| 验证证据 | 有效 RED/GREEN、受影响回归、评审、集成 Scenario、最终工作树或提交 |
| 完成状态 | 适用 Scenario 通过且重要问题闭合；集成、归档和知识摄入分别报告 |
