# Domain Modeling in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md), [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) and
> [ADR-FORMAT.md](ADR-FORMAT.md) are unmodified upstream files. This file says
> where their artifacts live here, and which half of the method this framework
> does not use. **Where the two disagree, this file wins.**

## The glossary lives in `docs/project/`

Upstream puts `GLOSSARY.md` at the repository root. This framework has a
documented directory ownership, so the glossary is a project artifact:

```
docs/project/GLOSSARY.md          single context
docs/project/GLOSSARY-MAP.md       multiple contexts, points at the per-context glossaries
```

- It is **human-authored**. The framework does not generate it, and
  `docs/project/`'s generated and human sections stay separate as the layout
  guide requires.
- Create it lazily: only when the first term is actually resolved. An empty
  glossary is noise.
- The knowledge base does not hold it. The knowledge policy governs what may
  be ingested, and a glossary is current project vocabulary rather than a
  verified, reusable experience. See
  [knowledge-policy.md](../../../docs/framework/knowledge-policy.md).

## Decision records are already covered

Upstream offers to write ADRs under `docs/adr/` when three conditions hold:
the decision is hard to reverse, surprising without context, and the result of
a real trade-off.

**This framework does not create a separate ADR set.** Decisions are recorded
where the framework already tracks them:

| Kind of decision | Where it goes |
|---|---|
| A decision about a change's scope, shape or trade-offs | the change's `design.md`, archived with the change |
| A standing architectural constraint of the project | `docs/project/architecture.md` and `docs/project/constraints.md` |
| A decision that only matters to one module | that module's local rules |

A second decision-record location would be a competing source of truth for
the same fact, which this framework's public rules forbid. The upstream ADR
format file is included because the upstream skill links to it; it is not
used.

## What the method is still good for

The upstream discipline is worth keeping in full for the glossary half:

- **Challenge a term against the glossary.** When the user uses a word that
  conflicts with the agreed vocabulary, say so immediately and ask which
  meaning is meant.
- **Sharpen vague language.** When one word carries several meanings, propose
  the canonical term and record the avoided ones.
- **Stress-test with concrete scenarios.** Invent edge cases that force the
  boundary between two concepts to be stated.
- **Cross-check the code.** When the user describes how something works and
  the code disagrees, surface the contradiction rather than accepting both.
- **Keep the glossary free of implementation detail.** It defines what a
  concept is, not how it is built.

## Glossary and the spec

The glossary and the OpenSpec change describe different things and neither
replaces the other:

- The **change** says what is being built now, for this scope, with scenarios
  and a completion state.
- The **glossary** says what the words mean, for the project as a whole,
  with no completion state.

When a change resolves a term, update the glossary as part of that change's
work — it is project fact, and it is captured in the same commit.

## Where the vocabulary must be used

A glossary that nothing reads is a dead document. Once a term is settled:

- use it in code: module, type, function and file names
- use it in the project's documents, including the module documents the
  framework generates
- use it in the knowledge pages written later, so the vocabulary does not
  fork into a third set of words

## Further reading in this group

- [SKILL.md](SKILL.md) — the upstream method
- [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) — the glossary file format and the multi-context map
- [ADR-FORMAT.md](ADR-FORMAT.md) — the upstream ADR format, not used here
