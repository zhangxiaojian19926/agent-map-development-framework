# completion-knowledge-ingest Specification

## Purpose

规定需求开发完成和问题解决完成后，把对应记录写入工程初始化时建立的项目知识库，并用回执挡住没有知识页的完成声明。

## Requirements

### Requirement: KI-01 完成的需求写入初始化知识库

系统 SHALL 在一次需求的任务已全部勾完、且能力规格已同步进 `openspec/specs/` 时，把该需求写成初始化知识库中的需求页。系统 MUST 在归档之前完成这次写入。系统 MUST NOT 在仍有未勾选任务时写入。目标 MUST 是初始化建立的 alias `project` 及其目录 `knowledge/project/`。

#### Scenario: 已同步的需求进入需求页

- **WHEN** 一个 change 的任务已全部勾完，且其能力规格已同步
- **THEN** 初始化知识库的需求目录中有该需求的页面，页面标明 `EXTRACTED`，并引用来源路径与来源哈希

#### Scenario: 任务未完成不写入

- **WHEN** 一个 change 仍有未勾选的任务
- **THEN** 系统不把它写成需求页

### Requirement: KI-02 解决的问题写入初始化知识库

系统 SHALL 在一个问题已验证解决、且承载它的 change 任务已全部勾完时，把该问题写成同一初始化知识库中的问题页。写入 MUST 发生在归档之前。问题完成 MUST 以验证记录为准，记录至少包含验证命令或证据位置、结论和限制。系统 MUST NOT 把未验证修复、推测或只有计划的问题写成已解决。临时规避 MUST 在页面上写明根因未消除。目标库与 KI-01 相同。

#### Scenario: 已验证的问题进入问题页

- **WHEN** 一个问题的验证记录结论为通过，并且承载它的 change 任务已全部勾完
- **THEN** 初始化知识库的问题目录中有该问题的页面，页面标明 `EXTRACTED`，并引用该验证记录

#### Scenario: 未验证的问题不写成已解决

- **WHEN** 一个问题没有验证记录，或验证结论不是通过
- **THEN** 系统不把它写成已解决的问题页

### Requirement: KI-03 这两类完成不再逐次询问

系统 SHALL 把 KI-01 与 KI-02 视为工程壳流程的长期授权。需求开发完成或问题解决完成时，系统 MUST 直接写入，MUST NOT 再询问是否摄入。系统 MUST NOT 把这份授权扩展到结晶、删除、新建知识库、修改 alias 注册表或推送。相同来源哈希的页面 MUST NOT 重复写入。

#### Scenario: 完成后直接写

- **WHEN** 一次需求开发或一次问题验证已经完成，且目标页的来源哈希尚未写入
- **THEN** 系统写入对应页面，不再提出是否摄入的问题

#### Scenario: 授权不包含推送

- **WHEN** 需求页或问题页已经写入初始化知识库
- **THEN** 系统不因此推送知识库，也不因此新建另一个知识库

### Requirement: KI-04 回执证明已经写入

系统 SHALL 为每个完成的 change 留下一张知识回执。回执 MUST 列出 change、alias `project`、每个页面的路径、种类、来源路径和来源哈希。需求页 MUST 出现在回执中。该 change 含有已验证问题记录时，问题页也 MUST 出现。页面内容 MUST 与回执中的来源哈希相符。回执放在该 change 目录中，并随归档一起移动。

#### Scenario: 回执与页面一致

- **WHEN** 读取一个已完成 change 的知识回执
- **THEN** 回执中的每个页面都在初始化知识库中，且来源哈希与回执一致

#### Scenario: 没有回执的完成不被接受

- **WHEN** 一个 change 的任务已全部完成，但没有知识回执，或回执指向的页面不存在
- **THEN** 完成检查把该 change 报为欠账，不把它视为已经完成

### Requirement: KI-05 没有初始化知识库时不新建

系统 SHALL 在 alias `project` 或 `knowledge/project/` 不存在时，把知识写入记为 `NOT_CONFIGURED`。系统 MUST NOT 为此创建知识库或注册 alias。该 change 的完成检查 MUST 仍报欠账。建立这个库只属于工程初始化。

#### Scenario: 未初始化不假装已写入

- **WHEN** 一个 change 的任务已全部完成，而项目没有初始化知识库
- **THEN** 检查报出 `NOT_CONFIGURED`，并且磁盘上没有新建的知识库目录或 alias 注册

### Requirement: KI-06 历史归档不回溯

系统 SHALL NOT 因为本能力，把本能力生效前已经归档、且没有知识回执的 change 报为欠账。本能力生效后新完成的 change MUST 遵守 KI-01 至 KI-05。

#### Scenario: 旧归档保持安静

- **WHEN** 一个 change 在本能力生效前已经位于归档目录，且没有知识回执
- **THEN** 完成检查不因为它缺少回执而失败
