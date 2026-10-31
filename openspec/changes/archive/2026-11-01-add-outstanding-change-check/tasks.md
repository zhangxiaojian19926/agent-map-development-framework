## 1. 工具

- [x] 1.1 新增只读工具 `tools/check-changes`，报出任务已全部完成却仍在活动区的 change
- [x] 1.2 区分两种情况：能力规格未同步进 `openspec/specs/`，以及已同步但未归档
- [x] 1.3 支持 `--json` 输出与非零退出码

## 2. 接入

- [x] 2.1 `tools/pre-commit-check` 在分发检查之后运行
- [x] 2.2 `.github/workflows/validate.yml` 增加该步骤
- [x] 2.3 `.github/workflows/release.yml` 在打 tag 前运行

## 3. 测试与文档

- [x] 3.1 新增测试：未完成的 change 不报、无任务文件的 change 不报、能力未同步要报、已同步未归档要报、已归档不报、skip_specs 的 change 仍要报、非零退出码、JSON 输出、本仓库自身无欠账
- [x] 3.2 `docs/maintainer/verification.md` 的基础检查清单与固定顺序更新

## 4. 验证

- [x] 4.1 `python3 tools/check-framework` 通过
- [x] 4.2 全量单元测试通过
- [x] 4.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 4.4 规格同步后归档本 change
