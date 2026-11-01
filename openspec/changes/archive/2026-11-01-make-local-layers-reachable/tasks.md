## 1. 登记与指针

- [x] 1.1 新增 `skill/local-layers.json`，登记 7 个技能的 7 个必读规则层
  - 交付行为：哪些文件是 Agent 执行该技能时必须一并读取的，有唯一登记
  - 关联：`local-layer-reachability` / 改编层登记完整
  - 验收：登记项逐个核对存在；技法参考、脚本与创作史不在登记里
  - 阻塞于：无

- [x] 1.2 AGENTS.md 阶段路由表为 `matt-pocock:tdd`、`matt-pocock:diagnosing-bugs`、`matt-pocock:to-tickets`、`matt-pocock:code-review` 标出对应本地层文件名
  - 交付行为：指针落在 Agent 必经的路由表上，与技能名同处一格
  - 关联：`local-layer-reachability` / 改编层可被读到
  - 验收：七个登记文件名在 AGENTS.md 里都能被找到
  - 阻塞于：1.1

- [x] 1.3 AGENTS.md 参考技能段为 `matt-pocock:retro`、`matt-pocock:domain-modeling` 标出对应本地层文件名
  - 交付行为：参考型技能同样带改编层指针
  - 关联：`local-layer-reachability` / 改编层可被读到
  - 验收：同上
  - 阻塞于：1.1

## 2. 自动检查

- [x] 2.1 `tools/check-framework` 新增 `local_layer_errors`：登记项必须存在于对应技能目录，登记的技能名必须是真实入口，登记的文件名必须在活文档被提及
  - 交付行为：登记与磁盘不一致、或登记了却无人指向，都会被检出
  - 关联：`local-layer-reachability` / 改编层登记完整、改编层可被读到
  - 验收：人为造三种偏差各自被报出
  - 阻塞于：1.1

- [x] 2.2 `tools/check-framework` 新增 `skill_routing_errors`：每个在包内的技能必须在活文档有落点；同一技能在两处契约的阶段归属必须一致
  - 交付行为：孤儿技能与归属漂移都被检出
  - 关联：`skill-routing` / 每个技能都有可指名的落点、阶段归属在两处契约里一致
  - 验收：人为造孤儿技能与归属不一致各自被报出
  - 阻塞于：无

- [x] 2.3 补测试：三项偏差的 RED 用例 + 当前仓库通过的 GREEN 用例
  - 交付行为：检查可被证伪
  - 关联：`local-layer-reachability` / 改编层登记完整
  - 验收：全量单元测试通过
  - 阻塞于：2.1、2.2

## 3. 路由与移除

- [x] 3.1 `superpowers:dispatching-parallel-agents` 的阶段归属从 AGENTS.md 的 DISCOVERY 改到 WORKSPACE，条件与流程契约一致
  - 交付行为：两处契约对同一技能的归属相同
  - 关联：`skill-routing` / 阶段归属在两处契约里一致
  - 验收：`skill_routing_errors` 不再报出归属不一致
  - 阻塞于：2.2

- [x] 3.2 移除 `skill/superpowers/using-superpowers/SKILL.md`，保留其 `references/` 五个文件
  - 交付行为：永久占上下文的技能入口消失，上游对参考文件的引用不断
  - 关联：`local-layer-reachability` / 移除技能不得断链；`skill-routing` / 被移除的技能不留悬空落点
  - 验收：分发结构检查的链接校验通过；技能计数相应减少
  - 阻塞于：无

- [x] 3.3 为 `superpowers:subagent-driven-development` 写本地改编层，让框架的评审与提交契约占上风
  - 交付行为：上游的任务级评审与 implementer 自行提交被框架的契约取代，并行实施的能力保留
  - 关联：`local-layer-reachability` / 改编层优先于上游
  - 验收：改编层写明评审走 `matt-pocock:code-review`、implementer 不自行提交；上游 `SKILL.md` 字节不变
  - 阻塞于：无

- [x] 3.4 `tools/update-manifest` 改为从文件系统推导技能分组计数
  - 交付行为：移除一个技能后不再留下手写的分组数字
  - 关联：`local-layer-reachability` / 改编层登记完整
  - 验收：刷新后清单的技能计数与实际入口数一致
  - 阻塞于：3.2

- [x] 3.5 更新 `docs/maintainer/retro-findings.md` 里 `using-superpowers` 那条候选的状态
  - 交付行为：复盘记录反映实际处置
  - 关联：无（维护者记录）
  - 验收：状态与实际一致
  - 阻塞于：3.2

## 4. 纠正上一轮的错误建议

- [x] 4.1 撤回"移除 `superpowers:subagent-driven-development`"的建议，并纠正"实施阶段无并行委派落点"的结论
  - 交付行为：维护者记录里的建议基于完整扫描，不再与流程契约冲突
  - 关联：`skill-routing` / 阶段归属在两处契约里一致
  - 验收：roadmap 与 CHANGELOG 里没有与 `development-workflow.md` 冲突的说法
  - 阻塞于：无

- [x] 4.2 记录"判断技能有没有落点必须扫全部活文档，不能只扫常驻那一份"这条教训
  - 交付行为：同类错误不被重复犯
  - 关联：`skill-routing` / 每个技能都有可指名的落点
  - 验收：roadmap 里能查到
  - 阻塞于：无

## 5. 验证与归档

- [x] 5.1 `python3 tools/check-framework` 通过
- [x] 5.2 `python3 -m unittest discover -s tests` 全量通过
- [x] 5.3 `openspec validate --all --strict --no-interactive` 通过
- [x] 5.4 `openspec validate --archived --no-interactive` 通过
- [x] 5.5 `python3 tools/check-changes` 无欠账
- [x] 5.6 提交后 `git diff --check HEAD^ HEAD` 无空白错误
- [x] 5.7 同步能力规格到 `openspec/specs/` 并归档本 change
