## 1. 请求与证据契约

- [x] 1.1 新增候选离线契约测试，覆盖有效请求、版本绑定、证据结果、公开产物与 CLI 互斥，并先运行确认目标行为缺失形成有效 RED。
- [x] 1.2 实现 `release-candidate-request/v1` 与 `delivery-evidence/v1` 校验、来源和附件哈希核验，以合法/过期/不安全输入测试确认写入前受控失败。

## 2. 状态与候选报告

- [x] 2.1 实现 READY、GAPS_OPEN、FAILED 的优先级和公开差距计算，以构建/功能/集成记录组合测试确认失败优先且缺证据不通过。
- [x] 2.2 实现 dist 白名单元数据、确定性公开候选报告、发布说明草案和固定 release=NOT_RUN，以隐私、哈希、字段稳定性测试确认不渲染附件正文。

## 3. 持久化与入口

- [x] 3.1 实现 dry-run、UNCHANGED/UPDATED、人工冲突和双产物失败恢复，以重复执行、篡改及故障注入测试确认既有内容保留。
- [x] 3.2 接入独立 `candidate --request` CLI 与 write 授权，以 dry-run、正式执行、退出码、默认 package 和不支持组合回归测试确认兼容。
- [x] 3.3 补充显式使用指南和分发清单，以链接、内容归属和框架检查确认普通初始化及逆向流程不新增必经步骤。

## 4. 最终验证

- [x] 4.1 运行候选专项与相关 package/parity/completion 回归并审查实际 diff，确认仅有 4A 范围且没有真实构建、测试声明或外部发布副作用。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-delivery-release-candidate --strict` 和 `git diff --check`，保存最终工作树真实结果；未经另行授权不提交、推送、归档或发布。
