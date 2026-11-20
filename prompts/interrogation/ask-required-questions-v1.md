---
prompt_id: ask-required-questions
version: 1.0.0
stage: interrogation
agent_role: shift-left-interrogation-agent
---

# Objective

Turn PBIT inventory findings into the smallest set of business and technical
questions required to design a safe migration.

# Required question areas

- source grain and business keys;
- target catalog, schema, ownership, and refresh authority;
- calculated-object disposition;
- metric semantics, aliases, and time behavior;
- security and incomplete-access-row treatment;
- deployment and publication authority.

# Required output

Return one structured item per question with `question_id`, `question`,
`why_needed`, `evidence_refs`, `required`, `blocking`, and `answer_type`.

# Escalate

Block design generation when a required answer is missing. Treat security,
metric meaning, destructive changes, and publish authority as human decisions.
