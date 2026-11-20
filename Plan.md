# Agentic Shift Left Application Plan

Status: Investigation and planning

Date started: 2026-10-23

Reference proof-of-concept material is isolated under `examples/` and is not part
of the generic application contract.

## 1. Business problem

Power BI templates frequently contain report-local Power Query shaping, calculated columns, helper tables, and DAX measures that are difficult to govern, reuse, test, deploy, and expose outside the report. Moving that logic into Databricks can improve reuse and governance, but the migration requires careful interpretation of the PBIT model, source grain, relationship behavior, semantic definitions, and report compatibility.

Today, that work depends on specialist analysis and bespoke scripts. The proposed application turns the repeatable parts into an agent-driven workflow with deterministic tools, explicit evidence, and human approval gates.

## 2. Project goals and desired outcomes

| Project goal | Desired outcome | Initial target metric | Primary users | Owner to confirm |
|---|---|---|---|---|
| Reduce the effort to shift-left Power BI reporting logic | A Power BI user can submit an approved PBIT and receive a reviewable shift-left package without hand-building every migration artifact | 60% reduction in specialist preparation time for supported PBITs | Power BI developers, BI analysts, data engineers | Product owner |
| Improve governance and reuse of report logic | Transformations and reusable metrics are represented in governed Databricks products with contracts, lineage, and tests | 100% of migrated report-local transformations have an identified governed destination or documented exception | Data governance, BI, data engineering | Data product owner |
| Preserve report behavior during migration | The updated PBIT opens, refreshes, and reconciles to the approved baseline within defined tolerances | 100% of release-gate test cases pass; no unexplained critical metric drift | BI owners, business reviewers | BI owner |
| Make agent-driven delivery trustworthy | Agents produce explainable plans, bounded changes, validation evidence, and escalation items rather than opaque edits | 100% of material changes have evidence, confidence, and human disposition | Governance, engineering, reviewers | Agent owner |
| Create a reusable foundation for metric insight products | Shift-left outputs can feed a future governed dashboard and application without re-profiling the PBIT manually | New metric-insight surface can consume the generated product contract and metric registry | Business teams, executives, analysts | Product owner |

## 3. Scope boundary

### MVP in scope

- Upload or select a `.pbit` file.
- Extract PBIT package metadata safely and deterministically.
- Profile queries, calculated columns/tables, relationships, measures, parameters, and report pages.
- Interrogate the user about authority, target catalog/schema, source systems, security, metric intent, and approval boundaries.
- Produce a shift-left design and a reviewable change plan.
- Generate a Databricks bundle or equivalent deployable asset package for supported patterns.
- Generate validation queries and a PBIT rewrite package.
- Run static/package validation and, when authorized, deploy/run Databricks assets.
- Return the updated PBIT, generated assets, evidence, review queue, and run manifest.

### Deferred

- Automatic publication to Power BI Service.
- Automatic creation of a metric-insight dashboard.
- Automatic creation of a user-facing application.
- Unsupervised changes to security policy, source-system ownership, or business definitions.
- General-purpose migration of arbitrary custom connectors or unsupported semantic-model features.

## 4. Core design thesis

The application should be an orchestrated evidence-producing workflow, not a single free-form coding agent.

```text
PBIT + user answers + target configuration
    -> deterministic inspection
    -> agent interpretation and interrogation
    -> governed migration design
    -> deterministic asset generation
    -> human review gate
    -> deployment and runtime validation
    -> PBIT rewrite and package validation
    -> handoff manifest and downstream-ready metric registry
```

The LLM is responsible for interpretation, planning, explanation, classification, prompt-driven review, and bounded coordination. Deterministic tools remain responsible for ZIP/package handling, metadata extraction, code rendering, schema checks, SQL execution, job deployment, and evidence capture.

## 5. MVP success definition

The MVP is ready for pilot when a supported PBIT can be processed end-to-end with:

- an accurate inventory of its model and report logic;
- an explicit migration plan with unsupported and ambiguous items called out;
- generated Databricks assets that pass static checks;
- a rewritten PBIT that opens in the supported Power BI Desktop version;
- runtime source-to-gold and old-to-new reconciliation evidence;
- a human approval record for material semantic/security decisions;
- a reproducible run manifest containing inputs, prompts/agent versions, outputs, logs, and validation results.

## 6. Key assumptions to test

1. PBIT metadata is sufficiently inspectable to generate a reliable migration inventory without opening Power BI Desktop.
2. A bounded set of common Power Query and DAX patterns covers the first supported migration cohort.
3. Databricks product templates can be parameterized across source views, catalogs, schemas, warehouses, and security models.
4. PBIT rewrites can preserve report-facing names and relationships while moving supported logic upstream.
5. Runtime reconciliation can be expressed as deterministic tests before the report is opened.
6. Human reviewers will prefer structured evidence and targeted decisions over reviewing raw generated code.

## 7. Initial risks

| Risk | Why it matters | Initial control |
|---|---|---|
| The agent invents business meaning | A plausible migration can still change metric semantics | Require source evidence, confidence, explicit assumptions, and approval for semantic changes |
| PBIT package metadata is internally coupled | A package can pass JSON parsing but fail in Power BI | Maintain version-specific package fixtures and open/refresh tests |
| Grain or relationship errors multiply facts | Metrics and security behavior can silently change | Require source profiling, key tests, orphan reporting, and human gate |
| DAX context semantics do not map directly to SQL metrics | Names can match while answers differ | Classify measures by semantic portability and run old/new reconciliation queries |
| Generated assets affect external systems | Deployment or publication can create operational impact | Separate plan, preview, deploy, and publish permissions |
| Credentials and sensitive report metadata are exposed | PBITs may contain connection information or business data | Scan/redact secrets, isolate workspaces, and log access |
| Unsupported report features are silently dropped | Users may trust an incomplete report | Detect unsupported features and fail closed with a review item |

## 8. Planning gates

- Gate 0: outcome, ownership, supported scope, and authority boundaries approved.
- Gate 1: inspection/interrogation outputs are complete for a representative PBIT cohort.
- Gate 2: migration design is accepted for one supported PBIT pattern.
- Gate 3: generated Databricks package passes static checks and preview review.
- Gate 4: runtime validation and PBIT open/refresh tests pass.
- Gate 5: pilot users accept the workflow and evidence package.

## 9. Immediate investigation questions

- Which PBIT versions and report features are in the first supported cohort?
- Which Databricks environments and deployment boundaries are allowed?
- What is the minimum level of Power BI compatibility required?
- Which actions may the agent perform automatically, and which require approval?
- Which business definitions must be supplied by the user rather than inferred?
- What is the required artifact contract for the returned PBIT, bundle, evidence, and review queue?
- Will the application run as a Databricks App, an internal web application, or another approved platform?
