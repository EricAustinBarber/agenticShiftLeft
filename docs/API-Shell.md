# Application API shell

The local API is the first application boundary over the persisted shift-left
workflow. It is intentionally dependency-light so the workflow can be tested
before selecting a hosted UI/API runtime.

Start it from the application directory:

```powershell
python tools/serve_api.py
```

The API accepts a local PBIT path for the prototype, or a base64-encoded PBIT
for an upload adapter:

```json
POST /runs
{
  "input_path": "C:\\path\\to\\report.pbit",
  "scenario_id": "my-report",
  "scenario_version": "0.1.0"
}
```

Core routes:

- `GET /runs/{run_id}` — persisted orchestration status and next action
- `GET /runs/{run_id}/review` — review packet and evidence references
- `GET /runs/{run_id}/agents` — prompt/skill versions and recorded agent decisions
- `POST /runs/{run_id}/agents/decisions` — record an agent decision and evidence refs
- `POST /runs/{run_id}/agents/{agent_name}/execute` — execute a configured live agent
- `POST /runs/{run_id}/review/answers` — answer one required review item
- `POST /runs/{run_id}/review/approve` — approve the interrogation gate
- `GET /runs/{run_id}/design` — migration design after generation
- `POST /runs/{run_id}/design/approve` — approve the design gate
- `GET /runs/{run_id}/artifacts` — list generated evidence and assets

The shell does not bypass approval gates and does not deploy Databricks assets.
Those remain explicit workflow stages. A production adapter should add
authentication, authorization, upload size limits, and durable job execution.

The optional FastAPI host also serves `static/index.html` at `/` for local
workflow testing. It is a development console, not the final production UX.

Agent execution is currently provider-neutral. `tools/run_agent.py` provides a
replay adapter for contract testing; a live model adapter will be added after
the output contracts are accepted. `tools/run_agent_live.py` supports both
authentication modes:

- `AGENT_LLM_AUTH_MODE=entra` uses `DefaultAzureCredential`; local development
  can use Azure CLI SSO and deployed applications can use managed identity.
- `AGENT_LLM_AUTH_MODE=api-key` uses `AGENT_LLM_API_KEY` for isolated testing.

Both modes use `AGENT_LLM_ENDPOINT` and `AGENT_LLM_MODEL`. The endpoint must
support a chat-completions-compatible JSON response with structured output.
