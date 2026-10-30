# 图文教程与 PDF 兼容验证记录

> 验证日期：2026-10-30。记录图文教程、PDF 分发兼容和发布渠道适配规格归档的最终证据，不代表业务项目运行、设备或部署验收。

## 最终版本与范围

- 最终提交：`b952cb368ee06fec6c0b851656281826c6cb9ac3`（`docs: add illustrated workflow guide`）。
- 教程：`docs/guide/from-zero-to-one.md`，覆盖 15 条主工作流、提示词模板、组合场景和故障排查。
- 图文 PDF：`docs/guide/from-zero-to-one.pdf`，38 页、16 张矢量流程图。
- 规格：`release-channel-adapter` 已同步到主规格，原 change 已归档到 `openspec/changes/archive/2026-10-29-add-release-channel-adapter/`。
- 兼容边界：PDF 可以留在公共分发仓库；初始化只复制运行时文本载荷，不把 PDF 解码为 UTF-8 或复制到新项目。

## 本地验证

| 检查 | 最终结果 | 证据边界 |
|---|---|---|
| `python3 tools/check-framework` | PASS | 307 个清单文件、23 个技能；指纹、链接和脚本语法通过 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` | PASS | 303 项测试全部通过 |
| PDF 内容完整性 | PASS | 15 条工作流标题和 16 张图均存在 |
| PDF 逐页渲染与联系表检查 | PASS | 38 页全部渲染；最终检查无警告，已消除异常空白页，抽查流程图、表格、目录树和中文显示正常 |
| 提交与推送 | PASS | 提交 `b952cb3` 已推送到 `origin/main`，推送后工作区干净 |

完整回归曾发现初始化流程把 PDF 当 UTF-8 文本读取。最终版本已在运行时载荷生成阶段排除 PDF，并重新通过全部 303 项测试；该结果不只依赖文档专项检查。

## GitHub Actions

- 工作流：`Validate public framework`
- Run：[`40969513133`](https://github.com/zhangxiaojian19926/agent-map-development-framework/actions/runs/40969513133)
- 绑定提交：`b952cb368ee06fec6c0b851656281826c6cb9ac3`
- 整体状态：`completed / success`

| Job | 框架检查 | 完整测试 | 结论 |
|---|---|---|---|
| `validate (ubuntu-24.04)` | PASS | 303 项通过 | success |
| `validate (macos-latest)` | PASS | 303 项通过 | success |

## 未扩展的证明范围

- 本次是文档、分发兼容和规格归档验证，不是业务应用运行验收。
- 未执行真实宿主、私有认证、设备、生产部署或业务发布验收，相关状态不因本次 CI 成功而改变。
- PDF 视觉检查属于本次自查，不冒充独立评审。
- 本次没有知识库内容摄入。
