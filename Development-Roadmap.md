# Development Roadmap

The roadmap is capability-based. Each phase has a usable evidence gate; a phase is not complete because code exists.

## Phase 0 — Alignment and product boundaries

Objective: confirm the business job, supported PBIT cohort, ownership, authority, and target operating model.

Deliverables:

- approved outcome alignment;
- named product, data, BI, governance, and agent owners;
- supported Power BI/PBIT version policy;
- approved Databricks target and deployment boundary;
- MVP artifact and security contract;
- initial pilot PBIT set represented by isolated demo fixtures.

Exit evidence: signed scope and decision log; no unresolved ownership or authority blocker.

## Phase 1 — Deterministic inspection engine

Objective: turn a PBIT into a complete, versioned inventory.

Deliverables:

- package intake and hashing;
- PBIT schema/report/query/measure/relationship extraction;
- transformation and unsupported-feature detectors;
- inventory schema and fixture corpus;
- redaction and sensitive-content handling.

Exit evidence: inventory completeness tests pass across the pilot fixture set; unsupported items are detected rather than silently omitted.

## Phase 2 — Agent interrogation and migration design

Objective: use agents to resolve business decisions and generate a reviewable migration plan.

Deliverables:

- stateful workflow/orchestrator;
- structured agent outputs;
- question prioritization and answer provenance;
- grain, security, and metric-semantics review checklists;
- product/contract/mapping design schema;
- human approval queue.

Exit evidence: reviewers can trace every material design choice to PBIT evidence, user input, or an explicit default.

## Phase 3 — Deterministic Databricks asset generation

Objective: generate deployable governed products from an approved design.

Deliverables:

- contract templates;
- notebook and SQL templates;
- metric-view and semantic-layer templates;
- DAB/job resource generation;
- static linting and bundle validation;
- preview diff and artifact manifest.

Exit evidence: a generated package validates and is reproducible from the same input manifest.

## Phase 4 — Runtime execution and evidence

Objective: deploy approved assets and capture trustworthy runtime evidence.

Deliverables:

- target-specific execution adapter;
- source-to-gold key/row/amount reconciliation;
- relationship/security/orphan tests;
- metric reconciliation queries;
- job/run/evidence collection;
- failure routing and retry policy.

Exit evidence: a pilot run produces a successful or explicitly failed release manifest with task-level evidence.

## Phase 5 — PBIT rewrite and compatibility validation

Objective: return a Power BI template that consumes the governed products without unexplained behavior changes.

Deliverables:

- deterministic PBIT rewrite engine;
- lineage-tag and metadata repair logic;
- query/relationship/measure mapping;
- package validator;
- supported Power BI Desktop open/refresh test strategy;
- old-versus-new reconciliation report.

Exit evidence: updated PBIT opens and refreshes for the pilot cohort, or the workflow fails closed with a precise blocker.

## Phase 6 — MVP application and pilot

Objective: expose the workflow to business/Power BI users with safe review and download behavior.

Deliverables:

- upload and run-status experience;
- interrogation UI;
- preview and approval UI;
- artifact/evidence download;
- run history and audit trail;
- support and feedback workflow.

Exit evidence: pilot users complete supported runs and achieve the target time/quality outcomes.

## Phase 7 — Metric insight dashboard and application foundation

Objective: consume the generated registry and governed products in reusable insight surfaces.

Deliverables:

- metric registry API/schema;
- dashboard template or generated insight surface;
- governed application data contract;
- permission-aware query layer;
- evaluation and adoption telemetry.

Exit evidence: dashboard/app consumes generated products without duplicating report-local transformation logic.

## Recommended build sequence

1. Build the inspection fixture corpus and schemas.
2. Define the interrogation and approval state machine.
3. Implement one vertical slice using an isolated representative PBIT fixture: inspect → design → generate → validate → rewrite.
4. Add failure handling and unsupported-feature gates.
5. Pilot with two or three additional PBITs before broadening templates.
6. Add the dashboard/app only after product contracts and metric evidence are stable.

## Release go/no-go criteria

Go only when:

- the input PBIT is supported and safely stored;
- all material transformations and measures have a disposition;
- source grain/security decisions are approved;
- generated assets pass static checks;
- runtime validation meets agreed tolerances;
- PBIT package validation passes;
- human approvals and run evidence are complete.

No-go when the workflow would silently drop report logic, weaken security, invent a metric definition, or publish without authorization.
