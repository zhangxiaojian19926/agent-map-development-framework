---
name: project-bootstrap
description: Use when onboarding an existing codebase, starting an approved new project, registering modules, or refreshing stale module maps in an Agent Map Framework project.
---

# Project bootstrap

This is a reference for the framework CLI, not a grant to run it. The public root AGENTS defines the development stages; project facts belong in docs/project.

## Entry and completion

Run `python3 .agent-framework/tools/framework doctor --target .` at task entry and completion. It is read-only. Use `python3 tools/framework --help` from the distribution for supported arguments. Never run a downloaded business script to discover modules.

| Situation | Action |
|---|---|
| Existing engineering project | Preview `init --target PATH --project-id ID --agent codex --dry-run`; inspect conflicts, then obtain the displayed capability grants |
| Only a new requirement | Clarify requirements, design and implementation plan using the root workflow; `new` needs current artifact hashes confirmed with `--approve requirements=SHA256`, `--approve design=SHA256`, `--approve plan=SHA256` |
| New downloaded module | `module add --target PATH --id ID --path REL`; confirm identity, not a guessed role |
| Ordinary clone or changed source | `module sync --target PATH --yes --allow write` updates observations; `refresh` runs separately authorized analysis/indexing |
| Manual Agent or failed authentication | Report WAITING_AGENT, not READY; retain deterministic scaffold and recovery instructions |

`--yes` confirms the listed action; explicit `--allow write`, `--allow agent`, `--allow index`, `--allow hooks`, `--allow openspec`, `--allow clone` grant separate capabilities. Downloaded `approved:true` grants none. Source analysis uses a bounded source packet; it does not run module code. Review the packet scope before permitting model transmission.

## Map contract

Actual relationships contain `id`, `from`, `to`, `kind`, `interface`, `provenance`, `runtime_validation`, `evidence`. Kinds: contains/build-dependency/runtime-call/data-exchange. Static analysis always uses runtime_validation=NOT_RUN. Evidence contains workspace-relative `path`, exact `anchor`, SHA256 `sha256`; STATIC_SUPPORTED requires both endpoints. Same names alone do not create edges. Record uncertainty rather than fabricate a connection.

The generator checks current source hashes before publishing observations. Approved design stays separate; a difference is SPEC_MISMATCH, not permission to rewrite the design. Existing module AGENTS is preserved; project-side module entries provide routing.

## Handoff

Report scaffold, navigation, indexing, Agent, map and runtime states separately. Exit 0 alone proves no business outcome. Continue feature work with OpenSpec apply context, the approved Superpowers plan, TDD, review and actual tests. Ask whether the solved problem should be ingested into the relevant module KB; without explicit content/target authorization, leave KB unchanged.
