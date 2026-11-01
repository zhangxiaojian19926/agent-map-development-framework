# Delegated Execution Rules in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md) is the unmodified upstream method. This
> file states how that method applies inside this framework. **Where the two
> disagree, this file wins.**
>
> The upstream method runs a complete review loop inside the delegated task:
> a per-task reviewer judges spec compliance and code quality, and the
> implementer commits its own work. This framework already owns both of
> those decisions, so the upstream versions of them are replaced here rather
> than run in parallel.

## The review is the framework's, not the skill's

The framework's review contract is [`matt-pocock:code-review`](../../matt-pocock/code-review/SKILL.md):
two axes, specification compliance sourced from the current OpenSpec change,
and code quality, plus an integration axis for cross-module work.

- **Do not dispatch the upstream `task-reviewer-prompt.md`.** It is a second
  implementation of the same two axes, and two reviewers judging the same
  diff by two different rules is exactly the competing completion judgement
  this framework exists to prevent.
- **Review the delegated task with `matt-pocock:code-review`**, against the
  change's requirement and scenario IDs. The upstream "spec compliance" axis
  takes its source from the change, not from an issue tracker, and the
  upstream method assumes an issue tracker this framework does not have.
- The upstream fix loop, its five-round cap and its rulings ledger are kept
  as-is. They are about how a review round converges, not about what a review
  decides, so they do not compete with the framework's review method.
- A self-review by the implementer never replaces the review. Both are
  needed, in that order.

## The implementer does not commit

The framework's integration contract is: the implementer produces the change
and the evidence; the user chooses merge, pull request, or keep, and nothing
is committed, pushed, deployed or published without the authorisation for
that specific action.

- **The implementer does not commit.** It reports the files it changed, the
  tests it ran with their output, and the open findings. The controller
  decides what to commit, and only after the user has been offered the
  choices.
- A delegated task that needs a commit in the middle asks for it explicitly,
  with the same authorisation the framework asks for anywhere else.
- The upstream "implements, tests, commits, self-reviews" line is read as
  "implements, tests, reports, self-reviews".

## The controller keeps its context clean

The upstream method's core discipline holds and is worth keeping: the
controller reads summaries and diff packages, never the full diff of every
task, and never fixes a finding itself. Fixing findings in the controller
session both pollutes the context and skips the review.

- Pass the reviewer a diff package built from the recorded base, never
  `HEAD~1`, which silently truncates a multi-commit task.
- Rulings are recorded in the ledger and surfaced in the final report. A
  ruling that dies with the workspace was a decision made in secret.

## What stays upstream

The method's judgement about when delegation is appropriate: tasks that are
independent, each with a clear brief, a report file, and a review that can
judge the result. The per-task brief, the report file, the scoped re-review
and the final whole-branch review are all upstream text and all still apply.
