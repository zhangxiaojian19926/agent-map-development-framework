---
name: llm-wiki
description: Use when querying a project knowledge base, explicitly creating or registering one, or ingesting, synthesizing, reviewing or removing knowledge with user authorization.
license: MIT
---

# Project-scoped llm-wiki

Public-framework adaptation of the locally declared MIT llm-wiki skill. Attribution and changes: [notices](../../THIRD_PARTY_NOTICES.md).
Read [knowledge policy](../../docs/framework/knowledge-policy.md) before writes. This skill is an Agent workflow; helpers do not call an LLM or complete semantic ingestion.

## Entry and routing

1. Identify the task's modules and explicitly associated KB aliases. Read project resources and selected KB AGENTS/purpose/schema before writes.
2. Use project-local llm-wiki-aliases.json; aliases are paths relative to its project root. Never use a global registry or infer association from the current directory.
3. Explicit alias is authoritative: unknown alias fails, never falls back to current KB. Explicit paths must be verified against the authorized target; '.' means deliberately select current KB.
4. Git boundaries stop automatic upward discovery. For non-Git projects use framework-project.json, or explicitly set FRAMEWORK_PROJECT_ROOT to a confirmed root containing the current directory.
5. No KB/registry: query --all returns NOT_CONFIGURED. Continue allowed research/planning, disclose missing history; do not initialize or register automatically.
6. KB-first at task entry and SPEC/APPLY/VERIFY; reuse within the stage unless scope/evidence changes.

## Commands

Run through Bash; script paths below are relative to this skill's directory. Python 3.9+ is required.

| Workflow | Command | Actual behavior |
|---|---|---|
| init | bash scripts/init.sh PATH TOPIC zh-or-en | Creates empty KB only; requires confirmation, refuses nonempty targets; does not register |
| register | bash scripts/common.sh add-alias NAME PATH | Separately authorized project registration; rejects conflicting alias |
| query | bash scripts/query.sh KB TOPIC | Read-only literal keyword search |
| query all | bash scripts/query.sh --all TOPIC | All project aliases; invalid mappings reported, partial failure nonzero |
| ingest | bash scripts/ingest.sh KB SOURCE_FILE | Prepares immutable raw copy, returns PREPARED and pending work; never claims ingestion complete |
| batch | bash scripts/batch-ingest.sh KB SOURCE_DIR | Snapshots Markdown input list; reports each preparation failure; nonzero on partial failure |
| digest | bash scripts/digest.sh KB TOPIC | PLAN_ONLY, relevant pages for Agent synthesis |
| status | bash scripts/status.sh KB | Read-only metadata and page count |
| lint | bash scripts/lint.sh KB --strict | Structural metadata and unique wikilink checks, including registered cross-KB links; not semantic proof |
| graph | bash scripts/graph.sh KB | Read-only JSON nodes/edges on stdout; no generated file |
| delete | bash scripts/delete.sh KB RAW_RELATIVE_PATH | PLAN_ONLY, exact target and references; never deletes or guesses a summary |
| crystallize | bash scripts/crystallize.sh KB FILE-or-stdin-dash TOPIC | PLAN_ONLY with INFERRED classification; Agent reads source and performs authorized synthesis |

Write helpers (init/register/ingest/batch) require WIKI_WRITE_CONFIRM=yes for each command, only AFTER current user authorization. This is accident prevention, not authentication. Never set it globally.
Source data may be sensitive: read only what is needed, de-identify before preparing raw. No secrets, personal identifiers or private full logs.
No persistent acknowledgement file bypasses future consent. A successful helper exit is not a completed knowledge workflow.

## Complete ingestion (Agent responsibility)

1. Confirm this content and ALL target KBs. An existing explicit authorization can cover preparation, pages, indexes and logs; new targets need confirmation.
2. Read actual source, not just a title. Preserve necessary raw evidence and traceable references.
3. Produce substantive source summary and applicable entities/topics/comparisons/synthesis according to schema; mark extracted facts EXTRACTED and reasoning INFERRED, with limitations.
4. Update index/log, verify references and source coverage, run structural checks, inspect actual diff in each owning Git repository.
5. Report verified content versus pending/failed items per KB. Raw copy or prompt generation is PREPARED, not completed ingestion.

For digest/crystallize, use the same source/authorization/verification process. For delete, first present the exact plan, obtain authority for affected records, use recoverable removal, repair references/index/log and validate. Do not blindly delete pages by similar names.
For a shared problem, root-cause KB gets the full record, other KBs get only independent lessons with a common problem ID. No duplicated full records or automatic integration KB.
Ask once at problem closure; refusal/defer/no response means no write and does not block the completed fix.
