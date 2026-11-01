## 1. 阶段路由表接线

- [x] 1.1 AGENTS.md 的 DISCOVERY 行补 `superpowers:dispatching-parallel-agents`，条件为"多个独立失败可并行分解时"，置于 `matt-pocock:diagnosing-bugs` 之后
  - 交付行为：排障阶段的并行分解有落点，与单线索诊断循环分工
  - 关联：`skill-routing` / 阶段技能必须带触发条件
  - 验收：该行每个技能名旁都有触发条件
  - 阻塞于：无

- [x] 1.2 AGENTS.md 的 KNOWLEDGE 行把"已选知识库技能"改为点名 `llm-wiki`
  - 交付行为：知识回流阶段有可指名的技能
  - 关联：`skill-routing` / 每个技能都有可指名的落点
  - 验收：路由表与参考段之外不再有"已选…技能"这种不点名写法
  - 阻塞于：无

## 2. 参考技能段分工

- [x] 2.1 AGENTS.md 参考技能段从"三个"改为"五个"，补 `matt-pocock:domain-modeling`（讨论领域术语、锐化含糊用词、用具体场景压测概念边界时）与 `superpowers:writing-skills`（新建技能时走"先看它失败"的验证流程）
  - 交付行为：每个参考技能带自己的触发条件，两个写作类技能分工写清
  - 关联：`skill-routing` / 参考技能之间分工不重叠；`agent-craft-skills` / 参考技能之间分工不重叠
  - 验收：`writing-for-agents` 管"怎么写"、`writing-skills` 管"新建技能时怎么验证"，读者不会当成重复
  - 阻塞于：无

## 3. 指南给出工作流的技能构成

- [x] 3.1 `docs/guide/from-zero-to-one.md` 第二部分在 15 条一览表之后补「每条工作流用到的技能」表
  - 交付行为：读者在指南里查到每条工作流用哪些技能、哪些不靠技能
  - 关联：`skill-routing` / 对外指南能查到每条工作流的技能
  - 验收：15 条全部出现；工作流 2 给出一行指向完整链条的位置
  - 阻塞于：1.1、1.2、2.1

## 4. 维护者记录

- [x] 4.1 `docs/maintainer/roadmap.md` 修正第 6 项的规格数量（29 → 32）与第 7 项的落点，登记本批
  - 交付行为：roadmap 不再引用过时数字，落点比原计划更具体
  - 关联：无（维护者记录）
  - 验收：roadmap 中所有数量与仓库实际一致
  - 阻塞于：无

- [x] 4.2 记录两个建议移除但本批不动的技能，以及"实施阶段仍无并行委派落点"这个已知缺口
  - 交付行为：缺口与建议有据可查，不被遗忘
  - 关联：`skill-routing` / 每个技能都有可指名的落点
  - 验收：roadmap 里能查到这两项
  - 阻塞于：无

## 5. 验证与归档

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 `python3 -m unittest discover -s tests` 全量通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 `openspec validate --archived --no-interactive` 通过
- [x] 5.5 `python3 tools/check-changes` 无欠账
- [x] 5.6 提交后 `git diff --check HEAD^ HEAD` 无空白错误
- [x] 5.7 同步能力规格到 `openspec/specs/` 并归档本 change
