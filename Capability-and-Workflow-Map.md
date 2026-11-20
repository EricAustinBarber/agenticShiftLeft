# Critical Capability and Workflow Map

## Outcome-to-capability map

| Outcome | Critical capability | Type | Priority | Why it is critical |
|---|---|---|---|---|
| Reduce specialist migration effort | Inspect a PBIT into a complete, versioned inventory | Data / Workflow | Must | The agent cannot plan safely from a partial model view |
| Reduce specialist migration effort | Interrogate users only for unresolved business and authority decisions | LLM / Workflow | Must | Questions must reduce uncertainty rather than add manual work |
| Improve governance and reuse | Map report-local logic to governed product, contract, or explicit exception | Data / Governance | Must | Every transformation needs an owned destination or review reason |
| Preserve report behavior | Reconcile source, gold, semantic, and report outputs | Data / Governance | Must | A successful deployment is not proof of semantic compatibility |
| Make agent work trustworthy | Generate explainable plans and bounded changes with provenance | LLM / Governance | Must | Users need to know what changed and why |
| Make execution repeatable | Render deployable Databricks assets from approved design inputs | Workflow / Data | Must | Generated assets must be reproducible and reviewable |
| Protect external systems | Enforce preview, deploy, and publish authorization boundaries | Governance | Must | Agent autonomy must not imply mutation authority |
| Enable future insight products | Produce a reusable metric/product registry and evidence manifest | Data / Adoption | Should | Downstream dashboards and apps need stable governed inputs |
| Improve adoption | Return a clear handoff package and review queue | Adoption / Workflow | Should | Users need usable outputs, not only generated code |

## Primary workflow: shift-left run

```text
Submit PBIT
  -> inspect and classify
  -> resolve questions
  -> design products and metric mappings
  -> preview generated assets
  -> approve material changes
  -> deploy/run Databricks assets
  -> validate data and semantics
  -> rewrite and validate PBIT
  -> return artifact package and evidence
```

## Agent roles

| Agent / service | Job | Allowed actions | Required evidence |
|---|---|---|---|
| Intake agent | Establish file, user, target, and authority context | Read metadata; create intake record; ask intake questions | Intake manifest |
| PBIT analyst agent | Interpret deterministic inventory | Classify objects; identify patterns; propose findings | Inventory references and confidence |
| Interrogation agent | Resolve material uncertainty | Ask bounded questions; record answers; escalate | Interrogation record |
| Data product architect agent | Propose governed products and contracts | Draft grain, keys, products, transformations, and semantic mappings | Migration design and assumptions |
| Asset generation agent | Coordinate deterministic renderers | Request code/package generation; explain diffs | Generated asset manifest |
| Review agent | Challenge design and generated output | Run review checklists; flag omissions and unsupported behavior | Review findings |
| Validation agent | Interpret deterministic test results | Summarize failures, reconcile metrics, route exceptions | Validation evidence |
| Release coordinator | Control handoff and authorization | Assemble package; require approvals; never bypass gates | Release manifest |

The first implementation should avoid many independent autonomous agents. Use a stateful orchestrator with specialized bounded roles and deterministic tools. Split agents only when a separate context, permission boundary, or evaluation target justifies the cost.

## Capability-to-tool alignment

| Capability | Workflow step | Candidate tool | Tool role | Main constraint |
|---|---|---|---|---|
| PBIT inspection | Inventory | Python package inspector and schema parser | Read ZIP members and model metadata | Power BI package formats vary by version |
| Pattern classification | Analysis | LLM with structured output | Classify transformations, measures, and risks | Must cite evidence and abstain when uncertain |
| Databricks asset generation | Render | Templates plus deterministic code generator | Produce contracts, notebooks, SQL, DAB resources | Templates must be versioned and tested |
| Runtime execution | Deploy/validate | Databricks CLI/API and SQL warehouse | Deploy and run approved assets | Credentials and target permissions |
| PBIT rewrite | Package update | Deterministic package transformer | Apply approved mappings and preserve metadata | Lineage tags and package internals are fragile |
| Report validation | Release gate | Power BI Desktop or supported automated validation path | Open, refresh, and test the package | Native Desktop automation may be unavailable |
| Evidence and traceability | All steps | Run manifest, artifact store, logs, evaluation store | Make decisions and outputs reproducible | Protect sensitive PBIT content |

## MVP workflow cards

### PBIT inspection

Trigger: user submits a `.pbit`.

Inputs: file, user identity, supported-version policy.

Steps: hash file, inspect package, parse model/report metadata, detect unsupported features, produce inventory.

Output: inventory and initial review items.

Failure modes: corrupt package, unsupported version, malformed metadata, secrets in package.

Evidence: fixture tests and inventory completeness checks.

### Migration design

Trigger: inventory is complete.

Inputs: inventory, interrogation answers, target configuration, templates.

Steps: classify logic, determine grain and products, map measures, identify exceptions, draft contracts and validation.

Output: migration plan and approval queue.

Failure modes: unresolved grain, semantic ambiguity, security impact, unsupported connector.

Evidence: design review and traceability from every material item to a decision.

### Generated execution package

Trigger: migration design approved.

Inputs: approved design, templates, target configuration.

Steps: render assets, run static checks, show diff, optionally deploy/run, capture IDs and results.

Output: Databricks bundle, validation queries, run manifest.

Failure modes: generation errors, target auth failure, SQL failure, data-quality failure.

Evidence: bundle validation, job run success, product checks, artifact hashes.

### PBIT rewrite and handoff

Trigger: governed products and validation evidence are available.

Inputs: approved mapping, source PBIT, validation results.

Steps: rewrite package deterministically, validate metadata, open/refresh test, assemble handoff.

Output: updated PBIT, diff summary, evidence, unresolved items.

Failure modes: stale lineage tags, broken relationships, missing queries, Power BI incompatibility.

Evidence: package validator plus Power BI open/refresh result.
