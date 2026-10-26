# 历史资料索引

本目录只保存历史计划、历史验收和证据回溯入口，不是当前操作说明、活跃任务状态或发布结论。当前使用从[工程壳首页](../../README.md)和[初始化入口](../../BOOTSTRAP.md)开始，公共壳维护从[维护者指南](../maintainer/repository-layout.md)开始。

## 内容边界

- `plans/`：已完成或已停止维护的历史实施计划，不控制当前 OpenSpec 状态；包括[工程初始化与模块地图](plans/2026-09-25-project-bootstrap.md)和[Agent 主导初始化](plans/2026-09-25-agent-led-project-intake.md)。
- [历史发布验收](acceptance.md)：特定版本和时间的验收快照，旧测试数量与工具版本不代表当前结果。
- `verification/`：历史验证记录，不能替代最终工作树的新鲜证据；包括 [Bootstrap 0.2.0 本地验收](verification/bootstrap-0.2.0.md)。
- 活跃 OpenSpec change 保留在 `openspec/changes/`，不作为历史文件移动；只有完成正常同步和归档门禁后才改变其生命周期状态。

阅读历史资料时必须同时核对日期、版本、适用环境和 NOT_RUN 项。历史文件中的命令、链接和结论不自动获得当前执行授权。
