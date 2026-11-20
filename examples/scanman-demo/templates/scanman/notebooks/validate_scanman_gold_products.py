# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
            return default


source_table = widget("source_table", "prod.operation_financials_v.scanman_workbench_v")
catalog = widget("target_catalog", "data_governance")
schema = widget("target_schema", "scanman")
invoice_table = f"{catalog}.{schema}.fact_scanman_invoice_current"
approval_table = f"{catalog}.{schema}.fact_scanman_invoice_approval_current"
project_table = f"{catalog}.{schema}.dim_scanman_project_current"
date_table = f"{catalog}.{schema}.dim_scanman_date"
user_table = f"{catalog}.{schema}.dim_scanman_user_current"
bridge_table = f"{catalog}.{schema}.bridge_scanman_user_project_relationship"
aging_snapshot_table = f"{catalog}.{schema}.fact_scanman_invoice_aging_snapshot"

invoice = spark.table(invoice_table)
approval = spark.table(approval_table)
project = spark.table(project_table)
date = spark.table(date_table)
user = spark.table(user_table)
bridge = spark.table(bridge_table)
aging_snapshot = spark.table(aging_snapshot_table)
source = spark.table(source_table)

required_invoice_columns = {
    "days_in_status",
    "current_status_display",
    "aging_days",
    "aging_bucket",
    "due_days_past_due",
    "due_bucket_key",
    "upload_month_start",
    "supplier_name_display",
    "assigned_to_name_display",
    "is_equipwarehouse_page",
    "is_in_last12months_upload",
}
missing_invoice_columns = sorted(required_invoice_columns - set(invoice.columns))
if missing_invoice_columns:
    raise RuntimeError(f"Invoice product is missing shifted-left columns: {missing_invoice_columns}")

snapshot_duplicates = (
    aging_snapshot.groupBy("as_of_date", "scanman_invoice_uuid")
    .count()
    .filter(F.col("count") > 1)
    .limit(1)
    .count()
)
if snapshot_duplicates:
    raise RuntimeError("Aging snapshot contains duplicate invoice/as-of-date keys")

invoice_rows = invoice.count()
invoice_uuids = invoice.select("scanman_invoice_uuid").distinct().count()
source_rows = source.count()
source_uuids = source.select("ScanmanInvoiceUUID").distinct().count()
approval_rows = approval.count()
approval_uuids = approval.select("scanman_invoice_uuid").distinct().count()

if invoice_rows != invoice_uuids:
    raise RuntimeError(f"Invoice product key failure: {invoice_rows} rows vs {invoice_uuids} UUIDs")
if source_rows != source_uuids:
    raise RuntimeError(f"Source key failure: {source_rows} rows vs {source_uuids} UUIDs")
if invoice_uuids != source_uuids:
    raise RuntimeError(
        f"Invoice product row-loss/duplication failure: source UUIDs={source_uuids}, gold UUIDs={invoice_uuids}"
    )
if approval_rows != approval_uuids:
    raise RuntimeError(f"Approval product key failure: {approval_rows} rows vs {approval_uuids} UUIDs")

for table, key in [
    (project, "project_number"),
    (date, "date"),
    (user, "active_directory_users_key"),
    (bridge, "bridge_user_project_relationship_key"),
]:
    null_keys = table.filter(F.col(key).isNull()).count()
    duplicate_keys = table.groupBy(key).count().filter(F.col("count") > 1).count()
    if null_keys or duplicate_keys:
        raise RuntimeError(f"Dimension key failure for {key}: nulls={null_keys}, duplicate_groups={duplicate_keys}")

orphan_users = (
    bridge.join(user.select("active_directory_users_key"), "active_directory_users_key", "left_anti").count()
)
orphan_projects = (
    bridge.filter(F.col("project_number").isNotNull())
    .join(project.select("project_number"), "project_number", "left_anti")
    .count()
)

print({
    "invoice_rows": invoice_rows,
    "invoice_distinct_uuid": invoice_uuids,
    "source_rows": source_rows,
    "source_distinct_uuid": source_uuids,
    "approval_rows": approval_rows,
    "approval_distinct_uuid": approval_uuids,
    "project_rows": project.count(),
    "date_rows": date.count(),
    "user_rows": user.count(),
    "bridge_rows": bridge.count(),
    "orphan_bridge_users": orphan_users,
    "orphan_bridge_projects": orphan_projects,
    "aging_snapshot_rows": aging_snapshot.count(),
    "aging_snapshot_dates": aging_snapshot.select("as_of_date").distinct().count(),
})

display(
    invoice.groupBy("current_status", "current_status_description")
    .agg(F.count("*").alias("rows"), F.sum("total_gross_amount").alias("gross_amount"))
    .orderBy("current_status")
)
