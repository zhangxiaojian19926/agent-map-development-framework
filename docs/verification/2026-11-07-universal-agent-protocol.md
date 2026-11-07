# Universal Agent Protocol 工程壳集成验证记录

> 验证日期：2026-11-07。本文件同时记录第一片（静态文件 / 单元测试 / 六道门禁）、同日闭环（独立 prepare/host 运行时证据、规格同步与归档），以及同日一条授权摄入的知识回流闭环（抛掷工程，非分发库、非 66.agent_prompt）。不代表跨模型效果、真实业务项目闭环或人格正文自动成长。本文件是自查，不冒充独立评审。单元测试计数不得升级为本闭环的运行时证据。

## 最终版本与范围

- 工作树：未提交。change `add-agent-persona` 已同步能力 `agent-persona` 进 [openspec/specs/agent-persona/spec.md](../../openspec/specs/agent-persona/spec.md)，并归档为 [2026-11-07-add-agent-persona](../../openspec/changes/archive/2026-11-07-add-agent-persona/proposal.md)。任务 4.2 已勾。
- 来源钉：提示词仓库提交 `7099de84f6a468734dffcaa9b4dc9ab14dc27328`（短显示 `7099de8`，说明：优化 v4.0 协议：区分明确第二交付物、补证据分层并加强包校验）。只复制短协议和三个子代理正文，并加壳绑定。不把该仓库做成子模块，也不搬它的每周发版。
- 相对该来源的唯一工具改动：来源在 `7099de8` 上 `uap-investigator` / `uap-challenger` / `uap-verifier` 的 `tools` 均为 `Read, Grep, Glob, Bash`。壳内 investigator 与 challenger 去掉 `Bash`，只留 `Read, Grep, Glob`；verifier 保留 `Bash`。
- 验收口径：能证明的是文件、安装、分发仓库外的真实 prepare/host 路径、归档后门禁，以及抛掷工程上一次授权摄入后的 KB 查询命中与跨进程持久。不能证明的见文末。

## 闭环主张（2026-11-07 独立运行时，不得用单测代替）

抛掷目录：`/tmp/uap-persona-loop-verify/`（在分发仓库外，避开 `TARGET_CONTAINS_DISTRIBUTION`）。CLI：`python3 -B tools/framework`。人格来源：`docs/framework/agent-persona.md`。

| 主张 | 状态 | 新鲜证据 |
|---|---|---|
| 托管段含人格正文、自改禁令与英文操作句 | PASS | `prepare --target /tmp/uap-persona-loop-verify/project-claude --project-id demo --agent current --yes --allow write` 退出 0，`status=PREPARED`。根 `AGENTS.md` 的 `FRAMEWORK_ENTRY` 含人格全文与自改禁令（不得修改 FRAMEWORK_ENTRY 托管段），并含读取公共工作流 `.agent-framework/AGENTS.md`、任务入口与收尾只读 doctor、地图发布条件、已批准 OpenSpec/TDD、以及询问摄入的英文操作句 |
| 运行包 AGENTS 以人格开头且阶段表仍在 | PASS | `.agent-framework/AGENTS.md` 以 `<!-- AGENT_PERSONA_START -->` 开头，含人格全文；`PERSONA_END` 之后含 `| 1. DISCOVERY |` 至 `| 11. KNOWLEDGE |` |
| Claude Code 只装 settings + 三个只读子代理 | PASS | `host --request host-apply.json --allow write --allow hooks` 退出 0：`{"files":[".claude/agents/uap-challenger.md",".claude/agents/uap-investigator.md",".claude/agents/uap-verifier.md",".claude/settings.json"],"host":"claude-code","status":"UPDATED"}`。目录内仅这四个文件。tools：challenger/investigator=`Read, Grep, Glob`；verifier=`Read, Grep, Glob, Bash`。无 `Write`/`Edit`/`MultiEdit`。无 `CODEBUDDY.md` |
| CodeBuddy 只装三个子代理，无 CODEBUDDY.md、无家目录写入、无编造 hook | PASS | 第二抛掷工程 `project-codebuddy`：`host --allow write` 退出 0，`files` 仅三个 `.codebuddy/agents/uap-*.md`。无 `CODEBUDDY.md`、无 `.codebuddy/settings.json`、无 `.codebuddy/hooks`、无 hook JSON。安装前后 `~/.codebuddy` 均不存在 |
| 不完整 / 改写的 FRAMEWORK_ENTRY 报 RULE_CONFLICT 且不覆盖 | PASS | 不完整块：退出 3，`{"error":"RULE_CONFLICT: invalid AGENTS managed block","status":"CONFLICT"}`，原文仍是 `<!-- FRAMEWORK_ENTRY_START -->\nuser edited incomplete block`。改写块：退出 3，`{"error":"RULE_CONFLICT: unowned or edited AGENTS block","status":"CONFLICT"}`，`TAMPERED` 仍在 |
| Claude Code CLI 最小冒烟 | PASS | 已安装 `/opt/homebrew/bin/claude`，版本 `2.1.311 (Claude Code)`。在抛掷工程上 `claude plugin validate .claude` 与 `claude plugin validate .claude/agents` 均为 `✔ Validation passed` 退出 0。`claude agents --json` 列出的是后台会话，不是项目子代理定义 |
| CodeBuddy CLI 最小冒烟 | NOT_RUN | 已试 `command -v codebuddy`、`which codebuddy`、`codebuddy --version`。结果：`codebuddy not found`，退出 1。未编造会话 |
| 规格同步与归档 | PASS | 新建 [openspec/specs/agent-persona/spec.md](../../openspec/specs/agent-persona/spec.md)，六条 ADDED 需求与十一条 Scenario 均在主规格中；无 delta 操作标题。change 移至 [openspec/changes/archive/2026-11-07-add-agent-persona/](../../openspec/changes/archive/2026-11-07-add-agent-persona/proposal.md)，任务 4.2 已勾 |
| 归档后六道门禁 | PASS | 见下一节。`check-framework` 曾因本文件仍链到活动区 change 而 FAIL；改链到归档路径并刷新清单后重跑通过 |
| 跨模型效果 | 未证明 | 未跑。壳的 CI 不跑模型 |
| 真实业务项目闭环 | 未证明 | 抛掷目录不是业务工程，未走完整开发周期 |
| 知识回流（授权摄入后下次能查到） | PASS | 见「知识回流闭环」。抛掷工程 `/tmp/uap-kb-reflux-verify/project`：prepare 后查询 `uap-investigator`  miss；`WIKI_WRITE_CONFIRM=yes` 摄入 EXTRACTED 摘录并写 verification 页后 hit；新进程再查仍 hit。provenance=`EXTRACTED`。未写入分发库 `knowledge/` |
| 人格正文自动成长 | 未证明 | 本次只写入抛掷工程 wiki 页面，未改人格正文、托管段或技能路由 |

## 独立运行时命令与原文

工作目录外抛掷根：`/tmp/uap-persona-loop-verify`。UTC 起始 `2026-11-07T11:10:29Z`。

### prepare（project-claude）

```
$ python3 -B tools/framework prepare --target /tmp/uap-persona-loop-verify/project-claude --project-id demo --agent current --yes --allow write
{
  "agent": { "status": "WAITING_AGENT" },
  "development": "NEEDS_DESIGN_APPROVAL",
  "initialization": "PARTIAL",
  "knowledge": { "alias": "project", "ingestion": "EMPTY", "status": "SCAFFOLDED" },
  "onboarding": "PREPARED",
  "runtime": "NOT_RUN",
  "scaffold": "READY",
  "status": "PREPARED"
}
[exit 0]
```

（完整 JSON 含 `documentation=MISSING`、`handoff.status=NEEDS_DESIGN_APPROVAL`、`hooks.status=NOT_CONFIGURED`、`maps.status=NOT_APPLICABLE`。这是空工程 prepare 的预期，不是人格注入失败。）

### host apply claude-code

```
$ python3 -B tools/framework host --target /tmp/uap-persona-loop-verify/project-claude --request .../host-apply.json --allow write --allow hooks
{
  "files": [
    ".claude/agents/uap-challenger.md",
    ".claude/agents/uap-investigator.md",
    ".claude/agents/uap-verifier.md",
    ".claude/settings.json"
  ],
  "host": "claude-code",
  "status": "UPDATED"
}
[exit 0]
```

`.claude/settings.json` 含项目级 `PreToolUse` hook：`python3 .agent-framework/tools/framework host --event --target .`。

### host apply codebuddy（第二抛掷工程）

```
$ python3 -B tools/framework host --target /tmp/uap-persona-loop-verify/project-codebuddy --request .../host-apply.json --allow write
{
  "files": [
    ".codebuddy/agents/uap-challenger.md",
    ".codebuddy/agents/uap-investigator.md",
    ".codebuddy/agents/uap-verifier.md"
  ],
  "host": "codebuddy",
  "status": "UPDATED"
}
[exit 0]
```

### RULE_CONFLICT

```
$ python3 -B tools/framework prepare --target .../project-conflict-incomplete ... --yes --allow write
{"error": "RULE_CONFLICT: invalid AGENTS managed block", "status": "CONFLICT"}
[exit 3]

$ python3 -B tools/framework prepare --target .../project-conflict-edited ... --yes --allow write
{"error": "RULE_CONFLICT: unowned or edited AGENTS block", "status": "CONFLICT"}
[exit 3]
```

### 宿主 CLI 冒烟

```
$ /opt/homebrew/bin/claude --version
2.1.311 (Claude Code)

$ /opt/homebrew/bin/claude plugin validate /tmp/uap-persona-loop-verify/project-claude/.claude
Validating components in: /tmp/uap-persona-loop-verify/project-claude/.claude
✔ Validation passed
[exit 0]

$ command -v codebuddy; which codebuddy
codebuddy not found
[exit 1]
NOT_RUN: codebuddy CLI not installed. Tried: command -v codebuddy; which codebuddy; codebuddy --version.
```

## 归档后六道门禁

在仓库根执行。先 `python3 tools/update-manifest`（输出：`Updated 511 fingerprints and 6 skill groups; inspect the diff.`）。回填本记录并修正归档链接后再次刷新清单，重跑 `check-framework` 与 `git diff --check`。

| 检查 | 结果 | 输出摘要 |
|---|---|---|
| `python3 tools/check-framework` | PASS | 改链前 FAIL：本文件仍指向活动区 `openspec/changes/add-agent-persona/proposal.md`。改链到归档路径并去掉误解析的相对链接后：`PASS: 511 inventoried files, 27 skills; hashes, links, syntax, invocation forms, document contract, status vocabulary, skill routing and local layers` |
| `python3 -m unittest discover -s tests` | PASS | `Ran 426 tests in 77.472s` / `OK`（`PYTHONDONTWRITEBYTECODE=1`）。此为回归，不是上面的独立 prepare/host 证据 |
| `openspec validate --all --strict --no-interactive` | PASS | `Totals: 39 passed, 0 failed (39 items)`，含 `spec/agent-persona`；活动区不再有 `change/add-agent-persona` |
| `openspec validate --archived --no-interactive` | PASS | `Totals: 29 passed, 0 failed (29 items)`，含 `change/2026-11-07-add-agent-persona` |
| `python3 tools/check-changes` | PASS | `PASS: no completed change is left unsynced or unarchived` |
| `git diff --check` | PASS | 退出码 0，无空白报错。只覆盖已跟踪文件的未暂存 diff；未跟踪新文件不在此命令范围内 |

`openspec validate --specs`（同步后、归档前）：`spec/agent-persona` 通过；`Totals: 37 passed, 0 failed (37 items)`。

## 第一片（历史，2026-11-07 早些时候）

下列主张来自实现阶段的文件核对与单元测试，**不是**本闭环的独立运行时证据，不得用来代替上一节。

- 人格进入托管段：`generation.py` 的 `persona_text()`；`tests/test_bootstrap_generation.py`
- 阶段表仍在：框架 `AGENTS.md` 标记之后仍有 DISCOVERY 到 KNOWLEDGE 路由表
- doctor 词典未改：工作树未修改 `docs/guide/framework-model.md`
- 不新建技能、不改路由规格：`openspec/specs/skill-routing/spec.md` 与 `skill/` 不在本变更 diff 中；Qwen 模板未改
- 当时六道门禁：`check-framework` 报 510 个清单文件；`unittest discover -s tests` 报 426 OK；`openspec validate --all --strict` 39 passed（含活动 change）；`openspec validate --archived` 28 passed；`check-changes` PASS（当时 4.2 未勾，故不视为已完成未归档）

用户给定（第一片请求，不能升级成本闭环的独立测过指标）：宿主测试 22 项通过、生成测试 16 项通过。

## 知识回流闭环（2026-11-07 授权摄入，仅此一条）

**主张**：Knowledge reflux works on an authorized ingest: after a real prepare, KB-first query misses the topic; after an authorized ingest of the existing agent-persona verification facts, a fresh query hits the same module wiki; provenance is EXTRACTED; a second query in the same project still finds it.

**状态：PASS**（抛掷工程；不是业务项目，不是分发库 wiki，不是跨模型。）

授权范围（用户给定）：仅该验证主题、仅抛掷目标。不是 wiki 总授权，不是生产，不是 `66.agent_prompt`。

11.12 清单：

| 项 | 值 |
|---|---|
| source_path | `/tmp/uap-kb-reflux-verify/agent-persona-verification-excerpt.md` |
| source_sha256 | `5fc727d2ddee2b29657d7e6f7713a4a166e9ffc1159cac9e9822f10557f718ce` |
| artifact_kind | verification |
| 目标 alias | `project` → `knowledge/project/` |
| 摘录事实 | 人格住在托管 AGENTS 块；三个只读子代理（含 uap-investigator）；change 已归档 `2026-11-07-add-agent-persona` |
| provenance | EXTRACTED |
| 抛掷目录 | 留下 `/tmp/uap-kb-reflux-verify/`（含 `project/` 与摘录文件） |

CLI 工作目录：分发库根目录做 prepare；查询与摄入在抛掷工程内用其 `.agent-framework/skill/llm-wiki/scripts/`。

### 1. prepare

```
$ python3 -B tools/framework prepare --target /tmp/uap-kb-reflux-verify/project --project-id kb-reflux-demo --agent current --yes --allow write
{
  "knowledge": { "alias": "project", "ingestion": "EMPTY", "status": "SCAFFOLDED" },
  "onboarding": "PREPARED",
  "scaffold": "READY",
  "status": "PREPARED"
}
[exit 0]
```

（完整 JSON 另含 `documentation=MISSING`、`development=NEEDS_DESIGN_APPROVAL`、`runtime=NOT_RUN`。空工程 prepare 的预期。）

资源登记（生成后原文）：

```
Knowledge alias `project` at `knowledge/project/`. The empty shell is not ingested content.
```

### 2. 基线 miss

```
$ cd /tmp/uap-kb-reflux-verify/project
$ bash .agent-framework/skill/llm-wiki/scripts/status.sh project
{
  "root": "/private/tmp/uap-kb-reflux-verify/project/knowledge/project",
  "topic": "kb-reflux-demo",
  "language": "zh",
  "shell": "READY",
  "ingestion": "EMPTY",
  "pages": 0,
  "raw": 0
}
[exit 0]

$ bash .agent-framework/skill/llm-wiki/scripts/query.sh project "uap-investigator"
{
  "root": "/private/tmp/uap-kb-reflux-verify/project/knowledge/project",
  "results": []
}
[exit 0]
```

同命令查询 `agent-persona` 与 `FRAMEWORK_ENTRY` 亦为 `"results": []`。`--all "uap-investigator"` 返回 alias `project` 且 results 为空。这是空壳基线，不是失败。

### 3. 摄入

无 `WIKI_WRITE_CONFIRM` 被拒绝（未伪造命中）：

```
$ bash .agent-framework/skill/llm-wiki/scripts/ingest.sh project /tmp/uap-kb-reflux-verify/agent-persona-verification-excerpt.md
ERROR: Write denied: obtain current user authorization, then set WIKI_WRITE_CONFIRM=yes for this command only
[exit 1]
```

授权后仅对该命令设置确认：

```
$ WIKI_WRITE_CONFIRM=yes bash .agent-framework/skill/llm-wiki/scripts/ingest.sh project /tmp/uap-kb-reflux-verify/agent-persona-verification-excerpt.md
{
  "status": "PREPARED",
  "raw": "raw/notes/2026-11-07-5fc727d2ddee-agent-persona-verification-excerpt.md",
  "pending": [
    "agent reads schema and source",
    "source/entity/topic pages",
    "index and log",
    "source/link verification"
  ]
}
[exit 0]
```

助手退出只表示 raw 已拷贝。此时 `status` 仍为 `ingestion=EMPTY`、`pages=0`、`raw=1`。按技能完成写入：

- 知识页 `knowledge/project/wiki/sources/verifications/agent-persona-uap-loop.md`（frontmatter `confidence: EXTRACTED`，`artifact_kind: verification`）
- 更新 `index.md` 与 `log.md`
- 页内引用 raw 相对路径

未写入分发仓库 `knowledge/`。未发明新主张。

### 4. 再次查询（必须 hit）与 lint

```
$ bash .agent-framework/skill/llm-wiki/scripts/status.sh project
{
  "root": "/private/tmp/uap-kb-reflux-verify/project/knowledge/project",
  "topic": "kb-reflux-demo",
  "language": "zh",
  "shell": "READY",
  "ingestion": "PRESENT",
  "pages": 1,
  "raw": 1
}
[exit 0]

$ bash .agent-framework/skill/llm-wiki/scripts/query.sh project "uap-investigator"
{
  "root": "/private/tmp/uap-kb-reflux-verify/project/knowledge/project",
  "results": [
    {
      "page": "wiki/sources/verifications/agent-persona-uap-loop.md",
      "matches": 26
    }
  ]
}
[exit 0]

$ bash .agent-framework/skill/llm-wiki/scripts/lint.sh project --strict
{
  "checked": 1,
  "errors": [],
  "scope": "structural only; agent must verify semantic accuracy, provenance and schema-specific requirements"
}
[exit 0]
```

`--all "uap-investigator"` 同样命中 alias `project` 的同一页。`query.sh project "agent-persona"` 与 `query.sh project "FRAMEWORK_ENTRY"` 亦命中该页。抛掷工程无 `.git`，`git diff --check` 不适用（`NO_GIT_REPO`）。

### 5. 新进程持久查询

```
$ bash -lc 'cd /tmp/uap-kb-reflux-verify/project && echo "PID:$$ SHELL:$0" && bash .agent-framework/skill/llm-wiki/scripts/query.sh project "uap-investigator"; echo "EXIT:$?"'
PID:8290 SHELL:bash
{
  "root": "/private/tmp/uap-kb-reflux-verify/project/knowledge/project",
  "results": [
    {
      "page": "wiki/sources/verifications/agent-persona-uap-loop.md",
      "matches": 26
    }
  ]
}
EXIT:0
```

同一项目、新进程仍找到同一模块 wiki 页。关闭「下次任务能查到」在本抛掷工程上的环。

## 未扩展的证明范围

下列各项**仍未证明**，不得写成已完成：

- **跨模型效果**：未跑。壳的 CI 不跑模型。
- **真实业务项目闭环**：未在业务工程上跑完整开发周期。抛掷目录的 `runtime=NOT_RUN`、`development=NEEDS_DESIGN_APPROVAL`。
- **人格正文自动成长**：本次只向抛掷工程 wiki 写入 EXTRACTED 验证页，未改人格正文、`FRAMEWORK_ENTRY`、hosts、doctor 词典、技能路由或 Qwen 模板。
- **提示词包同模型记录**：来源 `EVALUATION.md` 仍是栏目合规，不是效果验收。QBR 场景仍为 PARTIAL（主交付完成；明确要求的第二交付物「经营机制」未交付）。该记录不能外推到本工程壳。
- 未执行真实宿主安装到使用者项目、设备、生产部署或业务发布验收。
- CodeBuddy CLI 冒烟为 `NOT_RUN`（本机未安装）。未证明 CodeBuddy CLI 会话。
- 未证明 Claude 在真实对话中实际拉起 `uap-*`。
- 未证明人格覆盖已批准 TDD 路径。

知识回流已在上述抛掷工程授权摄入上 PASS；不得外推为分发库、生产或业务工程已自动成长。
