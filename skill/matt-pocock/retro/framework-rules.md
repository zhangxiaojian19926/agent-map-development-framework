# Running a Retro in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md) is the unmodified upstream method. This
> file points it at the places where this framework actually keeps its
> standards, checks and evidence. **Where the two disagree, this file wins.**
>
> This is the first user-invoked skill in the distribution: it carries both
> `disable-model-invocation: true` for Claude and
> `policy.allow_implicit_invocation: false` for Codex, so the agent does not
> volunteer a retrospective on its own.

## What counts as the session's primary sources

The upstream method reads the session's primary sources, which may mean
searching session logs on the machine. In this framework the evidence of
record is:

| Source | What it answers |
|---|---|
| `git log` on the affected range | What actually changed, and when |
| The GitHub Actions runs for that range | Whether the checks ran, and whether they were green |
| The change's `tasks.md` and its archived copy | What was claimed, and what was checked off |
| `docs/maintainer/legacy-change-status.md` | What was deliberately left unfinished, and why |
| The session's own transcript | Where time was lost, what was looked up, what was guessed |

**A red CI run is a finding about the local verification sequence, not
automatically about the change.** When a check catches something locally but
only on CI, the missing piece is usually the local sequence, not the check.

## Where this framework's standards live

There is no `CODING_STANDARDS.md` here. The equivalent is the public rule set
plus the workflow contract:

| Path | What it governs |
|---|---|
| `AGENTS.md` | The entry point and the stage routing table. Read during implementation for routing |
| `docs/framework/skill-policy.md` | How skills are chosen, what they may and may not claim |
| `docs/framework/development-workflow.md` | The stage contract: entry conditions, steps, exit conditions |
| `docs/framework/collaboration-policy.md` | Module responsibilities, interfaces, handoff, integration |
| `docs/framework/knowledge-policy.md` | Knowledge routing, ingestion, confirmation |
| `docs/maintainer/verification.md` | The maintainer's gate sequence and what each check covers |
| `docs/maintainer/repository-layout.md` | Directory ownership and what may be moved or overwritten |

Judgement calls — cross-file consistency, "matches the surrounding style",
anything no mechanical check could substitute for — live in these documents,
not in a separate standards file. Propose adding a rule by naming the
document it belongs in, not by inventing a new file.

## The repo's own checks

Read these before proposing a new check. A check that already exists but sits
unwired is the finding; a new check is the last resort.

```bash
python3 tools/check-framework        # distribution: fingerprints, links, syntax, skill count
python3 tools/pre-commit-check       # the full maintainer sequence, in order
openspec validate --all --strict --no-interactive   # spec and archive integrity
python3 -m unittest discover -s tests -q            # behaviour
git diff --check <base> HEAD         # whitespace in the committed range
```

The guardrails are `validate.yml` (on every push and pull request) and
`release.yml` (before a release is tagged). Both run the distribution check
and the tests; the release also runs the spec validation.

## Where the mechanical / judgement line falls

- **Mechanical** — file placement, manifest fingerprints, skill counts, link
  resolution, whitespace, spec structure, archive task completion. These
  belong in a check. `tools/check-framework` already covers the first group;
  the OpenSpec CLI covers the last.
- **Judgement** — whether a change is the right decomposition, whether an
  interface is the right shape, whether a requirement is faithfully met,
  whether a doc says what the code does. These belong in the review stage,
  and `matt-pocock:code-review` is where they are judged.

Default to building the check over writing the rule, as the upstream method
says. In this framework, adding to `tools/check-framework` is usually
cheaper than adding to a workflow, and it also protects target projects.

## The most expensive context consumer in this framework

`AGENTS.md` is pushed into the context of every agent working here, and it
carries a stage routing table plus pointers. Keep it to routing and
pointers. Detail belongs in `docs/framework/`, and reference material belongs
in a skill — a skill's description is the cheapest place to make something
discoverable.

Two known consumers worth naming during a retro:

- `using-superpowers` opens with an instruction that triggers on every
  conversation. It costs permanent context and competes for the agent's
  attention at the moment a task-scoped skill would be more useful.
- The stage routing table in `AGENTS.md` names a skill per stage. When a
  stage's method comes from a group with several skills, the table should
  name the roles, not enumerate every entry point.

## How to present the findings

Order by severity, as the upstream method says. For each candidate give:

1. **Category** — navigation, automated check, standards, steering file,
   tool economy, no-op instruction, or information access
2. **Evidence** — the specific thing in the session that shows the problem
3. **Proposed action** — one concrete change, naming the file it lands in
4. **What it costs** — and whether it can be done now or needs a decision

A candidate that cannot be tied to evidence in the session is a guess. Drop
it rather than filing it.

## Further reading in this group

- [SKILL.md](SKILL.md) — the upstream method and its categories
- [../../../docs/maintainer/retro-findings.md](../../../docs/maintainer/retro-findings.md) — this repository's retro records
