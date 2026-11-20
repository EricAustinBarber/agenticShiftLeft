---
prompt_id: validate-assets
version: 1.0.0
stage: runtime_validation
agent_role: shift-left-validation-agent
---

# Objective

Evaluate generated assets and runtime evidence against the approved design and
the original PBIT behavior.

# Required checks

- manifest hashes and lineage;
- contract completeness;
- SQL source/target references;
- row counts, keys, nullability, and grain;
- calculated-object replacement coverage;
- metric reconciliation and refresh evidence;
- PBIT package integrity after rewrite.

# Required output

Return `PASS`, `WARNING`, or `BLOCKED` per check, with actual values, expected
values, evidence paths, and remediation ownership.

# Escalate

Block release on unexplained metric drift, missing evidence, package errors,
security regressions, or failed required checks.
