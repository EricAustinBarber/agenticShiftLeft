# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


catalog = widget("target_catalog", "data_governance")
schema = widget("target_schema", "scanman")
source_table = f"{catalog}.{schema}.fact_scanman_invoice_current"
target_table = f"{catalog}.{schema}.fact_scanman_invoice_aging_snapshot"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
as_of_date = F.current_date()
source = spark.table(source_table)

end_date = F.when(
    F.col("current_status").isin("990", "999")
    & F.col("date_updated").isNotNull()
    & (F.to_date("date_updated") <= as_of_date),
    F.to_date("date_updated"),
).otherwise(as_of_date)

snapshot = (
    source.filter(
        F.col("invoice_date").isNotNull()
        & (F.col("total_gross_amount") > 0)
        & F.col("current_status").isNotNull()
        & (F.trim("current_status") != "070")
        & (F.to_date("invoice_date") <= as_of_date)
    )
    .select(
        F.current_date().alias("as_of_date"),
        "scanman_invoice_uuid",
        "invoice_date",
        "date_updated",
        "current_status",
        "total_gross_amount",
    )
    .withColumn("aging_end_date", end_date)
    .withColumn(
        "aging_days_as_of",
        F.greatest(F.lit(0), F.datediff("aging_end_date", "invoice_date")),
    )
    .drop("aging_end_date")
)

if snapshot.groupBy("as_of_date", "scanman_invoice_uuid").count().filter(F.col("count") > 1).limit(1).count():
    raise RuntimeError("Aging snapshot violated the one-row-per-invoice-per-as-of-date contract")

if not spark.catalog.tableExists(target_table):
    snapshot.write.format("delta").mode("overwrite").saveAsTable(target_table)
else:
    spark.sql(f"DELETE FROM {target_table} WHERE as_of_date = current_date()")
    snapshot.write.format("delta").mode("append").saveAsTable(target_table)

spark.sql(
    f"COMMENT ON TABLE {target_table} IS 'Daily current-state invoice aging snapshots used for historical as-of reporting.'"
)
print(f"Published {target_table}: {snapshot.count()} rows for {spark.sql('SELECT current_date()').first()[0]}")
