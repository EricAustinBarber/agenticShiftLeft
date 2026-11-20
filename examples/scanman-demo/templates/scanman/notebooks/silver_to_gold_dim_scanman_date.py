# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


source_table = widget("source_date_table", "prod.conformed_v.dim_date_v")
target_catalog = widget("target_catalog", "data_governance")
target_schema = widget("target_schema", "scanman")
target_table = f"{target_catalog}.{target_schema}.dim_scanman_date"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
result = (
    spark.table(source_table)
    .withColumn("YearMonth", F.year("date") * F.lit(100) + F.month("date"))
    .withColumn("year_month_label", F.date_format("date", "MMM yyyy"))
    .withColumn("MonthStart", F.trunc("date", "month"))
    .withColumn("MonthEnd", F.last_day("date"))
)

if result.filter(F.col("date").isNull()).limit(1).count():
    raise RuntimeError("Date dimension cannot publish null date values")
if result.groupBy("date").count().filter(F.col("count") > 1).limit(1).count():
    raise RuntimeError("Date dimension violated one-row-per-date")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Calendar and fiscal date dimension for Scanman reporting.'")
print(f"Published {target_table}: {result.count()} rows")
