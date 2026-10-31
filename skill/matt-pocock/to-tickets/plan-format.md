# Plan Format and Task Rules (local adaptation)

> **Source of the material:** adapted from `obra/superpowers`
> `writing-plans` (MIT, copyright Jesse Vincent), pinned at
> `5bf4e78011075bcfc0dc295f0724994cd123ee71`. The upstream skill was retired
> when this group was introduced; see `THIRD_PARTY_NOTICES.md` for the
> distribution-level attribution.
>
> **Local additions by this framework:** the requirement that slices and their
> blocking edges live in the change's `tasks.md`, the required per-step
> fields, and the cross-module fields the public collaboration rules expect.

The craft layer — how to cut the work into tracer-bullet slices and how to
declare what blocks what — is in [SKILL.md](SKILL.md). This file is the layer
that fixes where the slices live and what each one must carry.

## Where the slices live (framework addition)

**The slices are the change's tasks.** Write them into the current OpenSpec
change's `tasks.md` and declare their blocking edges there. There is exactly
one task-state source, and it is the one the change is tracked by.

```
openspec/changes/<change>/tasks.md
  ## 1. <切片组名>
  - [ ] 1.1 <垂直切片：一个端到端的可演示行为>
        阻塞于：无
        覆盖：Req/SRC-01, SRC-02
        验收：<可观察的完成条件>
  - [ ] 1.2 <垂直切片>
        阻塞于：1.1
```

The detailed implementation plan — files, interfaces, code, test commands —
is a separate companion document. Store it where the project's plan
convention says and reference it from the change. It carries the detail the
tasks do not; it never carries a second copy of the task state.

## Required fields per slice

Each task entry must carry:

| Field | Meaning |
|---|---|
| **What it builds** | The end-to-end behaviour this slice makes work, from the user's perspective — not a layer-by-layer implementation list |
| **Blocked by** | Which other slices must complete first; `None` means it can start immediately |
| **Covers** | The Requirement and Scenario identifiers this slice implements |
| **Acceptance** | The observable conditions that mean it is done |
| **Module and files** | Target module and the files it creates or modifies |
| **Interfaces** | What it consumes from earlier slices and what later slices rely on |
| **Test** | The minimal test and its expected result |

A slice's implementer may only read their own slice. The **Interfaces**
block is how they learn the names and types the neighbouring slices use, and
the **Blocked by** line is how they know what must exist first.

## Task right-sizing

A slice is the smallest unit that carries its own test cycle and is worth a
reviewer's gate. When drawing slice boundaries:

- Fold setup, configuration, scaffolding and documentation into the slice
  whose deliverable needs them.
- Split only where a reviewer could meaningfully reject one slice while
  approving its neighbour.
- Each slice ends with an independently verifiable deliverable.

## Bite-sized steps inside a slice

A slice is vertical, but its steps are small:

- Write the failing test
- Run the test to verify it fails
- Write the minimal implementation
- Run the test to verify it passes
- Commit

Each step is one action. A step that says "implement the parser" is not a
step; a step that shows the code is.

## File structure before slices

Before defining slices, map out which files will be created or modified and
what each one is responsible for. This is where decomposition decisions get
locked in.

- Design units with clear boundaries and well-defined interfaces; each file
  has one clear responsibility.
- Files that change together live together. Split by responsibility, not by
  technical layer.
- In existing codebases, follow established patterns. Do not restructure
  large files unilaterally, but if a file you must edit has grown unwieldy,
  splitting it inside the plan is reasonable.

## Scope check

If the spec covers multiple independent subsystems, it should have been
broken into sub-projects during design. If it was not, say so and propose
one plan per subsystem — each producing working, testable software on its
own.

## Cross-module fields

The public collaboration rules require these for work that crosses module
boundaries. Put them on the slice that owns the crossing:

| Field | Requirement |
|---|---|
| **Dependency order** | Which slices must finish before this one starts |
| **Interface responsibility** | Which module owns the contract and which consumes it |
| **Parallel boundary** | Which slices can run at the same time and which share a file |
| **Integration acceptance** | The Scenario that proves the modules work together |
| **Recovery** | What happens if the integration fails part way |

One file has one writing owner. A slice that touches another's files states
the dependency instead.

## Plan document header

The companion plan document starts with:

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Spec:** [path to the change this plan implements]

**Slices:** [path to the change's tasks.md, where the slices and their
blocking edges live]

## Global Constraints

[The change's project-wide requirements — version floors, dependency limits,
naming rules, platform requirements — one line each, with exact values
copied verbatim. Every slice's requirements implicitly include this section.]
```

## No placeholders

Every step must contain the actual content an implementer needs. These are
plan failures — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without the actual test code)
- "Similar to slice N" — repeat it; the implementer may read slices out of order
- Steps that describe what to do without showing how
- References to types, functions or methods no slice defines

## Self-review

After writing the plan, look at it with fresh eyes:

1. **Spec coverage** — skim each requirement and scenario in the change. Can
   you point to a slice that implements it? List the gaps.
2. **Placeholder scan** — search for the red flags above. Fix them.
3. **Type consistency** — do the names and signatures used by later slices
   match the ones earlier slices define? A `clearLayers()` in one slice and
   `clearFullLayers()` in another is a bug.
4. **Blocking-edge check** — does every edge point at a slice that actually
   gates it, and is every slice with no blocker actually startable?

Fix issues inline; no need to re-review. If a requirement has no slice, add
the slice.

## Execution handoff

After the plan is approved, offer the execution choice:

**1. Subagent-driven (recommended)** — dispatch a fresh subagent per slice,
review between slices, fast iteration.

**2. Inline execution** — execute slices in this session in batches with
checkpoints for review.

Either way, the slice state is updated in the change's `tasks.md`, never in
the plan document.

## Further reading in this group

- [SKILL.md](SKILL.md) — tracer-bullet slices, blocking edges, expand-contract, the breakdown review
- [plan-document-reviewer-prompt.md](plan-document-reviewer-prompt.md) — template for an independent plan review
