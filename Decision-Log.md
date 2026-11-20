# Decision Log

| ID | Date | Decision | Status | Rationale / evidence | Review trigger |
|---|---|---|---|---|---|
| D-001 | 2026-10-23 | Treat domain-specific demo material as a regression fixture, not as the generic architecture | Proposed | Demo assets contain assumptions that must not become application defaults | After first external pilot |
| D-002 | 2026-10-23 | Use deterministic tools for package manipulation, code generation, deployment, and validation; use LLM agents for interpretation, interrogation, planning, and explanation | Proposed | Reduces silent corruption and makes outputs reproducible | Architecture review |
| D-003 | 2026-10-23 | Require human approval for grain, security, material metric semantics, destructive changes, deployment, and publication | Proposed | These decisions cannot safely be inferred from package syntax alone | Governance review |
| D-004 | 2026-10-23 | Make the first release preview-first with explicit deploy/publish modes | Proposed | Users need to review changes before external mutations | MVP design review |
| D-005 | 2026-10-23 | Preserve report-facing names through a compatibility layer when practical | Proposed | Allows the PBIT to retain visual/measure references while logic moves upstream | PBIT rewrite prototype |
| D-006 | 2026-10-23 | Treat metric portability as a classification problem, not a name-matching problem | Proposed | DAX filter/context behavior may differ from warehouse aggregates | Metric evaluation design |
| D-007 | 2026-10-23 | Defer automatic dashboard/app generation until the product and metric registry contracts are stable | Proposed | Prevents a second layer of duplicated semantics | Phase 7 planning |

## Open decisions

1. Application hosting model: Databricks App, internal web application, or another approved platform.
2. Authentication and authorization model for PBIT upload, target workspace access, and artifact download.
3. Whether the application may deploy directly to Databricks or must create a pull request/package for a platform team.
4. Supported Power BI Desktop release range and how native open/refresh validation will run in automation.
5. Approved model/runtime providers and whether customer PBIT contents may leave the controlled environment.
6. Artifact retention, encryption, deletion, and audit requirements.
7. Initial supported transformation/DAX pattern catalog.
8. Business owner and pilot users for the first external PBIT.
