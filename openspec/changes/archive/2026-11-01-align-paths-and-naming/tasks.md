## 1. 技能组改名

- [x] 1.1 `git mv skill/super-powers skill/superpowers`
- [x] 1.2 更新 `skill/matt-pocock/code-review/framework-rules.md` 的跨组链接
- [x] 1.3 更新 `THIRD_PARTY_NOTICES.md` 与 `docs/integrations.md` 的路径表述

## 2. 计划文档位置

- [x] 2.1 `docs/maintainer/repository-layout.md` 的迁移对照表与目录归属表
- [x] 2.2 `tools/framework_core/generation.py` 的运行时排除清单，并清掉已失效条目
- [x] 2.3 `requesting-code-review` 与 `subagent-driven-development` 的示例路径改为中性表述
- [x] 2.4 `tests/test_bootstrap_generation.py` 夹具中的路径
- [x] 2.5 清理磁盘上残留的空目录

## 3. 调度与记录

- [x] 3.1 `.github/workflows/release.yml` 的 cron 避开整点
- [x] 3.2 `docs/maintainer/retro-findings.md` 两条候选的状态更新

## 4. 验证

- [x] 4.1 全仓搜索确认无遗留的旧路径引用（历史记录除外）
- [x] 4.2 `python3 tools/check-framework` 通过
- [x] 4.3 全量单元测试通过
- [x] 4.4 `openspec validate --all --strict --no-interactive` 通过
- [x] 4.5 规格同步后归档本 change
