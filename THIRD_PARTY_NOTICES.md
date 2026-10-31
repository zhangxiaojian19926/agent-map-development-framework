# Third-party notices and local adaptations

## Superpowers

Source: https://github.com/obra/superpowers
License: MIT, copyright Jesse Vincent; full notice in skill/super-powers/LICENSE.
This distribution carries a local skill snapshot and its supporting files, not a claim of byte-for-byte equivalence to a tagged upstream release.
Upstream license checked at 5bf4e78011075bcfc0dc295f0724994cd123ee71. Distributed file hashes are pinned in framework-manifest.json.
The `test-driven-development` skill was retired in favour of the merged `matt-pocock/tdd` skill. Its compliance material (Iron Law, rationalization table, red flags, completion checklist) and its test-quality reference survive as declared local adaptations inside that skill, each carrying its own source header. The remaining superpowers skills carry local edits limited to skill references and this framework's directory and authorization rules; `skill/super-powers/systematic-debugging/CREATION-LOG.md` is kept as upstream history and was not edited.

## OpenSpec skills

Source: https://github.com/Fission-AI/OpenSpec
License: MIT, copyright OpenSpec Contributors; notice in skill/openspec/LICENSE.
Six locally generated skill documents are included; the CLI is not bundled. Generated metadata is preserved and CLI compatibility must be verified at use.
Upstream license checked at db2309783547a14e150dbcbfc19120e4028446c3.

## llm-wiki

Source: https://github.com/sdyckjq-lab/llm-wiki-skill
The imported local metadata declared MIT and attributed its adaptation to Mavis, based on upstream v3.6.4. Exact correspondence to that release was not independently established; no upstream version equivalence is asserted.
Upstream README and package metadata declare MIT at efa2294dd7c00479f7d8463fef88812d2fd5d1bc; a standalone upstream LICENSE file was absent at that revision. The included MIT terms retain source/adapter attribution rather than inventing an upstream copyright year.
This public adaptation replaces the local helper implementation and entry documentation to enforce project-scoped routing and truthful completion states; base page templates are retained with distribution hashes.

## mattpocock/skills

Source: https://github.com/mattpocock/skills
License: MIT, copyright Matt Pocock; notice in skill/matt-pocock/LICENSE.
This distribution carries reference and workflow skills and their supporting files, not a claim of byte-for-byte equivalence to a tagged upstream release.
Upstream license checked at a496f5513d4a4cf889bc48e189e579f4b0bdf6aa. Distributed file hashes are pinned in framework-manifest.json.
`writing-for-agents`, `codebase-design` and the three upstream files of `tdd` are unmodified upstream copies. Two files inside `tdd` are declared local adaptations that carry superpowers-derived material plus this framework's own seam and refactor rules: `discipline.md` and `test-quality.md`. Each carries its own source header. The upstream `agents/openai.yaml` files that distinguish user-invoked from model-invoked skills are not included; that invocation-form mechanism is handled separately.

## Boundaries

No upstream runtime, private project data, bundled node_modules or original project Git history is included.
Source declarations and notices do not certify every downstream use or future upstream release. Preserve third-party attribution when redistributing substantial portions.
