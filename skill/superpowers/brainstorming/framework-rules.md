# Brainstorming Rules in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md) is the upstream method. This file states
> how that method applies inside this framework. **Where the two disagree,
> this file wins.**

## The next item is the active flow

下一项只由活动中的 flow 正文宣布。

flow-02 宣布进入规格时才是 openspec-propose 或 openspec-update-change，然后再 to-tickets。只有要改行为、接口或验收才进入规格。探针停在建议。不按有界路径直接写实现。

flow-08 已宣布停在设计对话、不创建 OpenSpec change、不把 openspec-propose 或 to-tickets 当作下一项。这句优先。

上游 SKILL.md 架构路径第 6–9 步若把 openspec-propose 和 to-tickets 写成收尾，该收尾不是下一项，除非活动 flow 点名它们。

A spike stops at a recommendation. It does not become production code.

## What this file does not do

This file does not announce the skill that comes after brainstorming.
The active `flow-*` router states the next item.
