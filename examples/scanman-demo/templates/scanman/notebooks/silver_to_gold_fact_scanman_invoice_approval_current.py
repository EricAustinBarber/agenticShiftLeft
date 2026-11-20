# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


source_table = widget("source_table", "prod.operation_financials_v.scanman_workbench_v")
target_catalog = widget("target_catalog", "data_governance")
target_schema = widget("target_schema", "scanman")
target_table = f"{target_catalog}.{target_schema}.fact_scanman_invoice_approval_current"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
source = spark.table(source_table)

result = (
    source.filter(F.col("approval_status").isNotNull() | F.col("project_number").isNotNull())
    .select(
        F.col("ScanmanInvoiceUUID").alias("scanman_invoice_uuid"),
        F.col("Business_Unit").alias("business_unit"),
        F.col("project_number").alias("project_number"),
        F.col("person_responsible").alias("person_responsible"),
        F.col("person_responsible_name").alias("person_responsible_name"),
        F.col("approval_status").alias("approval_status"),
        F.col("approval_limit").alias("approval_limit"),
        F.col("code_approval_routing").alias("code_approval_routing"),
        F.col("released_by").alias("released_by"),
        F.col("reason").alias("reason"),
        F.col("comments").alias("comments"),
        F.col("program_id").alias("program_id"),
        F.col("user_id").alias("user_id"),
        F.col("work_station_id").alias("work_station_id"),
        F.col("creation_date").cast("long").alias("creation_date_jde"),
        F.col("released_date").cast("long").alias("released_date_jde"),
        F.col("date_updated").cast("long").alias("date_updated_jde"),
        F.col("date_of_last_sent_reminder").cast("long").alias("date_of_last_sent_reminder_jde"),
        F.col("number_of_sent_reminders1").alias("number_of_sent_reminders"),
        F.col("level_of_last_sent_reminder").alias("level_of_last_sent_reminder"),
        F.col("etl_gold_timestamp").alias("source_etl_gold_timestamp"),
    )
    .withColumn("etl_gold_timestamp", F.current_timestamp())
)

if result.filter(F.col("scanman_invoice_uuid").isNull()).limit(1).count():
    raise RuntimeError("Approval records cannot be published without ScanmanInvoiceUUID")

duplicates = result.groupBy("scanman_invoice_uuid").count().filter(F.col("count") > 1).limit(1).count()
if duplicates:
    raise RuntimeError("Approval product violated the one-row-per-UUID contract")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Current Scanman approval/project slice keyed by ScanmanInvoiceUUID; numeric JDE dates remain explicit until conversion is approved.'")
print(f"Published {target_table}: {result.count()} rows")
