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

本技能在根因前后都不改生产代码，也不提出由本技能执行的修复。不存在「先试三次修复」。

Symptom fixes are failures. A fix that makes the error message go away
without explaining why the error happened is not a fix; it is a delay.

这些动作不算修复：说不清坏值从哪来，就在报错处加空值判断、try/catch、重试、sleep 或加大超时；只对报告的那一个输入写特判；放宽、跳过或删除失败测试；一次改好几处却说不清是哪一处起作用。兜底如果还要，单独写明，不把它当成根因修复。入口校验如果就是坏数据第一次产生的地方，空值判断仍然算修复。本技能仍不改产品代码。

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

根因陈述除了因果链和代码位置，还要能解释全部现象，包括为什么以前不出现、为什么只在某些输入或环境下出现。查过历史就写引入提交的短哈希；没查就写未验证，不凭提交说明下结论。

提交多、范围看不出时，用 git worktree add --detach 在临时目录里 git bisect run。复现材料还没提交的，用新文件名拷进去。结束只 git worktree remove 这个临时目录。当前分支、工作区和暂存区不动。构建失败的版本用退出码 125 跳过。新 worktree 要装依赖或联网时先问。本技能仍不改生产代码。卫生清单和进入 finishing 前的只读事实仍不执行 git worktree remove。

## 本技能在根因前后都不改生产代码

本技能在根因前后都不改生产代码；不存在「先试三次修复」。三次失败若发生在 tdd 里，由 tdd 在活动 flow 把 tdd 写成下一项之后处理。flow-01 与 flow-14 连 tdd 都没有。

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
| 本技能在根因前后都不改生产代码 | 不存在「先试三次修复」。三次失败若发生在 tdd 里，由 tdd 在活动 flow 把 tdd 写成下一项之后处理。flow-01 与 flow-14 连 tdd 都没有。 |

## Red flags — STOP and return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see what happens"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably this, let me just change it"
- "I don't fully understand but let's try"
- Proposing solutions before tracing data flow
- 本技能在根因前后都不改生产代码；不存在「先试三次修复」。三次失败若发生在 tdd 里，由 tdd 在活动 flow 把 tdd 写成下一项之后处理。flow-01 与 flow-14 连 tdd 都没有。
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

在根因陈述里点明失败落在内容、取用、验证、流程还是方法。本技能不因此新建概念页，也不改 flow 契约。概念页和问题页仍走 flow-02 的知识步骤。

| Layer | What the failure looks like | What to change | Where it lands |
|---|---|---|---|
| Content | A concept is missing, or two things that share a name were treated as one concept | 根因陈述点明失败落在内容。本技能不因此新建概念页，也不改 flow 契约。 | 概念页和问题页仍走 flow-02 的知识步骤 |
| Access | The concept was already right, but retrieval returned a similar case whose conditions did not match | 根因陈述点明失败落在取用。本技能不因此新建概念页，也不改 flow 契约。 | 概念页和问题页仍走 flow-02 的知识步骤 |
| Verification | Retrieval and interpretation were both right, but a data-side check was skipped | 根因陈述点明失败落在验证。本技能不因此新建概念页，也不改 flow 契约。 | 概念页和问题页仍走 flow-02 的知识步骤 |
| Flow | The failure was not a knowledge problem at all — the sequence, the authorization or the gate was wrong | 根因陈述点明失败落在流程。本技能不因此新建概念页，也不改 flow 契约。 | 概念页和问题页仍走 flow-02 的知识步骤 |
| Method | Many failures of the same kind each missing the same thing — the extraction itself is systematically incomplete | 根因陈述点明失败落在方法。本技能不因此新建概念页，也不改 flow 契约。 | 概念页和问题页仍走 flow-02 的知识步骤 |

Two records, not one. **Which knowledge base the record belongs to** is the
module routing decision; **which layer the failure belongs to** is this
attribution. Record both — they do not substitute for each other. 记录不在本技能里落成新页或改契约。

失败落在内容、取用、验证、流程还是方法。本技能不因此新建概念页，也不改 flow 契约。概念页和问题页仍走 flow-02 的知识步骤。

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
