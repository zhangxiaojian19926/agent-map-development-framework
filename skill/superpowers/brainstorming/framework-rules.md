# Brainstorming Rules in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md) is the upstream method. This file states
> how that method applies inside this framework. **Where the two disagree,
> this file wins.**

## Bounded work still enters the spec

The upstream method can treat a small, bounded design as ready to implement.
In this framework that ending is suspended when the work changes behavior,
a public interface, or acceptance.

When that is true:

1. The next step is `openspec-propose` or `openspec-update-change`.
2. After the spec, the next step is `to-tickets` and `plan-format.md`.
3. Do not write the implementation from the bounded path.

A spike stops at a recommendation. It does not become production code.

## What this file does not do

This file does not announce the skill that comes after brainstorming.
The active `flow-*` router states the next item.
