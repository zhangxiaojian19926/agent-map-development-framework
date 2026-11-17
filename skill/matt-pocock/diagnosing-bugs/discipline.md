# Debugging Discipline (local adaptation)

> **Source of the compliance material:** adapted from `obra/superpowers`
> `systematic-debugging` (MIT, copyright Jesse Vincent), pinned at
> `5bf4e78011075bcfc0dc295f0724994cd123ee71`. The upstream skill was retired
> when this group was introduced; see `THIRD_PARTY_NOTICES.md` for the
> distribution-level attribution.
>
> **Local additions by this framework:** the environment-failure rule, the
> evidence-binding rule, and the framework's own rules about symptom fixes.
>
> The craft layer — how to build a feedback loop, rank hypotheses, instrument
> and clean up — lives in [SKILL.md](SKILL.md). This file is the layer that
> holds you to it.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you have not completed Phase 1, you cannot propose fixes.

Symptom fixes are failures. A fix that makes the error message go away
without explaining why the error happened is not a fix; it is a delay.

## Environment failures are not red signals (framework addition)

A missing compiler, an unreachable device, a broken network or a dead runner
is **INFRA_ERROR**, not a failing test. It never counts as a red signal,
and it never counts as a green verification. A genuine red signal does not
license this skill to write production code.

```
Environment is broken      → INFRA_ERROR, fix the environment, re-run
Environment works, behavior missing → genuine RED. 本技能不写生产代码。
查完根因后不先写测试再修复。回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做。
```

Do not dress an environment failure up as a red signal, and do not report an
environment failure as a passing verification. Both are lies about what was
proven.

## Evidence must bind to the tree you are changing (framework addition)

A diagnosis is only worth as much as the tree it was observed in. Bind every
conclusion to the actual worktree or commit:

- which revision was inspected
- the exact command that produced the signal
- what the output showed, with secrets redacted

A root cause found on an older revision, or a signal from a different
environment, is a hypothesis — not a finding. Re-verify before acting on it.

## When three fixes fail, question the architecture

Each failed fix reveals a new shared state, a new coupling, or a new symptom
elsewhere. That is not bad luck; it is the shape of the problem.

```
STOP after the third failed attempt.
Do not start fix #4.

Each fix reveals new shared state / coupling / problem in a different place
Fixes require massive refactoring
Each fix creates new symptoms elsewhere

→ The pattern is the finding. Question the fundamentals:
  is this pattern sound, or are we continuing out of inertia?
```

Discuss it with your human partner before attempting another fix. Three
attempts that fail the same way is an architectural signal, not a debugging
technique.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Issue is simple, don't need process" | Simple issues still have root causes. The process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | 查完根因后不先写测试再修复。回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做。 |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees mistakes. Read it completely. |
| "The code is the issue, let me just fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Red flags — STOP and return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see what happens"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably this, let me just change it"
- "I don't fully understand but let's try"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

## Signals you are doing it wrong

Watch for these redirections from your human partner:

| Signal | What it means |
|---|---|
| "That's not happening" | You assumed without verifying. |
| "Will it show us...?" | You should have added evidence gathering. |
| "Stop guessing" | You are proposing fixes without understanding. |
| "Ultra-think this" | Question fundamentals, not just symptoms. |
| "We're stuck?" | You should have asked for help. |

**When you see these: STOP. Return to Phase 1.**

## When there genuinely is no root cause

If the investigation shows the issue is environmental, timing-dependent, or
external:

1. You have completed the process
2. Document what you investigated
3. 本技能不写生产代码。
4. Do not add monitoring or logging here. 回归测试和修复只在活动路由把 tdd 写成下一项时由 tdd 做。

**But:** the large majority of "no root cause" cases are incomplete
investigation. Say so explicitly before accepting that conclusion.

## Attribution: which layer this failure belongs to (framework addition)

A fix that works is not the end of the investigation. Before the loop closes,
name the layer this failure belongs to. Without that, the same class of
failure returns with a different symptom, and the fix accumulates as reminders
instead of as knowledge — and the same reminder cannot fix a problem of a
different kind.

| Layer | What the failure looks like | What to change | Where it lands |
|---|---|---|---|
| Content | A concept is missing, or two things that share a name were treated as one concept | Add the concept, or split the concepts that were merged | A `concept` page carrying the conditions it holds under |
| Access | The concept was already right, but retrieval returned a similar case whose conditions did not match | The index and the applicability filter | The fields a query filters on |
| Verification | Retrieval and interpretation were both right, but a data-side check was skipped | The workflow and the verification tool | The assertion or the check before the action |
| Flow | The failure was not a knowledge problem at all — the sequence, the authorization or the gate was wrong | The flow contract | `development-workflow.md` |
| Method | Many failures of the same kind each missing the same thing — the extraction itself is systematically incomplete | The extraction method | Needs cross-task validation before it counts |

Two records, not one. **Which knowledge base the record belongs to** is the
module routing decision; **which layer the failure belongs to** is this
attribution. Record both — they do not substitute for each other.

The layer decides what you write down next:

- Content becomes a `concept` page or a revised applicability condition.
- Access becomes a change to the fields a query filters on.
- Verification becomes an assertion, or a check before the action.
- Flow becomes a change to the flow contract.
- Method becomes a change to the extraction method — and that one needs
  cross-task validation before it counts as an improvement. Allowing the
  method to improve and allowing the standard that scores it to be lowered are
  two different permissions.

## Redaction

Commands, outputs and captured artifacts carry secrets. Write `<REDACTED>`
in place of every credential before showing or storing anything. Build loops
against environment variables so the credential stays in the environment
rather than in what you display. Captured artifacts carry auth headers: quote
only the lines that carry the signal.

If redacted output is not enough to diagnose the bug, say so and ask the
user for the missing artifact rather than guessing.

## Further reading in this group

- [SKILL.md](SKILL.md) — the feedback loop, hypotheses, instrumentation, and cleanup phases
- [root-cause-tracing.md](root-cause-tracing.md) — tracing a bad value back to its origin
- [defense-in-depth.md](defense-in-depth.md) — validating at several layers after the root cause is known
- [condition-based-waiting.md](condition-based-waiting.md) — replacing fixed timeouts with condition polling
- [scripts/hitl-loop.template.sh](scripts/hitl-loop.template.sh) — a structured loop for the cases only a human can drive
- [CREATION-LOG.md](CREATION-LOG.md) — upstream's account of how the original skill was extracted
