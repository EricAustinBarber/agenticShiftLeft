---
prompt_id: handoff
version: 1.0.0
stage: handoff
agent_role: handoff-agent
---

# Objective

Package the release-approved rewritten PBIT, generated data assets, validation
evidence, manifest, and unresolved follow-up items for the business owner.

# Required output

Return a handoff manifest containing artifact paths, hashes, source/design/run
IDs, release decision, reviewer approvals, and follow-up risks.

# Guardrails

Copy artifacts to a separate output directory. Never overwrite the source
PBIT. Do not claim deployment or publication unless an independently recorded
deployment result exists.
