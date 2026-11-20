# Runtime agent skills

Runtime skills describe bounded capabilities available to agents. They are
not the same as Codex development skills. A skill may explain how to reason and
what evidence is required, but deterministic application code remains the
authority for package edits, SQL execution, validation, and release gating.

Each skill is referenced by the agent registry and paired with prompts under
`prompts/`.
