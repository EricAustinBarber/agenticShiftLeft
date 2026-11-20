# Sundt Databricks CLI setup for Agentic Shift Left

This guide prepares a Sundt user workstation to connect the Agentic Shift Left
tooling to the CDM Databricks workspace. Each user authenticates with their own
Sundt identity. The profile stores local authentication configuration; it does
not grant workspace, catalog, schema, warehouse, or job permissions.

## CDM connection values

| Setting | Value |
| --- | --- |
| CLI profile name | `sundt-citizen` |
| Azure Databricks workspace | `https://adb-751266416173271.11.azuredatabricks.net` |
| SQL warehouse | `Serverless Starter Warehouse` |
| SQL warehouse ID | `467af2fc060984c3` |
| CLI authentication | `databricks-cli` (browser-based user sign-in) |

The warehouse ID is for the Serverless Starter Warehouse. The warehouse was
reported as stopped when this guide was prepared. This guide does not start it;
coordinate with the CDM/workspace administrator if a later query needs it.

## 1. Install and check the Databricks CLI

Install the Databricks CLI using Sundt's approved software distribution method.
Then open PowerShell, Windows Terminal, or Git Bash and check that it is
available:

```shell
databricks version
```

## 2. Create the named user profile

In PowerShell or Git Bash, run:

```shell
databricks configure --profile sundt-citizen
```

When prompted, enter the CDM workspace URL:

```text
https://adb-751266416173271.11.azuredatabricks.net
```

Choose the CLI/browser user authentication flow (`databricks-cli`) if prompted,
then complete sign-in as the individual Sundt user. Do not share another user's
token or copy their credential store. The CLI should save the profile in the
user's local Databricks configuration and use the OS keyring where supported.

If the installed CLI does not prompt for authentication type, use the current
Databricks CLI authentication setup flow for your installed version, selecting
browser-based user authentication and the same profile name and host. Do not
put a personal access token or client secret in this guide or source control.

## 3. Confirm the profile

```shell
databricks auth describe --profile sundt-citizen
```

Confirm the host is the CDM URL above and the authenticated user is the
currently signed-in Sundt user. The output should indicate `databricks-cli`
authentication. Before sharing output for troubleshooting, remove personal
identifiers and any token or secret values.

## 4. Confirm warehouse visibility

```shell
databricks warehouses list --profile sundt-citizen
```

Locate `Serverless Starter Warehouse` and confirm its ID is
`467af2fc060984c3`. Its state may be `STOPPED`; listing it does not start it.
If it is missing, ask the CDM/workspace administrator to confirm the user's
workspace and warehouse permissions. Do not start it as part of setup.

## 5. Use the profile with the tool

The adapter uses an explicit profile name. Configure the tool to use
`sundt-citizen` and warehouse ID `467af2fc060984c3` for read-only SQL evidence
collection. Bundle validation also uses this profile. Job execution is a
separate authorized operation and should only be enabled for users with the
required approvals and workspace permissions.

Example CLI option pattern:

```shell
databricks <command> --profile sundt-citizen
```

The local CLI profile is for developer workstation use. A deployed application
should use its approved managed identity/service identity boundary, as defined
in the [Identity and Access Plan](Identity-and-Access-Plan.md), rather than a
developer's personal profile.

## Troubleshooting checklist

- **Profile not found:** check the spelling `sundt-citizen` and that the
  command is running as the Windows user who created the profile.
- **Sign-in fails:** complete the browser flow with the user's Sundt account;
  confirm the user can access the CDM workspace in a browser.
- **Warehouse is not listed:** ask the workspace administrator to verify
  workspace access and warehouse permissions. The CLI only returns warehouses
  visible to the signed-in identity.
- **Permission denied on data:** profile authentication succeeded, but the
  user may still need the appropriate Unity Catalog privileges on the catalog,
  schema, and tables used by the scenario.
- **Do not share credentials:** never send tokens, client secrets, or the
  local `.databrickscfg`/keyring contents. Share only the sanitized output
  needed to diagnose the issue.
