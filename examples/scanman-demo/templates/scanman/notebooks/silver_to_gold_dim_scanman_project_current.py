# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


source_table = widget("source_project_table", "prod.conformed_v.dim_project_v")
target_catalog = widget("target_catalog", "data_governance")
target_schema = widget("target_schema", "scanman")
target_table = f"{target_catalog}.{target_schema}.dim_scanman_project_current"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
source = spark.table(source_table)
result = (
    source.filter(F.col("etl_is_active") == True)
    .withColumn("project_number-int", F.expr("try_cast(project_number AS BIGINT)"))
)

if result.filter(F.col("project_number").isNull()).limit(1).count():
    raise RuntimeError("Project dimension cannot publish null project_number values")
if result.groupBy("project_number").count().filter(F.col("count") > 1).limit(1).count():
    raise RuntimeError("Project dimension violated one-row-per-project_number")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Current active Scanman project dimension sourced from the conformed project view.'")
print(f"Published {target_table}: {result.count()} rows")
