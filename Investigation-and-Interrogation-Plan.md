# Investigation and Interrogation Plan

## Purpose

Determine whether a submitted PBIT is supported, what must move into governed data products, what the agent must ask the user, and what evidence is required before any asset is generated or deployed.

The interrogation is not a conversational personality layer. It is a controlled requirements and risk-resolution workflow. Each question must either change a design decision, clear a gate, assign an owner, or document an explicit assumption.

## 1. Investigation sequence

| Step | Investigation | Deterministic evidence | Agent responsibility | Gate / output |
|---|---|---|---|---|
| 1 | Intake and safety scan | File hash, size, package members, metadata redaction scan | Explain scope and request missing intake information | Intake manifest |
| 2 | PBIT inventory | Tables, columns, partitions, M expressions, parameters, relationships, measures, report pages, visuals, bookmarks, security metadata | Classify objects as source, transformation, semantic, security, presentation, or unsupported | PBIT inventory |
| 3 | Transformation inventory | Power Query step graph, calculated columns/tables, helper tables, local constants | Identify candidate shift-left transformations and preserve report-facing names | Transformation map |
| 4 | Semantic inventory | DAX expressions, measure dependencies, filter/context patterns, hardcoded lists | Classify measures as portable, context-sensitive, unresolved, diagnostic, or unsupported | Metric migration map |
| 5 | Grain and relationship analysis | Candidate keys, duplicates, nulls, cardinality, relationship direction, security bridge coverage | State grain assumptions and identify questions that cannot be inferred safely | Grain/security findings |
| 6 | Source and target interrogation | User answers, source authority, target catalog/schema, warehouse, deployment profile | Ask only decision-relevant questions and record answers with provenance | Approved design inputs |
| 7 | Migration design | Proposed products, contracts, SQL/notebooks, PBIT mappings, unsupported items | Explain options, tradeoffs, confidence, and required approvals | Migration plan |
| 8 | Preview generation | Rendered code/assets, package diff, expected validation tests | Summarize material changes and identify review hotspots | Preview package |
| 9 | Approval and execution | Approval record, deployment authorization, run IDs | Enforce boundaries and route exceptions | Approved execution |
| 10 | Runtime validation | Job results, row/key/metric reconciliation, PBIT open/refresh result | Explain evidence and unresolved deviations | Release evidence |

## 2. Interrogation domains

### A. Business intent

Ask:

- What business decisions does this report support?
- Which pages, visuals, and measures are critical for the first release?
- Which numbers must remain exactly compatible with the existing report?
- Which report-local definitions are known to be provisional or incorrect?
- Who owns approval of metric meaning and exceptions?

Do not proceed with semantic replacement when the business owner or critical measure set is unknown.

### B. Source authority and grain

Ask:

- Which source tables/views are authoritative for each report table?
- Is the report table current-state, event-grained, snapshot-grained, or mixed-grain?
- What is the business identity key for the main entity?
- Which fields are safe to aggregate, and which are attributes from a separate grain?
- Are missing or unmatched keys expected, or are they defects?

Required evidence: source profile, candidate key profile, duplicate analysis, and relationship/cardinality findings.

### C. Target Databricks design

Ask:

- Which workspace/profile, catalog, schema, SQL warehouse, and deployment target are approved?
- Should the application create or reuse existing products?
- What naming, ownership, tagging, and contract standards apply?
- Should outputs be tables, views, metric views, or a combination?
- What refresh cadence and performance target are required?

Required evidence: target configuration and ownership record.

### D. Security and privacy

Ask:

- Does the PBIT contain row-level security, object-level security, or user/project bridges?
- Which identity source is authoritative?
- How should unmatched users/projects be handled?
- What access may the agent use during inspection, deployment, and validation?
- Which fields or artifacts must be redacted from logs and downloads?

Required evidence: security map, orphan report, access-test plan, and redaction result.

### E. Metric semantics

Ask only when evidence cannot resolve the answer:

- Is this measure a current-state, event, snapshot, or as-of metric?
- Does it count rows, distinct business identities, or distinct business-document numbers?
- Which statuses, amounts, dates, blanks, negatives, and exclusions are intentional?
- Is filter removal part of the business meaning or only a visual workaround?
- Are ranking ties required to be deterministic?

Required evidence: metric definition, filter/context basis, temporal basis, source columns, and reconciliation test.

### F. Execution authority

Ask before any external mutation:

- Is this a preview-only run, a deploy-to-development run, or an approved publish run?
- Which resources may be created, updated, or overwritten?
- Who approves the PBIT rewrite and deployment?
- What rollback artifact and run manifest must be retained?

The agent must never infer publish authority from a general request to analyze or plan.

## 3. Interrogation rules

- Batch questions by decision domain rather than asking one question for every field.
- Do not ask questions that deterministic inspection can answer.
- Ask the highest-impact unresolved question first.
- Present the evidence that triggered the question.
- Offer constrained choices only when they reflect real design alternatives; preserve free-text explanations when business meaning is nuanced.
- Mark unanswered questions as blockers, assumptions, or deferred decisions.
- Never turn an agent inference into an approved business definition without owner confirmation.
- Persist each answer with question ID, timestamp, actor, evidence references, and affected decisions.

## 4. Interrogation output contract

```yaml
question_id: metric.temporal_basis.001
domain: metric_semantics
question: Is Average Aging based on the current refresh date or an as-of reporting date?
evidence:
  - pbit://DataModelSchema/measure/...
  - pbit://Report/Layout/page/...
options:
  - current_refresh_date
  - historical_as_of_date
  - unresolved
answer: unresolved
answer_source: pending_business_owner
confidence: low
affected_artifacts:
  - fact_product
  - metric_view
  - pbit_measure
gate: migration_design
```

## 5. Investigation outputs

- `intake-manifest.json`
- `pbit-inventory.json`
- `transformation-map.json`
- `relationship-and-security-map.json`
- `metric-migration-map.json`
- `interrogation-record.json`
- `migration-plan.json`
- `unsupported-and-review-items.json`
- `evidence-manifest.json`

These are product artifacts for the application, not ad hoc notes. Their schemas should be versioned before MVP implementation.

## 6. Investigation stop conditions

Stop and route to human review when:

- package integrity or supported PBIT version cannot be established;
- an authoritative source or grain cannot be determined;
- a security relationship is ambiguous or has material orphan coverage;
- a measure has material context semantics that cannot be reconciled;
- the proposed change would drop fields, visuals, relationships, or security behavior;
- credentials, sensitive content, or deployment authority are missing;
- validation evidence cannot be generated or the PBIT cannot be opened in the supported Power BI version.
