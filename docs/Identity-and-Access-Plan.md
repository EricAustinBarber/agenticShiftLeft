# Identity and access plan

The application will use Entra ID for user sign-in and a managed identity for
model/data-plane calls made by the application. These are separate identities:

```text
business user → Entra-authenticated application → managed identity → LLM / Databricks
```

The user identity is used for application authorization and audit. The managed
identity is used for service-to-service access. A user-provided `requested_by`
field is not an authentication mechanism and must never replace validated token
claims.

## Application roles

| Role | Intended authority |
| --- | --- |
| `ShiftLeft.User` | Upload a PBIT and view own runs |
| `ShiftLeft.Reviewer` | Answer review questions and request changes |
| `ShiftLeft.Approver` | Approve designs and release gates |
| `ShiftLeft.Operator` | Execute authorized validation, rewrite, and handoff operations |

## Implementation sequence

1. Add Entra OIDC/JWT middleware to the production API host.
2. Validate tenant, issuer, audience, signature, expiry, and roles.
3. Construct `IdentityContext` only from validated claims.
4. Require roles at each API route.
5. Persist the identity context in the run manifest and decision events.
6. Use managed identity/RBAC for Azure OpenAI and Databricks access.

The current local HTTP shell is not production-authenticated. It can exercise
workflow behavior, but deployment must not expose it until the middleware and
role checks are active.

The first production host is scaffolded in `src/agentic_shift_left/web_app.py`
and `tools/serve_web_api.py`. It requires the `web` optional dependencies and
`ENTRA_TENANT_ID` plus `ENTRA_API_AUDIENCE`; missing settings fail closed.

For local-only development, set `AGENT_LOCAL_DEV_MODE=true` and keep the host
bound to `127.0.0.1`. This creates a clearly labeled `local-dev` identity and
does not validate Entra tokens. It must never be enabled in a shared or
production deployment.
