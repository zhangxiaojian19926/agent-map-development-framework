## 1. 研究契约

- [x] 1.1 新增市场研究离线契约测试，覆盖有效交接、公开来源、事实与推断、设计待确认和 CLI 互斥，并先运行确认目标行为缺失形成有效 RED。
- [x] 1.2 实现 `market-research-request/v1` 严格校验、URL/日期/哈希和引用关系检查，以非法协议、凭据、重复 ID、未知引用和私有路径输入测试确认写入前失败。

## 2. 公开交接报告

- [x] 2.1 实现确定性研究摘要与待确认设计草案渲染，以来源事实/Agent 推断分区、固定 NOT_RUN、公开字段和既有 design-input 不变测试确认边界。
- [x] 2.2 实现 dry-run、UNCHANGED/UPDATED、人工冲突和第二份写入恢复，以重复执行、篡改及故障注入测试确认无私下覆盖或部分成功。

## 3. 入口与指南

- [x] 3.1 接入独立 `research --request` CLI 与 write 授权，以预检、正式执行、错误退出和不支持组合测试确认默认 CLI 兼容。
- [x] 3.2 补充可选市场研究使用指南和分发清单，以链接、内容归属和框架检查确认普通初始化、逆向和 4A 不新增研究或网络步骤。

## 4. 最终验证

- [x] 4.1 运行研究专项及相关 design-handoff、candidate、completion 回归并审查实际 diff，确认仅有 4B 范围且无网络、需求审批或业务代码副作用。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-market-research-handoff --strict` 和 `git diff --check`，保存最终工作树真实结果；未经另行授权不提交、推送、归档或发布。
