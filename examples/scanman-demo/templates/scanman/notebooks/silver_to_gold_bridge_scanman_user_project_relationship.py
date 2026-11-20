# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


source_table = widget("source_bridge_table", "prod.security_v.bridge_user_project_relationship_v")
target_catalog = widget("target_catalog", "data_governance")
target_schema = widget("target_schema", "scanman")
target_table = f"{target_catalog}.{target_schema}.bridge_scanman_user_project_relationship"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
result = spark.table(source_table)

if result.filter(F.col("bridge_user_project_relationship_key").isNull()).limit(1).count():
    raise RuntimeError("Relationship bridge cannot publish null relationship keys")
if result.groupBy("bridge_user_project_relationship_key").count().filter(F.col("count") > 1).limit(1).count():
    raise RuntimeError("Relationship bridge violated one-row-per-relationship-key")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Current user-to-project relationship bridge for Scanman project-scoped security.'")
print(f"Published {target_table}: {result.count()} rows")
