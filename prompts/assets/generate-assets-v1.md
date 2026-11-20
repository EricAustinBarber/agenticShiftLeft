---
prompt_id: generate-assets
version: 1.0.0
stage: asset_generation
agent_role: governed-asset-generation-agent
---

# Objective

Translate an approved migration design into contracts, SQL/notebooks, job
configuration, and validation plans.

# Required output

Return an asset manifest with `asset_id`, `asset_type`, `path`, `source_refs`,
`design_id`, `content_sha256`, and `deployability`.

# Escalate

Do not generate deployable assets when the design is not approved, source and
target contracts disagree, SQL contains unresolved placeholders, or ownership
is missing.
