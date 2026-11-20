# Scanman original PBIT migration mapping

Baseline: `C:\Users\eabarber\CodeX\Scanman\PowerBi\exe-E1 Executive Scanman Workbench.pbit`

Inventory artifact: `examples/scanman-demo/artifacts/scanman/inventory/original-pbit-inventory.json`

## Baseline evidence

- 7 model tables
- 5 relationships
- 40 measures on `scanman_workbench_v`
- 1 calculated partition: `AgingDim`
- 13 calculated columns across `scanman_workbench_v` and `AgingDim`
- 10 unapplied Power Query queries/parameters
- Package structure validates successfully

## First-pass disposition

| PBIT object | Current behavior | Target disposition | Status |
|---|---|---|---|
| `scanman_workbench_v` | Databricks source plus local `StatusOrder` and `BusinessUnit_Num` transformations | Repoint to governed Scanman report-facing product; move report-local calculated columns to the governed product or semantic layer | Requires column-level mapping |
| `dim_project` | Source view plus active-row filter, duplicate/type conversion | Repoint to `dim_scanman_project_current`; confirm active-row and numeric project key contract | Candidate mapping |
| `bridge_user_project_relationship_v` | Direct security view | Repoint to `bridge_scanman_user_project_relationship` | Candidate mapping |
| `dim_active_directory_user_v` | Direct security/user view | Repoint to `dim_scanman_user_current` | Candidate mapping |
| `dim_date_v` | Source view plus year/month helper columns | Repoint to `dim_scanman_date`; confirm helper-column ownership | Candidate mapping |
| `AgingDim` | Local calculated table with two calculated columns | Repoint to governed `scanman_aging_dim` product | Requires source/contract confirmation |
| `Last Refresh` | Local fixed Arizona timestamp calculation | Repoint to `scanman_refresh_audit` or retain as a report-only display helper if the audit product is not approved | Decision required |
| `scanman_audittrail_v` | Unapplied query points to a `test` source view | Repoint to governed refresh audit output or remove if unused | Decision required |
| `environment_*` | Power Query parameters contain multiple historical environments | Replace with target-specific application configuration and approved PBIT parameter values | Required |

## Calculated-column migration queue

These objects must receive an explicit disposition before the rewrite manifest is populated:

- `scanman_workbench_v.Days in Status`
- `scanman_workbench_v.CurrentStatus_Display`
- `scanman_workbench_v.Aging Days`
- `scanman_workbench_v.Aging Bucket`
- `scanman_workbench_v.Is_EquipWarehouse_Page`
- `scanman_workbench_v.Supplier Name (Display)`
- `scanman_workbench_v.Due Days Past Due`
- `scanman_workbench_v.Due Bucket Key`
- `scanman_workbench_v.UploadMonthStart`
- `scanman_workbench_v.IsInLast12Months_Upload`
- `scanman_workbench_v.AssignedToName Display`
- `AgingDim.Aging Bucket`
- `AgingDim.SortOrder`

The proposed warehouse mappings are:

| Calculated object | Proposed target | Disposition |
|---|---|---|
| `Days in Status` | `scanman_workbench_report.days_in_status` | Warehouse candidate; confirm today/refresh-time semantics |
| `CurrentStatus_Display` | `scanman_workbench_report.current_status_display` | Warehouse candidate |
| `Aging Days` | `scanman_workbench_report.aging_days` | Warehouse candidate; confirm processed-status rule |
| `Aging Bucket` | `scanman_workbench_report.aging_bucket` | Warehouse candidate; confirm boundary labels |
| `Is_EquipWarehouse_Page` | `scanman_workbench_report.is_equipwarehouse_page` | Warehouse candidate; confirm business-unit ranges |
| `Supplier Name (Display)` | `scanman_workbench_report.supplier_name_display` | Warehouse candidate |
| `Due Days Past Due` | `scanman_workbench_report.due_days_past_due` | Warehouse candidate; confirm current-date semantics |
| `Due Bucket Key` | `scanman_workbench_report.due_bucket_key` | Warehouse candidate |
| `UploadMonthStart` | `scanman_workbench_report.upload_month_start` | Warehouse candidate |
| `IsInLast12Months_Upload` | `scanman_workbench_report.is_in_last12months_upload` | Warehouse candidate; confirm rolling-window semantics |
| `AssignedToName Display` | `scanman_workbench_report.assigned_to_name_display` | Warehouse candidate |
| `AgingDim.Aging Bucket` | `scanman_aging_dim.aging_bucket` | Governed dimension candidate |
| `AgingDim.SortOrder` | `scanman_aging_dim.sort_order` | Governed dimension candidate |

The proposed rewrite manifest contains these mappings as draft operations. It cannot execute until its status is changed to `approved`, and the semantic/temporal confirmations above are complete.

## Immediate decisions before rewrite

1. Confirm whether the target report-facing view is `data_governance.scanman.scanman_workbench_report` or a different governed product name.
2. Confirm the target catalog, schema, SQL warehouse, and Power BI connection parameters for the pilot.
3. Map each calculated column to a contract column or semantic definition.
4. Confirm whether `Last Refresh` and `scanman_audittrail_v` are replaced by `scanman_refresh_audit`.
5. Reconcile the five model relationships after calculated columns and `AgingDim` are migrated.

Only after these decisions are approved should the empty Scanman rewrite manifest be populated with production operations.
