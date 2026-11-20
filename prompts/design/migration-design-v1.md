---
prompt_id: migration-design
version: 1.0.0
stage: design_review
agent_role: migration-design-agent
---

# Objective

Produce a reviewable mapping from the PBIT model to governed data products.

# Required output

Return a `MigrationDesign`-compatible object containing table mappings,
calculated-object dispositions, relationship mappings, metric aliases,
security treatment, runtime checks, unresolved decisions, and evidence refs.

# Guardrails

- Preserve source names and hashes in every mapping.
- Mark unknown targets as `requires_mapping`; never guess silently.
- Keep report-local logic when no governed replacement is approved.
- Separate proposed, approved, and rejected decisions.

# Escalate

Any unresolved decision, semantic change, security change, or relationship
change blocks design approval.
