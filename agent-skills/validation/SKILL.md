---
skill_id: validation
version: 1.0.0
---

# Shift-left validation skill

Purpose: validate generated assets and runtime evidence against the approved
design and original PBIT requirements.

Allowed tools: static validators, read-only Databricks evidence queries, PBIT
package validator, reconciliation checks.

Must produce: check-level status, actual/expected values, evidence paths, and
release recommendation. Never suppress a failed required check.
