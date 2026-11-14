---
type: {{TYPE}}
artifact_kind: {{ARTIFACT_KIND}}
created: {{DATE}}
confidence: {{CONFIDENCE}}
status: {{STATUS}}
module_ids: []
source_path: {{SOURCE_PATH}}
source_sha256: {{SOURCE_SHA256}}
problem_id: {{PROBLEM_ID}}
sources: []
applies_when:
not_applicable_when:
preconditions: []
confusable_with: []
supersedes:
superseded_by:
retraction_reason:
derived_from: []
affects: []
---

# {{TITLE}}

`artifact_kind` is design, requirement, plan, problem, module, verification, constraint, or concept.
`status` is approved, verified, temporary-workaround, superseded, retracted, or needs-review. A temporary workaround states that the root cause remains.
A page with status `superseded` names its successor in `superseded_by` and is kept but no longer counts as a rule. A page with status `retracted` states why in `retraction_reason`; the original event stays, it just no longer guides new work. A page with status `needs-review` is being questioned and must not be used as a confirmed rule until it is settled.
EXTRACTED follows the source. INFERRED is synthesis and is not a released fact.
Same `source_sha256` is not written again. A changed source updates this page and log.md.
`applies_when` states the conditions this conclusion holds under. `not_applicable_when` states the conditions it must not be used under. A value that is still an unfilled `{{placeholder}}` counts as missing.
`artifact_kind` problem and concept must declare a non-empty `applies_when`; problem must also declare a non-empty `not_applicable_when`. `requirement` does not require them.
`preconditions`, `confusable_with`, `supersedes`, `superseded_by`, `derived_from` and `affects` are optional and may stay empty.
A concept page does not restate the definition: it points at the project glossary through `source_path` and `source_sha256` and adds only the extended meaning — applicability, confusable objects, engineering mapping, constraints, and where to verify it.

## 记录

- 来源：
- 模块：
- 结论：
- 验证或批准依据：
- 限制：
- 触发条件：
- 不适用条件：
- 被排除的解释：
