# 验证报告模板

任务范围、时间、环境：
各模块版本组合、工作树/产物标识：
报告与证据保存位置、最终 commit 或工作树 diff：
| Req / Scenario | Task / module | Test | Environment | Evidence | Result |
|---|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | NOT_RUN |

PASS 仅用于实际断言通过；未运行 NOT_RUN；不适用 N/A 并解释；环境错误 INFRA_ERROR。
实现、局部验证、集成、评审、发布、归档和知识摄入分别报告。

## 可选机器核验记录

需要生成功能差距报告时，在同一 change 的 `docs/verification/<change>/` 下提供 `verification-evidence/v1`。每条 record 固定填写 `id,requirement,scenario,task,test,environment,result,category,artifact,reason`；category 为 FUNCTION、VISUAL、ACCESSIBILITY 或 BRAND。PASS 必须附本地 artifact 路径及 SHA-256，INFRA_ERROR 和 N/A 必须给公开原因分类；未执行保持 NOT_RUN。findings 固定填写 `id,severity,status,category,evidence_id`，开放问题由请求中的 S1–S4 BLOCK/REPORT 策略处理。

再用 `feature-parity-request/v1` 绑定当前产品集合、多个 spec、tasks、证据哈希、逐项映射与排除范围。运行 `parity --request ... --dry-run` 预览，批准后仅以 `--allow write` 生成。工具不执行测试；只有已完成 task 上匹配 Scenario 的 FUNCTION/PASS 和有效 artifact 支持 VERIFIED，其他诊断不能替代功能验证。公开报告不得包含产品私有自由文本、凭据或原始观察。
