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
target_table = f"{target_catalog}.{target_schema}.fact_scanman_invoice_current"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{target_schema}")
source = spark.table(source_table)

status_order = (
    F.when(F.col("current_status") == "050", 1)
    .when(F.col("current_status") == "110", 2)
    .when(F.col("current_status") == "720", 3)
    .when(F.col("current_status") == "740", 4)
    .when(F.col("current_status") == "795", 5)
    .when(F.col("current_status") == "797", 6)
    .otherwise(7)
)

invoice_date = F.col("invoice_date")
processed_end = F.when(
    (F.col("current_status") == "990") & F.col("date_updated").isNotNull(),
    F.col("date_updated"),
).otherwise(F.current_date())
aging_days = F.when(invoice_date.isNull(), F.lit(None).cast("int")).otherwise(
    F.greatest(F.lit(0), F.datediff(processed_end, invoice_date))
)
due_days = F.when(F.col("invoice_due_date").isNull(), F.lit(None).cast("int")).otherwise(
    F.greatest(F.lit(0), F.datediff(F.current_date(), F.col("invoice_due_date")))
)
business_unit_num = F.expr("try_cast(business_unit as int)")
days_in_status = F.when(
    F.col("date_updated").isNull(), F.lit(None).cast("int")
).otherwise(F.datediff(F.current_date(), F.col("date_updated")))
upload_month_start = F.trunc("upload_date", "month")
this_month = F.trunc(F.current_date(), "month")
last_12_months_start = F.add_months(this_month, -11)
is_in_last12months_upload = F.when(
    F.col("upload_date").isNull(), F.lit(False)
).otherwise(
    (upload_month_start >= last_12_months_start)
    & (upload_month_start <= this_month)
)

result = (
    source.select(
        F.col("ScanmanInvoiceUUID").alias("scanman_invoice_uuid"),
        F.col("InvoiceNumber").alias("invoice_number"),
        F.col("SupplierNumber").alias("supplier_number"),
        F.col("SupplierName").alias("supplier_name"),
        F.col("OCRSupplierName").alias("ocr_supplier_name"),
        F.col("TotalGrossAmount").cast("decimal(18,2)").alias("total_gross_amount"),
        F.col("TotalAmountTaxable").cast("decimal(18,2)").alias("total_amount_taxable"),
        F.col("TotalAmountToDistribute").cast("decimal(18,2)").alias("total_amount_to_distribute"),
        F.col("InvoiceDate").alias("invoice_date"),
        F.col("InvoiceDueDate").alias("invoice_due_date"),
        F.col("GLDate").alias("gl_date"),
        F.col("DateUpdated").alias("date_updated"),
        F.col("UploadDate").alias("upload_date"),
        F.col("AuditDate").alias("audit_date"),
        F.col("CurrentStatus").alias("current_status"),
        F.col("CurrentStatusDescription").alias("current_status_description"),
        F.col("NextStatus").alias("next_status"),
        F.col("NextStatusDescription").alias("next_status_description"),
        F.col("AssignedTo").alias("assigned_to"),
        F.col("AssignedToName").alias("assigned_to_name"),
        F.col("Business_Unit").alias("business_unit"),
        F.col("ProcessCompany").alias("process_company"),
        F.col("ProcessPONumber").alias("process_po_number"),
        F.col("ProcessPOtype").alias("process_po_type"),
        F.col("DaysOpen").alias("days_open"),
        F.col("Comments_Tracing").alias("comments_tracing"),
        F.col("PaymentRemark").alias("payment_remark"),
        F.col("ScanmanOriginalFileName").alias("scanman_original_file_name"),
        F.col("etl_gold_timestamp").alias("source_etl_gold_timestamp"),
    )
    .withColumn("status_order", status_order)
    .withColumn("current_status_display", F.concat_ws(" - ", "current_status", "current_status_description"))
    .withColumn("aging_days", aging_days)
    .withColumn(
        "aging_bucket",
        F.when(F.col("aging_days").isNull(), F.lit(None).cast("string"))
        .when(F.col("aging_days") <= 30, "Current (0–30)")
        .when(F.col("aging_days") <= 60, "31–60")
        .when(F.col("aging_days") <= 90, "61–90")
        .when(F.col("aging_days") <= 120, "91–120")
        .otherwise("120+"),
    )
    .withColumn("due_days_past_due", due_days)
    .withColumn(
        "due_bucket_key",
        F.when(F.col("invoice_due_date").isNull(), 0)
        .when(F.col("due_days_past_due") <= 30, 1)
        .when(F.col("due_days_past_due") <= 60, 2)
        .when(F.col("due_days_past_due") <= 90, 3)
        .otherwise(4),
    )
    .withColumn("upload_month_start", F.trunc("upload_date", "month"))
    .withColumn("days_in_status", days_in_status)
    .withColumn("is_in_last12months_upload", is_in_last12months_upload)
    .withColumn("business_unit_num", business_unit_num)
    .withColumn("supplier_name_display", F.coalesce(F.nullif(F.trim("supplier_name"), F.lit("")), F.lit("No Supplier Name")))
    .withColumn("assigned_to_name_display", F.coalesce(F.nullif(F.trim("assigned_to_name"), F.lit("")), F.lit("Not Assigned")))
    .withColumn("is_equipwarehouse_page", F.coalesce((F.upper(F.trim("business_unit")) == "SHOPRENTALS") | ((F.col("business_unit_num") >= 10050) & (F.col("business_unit_num") <= 10999)), F.lit(False)))
    .withColumn("etl_gold_timestamp", F.current_timestamp())
)

if result.filter(F.col("scanman_invoice_uuid").isNull()).limit(1).count():
    raise RuntimeError("ScanmanInvoiceUUID cannot be null in the current invoice product")

duplicates = result.groupBy("scanman_invoice_uuid").count().filter(F.col("count") > 1).limit(1).count()
if duplicates:
    raise RuntimeError("The current invoice product violated the one-row-per-UUID contract")

(result.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(target_table))
spark.sql(f"COMMENT ON TABLE {target_table} IS 'Current Scanman invoice/workflow product at one row per ScanmanInvoiceUUID; derived aging is refresh-date based.'")
print(f"Published {target_table}: {result.count()} rows")
