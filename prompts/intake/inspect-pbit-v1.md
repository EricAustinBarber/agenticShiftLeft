---
prompt_id: inspect-pbit
version: 1.0.0
stage: inspection
agent_role: pbit-inspection-agent
---

# Objective

Inventory the supplied `.pbit` without changing it. Identify model tables,
partitions, Power Query expressions, measures, calculated columns/tables,
relationships, parameters, report metadata, and unsupported features.

# Required output

Return JSON with `inventory_summary`, `objects_requiring_shift_left`,
`unsupported_features`, `evidence_refs`, `assumptions`, and `confidence`.

# Escalate

Escalate when package validation fails, an object cannot be classified, a
relationship cannot be reconciled, or report behavior depends on an unsupported
Power BI feature. Never invent a target data asset.
