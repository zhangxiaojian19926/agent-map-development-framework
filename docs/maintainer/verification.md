# 公共工程壳验证

本页面向公共工程壳维护者，不是业务项目初始化前置步骤。业务项目验证按其[测试与交付指南](../guide/testing-and-delivery.md)执行。

## 每次变更的基础检查

```bash
python3 tools/check-framework
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
openspec validate --all --strict --no-interactive
git diff --check
```

清单新增或内容变化后运行 `python3 tools/update-manifest`，再核对指纹 diff。文档任务验证真实相对链接、内容归属和规则一致性；行为变化必须先获得有效 RED，再完成 GREEN 和受影响回归。

## 目录治理专项

- 使用者与维护者入口分别走查，历史资料不出现在当前最短操作路径。
- 新项目只包含运行时白名单，必要入口、技能、模板、CLI 和许可证完整。
- 升级只清理旧受管且哈希未变的冗余文件；人工修改和归属不明路径保留并冲突。
- `docs/project/` 人工正文、模块规则、业务源码、知识内容和活跃 change 在升级前后保持指纹。
- 旧 change 对账不代替其真实宿主、恢复、集成或发布验收。

## 证据矩阵

| Requirement/Scenario | Task | Test/走查 | 环境 | 最终版本 | 结果/限制 |
|---|---|---|---|---|---|
| 实际 ID | 实际任务 | 命令或场景 | Host/CI/Integration | commit 或工作树 diff | PASS/NOT_RUN/INFRA_ERROR |

CI 通过只证明其覆盖范围。真实宿主、私有认证、设备、部署和发布需要各自新鲜证据，未执行保持 NOT_RUN。

## 完成边界

最终验证须绑定最终工作树或提交。独立评审不可用时明确标注自查，不能把自查称为独立批准。提交、推送、发布和知识摄入分别按用户授权处理。

## 验证记录

- [2026-10-30 图文教程与 PDF 兼容验证](../verification/2026-10-30-illustrated-guide.md)：提交 `b952cb3`，本地及 Ubuntu、macOS CI 各 303 项测试通过。
