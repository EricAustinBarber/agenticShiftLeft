# Original PBIT versus approved Databricks Scanman products

Comparison profile: `sundt-citizen`

Workspace: `adb-751266416173271.11.azuredatabricks.net`

Catalog/schema: `data_governance.scanman`

Baseline PBIT: `C:\Users\eabarber\CodeX\Scanman\PowerBi\exe-E1 Executive Scanman Workbench.pbit`

## Catalog result

All proposed target assets are present:

- `scanman_workbench_report` view
- `dim_scanman_project_current`
- `bridge_scanman_user_project_relationship`
- `dim_scanman_user_current`
- `dim_scanman_date`
- `scanman_aging_dim` view
- `scanman_refresh_audit` view
- `scanman_invoice_metrics` metric view
- `scanman_invoice_aging_metrics` metric view

## Report-facing column comparison

The original PBIT has 84 non-calculated `scanman_workbench_v` columns. The approved `scanman_workbench_report` view has 94 columns.

- All 11 report-local calculated-column replacements are present in the view with matching names and compatible types.
- The only original non-calculated PBIT column not present in the report view is `etl_gold_timestamp`. This is ETL metadata and is not used by the report-facing model; it should be treated as intentionally excluded or added only if lineage/audit requirements need it.
- The view has the 11 migrated calculated columns as physical fields, which supports removing the local DAX columns after the replacement query is applied.

## Dimension and helper comparison

| Original PBIT object | Approved target | Result | Required handling |
|---|---|---|---|
| `dim_project` | `dim_scanman_project_current` | All 74 PBIT columns present; target has 3 additional columns | Existing query preserves `project_number-int`; extra target columns are harmless unless model metadata is expanded |
| `bridge_user_project_relationship_v` | `bridge_scanman_user_project_relationship` | 8 of 8 columns match | Direct replacement is compatible |
| `dim_active_directory_user_v` | `dim_scanman_user_current` | 15 of 15 columns match | Direct replacement is compatible |
| `dim_date_v` | `dim_scanman_date` | Same 54 fields after transformation | Existing query must rename `year_month_label` to `YearMonth Label` |
| `AgingDim` | `scanman_aging_dim` | Target has the required aging bucket and sort columns | Existing query must rename `aging_bucket` and `sort_order` |
| `Last Refresh` | `scanman_refresh_audit` | Target includes `LastRefreshArizona` plus source/report timestamps | Model measure should continue to use `LastRefreshArizona`; extra audit columns remain available to the governed audit product |

## Metric comparison

The approved metric views contain 38 of the 41 PBIT measure names when counting the `Last Refresh` table measure.

The three differences are naming/ownership differences, not missing business coverage:

| PBIT measure | Approved Databricks equivalent | Action |
|---|---|---|
| `Largest Pending Invoice - Invoice #` | `Largest Pending Invoice - Invoice` | Add a governed alias or update the report measure display name while preserving the PBIT-facing name if visuals depend on it |
| `Oldest Open Invoice - Invoice #` | `Oldest Open Invoice - Invoice` | Add a governed alias or update the report measure display name while preserving the PBIT-facing name if visuals depend on it |
| `Data Last Refreshed` | `scanman_refresh_audit.ReportSurfaceRefreshedAt` / `LastRefreshArizona` | Keep the formatted report display measure, sourced from the approved audit view |

## Decision

The proposed warehouse mappings are structurally viable for the first generated PBIT. The rewrite can proceed after three explicit approvals:

1. Treat `etl_gold_timestamp` as intentionally excluded from the report-facing view.
2. Preserve the date and aging dimension rename steps in the PBIT query mappings.
3. Preserve the three metric display-name aliases so existing visuals and report semantics remain stable.

## Runtime evidence snapshot

Read-only checks against the approved products returned:

| Check | Result | Interpretation |
|---|---:|---|
| `scanman_workbench_report` rows | 319,309 | Current report-facing product is populated |
| Distinct invoice UUIDs | 319,309 | No duplicate invoice UUIDs in the current report-facing view |
| Null invoice UUIDs | 0 | Invoice identity is complete for the report view |
| Null business units | 0 | Report relationship key input is populated |
| `scanman_aging_dim` rows/buckets | 5 / 5 | Aging helper dimension is complete |
| Aging helper incomplete rows | 0 | No null bucket or sort values |
| Security bridge rows | 191,132 | User/project access product is populated |
| Security bridge complete rows | 189,706 | 1,426 rows have a null user key or project number |
| Security bridge null user keys | 58 | Requires orphan/security review before production cutover |
| Security bridge null project numbers | 1,369 | Requires approved treatment; do not silently drop without a security decision |
| Refresh audit rows | 1 | Current audit output is available |
| Latest source refresh | `2026-10-22T07:28:57Z` | Source freshness evidence present |
| Latest report refresh | `2026-10-22T00:28:57Z` | Report-surface timestamp present |

The security bridge exceptions are the only material runtime quality issue found in this first comparison. They do not block schema generation, but they must be dispositioned before enabling a permission-aware production agent or releasing the rewritten report broadly.

No Databricks data or PBIT source was modified during this comparison. Queries were metadata/schema comparisons only.
