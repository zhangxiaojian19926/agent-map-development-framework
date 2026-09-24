# llm-wiki public adapter

See [SKILL.md](SKILL.md) for the authoritative invocation and completion contract.
Public adaptation keeps query, init, ingest, batch, digest, status, lint, graph, delete and crystallize workflows.
Helpers use Python standard library, do not install dependencies, call providers, auto-commit or write global aliases.
Generated knowledge remains an Agent task; source preparation is not ingestion completion.
The former local Bash implementation has been replaced for path portability, explicit routing, no-overwrite writes and visible failures. Upstream source attribution is in [notices](../../THIRD_PARTY_NOTICES.md).
