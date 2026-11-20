# Databricks notebook source
from pyspark.sql import functions as F


def widget(name, default):
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except Exception:
        return default


source_table = widget("source_user_table", "prod.security_v.dim_active_directory_user_v")
target_catalog = widget("target_catalog", "data_governance")
target_schema = widget("target_schema", "scanman")
target_table = f"{target_catalog}.{target_schema}.dim_scanman_user_current"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
result = spark.table(source_table)

if result.filter(F.col("active_directory_users_key").isNull()).limit(1).count():
    raise RuntimeError("User dimension cannot publish null active_directory_users_key values")
if result.groupBy("active_directory_users_key").count().filter(F.col("count") > 1).limit(1).count():
    raise RuntimeError("User dimension violated one-row-per-active_directory_users_key")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Current directory-user dimension for Scanman assignment and security joins.'")
print(f"Published {target_table}: {result.count()} rows")
