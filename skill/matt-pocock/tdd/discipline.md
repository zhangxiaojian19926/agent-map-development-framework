# TDD Discipline (local adaptation)

> **Source of the compliance material:** adapted from `obra/superpowers`
> `test-driven-development` (MIT, copyright Jesse Vincent), pinned at
> `5bf4e78011075bcfc0dc295f0724994cd123ee71`. The upstream skill was retired
> when this group was introduced; see `THIRD_PARTY_NOTICES.md` for the
> distribution-level attribution.
>
> **Local additions by this framework:** the seam confirmation rule, the
> refactor attribution rule, and the seam-bound checks in the completion table.
>
> The craft layer — where to test, what makes a test good, how to advance —
> lives in [SKILL.md](SKILL.md). This file is the layer that holds you to it.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Seam confirmation (framework addition)

Before writing any test, name the seam you are testing at and confirm it:

```
Which public interface does this test cross?
What does this seam catch, and what does it miss?
Does the seam match the module's interface contract?
```

**No test is written at an unconfirmed seam.** A seam that contradicts the
module's published interface is a design problem, not a testing problem: stop
and route it back to design rather than quietly testing around the boundary.

The seam comes from the module's interface contract (see the public
collaboration rules), not from wherever the code happens to be reachable
from. Test the interface; do not reach inside to find a convenient entry
point.

## The loop

```
RED      write one failing test at a confirmed seam
VERIFY  watch it fail, and confirm it failed for the right reason
GREEN   the smallest implementation that passes it
REPEAT  one slice at a time
```

**Red before green.** Write the failing test first, then only enough code
to pass it. Do not anticipate future tests or add speculative features.

**One slice at a time.** One seam, one test, one minimal implementation per
cycle. Writing all the tests first and then all the implementation tests
imagined behavior, not real behavior.

**Verify red.** A test that passes immediately is testing existing behavior;
fix the test. A test that errors has a broken setup; fix the error and re-run
until it fails correctly.

**Verify green.** The test passes, the other tests still pass, and the output
is clean. If the test fails, fix the code, not the test.

## Where refactoring belongs (framework addition)

The implementation stage has a cleanup step, and its scope is deliberately
narrow:

- **In scope here:** duplication inside the current task, unclear names, and
  helpers worth extracting. Keep the tests green. Do not change the public
  interface while doing it.
- **Out of scope here:** design-level restructuring — moving a seam, changing
  a module's responsibilities, or reshaping an interface. Those belong in the
  review stage, where they are discussed and decided, and may need their own
  change.

`SKILL.md` says refactoring is not part of the red-to-green loop and belongs
to review. Both are true here: the cleanup that keeps the current task
readable happens with the implementation; the restructuring that changes what
the module is happens at review.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests written after pass immediately — which proves nothing. They may test the wrong thing, test the implementation instead of the behavior, or miss the edge case you forgot. You never watched it fail, so you never proved it can catch the bug. |
| "Already manually tested it" | Manual testing is ad-hoc: no record of what you covered, no way to re-run it when the code changes, easy to forget cases under pressure. Automated tests run the same way every time. |
| "Deleting X hours is wasteful" | Sunk cost fallacy — that time is already spent either way. The real choice: rewrite with TDD (high confidence) vs. keep it and bolt tests on after (low confidence, likely bugs). Keeping code you can't trust is the waste. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away the exploration, start with TDD. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD IS the pragmatic path: catches bugs before commit, prevents regressions, lets you refactor without fear. "Pragmatic" shortcuts mean debugging in production — slower and costlier. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |
| "The seam is awkward to reach" | That's a design signal. Route it back to design; don't test around the boundary. |

## Red flags — STOP and go back

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why the test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"
- "TDD is dogmatic, I'm being pragmatic"
- "This is different because..."
- A test written at an unconfirmed seam

**All of these mean: delete the code, start over.**

## Completion checklist

Before marking a task verified:

- [ ] The seam was named and confirmed before the test was written
- [ ] The seam matches the module's interface contract
- [ ] Every new function or method has a test
- [ ] You watched each test fail before implementing
- [ ] Each test failed for the expected reason (feature missing, not a typo)
- [ ] You wrote the minimal code to pass each test
- [ ] All tests pass
- [ ] Output is clean — no errors, no warnings
- [ ] The expected values come from an independent source, not from the code under test
- [ ] Edge cases and error paths are covered

Can't check all boxes? You skipped TDD. Start over.

## When stuck

| Problem | Solution |
|---|---|
| Don't know how to test | Write the wished-for API. Write the assertion first. Ask your human partner. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify the design. |

## Further reading in this group

- [SKILL.md](SKILL.md) — where to test, what makes a test good, how to advance
- [test-quality.md](test-quality.md) — naming the break a test catches, testing the real thing, the mutation check
- [tests.md](tests.md) — good and bad test examples
- [mocking.md](mocking.md) — where mocking is allowed
