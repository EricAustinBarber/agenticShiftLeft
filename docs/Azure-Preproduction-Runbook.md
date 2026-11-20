# Azure pre-production runbook

This runbook is the final configuration step for the first authenticated
vertical slice. It does not grant permissions or deploy resources by itself.

## 1. Register the application

Create an Entra application registration for the API and configure its
audience as the value used by `ENTRA_API_AUDIENCE`. Define application roles:

- `ShiftLeft.User`
- `ShiftLeft.Reviewer`
- `ShiftLeft.Approver`
- `ShiftLeft.Operator`

Assign the appropriate roles to the pilot users or groups. Keep approval and
operator roles separate from ordinary user access.

## 2. Configure the hosting identity

Deploy the application with a managed identity. Grant that identity only the
permissions required to call the approved Azure OpenAI deployment and the
approved Databricks validation boundary.

Do not put API keys, client secrets, or tenant secrets in the repository.

## 3. Configure environment values

```text
ENTRA_TENANT_ID=<tenant-id>
ENTRA_API_AUDIENCE=<api-application-id-uri-or-audience>
ENTRA_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0
AGENT_LLM_AUTH_MODE=entra
AGENT_LLM_ENDPOINT=<approved-openai-compatible-endpoint>
AGENT_LLM_MODEL=<approved-deployment-name>
```

## 4. Smoke-test sequence

1. `GET /health` without a token — confirm the service is reachable.
2. `POST /runs` without a token — confirm `401`.
3. `POST /runs` with a valid user token — confirm a run is created.
4. Confirm `requester.json` and `requester_authenticated` are persisted.
5. Run the read-only `pbit_inspection` agent.
6. Confirm the agent manifest contains prompt, skill, model, identity, and
   response evidence.
7. Confirm a user without reviewer/approver roles cannot approve the run.

## Exit criteria

The first slice is successful when a signed-in pilot user can submit a PBIT,
the agent completes inspection through Entra-authenticated model access, and
the persisted evidence is sufficient to reproduce and review the result.

The initial smoke test must not deploy Databricks assets, rewrite the source
PBIT, or publish a report.

## Local development without login

The workflow can be exercised locally without Entra login:

```powershell
$env:AGENT_LOCAL_DEV_MODE = "true"
python tools/serve_web_api.py
```

This mode is intended for a developer workstation only. It defaults to a
localhost listener and labels all runs as `local-dev`. It is not an
authentication substitute for a shared environment.
