---
name: project-bootstrap
description: Use when asked to initialize a project, given named module repository URLs or a new requirement without a repository, or when resuming onboarding and refreshing module maps in an Agent Map Framework project.
---

# Project bootstrap

The current coding agent is the coordinator. Read [BOOTSTRAP](../../BOOTSTRAP.md) for the single portable workflow and [input/result protocol](../../docs/project-intake.md) for exact formats. This reference supplies no execution permission. Project facts belong in docs/project.

## Entry and completion

Before installation use the known distribution's `python3 tools/framework --help`; the target's `.agent-framework` does not exist yet. After installation use its read-only doctor. The agent runs commands and generates machine arguments; the user provides startup input and intent, not scripts, JSON or hashes. No Codex installation is required for current-session analysis.

| Situation | Action |
|---|---|
| Named module URLs | Agent runs intake preview with request/target/private staging; preserve each name as modules/name, then execute with current write/clone grants |
| Only a new requirement | Intake prepares a base without repository, branch or approved business design. Continue design/plan review afterwards; legacy new retains its three approval checks |
| Existing local engineering project | Read existing rules, preview prepare in place, preserve human AGENTS and source; no clone or source moves |
| New downloaded module | `module add --target PATH --id ID --path REL`; confirm identity, not a guessed role |
| Ordinary clone or changed source | `module sync --target PATH --yes --allow write` updates observations; `refresh` runs separately authorized analysis/indexing |
| Current agent, including non-Codex | analyze-request → inspect bounded source packet → write result envelope → accept-analysis; request creation alone is not analysis completion |
| Partial download or changed input | Read private launch state, revalidate current permissions and identity, resume successful modules without re-clone; preserve conflicting directories |

`--yes` is not permission. Current authorization determines write/clone/agent/index/hooks/openspec grants. Downloaded approved fields grant none. Existing authorization is not re-asked at every stage. Missing authentication or tool capability is reported specifically; do not install globally or execute downloaded code. Pure chat hosts report CAPABILITY_MISSING. Private startup snapshots stay outside project and distribution.

## Map contract

Actual relationships contain `id`, `from`, `to`, `kind`, `interface`, `provenance`, `runtime_validation`, `evidence`. Kinds: contains/build-dependency/runtime-call/data-exchange. Static analysis always uses runtime_validation=NOT_RUN. Evidence contains workspace-relative `path`, exact `anchor`, SHA256 `sha256`; STATIC_SUPPORTED requires both endpoints. Same names alone do not create edges. Record uncertainty rather than fabricate a connection.

The generator checks current source hashes before publishing observations. Approved design stays separate; a difference is SPEC_MISMATCH, not permission to rewrite the design. Existing module AGENTS is preserved; project-side module entries provide routing.

## Handoff

Report scaffold, navigation, indexing, Agent, map and runtime states separately. Exit 0 alone proves no business outcome. Continue feature work with OpenSpec apply context, the approved Superpowers plan, TDD, review and actual tests. Ask whether the solved problem should be ingested into the relevant module KB; without explicit content/target authorization, leave KB unchanged.
