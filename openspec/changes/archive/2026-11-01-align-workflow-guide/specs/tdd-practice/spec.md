## MODIFIED Requirements

### Requirement: 重构归属

系统 SHALL 把实现阶段的重构步限定为当前任务必要的整理（去重复、改名、抽 helper），并 SHALL 把设计级重构归入评审阶段讨论。系统 SHALL 把实现阶段的任务循环固定为 RED → GREEN → REFACTOR → REGRESSION → TASK_VERIFIED 五步，并 SHALL 保持实现阶段的既有步骤顺序与退出条件不变。

#### Scenario: 任务内整理留在实现阶段

- **WHEN** 实现完成后存在当前任务范围内的重复或命名问题
- **THEN** Agent 在实现阶段的整理步内处理，并保持测试全绿，不在此时改变对外接口

#### Scenario: 设计级重构归入评审阶段

- **WHEN** 发现模块边界或接口设计需要重构
- **THEN** Agent 不在实现阶段直接改动设计，而是把它记入评审阶段讨论，由评审决定是否另开变更

#### Scenario: 任务循环的五步不可缺

- **WHEN** 实现阶段推进一个任务
- **THEN** 按 RED → GREEN → REFACTOR → REGRESSION → TASK_VERIFIED 顺序执行，回归步不得跳过
