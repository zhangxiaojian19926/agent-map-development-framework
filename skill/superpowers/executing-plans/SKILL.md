---
name: executing-plans
description: Compare a written plan with the approved slices. This skill does not implement the plan and does not choose delegation.
---

# Executing Plans

## Overview

Compare an approved slice list with the plan text. This skill does not implement the plan and does not mark tasks complete.

**Announce at start:** "I'm using the executing-plans skill to compare this plan with the approved slices."

**Note:** This skill does not choose delegation. A product list does not choose delegation. Delegation happens only when the user has already authorized it and the host provides subagents. The delegated implementer still uses tdd.

## The Process

### Step 1: Load and Review Plan

1. Read the approved slices in the active change `tasks.md`
2. Read the plan file if one is referenced
3. Review critically - identify any questions or concerns about the plan
4. If concerns: raise them with your human partner before any implementation
5. If no concerns: stop. Do not create a second task list and do not start writing code

### Step 2: Do not execute

This skill does not implement.

1. Do not edit business source
2. Do not follow plan steps as an implementation loop
3. Do not mark tasks completed
4. The implementer is tdd, after the route says so

### Step 3: Hand back

After the comparison:

- Report mismatches between the plan and the approved slices
- Do not start implementation from this skill
- Return to the route. The next implementer is tdd

## When to Stop and Ask for Help

**Stop and return to the route when:**

- The plan and the approved slices disagree
- A slice is missing a verification the route requires
- You do not understand an instruction

**Ask for clarification rather than guessing.** Do not choose another skill because a particular product is installed.

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**

- The approved slices change
- The comparison finds a gap in the slice text

**Do not force a code change from this skill.** Slice text belongs to to-tickets. Implementation belongs to tdd.

## Remember

- This skill does not implement
- This skill does not choose delegation
- Compare the plan with the approved slices, then stop
- Do not mark tasks complete here
