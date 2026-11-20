# Databricks notebook source
# Phase 2 validation scaffold. Keep this notebook non-deployable until the
# authoritative catalog, source grain, and product keys are approved.

from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


SOURCE_TABLE = widget("source_table", "prod.operation_financials_v.scanman_workbench_v")

REQUIRED_COLUMNS = [
    "ScanmanInvoiceUUID",
    "InvoiceNumber",
    "SupplierName",
    "TotalGrossAmount",
    "InvoiceDate",
    "InvoiceDueDate",
    "GLDate",
    "UploadDate",
    "DateUpdated",
    "CurrentStatus",
    "CurrentStatusDescription",
    "Business_Unit",
]


def assert_required_columns(df, required_columns):
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise RuntimeError(f"Missing required Scanman source columns: {', '.join(missing)}")


def profile_candidate_keys(df):
    return {
        "rows": df.count(),
        "null_uuid": df.filter(F.col("ScanmanInvoiceUUID").isNull()).count(),
        "blank_uuid": df.filter(F.trim(F.col("ScanmanInvoiceUUID")) == "").count(),
        "distinct_uuid": df.select("ScanmanInvoiceUUID").distinct().count(),
        "distinct_invoice_number": df.select("InvoiceNumber").distinct().count(),
        "duplicate_uuid_rows": (
            df.groupBy("ScanmanInvoiceUUID")
            .count()
            .filter((F.col("ScanmanInvoiceUUID").isNotNull()) & (F.col("count") > 1))
            .agg(F.coalesce(F.sum("count"), F.lit(0)).alias("rows"))
            .first()["rows"]
        ),
    }


def profile_relationship_values(df):
    return (
        df.select(
            F.count(F.lit(1)).alias("rows"),
            F.countDistinct("Business_Unit").alias("distinct_business_units"),
            F.countDistinct("project_number").alias("distinct_project_numbers"),
            F.sum(F.when(F.col("Business_Unit").isNull(), 1).otherwise(0)).alias("null_business_units"),
            F.sum(F.when(F.col("project_number").isNull(), 1).otherwise(0)).alias("null_project_numbers"),
        )
        .collect()[0]
        .asDict()
    )


df = spark.table(SOURCE_TABLE)
assert_required_columns(df, REQUIRED_COLUMNS)

print(f"Source table: {SOURCE_TABLE}")
print(f"Columns: {len(df.columns)}")
print("Candidate key profile:", profile_candidate_keys(df))
print("Relationship value profile:", profile_relationship_values(df))

print("Status profile")
display(
    df.groupBy("CurrentStatus", "CurrentStatusDescription")
    .agg(F.count(F.lit(1)).alias("source_rows"), F.countDistinct("ScanmanInvoiceUUID").alias("distinct_invoices"))
    .orderBy("CurrentStatus")
)

print("Date completeness profile")
display(
    df.select(
        F.count(F.lit(1)).alias("rows"),
        *[
            F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(f"null_{c.replace(' ', '_')}")
            for c in ["InvoiceDate", "InvoiceDueDate", "GLDate", "UploadDate", "DateUpdated"]
        ],
    )
)

print("Next gate: approve the grain and relationship findings before creating the gold fact.")
