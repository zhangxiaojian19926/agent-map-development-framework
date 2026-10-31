## Purpose

规定任务已完成的 change 必须先进入能力规格库、再归档，并规定用只读检查发现这类欠账。目的是让规格库始终反映仓库实际拥有的能力。

## ADDED Requirements

### Requirement: 完成的 change 必须同步并归档

系统 SHALL 要求任务已全部完成的 change 把它声明的能力规格同步进 `openspec/specs/`，并把 change 移入 `openspec/changes/archive/`。系统 SHALL NOT 让一个完成的 change 长期留在活动区而不同步。

#### Scenario: 能力规格缺失

- **WHEN** 一个 change 的任务已全部完成，但它的能力规格不在 `openspec/specs/` 里
- **THEN** 检查报出该 change 及其缺失的能力

#### Scenario: 已同步但未归档

- **WHEN** 一个 change 的任务已全部完成且能力规格已同步，但它仍在活动区
- **THEN** 检查报出该 change 需要走归档流程

### Requirement: 检查只读

系统 SHALL 让该检查只读不写：它不移动 change，不合并规格。系统 SHALL 报告未完成的状态与下一步，不代替规格同步与归档。

#### Scenario: 检查不修改仓库

- **WHEN** 运行该检查
- **THEN** 仓库内容不发生任何改变

#### Scenario: 报出可执行的下一步

- **WHEN** 检查发现未完成的 change
- **THEN** 报告说明缺哪些能力的同步、该走哪一步归档

### Requirement: 判定依据是任务清单

系统 SHALL 以 `tasks.md` 中没有未勾选任务判定该 change 已完成。系统 SHALL NOT 报告没有任务清单的 change。系统 SHALL 仍要求声明了跳过规格的 change 完成归档。

#### Scenario: 未完成的 change 不报

- **WHEN** 一个 change 仍有未勾选的任务
- **THEN** 检查不报告它

#### Scenario: 没有任务清单不判定

- **WHEN** 一个 change 没有任务清单
- **THEN** 检查不报告它

#### Scenario: 跳过规格的 change 仍要归档

- **WHEN** 一个 change 声明跳过规格且任务已全部完成
- **THEN** 检查仍要求它归档

### Requirement: 检查接入三处

系统 SHALL 在本地提交前检查、每次推送与拉取请求的校验、以及发布打标签之前运行该检查。

#### Scenario: 本地在提交前发现

- **WHEN** 维护者在本地运行提交前检查
- **THEN** 检查在分发检查之后运行并报出未完成的 change

#### Scenario: 发布前被拦

- **WHEN** 发布流水线运行到打标签之前
- **THEN** 该检查作为前置条件，欠账存在时不打标签
