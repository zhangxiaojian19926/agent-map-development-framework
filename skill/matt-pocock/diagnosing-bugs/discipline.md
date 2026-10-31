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
is **INFRA_ERROR**, not a failing test. It never counts as the red that
licenses writing production code, and it never counts as a green verification.

```
Environment is broken      → INFRA_ERROR, fix the environment, re-run
Environment works, behavior missing → genuine RED, now write code
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
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves the fix. |
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
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring or logging for future investigation

**But:** the large majority of "no root cause" cases are incomplete
investigation. Say so explicitly before accepting that conclusion.

## Redaction

Commands, outputs and captured artifacts carry secrets. Write `<REDACTED>`
in place of every credential before showing or storing anything. Build loops
against environment variables so the credential stays in the environment
rather than in what you display. Captured artifacts carry auth headers: quote
only the lines that carry the signal.

If redacted output is not enough to diagnose the bug, say so and ask the
user for the missing artifact rather than guessing.

## Further reading in this group

- [SKILL.md](SKILL.md) — the feedback loop, hypotheses, instrumentation, fix and cleanup phases
- [root-cause-tracing.md](root-cause-tracing.md) — tracing a bad value back to its origin
- [defense-in-depth.md](defense-in-depth.md) — validating at several layers after the root cause is known
- [condition-based-waiting.md](condition-based-waiting.md) — replacing fixed timeouts with condition polling
- [scripts/hitl-loop.template.sh](scripts/hitl-loop.template.sh) — a structured loop for the cases only a human can drive
- [CREATION-LOG.md](CREATION-LOG.md) — upstream's account of how the original skill was extracted
