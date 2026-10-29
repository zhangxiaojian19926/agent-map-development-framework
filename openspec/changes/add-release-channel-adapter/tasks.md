## 1. 渠道契约与来源门禁

- [x] 1.1 新增发布渠道离线契约测试，以临时项目建立真实 4A READY 候选，覆盖有效 GitHub 适配、公开产物、固定 NOT_RUN 和 CLI 互斥，并先运行确认目标行为缺失形成有效 RED。
- [x] 1.2 实现 `release-channel-request/v1` 严格校验、静态渠道选择、GitHub 目标与资产名称检查，以未知渠道、凭据、非法 tag、非布尔属性、重复及大小写冲突名称测试确认写入前失败。
- [x] 1.3 实现 4A dry-run 候选重核验和显式请求/报告哈希绑定，以 GAPS_OPEN、FAILED、候选篡改、证据过期和当前资产变化测试确认非 READY 或过期来源不能适配。

## 2. 确定性渠道产物与事务

- [x] 2.1 实现显式资产映射、资源预算、原字节复制、Release 说明和 `release-channel-manifest/v1`，以候选外资产、私有路径、超限、清单元数据和私有附件不泄漏测试确认公开边界。
- [x] 2.2 实现公开渠道报告和私有回执，以请求/候选/资产哈希、受管标记及 `publish=NOT_RUN`、`execution=NOT_RUN` 测试确认适配不被表述为真实发布。
- [x] 2.3 实现目录暂存、多产物提交与恢复，以 dry-run 零写入、重复 UNCHANGED、合法 UPDATED、额外文件、人工修改、产物缺失及目录/报告/回执各阶段故障注入测试确认完整恢复。

## 3. 入口与指南

- [x] 3.1 接入独立 `channel --request` CLI 与 write 授权，以预检、正式执行、非 READY/错误退出和不支持组合测试确认默认 CLI 兼容。
- [x] 3.2 在测试与交付指南补充可选渠道适配入口并更新分发清单，以链接、内容归属和框架检查确认普通初始化、逆向、4A、4B 和公共壳 release 不新增渠道或网络步骤。

## 4. 最终验证

- [x] 4.1 运行渠道专项及 candidate、market-research、package、release、CI 相关回归并审查实际 diff，确认仅有 4C 范围且无网络、Git、上传、Release 或业务执行副作用；独立评审不可用时如实标注。
- [x] 4.2 运行 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`、`python3 tools/check-framework`、`openspec validate add-release-channel-adapter --strict` 和 `git diff --check`，保存最终工作树真实结果；未经另行授权不提交、推送、归档或发布。
