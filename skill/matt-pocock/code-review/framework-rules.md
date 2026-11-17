# Review Rules in This Framework (local adaptation)

> **Layer note:** [SKILL.md](SKILL.md) is the unmodified upstream method. This
> file states how that method applies inside this framework. **Where the two
> disagree, this file wins.**
>
> The upstream file assumes an issue tracker and a `/setup-matt-pocock-skills`
> setup step. This framework has neither. Do not ask the user to run a setup
> skill that does not exist here.

## Where the spec comes from

The upstream method looks for the originating issue or spec file. In this
framework, **the specification is the OpenSpec change**:

```
1. Find the change the work belongs to
   → the active change under openspec/changes/, or the archived one the
     commit series was produced under

2. Read, in this order:
   → openspec/changes/<change>/specs/<capability>/spec.md
     the Requirement and Scenario definitions
   → openspec/changes/<change>/tasks.md
     the slices, their blocking edges, and which are checked
   → openspec/changes/<change>/design.md   (when present)
   → openspec/changes/<change>/proposal.md (when present)

3. If the change is archived, read the archived copy under
   openspec/changes/archive/. The archived task list is the record of what
   was actually claimed done.

4. If no change can be found, say so and report the Spec axis as "no spec
   available" — exactly as the upstream method prescribes for a missing
   spec. Do not substitute the commit message for the specification, and do
   not treat the diff's own description as the requirement.

**Commit messages are evidence of intent, not the specification.** A commit
message saying "fix the parser" is not a requirement; the Scenario is.

## The diff range is the review scope

The upstream method pins a fixed point and diffs against it. In this
framework:

- The range must be the change's actual scope, not an arbitrary recent
  commit. If the work spans several modules, the base is the merge base
  with the branch's target, and every participating repository's range is
  stated separately.
- A multi-repo change is reviewed per repository, with the version
  combination recorded. A cross-module conclusion requires the combination
  to be stated.

## Two axes, but three reviews

The upstream method runs Standards and Spec as parallel sub-agents so neither
pollutes the other. Add a third dimension this framework requires:

| Axis | Question | Source |
|---|---|---|
| **Standards** | Does the change follow the repository's documented rules? | The repo's own standards, plus the Fowler baseline |
| **Spec** | Does it faithfully implement the originating Requirement and Scenario? | The OpenSpec change |
| **Integration** | Does it hold across module boundaries and the declared version combination? | The change's cross-module fields and the integration Scenario |

The Integration axis is skipped only when the change genuinely touches one
module; say that it was skipped and why, rather than silently omitting it.

## Self-review is not an independent review

The framework's rule is blunt: **a self-review must be labeled as a
self-review and must never be reported as an independent approval.**

- Reviewing your own diff and reporting "review passed" is a self-review.
- If a reviewer sub-agent or a human actually reviewed it, record who and
  which mechanism.
- If no reviewer was available, say so. An unavailable independent review is
  a limitation to report, not a box to tick.

## Closure rules

评审不改业务源码，不往 tasks.md 追加切片。发现写入交付报告。

- **Important** 活动路由把 tdd 写成下一项时，修改回到 tdd。flow-04 与 flow-09 没有这句，评审到报告为止。
- **Minor** 发现只写入交付报告，不往 tasks.md 追加切片。
- A finding that is rejected needs a reason recorded, not silence.

## 风险分档

纯界面、文案、辅助脚本且没碰到高风险目录，走轻量核对，不要求独立只读上下文。并发、数据格式与迁移、不可逆删除、鉴权、对外契约、打包发布，以及仓库已写明的高风险或禁改目录，才需要独立只读上下文。不为此新造一份目录名册。没有已授权的只读子代理时，报告标明自审。自审必须标明自审。对照活动 OpenSpec change 核对允许修改的路径、本期不做、方案点名必须复用的代码。缺陷修复再核对改动是否在坏数据第一次产生的位置。这些动作不算修复：说不清坏值从哪来，就在报错处加空值判断、try/catch、重试、sleep 或加大超时；只对报告的那一个输入写特判；放宽、跳过或删除失败测试；一次改好几处却说不清是哪一处起作用。兜底如果还要，单独写明，不把它当成根因修复。入口校验如果就是坏数据第一次产生的地方，空值判断仍然算修复。这些句子只追加，不把评审改回改业务源码。flow-04 与 flow-09 只把这些问题写入交付报告，不把修改交回 tdd。独立只读上下文返回的每条问题，回读对应代码后才写入交付报告；读不出依据的标待确认或剔除，不交给 tdd。审完看 git status 没有变化。只 mock 自证、没有业务断言、靠固定长 sleep 的测试，同样只记进报告。

## Evidence binding

Every review conclusion binds to what was actually reviewed:

- the exact range or ranges reviewed
- the specification revision reviewed against
- the commands whose output supports each finding

A review of a range that has since moved does not cover the current tree.
Re-review, or say which part is stale.

## Reporting format

The upstream method's two-section report stands. This framework adds:

- Each axis reported separately, never merged or re-ranked. A change can
  pass one axis and fail the other, and that is the point of the split.
- Important and Minor findings marked as such, so closure can be tracked.
- Findings tied to Requirement or Scenario identifiers where the Spec axis
  produced them.
- The limitations section states what was not reviewed: files outside the
  range, environments not exercised, reviewers not available.

## Further reading in this group

- [SKILL.md](SKILL.md) — the two-axis method, the smell baseline, the sub-agent briefs
- [../../superpowers/requesting-code-review/code-reviewer.md](../../superpowers/requesting-code-review/code-reviewer.md) — the single-reviewer dispatch template used for per-task reviews
