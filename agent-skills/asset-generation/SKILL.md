---
skill_id: asset-generation
version: 1.0.0
---

# Governed asset generation skill

Purpose: generate contracts, SQL, notebooks, jobs, and validation plans from
an approved migration design.

Allowed tools: deterministic generators, template renderer, hash manifest
writer.

Must produce: reproducible files and an asset manifest. Planned-only output is
required when any source/target mapping or SQL body remains unresolved.
