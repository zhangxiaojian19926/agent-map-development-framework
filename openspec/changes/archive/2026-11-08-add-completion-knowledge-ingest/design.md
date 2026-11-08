## Context

完成判定已经集中在 `tools/framework_core/closure.py` 的 `outstanding_changes`。`tools/check-changes` 发现欠账就失败；`tools/check-project` 报告同一份活动 change 欠账，默认退出 0，`--strict` 才失败。`flow-02` 的下一项由 `tools/framework_core/workflows/combinations.json` 生成。初始化知识库是 alias `project`、目录 `knowledge/project/`。本分发仓库目前没有这份注册表，查询结果是 `NOT_CONFIGURED`。

## Goals / Non-Goals

**Goals:**

- 任务全部勾完且规格已同步时写入需求页；有已验证问题记录时同时写入问题页。
- 回执先于归档存在，归档把回执一起带走。
- 公共壳与使用者项目共用同一份欠账判定。

**Non-Goals:**

- 不回溯 `2026-11-08-add-agent-workflow-routers` 或其他已归档 change。
- 不在保存、提交或会话结束时写入。
- 不写设计、计划、约束、模块、验证专页，也不写 `INFERRED` 综合。
- 不复制到模块知识库，不结晶、不删除、不推送、不新建 alias。
- 不给 doctor 增加状态词。`flow-05` 仍负责查询和其他种类，那些写入继续逐次授权。

## Decisions

1. **写入点放在规格同步之后、归档之前。** 页面引用已经同步的规格，回执放在 change 目录的 `knowledge-receipt.json`。归档只移动目录。若等归档后才写，活动区的完成检查永远看不到回执。

2. **回执是结构，检查不猜测内容。** 回执含 `change`、`alias`（必须是 `project`）、`pages`。每个页面含 `path`、`artifact_kind`、`source_path`、`source_sha256`。需求页的种类必须是 `requirement`。问题要么是一条 `problem` 页面，要么是 `{ "status": "not_applicable", "reason": "..." }`。来源哈希相同则不重写页面，但回执仍必须在。

3. **已验证问题用 change 内的 `verified-problem.json`。** 字段是 `id`、`conclusion`、`evidence`、`limits`。`conclusion` 为 `pass` 时必须有问题页，`not_applicable` 无效。没有该文件时才允许 `not_applicable`。页面引用这个文件的路径和哈希，不另写验证专页。临时规避把 `limits` 中的根因未消除写进问题页。

4. **欠账判定只扩一处。** `outstanding_changes` 在任务已完成且规格已同步时，把回执缺失、页面缺失、哈希不符和 `NOT_CONFIGURED` 列为欠账。`check-changes` 因此失败。`check-project` 的同一列表沿用现有退出规则。只扫描活动 change，所以生效前的归档自然不报。

5. **没有注册表就不建库。** alias `project` 解析不到 `knowledge/project/` 时，欠账原因是 `NOT_CONFIGURED`，不创建目录，不写 `llm-wiki-aliases.json`。本仓库要让这个 change 自己过门禁，仍需一次单独的初始化授权。

6. **页面只收规格和问题记录。** 需求页来源是已同步的能力规格，问题页来源是 `verified-problem.json`。使用 `skill/llm-wiki/templates/engineering-template.md`，`confidence` 为 `EXTRACTED`。来源像密钥、差异、CodeGraph 输出或反编译文本时不复制，并把该页记为欠账。

7. **路由和人格各改来源，不手改生成结果。** `flow-02` 的下一项改组合清单后重新生成路由。人格句改 `docs/framework/agent-persona.md`，并同时改根 `AGENTS.md` 中同一段，避免两处不一致。托管标记的结构不动。

## Risks / Trade-offs

- [本仓库没有知识库，本 change 的任务一旦全部勾完就会让 `check-changes` 失败] → 写入回执的任务保持未勾，直到获得初始化授权。
- [只检查活动 change，手工搬进归档的 change 可以没有回执] → 与今天的规格同步门禁相同；归档步骤把回执作为移动前条件。
- [问题记录是新增文件，旧习惯只在 `docs/verification/` 写结论] → `flow-02` 写明有已验证问题时必须先留下 `verified-problem.json`。
- [人格句测试仍在找「询问摄入」] → 实现时与人格来源一起改测试。

## Migration Plan

1. 先改政策和路由来源，再扩展 `outstanding_changes`。
2. 本 change 在知识库存在并写好自己的回执之前保持活动。
3. 回退时撤掉欠账条款并恢复路由下一项。已经写入的页面保留，不删除。

## Open Questions

无。生效前的归档不回溯，已在规格 KI-06 中定下。
