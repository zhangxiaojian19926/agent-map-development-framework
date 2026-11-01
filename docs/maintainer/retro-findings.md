# Retro Findings

Records of retrospectives run on this repository with the
`matt-pocock:retro` skill. Each entry is dated, lists the candidates with
the evidence that produced them, and marks what was done, what is scheduled,
and what is still a decision.

Candidates without evidence from the session are dropped rather than filed.

---

## 2026-10-31 — Skill import and CI gate work

**Scope**: the three skill replacements (`tdd`, `diagnosing-bugs`, `to-tickets`),
the CI gate upgrade, and the spec-store backfill. This was the session that
produced two self-inflicted CI failures, so most candidates come from the
mechanics of the work rather than from the content of it.

### Automated checks

**Local verification sequence did not match CI — CI caught it twice.**
Evidence: run #35 failed on the whitespace check for a trailing blank line
that a pre-commit `git diff --check` had not caught, because the pre-commit
run inspected the working tree while CI inspects the committed range. Run #36
then failed on a stale manifest fingerprint, because the file was edited
after `tools/update-manifest` had last run.
Action: **done.** `tools/pre-commit-check` runs the fixed sequence — refresh
the manifest, distribution check, tests, staged whitespace — and its
`--committed` mode re-checks the range CI will inspect. It is documented in
`docs/maintainer/verification.md`.

**Nothing flags a change whose tasks are all complete but which was never
archived.**
Evidence: auditing eight active changes against the spec store found six at
100% task completion with no capability spec in `openspec/specs/`, and the
spec store therefore understated the shell's actual capability set. No
existing check noticed: `openspec validate --all` validates spec structure,
not whether a finished change was archived.
Action: **open.** A check that reports active changes with every task
checked would have surfaced this in days rather than weeks. It belongs in
`tools/check-framework` or a separate read-only command; it is not a
spec-format change.

### Navigation

**The `superpowers:` skill prefix did not match the `super-powers/`
directory.**
Evidence: a search for the retired `test-driven-development` skill by
directory name and by invocation prefix returned different things, and the
prefix was mistaken for a broken path reference before the framework's own
convention was found in `AGENTS.md`.
Action: **done.** The group was renamed to `skill/superpowers/`, so the
directory now matches the invocation prefix. The `openspec/` group already
matched its prefix.

**The plan location still carries a retired skill's namespace.**
Evidence: `docs/superpowers/plans/` remained the stated plan convention after
the plan skill moved to another group, and the directory no longer existed
in the tree.
Action: **done.** The convention is now `docs/plans/`, the leftover empty
directory was removed, and the runtime payload excludes the new location so
plan documents still never reach a target project.

### Tool economy

**Pushing from a non-interactive shell is blocked by the keychain.**
Evidence: three consecutive `git push` attempts hung inside
`git-remote-https` with no output. The credential lives in a keychain
internet-password item whose read requires a GUI authorization that a
non-interactive session cannot answer. Pushing over SSH succeeded
immediately.
Action: **open.** The maintainer guide should state the SSH push path and
that the repository's `origin` is configured for SSH. Two other sessions
hitting this will lose the same time.

**Unauthenticated GitHub API runs out after 60 calls an hour.**
Evidence: CI status polling exhausted the quota three times in one session,
forcing a switch to the badge endpoint and then to the browser.
Action: **open.** The maintainer guide should record the rate limit and the
badge endpoint as the cheap fallback.

**`curl` to `raw.githubusercontent.com` fails TLS on this machine.**
Evidence: every direct fetch of an upstream file failed with exit code 35,
while `api.github.com` and the SSH transport worked. The upstream files were
obtained by a shallow SSH clone and verified by blob hash.
Action: **open.** Record the SSH clone route for fetching upstream sources;
it is also the only route that gives byte-exact files.

### Information access

**The OpenSpec CLI is installed but not on the non-interactive PATH.**
Evidence: `openspec` was reported as absent, then found at
`/opt/homebrew/bin/openspec` (1.11.0). A separate pinned copy was
installed into a temporary prefix for the strict validation runs.
Action: **open.** The maintainer verification guide should state where the
CLI lives, that a non-interactive shell must add it to `PATH`, and that CI
installs a pinned version instead.

### Steering files and no-ops

**`using-superpowers` opens with an instruction that triggers on every
conversation.**
Evidence: its description is "Use when starting any conversation", which
costs permanent context and competes for attention at the moment a
task-scoped skill would be more useful.
Action: **done** — the skill entry point was removed on 2026-11-01. The
framework's stage routing table and `docs/framework/skill-policy.md` already
cover when a skill is reached, and the upstream rule that a skill must be
invoked whenever there is even a 1% chance conflicts with the framework's own
instruction to load only what the task needs. Its `references/` directory is
kept: `executing-plans` and `writing-skills` are upstream files that link to
those platform adapters, and removing them would break those links.

**A candidate with no evidence was dropped.** The upstream method asks for
no-op instructions in steering files. The framework's `AGENTS.md` and
`docs/framework/` were read for this and no instruction was found that does
not change behaviour. None is filed.

### Not filed

The remaining upstream skills — `prototype`, `wizard`, `teach`,
`to-questionnaire`, `wait-what`, `grill-me`,
`improve-codebase-architecture`, `resolving-merge-conflicts`, and the
issue-tracker-dependent family — were considered against this framework's
boundaries and are not retro candidates. They are either a different
interaction model, a dependency this framework does not have, or a
deliberate exclusion recorded in the skill evaluation.
