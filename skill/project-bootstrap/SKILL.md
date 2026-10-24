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
| Only a new requirement | Prepare without Git/branch; write a safe public design draft and dossier. Until the user's actual design approval, handoff is NEEDS_DESIGN_APPROVAL and initialization PARTIAL; legacy new retains its three approval checks |
| Existing local engineering project | Read existing rules, preview prepare in place, preserve human AGENTS and source; no clone or source moves |
| New downloaded module | `module add --target PATH --id ID --path REL`; confirm identity, not a guessed role |
| Ordinary clone or changed source | `module sync --target PATH --yes --allow write` updates observations; `refresh` runs separately authorized analysis/indexing |
| Any current coding agent | Do not launch Codex or another agent CLI. With sources: `refresh --index --allow write --allow index --allow index-install`, then `map` until the first map is published, then accept-docs and doctor. Later, publish `map` only when module boundaries or cross-module relationships change |
| CodeGraph missing | `index-install` installs the locked CLI under `$TARGET/.framework/tools/codegraph`. No global npm and no `codegraph install`. Existing trees use `init`; later edits use `sync` after the managed allowlist is updated. Index READY does not publish the relationship map |
| Partial download or changed input | Read private launch state, revalidate current permissions and identity, resume successful modules without re-clone; preserve conflicting directories |

`--yes` is not permission. Current authorization determines write/clone/agent/index/index-install/hooks/openspec grants. Downloaded approved fields grant none. Existing authorization is not re-asked at every stage. Missing authentication or tool capability is reported specifically; do not install globally or execute downloaded code. Pure chat hosts report CAPABILITY_MISSING. Private startup snapshots stay outside project and distribution.

## Map contract

Actual relationships contain `id`, `from`, `to`, `kind`, `interface`, `provenance`, `runtime_validation`, `evidence`. Kinds: contains/build-dependency/runtime-call/data-exchange. Static analysis always uses runtime_validation=NOT_RUN. Evidence contains workspace-relative `path`, exact `anchor`, SHA256 `sha256`; STATIC_SUPPORTED requires both endpoints. Same names alone do not create edges. Record uncertainty rather than fabricate a connection.

The generator checks source/catalog/framework bindings before publishing observations. Never truncate a large project to the first packet: coverage must include every declared batch; out-of-scope files remain an explicit limitation. Resume accepted summaries without reanalysis only for the same binding. Approved design stays separate; a difference is SPEC_MISMATCH, not permission to rewrite the design.

## Complete documentation, not routing stubs

Generate the dossier yourself using the linked protocol. Project docs describe goal, architecture, interface owners and integration order; module docs contain all local roles, boundaries, inputs/outputs, dependencies, command prerequisites and evidence. A map summary is not a complete module AGENTS. Commands remain NOT_RUN. After initialization the project KB shell is SCAFFOLDED and its ingestion is EMPTY; write NOT_CONFIGURED only when the alias registry is absent. Do not initialize `knowledge/project/` again. Preserve human text; report managed-block edits and semantic conflicts instead of overwriting. Read-only modules receive complete project-side documentation. Public skills/policy remain public, not copied into each module.

## Handoff

Run doctor after documentation acceptance. Report full initialization only when initialization=COMPLETE; PREPARED, a STATIC_SUPPORTED map or exit 0 is insufficient. Do not trade coverage/documentation for a deadline. New requirements with no design decision stop at a resumable NEEDS_DESIGN_APPROVAL draft, not a claimed completion. The agent computes design hashes only for genuinely approved content, never treats a file as approval.

On “continue”, read persisted handoff and fresh OpenSpec apply context plus the approved plan; ask only for a missing decision. New/missing/moved modules or changed source/docs invalidate previous completion: update observations and dossier without deleting historical or human files. If this task changes module boundaries or cross-module relationships, run `map` once before treating the map as current. Internal edits leave the map in place. Continue feature work through TDD, review and actual tests. Ask whether the solved problem should be ingested into the relevant module KB; without explicit content/target authorization, leave KB unchanged.
