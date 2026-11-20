# Agentic Shift Left

Planning workspace for an agent-driven application that converts Power BI `.pbit` templates into governed, warehouse-backed reporting assets.

This workspace contains the generic product investigation, capability alignment,
interrogation plan, delivery roadmap, and agent prompt/evaluation specifications.
Domain-specific proof-of-concept material is isolated under `examples/`.

## Intended product outcome

Given an approved Power BI `.pbit` template and a configured Databricks target, the application should guide or execute a controlled shift-left workflow that:

1. profiles the PBIT model, queries, calculated objects, relationships, measures, and report metadata;
2. identifies transformations and semantic definitions that should move into governed data products;
3. generates or updates Databricks contracts, notebooks, SQL, jobs, and validation checks;
4. rewrites the PBIT to consume the governed products while preserving report behavior;
5. validates the warehouse outputs and report package;
6. returns the updated PBIT, the deployable Databricks assets, validation evidence, and unresolved review items.

Future releases may generate a metric-insight dashboard and an application over the resulting products. Those are downstream capabilities, not MVP prerequisites.

## Planning artifacts

- [Project Plan](Plan.md)
- [Investigation and Interrogation Plan](Investigation-and-Interrogation-Plan.md)
- [Capability and Workflow Map](Capability-and-Workflow-Map.md)
- [Development Roadmap](Development-Roadmap.md)
- [Decision Log](Decision-Log.md)
- [Process Map](draw.io/Agentic-Shift-Left-Process-Map.drawio)
- [Risk Register](Risk-Register.md)
- [Sundt Databricks CLI Setup](docs/Sundt-Databricks-CLI-Setup.md)

## Initial application foundation

The first reusable code/configuration slice is now staged here:

- `src/agentic_shift_left/pbit/` — generic PBIT package reading, hashing, inventory extraction, and structural validation;
- `src/agentic_shift_left/pbit/rewrite.py` and `tools/rewrite_pbit.py` — manifest-driven PBIT rewrite primitives and CLI; source templates are preserved and outputs are written separately;
- `src/agentic_shift_left/workflow.py` and `tools/start_shift_left_run.py` — run orchestration through intake and inspection, pausing at the interrogation/review gate;
- `src/agentic_shift_left/review.py` and `tools/review_run.py` — structured review packets, question answers, audit decisions, and approval gating;
- `src/agentic_shift_left/persistence.py` — versioned scenario-pack manifests and append-only resumable run events;
- `src/agentic_shift_left/design.py` and `tools/design_run.py` — review-gated migration design generation, validation, and approval;
- `src/agentic_shift_left/generator.py` and `tools/generate_assets.py` — deterministic contract, SQL, validation-plan, and artifact-manifest generation from an approved design;
- `src/agentic_shift_left/asset_validator.py` and `tools/validate_assets.py` — static validation and PASS/WARNING/BLOCKED reports for generated bundles;
- `src/agentic_shift_left/databricks_adapter.py` and `tools/validate_databricks.py` — profile-explicit bundle validation, read-only SQL evidence collection, and authorization-gated job execution;
- `src/agentic_shift_left/runtime_evidence.py` and `tools/collect_runtime_evidence.py` — named runtime checks and JSON/Markdown evidence reports;
- `src/agentic_shift_left/release.py` and `tools/evaluate_release.py` — combined static/runtime release gate and handoff evidence;
- `src/agentic_shift_left/handoff.py` and the rewrite/handoff tools — release-gated PBIT rewrite and hashed artifact handoff packaging;
- `src/agentic_shift_left/orchestrator.py` and `tools/run_status.py` — resumable checkpoint inspection and next-stage coordination;
- `scenario_packs/` and `runs/` — durable storage boundaries for reusable scenarios and execution checkpoints;
- `config/application.yml` — application defaults, workflow stages, and Databricks target configuration;
- `examples/` — isolated demo and regression fixtures; these are not application defaults;
- `tests/` — initial package primitive smoke test.
- `prompts/` — versioned runtime prompt contracts for each agent stage;
- `agent-skills/` — bounded runtime capabilities and evidence rules for agents;
- `config/agent-registry.yml` — prompt, skill, and deterministic-tool bindings.
- `src/agentic_shift_left/agent_runtime.py` and `tools/run_agent.py` — provider-neutral agent execution, output validation, replay testing, and evidence recording.
- `src/agentic_shift_left/http_provider.py` and `tools/run_agent_live.py` — credential-externalized OpenAI-compatible live provider boundary.
- `src/agentic_shift_left/identity.py` and `docs/Identity-and-Access-Plan.md` — Entra identity, role, and audit contracts for the production API.
- `src/agentic_shift_left/entra_auth.py`, `src/agentic_shift_left/web_app.py`, and `tools/serve_web_api.py` — optional Entra-authenticated FastAPI host.
- `docs/Azure-Preproduction-Runbook.md` — configuration and exit criteria for the first authenticated vertical slice.
- Local development can use `AGENT_LOCAL_DEV_MODE=true`; production continues to require Entra authentication.
- The optional web host exposes the first end-to-end run, review, approval, artifact, and agent-execution routes.
- `static/index.html` — initial local browser console over the workflow API.

The engine is developed against isolated demo fixtures, but no domain-specific
report, catalog, schema, or PBIT path is an application default. Rewrite behavior
is driven by a scenario manifest and approved mapping rather than a hard-coded
report path.

## Working principles

- The LLM proposes, explains, and coordinates work; deterministic tooling performs package manipulation, code generation, validation, and deployment.
- No agent may silently change a report or publish assets without an evidence-backed review gate.
- The source PBIT is treated as a requirements and reconciliation artifact, not as proof that every existing definition is correct.
- Every generated asset must retain lineage to the input PBIT, the source evidence, the agent decision, and the validation run.
- Human review is required for ambiguous grain, security, metric semantics, destructive changes, and publish actions.
