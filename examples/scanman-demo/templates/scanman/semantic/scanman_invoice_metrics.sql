-- Small report-support products that used to be created inside the PBIT.
-- Keeping them in the governed schema removes the last local DATATABLE/#table
-- dependencies from the report while preserving the existing report names.
CREATE OR REPLACE VIEW data_governance.scanman.scanman_aging_dim AS
SELECT *
FROM VALUES
  ('Current (0–30)', 1),
  ('31–60', 2),
  ('61–90', 3),
  ('91–120', 4),
  ('120+', 5)
AS aging(aging_bucket, sort_order);

CREATE OR REPLACE VIEW data_governance.scanman.scanman_refresh_audit AS
SELECT
  from_utc_timestamp(MAX(source_etl_gold_timestamp), 'America/Phoenix') AS `LastRefreshArizona`,
  MAX(source_etl_gold_timestamp) AS `LatestSourceRefresh`,
  from_utc_timestamp(CURRENT_TIMESTAMP(), 'America/Phoenix') AS `ReportSurfaceRefreshedAt`
FROM data_governance.scanman.fact_scanman_invoice_current;

CREATE OR REPLACE VIEW data_governance.scanman.scanman_workbench_report AS
SELECT
  scanman_invoice_uuid AS `ScanmanInvoiceUUID`,
  invoice_number AS `InvoiceNumber`,
  supplier_number AS `SupplierNumber`,
  supplier_name AS `SupplierName`,
  total_gross_amount AS `TotalGrossAmount`,
  total_amount_taxable AS `TotalAmountTaxable`,
  total_amount_to_distribute AS `TotalAmountToDistribute`,
  invoice_date AS `InvoiceDate`,
  invoice_due_date AS `InvoiceDueDate`,
  gl_date AS `GLDate`,
  date_updated AS `DateUpdated`,
  upload_date AS `UploadDate`,
  audit_date AS `AuditDate`,
  current_status AS `CurrentStatus`,
  current_status_description AS `CurrentStatusDescription`,
  next_status AS `NextStatus`,
  next_status_description AS `NextStatusDescription`,
  assigned_to AS `AssignedTo`,
  assigned_to_name AS `AssignedToName`,
  business_unit AS `Business_Unit`,
  process_company AS `ProcessCompany`,
  process_po_number AS `ProcessPONumber`,
  process_po_type AS `ProcessPOtype`,
  days_open AS `DaysOpen`,
  comments_tracing AS `Comments_Tracing`,
  payment_remark AS `PaymentRemark`,
  scanman_original_file_name AS `ScanmanOriginalFileName`,
  days_in_status AS `Days in Status`,
  status_order AS `StatusOrder`,
  current_status_display AS `CurrentStatus_Display`,
  aging_days AS `Aging Days`,
  aging_bucket AS `Aging Bucket`,
  business_unit_num AS `BusinessUnit_Num`,
  is_equipwarehouse_page AS `Is_EquipWarehouse_Page`,
  supplier_name_display AS `Supplier Name (Display)`,
  due_days_past_due AS `Due Days Past Due`,
  due_bucket_key AS `Due Bucket Key`,
  upload_month_start AS `UploadMonthStart`,
  assigned_to_name_display AS `AssignedToName Display`,
  is_in_last12months_upload AS `IsInLast12Months_Upload`,
  CAST(NULL AS STRING) AS `OCRInvoiceNumber`,
  CAST(NULL AS STRING) AS `Email`,
  CAST(NULL AS STRING) AS `EmailSubject`,
  CAST(NULL AS STRING) AS `DocumentNumber`,
  CAST(NULL AS STRING) AS `DocumentType`,
  CAST(NULL AS STRING) AS `DocumentCompany`,
  CAST(NULL AS STRING) AS `QuestionStatus`,
  CAST(NULL AS STRING) AS `QuestionStatusDescription`,
  CAST(NULL AS STRING) AS `ProcessPOCompany`,
  CAST(NULL AS STRING) AS `PayItem`,
  CAST(NULL AS STRING) AS `OCRCompany`,
  CAST(NULL AS STRING) AS `OCRCompanyName`,
  CAST(NULL AS STRING) AS `OCRSupplierID`,
  CAST(NULL AS STRING) AS `OCRSupplierName`,
  CAST(NULL AS STRING) AS `OCRPONumber`,
  CAST(NULL AS STRING) AS `AuditUser`,
  CAST(NULL AS STRING) AS `AuditUserName`,
  CAST(NULL AS STRING) AS `TransactionOriginator`,
  CAST(NULL AS STRING) AS `person_responsible`,
  CAST(NULL AS STRING) AS `person_responsible_name`,
  CAST(NULL AS STRING) AS `project_number`,
  CAST(NULL AS STRING) AS `document_company`,
  CAST(NULL AS STRING) AS `document_number`,
  CAST(NULL AS STRING) AS `document_type`,
  CAST(NULL AS STRING) AS `journal_entry_line_number`,
  CAST(NULL AS DECIMAL(18,2)) AS `amount`,
  CAST(NULL AS DECIMAL(18,2)) AS `approval_limit`,
  CAST(NULL AS TIMESTAMP) AS `creation_date`,
  CAST(NULL AS STRING) AS `released_by`,
  CAST(NULL AS TIMESTAMP) AS `released_date`,
  CAST(NULL AS STRING) AS `code_approval_routing`,
  CAST(NULL AS STRING) AS `approval_status`,
  CAST(NULL AS STRING) AS `reason`,
  CAST(NULL AS STRING) AS `comments`,
  CAST(NULL AS STRING) AS `program_id`,
  CAST(NULL AS STRING) AS `user_id`,
  CAST(NULL AS STRING) AS `work_station_id`,
  CAST(NULL AS TIMESTAMP) AS `date_updated`,
  CAST(NULL AS STRING) AS `level_of_last_sent_reminder`,
  CAST(NULL AS STRING) AS `date_of_last_sent_reminder`,
  CAST(NULL AS INT) AS `number_of_sent_reminders1`,
  CAST(NULL AS STRING) AS `user_reserved_code`,
  CAST(NULL AS STRING) AS `user_reserved_ref`,
  CAST(NULL AS TIMESTAMP) AS `user_reserved_date`,
  CAST(NULL AS STRING) AS `user_reserved_number`,
  CAST(NULL AS DECIMAL(18,2)) AS `user_reserved_amount`,
  CAST(NULL AS STRING) AS `hold_orders_code`,
  CAST(NULL AS STRING) AS `address_number`,
  CAST(NULL AS STRING) AS `supplier_invoice_number`,
  CAST(NULL AS DATE) AS `invoice_date`,
  CAST(NULL AS STRING) AS `order_type`,
  CAST(NULL AS DATE) AS `disc_due_date`,
  CAST(NULL AS DATE) AS `date_net_due`,
  CAST(NULL AS STRING) AS `remark`
FROM data_governance.scanman.fact_scanman_invoice_current;

CREATE OR REPLACE VIEW data_governance.scanman.scanman_invoice_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1

source: data_governance.scanman.fact_scanman_invoice_current

comment: "Governed Scanman current-state invoice metrics at one row per ScanmanInvoiceUUID. Current-state metrics are not status-history event counts."

dimensions:
  - name: Invoice UUID
    expr: scanman_invoice_uuid
    comment: "Stable current-state invoice identity from Scanman. Use this key for distinct invoice counts; Invoice Number is not unique."
    display_name: "Invoice UUID"

  - name: Invoice Number
    expr: invoice_number
    comment: "Source invoice number; may be blank and must not be used as the unique invoice identity."
    display_name: "Invoice Number"

  - name: Aging Days
    expr: aging_days
    comment: "Refresh-date-based aging days from Invoice Date through the published refresh date; null when Invoice Date is unavailable. This is not due-date aging."
    display_name: "Aging Days"

  - name: Invoice Due Date
    expr: invoice_due_date
    comment: "Source invoice due date; null values represent a data-quality gap."
    display_name: "Invoice Due Date"
    format:
      type: date
      date_format: year_month_day

  - name: Status
    expr: current_status
    comment: "Current Scanman workflow status code."
    display_name: "Current Status"

  - name: Status Description
    expr: current_status_description
    comment: "Human-readable current Scanman workflow status description. This is a current-state value, not a status transition history."
    display_name: "Status Description"

  - name: Supplier
    expr: supplier_name_display
    comment: "Supplier name, with missing values presented as No Supplier Name."
    display_name: "Supplier"

  - name: Business Unit
    expr: business_unit
    comment: "Source business-unit value from Scanman. It is not assumed to be a conformed project number and may include non-project values."
    display_name: "Business Unit"

  - name: Assigned To
    expr: assigned_to_name_display
    comment: "Scanman assignment display value; missing assignments are Not Assigned."
    display_name: "Assigned To"

  - name: Aging Bucket
    expr: aging_bucket
    comment: "Refresh-date-based aging bucket using the PBIT definitions: Current (0–30), 31–60, 61–90, 91–120, and 120+. Blank values indicate missing Invoice Date."
    display_name: "Aging Bucket"

  - name: Upload Month
    expr: upload_month_start
    comment: "Calendar month containing the invoice upload date. Use this dimension for monthly intake trends, not payment timing."
    display_name: "Upload Month"
    format:
      type: date
      date_format: year_month_day

  - name: Invoice Date
    expr: invoice_date
    comment: "Invoice business date used as the start date for invoice-to-upload timing and refresh-date aging."
    display_name: "Invoice Date"
    format:
      type: date
      date_format: year_month_day

  - name: Upload Date
    expr: upload_date
    comment: "Date the invoice was uploaded to Scanman. Use this for Scanman intake date-range questions; do not substitute Invoice Date."
    display_name: "Upload Date"
    format:
      type: date
      date_format: year_month_day

  - name: Equipment/Warehouse Scope
    expr: is_equipwarehouse_page
    comment: "PBIT equipment/warehouse page classification: SHOPRENTALS or numeric business units 10050 through 10999."
    display_name: "Equipment/Warehouse Scope"

measures:
  - name: Invoice Rows
    expr: COUNT(1)
    comment: "Count of current Scanman product rows. The published product is currently one row per ScanmanInvoiceUUID, but this measure is row count rather than distinct-invoice logic."
    display_name: "Invoice Rows"

  - name: Invoices
    expr: COUNT(DISTINCT scanman_invoice_uuid)
    comment: "Distinct current Scanman invoices by ScanmanInvoiceUUID. This is the governed invoice-volume measure; do not count Invoice Number."
    display_name: "Invoices"

  - name: Gross Amount
    expr: SUM(total_gross_amount)
    comment: "Sum of source total gross amount, including credits, negative values, and zero amounts. Use Positive Gross Amount when credits and negative values should be excluded."
    display_name: "Gross Amount"

  - name: Positive Gross Amount
    expr: SUM(total_gross_amount) FILTER (WHERE total_gross_amount > 0)
    comment: "Sum of source total gross amount restricted to values greater than zero; excludes zero-dollar and negative or credit amounts."
    display_name: "Positive Gross Amount"

  - name: Zero Sum Invoices
    expr: COUNT(1) FILTER (WHERE total_gross_amount = 0)
    comment: "Current invoice rows whose source total gross amount equals exactly zero. This is a zero-value condition, not a missing-invoice condition."
    display_name: "Zero Sum Invoices"

  - name: Average Aging Days
    expr: AVG(aging_days)
    comment: "Average refresh-date-based aging days from Invoice Date through the published refresh date; invoices without Invoice Date are excluded by null aggregate behavior."
    display_name: "Average Aging Days"

  - name: Median Aging Days
    expr: MEDIAN(aging_days)
    comment: "Median refresh-date-based aging days from Invoice Date through the published refresh date."
    display_name: "Median Aging Days"

  - name: Average Days Invoice to Upload
    expr: AVG(DATEDIFF(upload_date, invoice_date))
    comment: "Average calendar days from Invoice Date to Upload Date using DATEDIFF(upload_date, invoice_date); null dates are excluded. Negative values indicate upload before invoice date in source data."
    display_name: "Average Days Invoice to Upload"

  - name: Average Days Upload to GL
    expr: AVG(DATEDIFF(gl_date, upload_date))
    comment: "Average calendar days from Upload Date to GL Date using DATEDIFF(gl_date, upload_date); null dates are excluded."
    display_name: "Average Days Upload to GL"

  - name: Blank Due Date Invoices
    expr: COUNT(1) FILTER (WHERE invoice_due_date IS NULL)
    comment: "Current invoices with no invoice due date. This is a data-quality condition and is not proof of overdue status."
    display_name: "Blank Due Date Invoices"

  - name: Unassigned Invoices
    expr: COUNT(1) FILTER (WHERE assigned_to_name_display = 'Not Assigned')
    comment: "Current invoices whose assignment display value is Not Assigned. This indicates missing Scanman assignment, not user access or responsibility."
    display_name: "Unassigned Invoices"

  - name: Unassigned Gross Amount
    expr: SUM(total_gross_amount) FILTER (WHERE assigned_to_name_display = 'Not Assigned')
    comment: "Gross amount associated with current invoices whose assignment display value is Not Assigned; includes credits and negative values."
    display_name: "Unassigned Gross Amount"

  # Power BI parity measures. These retain the simple aggregate semantics while
  # the context-sensitive and ranking measures are reconciled separately.
  - name: Total Invoices
    expr: COUNT(DISTINCT scanman_invoice_uuid) FILTER (WHERE total_gross_amount > 0 AND scanman_invoice_uuid IS NOT NULL)
    comment: "Positive-value current invoices, matching the report's Total Invoices measure."
    display_name: "Total Invoices"

  - name: Invoices by Status
    expr: COUNT(1)
    comment: "Current invoice rows; group by Status for the report's status breakdown."
    display_name: "Invoices by Status"

  - name: Average Days in Status
    expr: AVG(days_in_status)
    comment: "Average warehouse-published days in status."
    display_name: "Average Days in Status"

  - name: Total Gross Amount
    expr: SUM(total_gross_amount)
    comment: "Current gross amount including credits and zero values."
    display_name: "Total Gross Amount"

  - name: Total Amount by Status
    expr: SUM(total_gross_amount)
    comment: "Gross amount grouped by current status."
    display_name: "Total Amount by Status"

  - name: Avg Days by Status
    expr: AVG(days_in_status)
    comment: "Average days in status grouped by current status."
    display_name: "Avg Days by Status"

  - name: Max Days in Status
    expr: MAX(days_in_status)
    comment: "Maximum warehouse-published days in status grouped by current status."
    display_name: "Max Days in Status"

  - name: Total Invoices by Aging
    expr: COUNT(DISTINCT scanman_invoice_uuid)
    comment: "Distinct current invoices grouped by the warehouse-published Aging Bucket."
    display_name: "Total Invoices by Aging"

  - name: Total Amount by Aging
    expr: SUM(total_gross_amount)
    comment: "Gross amount grouped by the warehouse-published Aging Bucket."
    display_name: "Total Amount by Aging"

  - name: Average Days Aging
    expr: AVG(aging_days) FILTER (WHERE total_gross_amount > 0 AND invoice_date IS NOT NULL)
    comment: "Average warehouse-published refresh-date aging for positive-value invoices."
    display_name: "Average Days Aging"

  - name: 990 Total Gross Amount
    expr: SUM(total_gross_amount) FILTER (WHERE current_status = '990')
    comment: "Gross amount for current status 990."
    display_name: "990 Total Gross Amount"

  - name: Zero Sum Invoice Count
    expr: COUNT(DISTINCT scanman_invoice_uuid) FILTER (WHERE total_gross_amount = 0)
    comment: "Distinct current invoices with exactly zero gross amount."
    display_name: "Zero Sum Invoice Count"

  - name: Unassigned Supplier Balance
    expr: SUM(total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND supplier_name IS NULL)
    comment: "Positive gross amount where the source supplier name is blank."
    display_name: "Unassigned Supplier Balance"

  - name: Oldest Days Aging
    expr: MAX(DATEDIFF(current_date(), invoice_date)) FILTER (WHERE total_gross_amount > 0 AND invoice_date IS NOT NULL)
    comment: "Maximum current age in days for positive-value invoices."
    display_name: "Oldest Days Aging"

  - name: Blank Invoice Due Date Count
    expr: COUNT(1) FILTER (WHERE invoice_due_date IS NULL)
    comment: "Current invoice rows with a blank due date."
    display_name: "Blank Invoice Due Date Count"

  - name: Average Days Invoice to Upload (Per UUID, Base)
    expr: AVG(DATEDIFF(upload_date, invoice_date)) FILTER (WHERE total_gross_amount > 0 AND invoice_date IS NOT NULL AND upload_date IS NOT NULL)
    comment: "Average calendar days from invoice date to upload date for positive-value invoices."
    display_name: "Average Days Invoice to Upload (Per UUID, Base)"

  - name: Average Days Invoice to Upload (Trend incl 990)
    expr: AVG(DATEDIFF(upload_date, invoice_date)) FILTER (WHERE current_status IN ('050','110','720','740','795','797','990','999') AND invoice_date IS NOT NULL AND upload_date IS NOT NULL)
    comment: "Average invoice-to-upload days for the report's trend status set."
    display_name: "Average Days Invoice to Upload (Trend incl 990)"

  - name: Current Outstanding Balance (Distinct Invoice)
    expr: SUM(total_gross_amount)
    comment: "Current gross amount at the published one-row-per-UUID grain."
    display_name: "Current Outstanding Balance (Distinct Invoice)"

  - name: Invoices Uploaded Last 7 Days (Count)
    expr: COUNT(DISTINCT scanman_invoice_uuid) FILTER (WHERE upload_date BETWEEN date_sub(current_date(), 6) AND current_date())
    comment: "Distinct current invoices uploaded during the seven calendar days ending today."
    display_name: "Invoices Uploaded Last 7 Days (Count)"

  - name: Invoices Uploaded Last 7 Days ($)
    expr: SUM(total_gross_amount) FILTER (WHERE upload_date BETWEEN date_sub(current_date(), 6) AND current_date())
    comment: "Gross amount for invoices uploaded during the seven calendar days ending today."
    display_name: "Invoices Uploaded Last 7 Days ($)"

  - name: Avg Days Aging (Card - GLDate start, 990/999 stop at DateUpdated)
    expr: AVG(DATEDIFF(CASE WHEN current_status IN ('990','999') AND date_updated IS NOT NULL THEN date_updated ELSE current_date() END, gl_date)) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status <> '070' AND gl_date IS NOT NULL)
    comment: "Current-date GL-date aging for positive-value invoices, excluding status 070 and stopping processed statuses at DateUpdated."
    display_name: "Avg Days Aging (Card - GLDate start, 990/999 stop at DateUpdated)"

  - name: Largest Pending Invoice ($)
    expr: MAX(total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070'))
    comment: "Largest positive pending invoice amount."
    display_name: "Largest Pending Invoice ($)"

  - name: Largest Pending Invoice - Supplier
    expr: MAX_BY(supplier_name, total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070'))
    comment: "Supplier associated with the largest positive pending invoice amount."
    display_name: "Largest Pending Invoice - Supplier"

  - name: Largest Pending Invoice - Invoice #
    expr: MAX_BY(invoice_number, total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070'))
    comment: "Invoice number associated with the largest positive pending invoice amount."
    display_name: "Largest Pending Invoice - Invoice #"

  - name: Largest Pending Invoice - Age in Days
    expr: MAX(DATEDIFF(current_date(), invoice_date)) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Current age of the largest-pending population; use the largest-invoice detail measures for the selected invoice."
    display_name: "Largest Pending Invoice - Age in Days"

  - name: Largest Pending Invoice - Status Description
    expr: MAX_BY(current_status_description, total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070'))
    comment: "Status description associated with the largest positive pending invoice amount."
    display_name: "Largest Pending Invoice - Status Description"

  - name: Largest Pending Invoice - Age Status (Text)
    expr: CONCAT(CAST(DATEDIFF(current_date(), MAX_BY(invoice_date, total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)) AS STRING), ' days old')
    comment: "Current age text for the invoice selected by the largest-pending amount rule."
    display_name: "Largest Pending Invoice - Age Status (Text)"

  - name: Oldest Open Invoice (Days)
    expr: MAX(DATEDIFF(current_date(), invoice_date)) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Current age in days of the oldest positive open invoice."
    display_name: "Oldest Open Invoice (Days)"

  - name: Oldest Open Invoice - Supplier
    expr: MAX_BY(supplier_name, invoice_date) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Supplier associated with the oldest positive open invoice."
    display_name: "Oldest Open Invoice - Supplier"

  - name: Oldest Open Invoice - Invoice #
    expr: MAX_BY(invoice_number, invoice_date) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Invoice number associated with the oldest positive open invoice."
    display_name: "Oldest Open Invoice - Invoice #"

  - name: Oldest Open Invoice - Amount ($)
    expr: MAX_BY(total_gross_amount, invoice_date) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Amount associated with the oldest positive open invoice."
    display_name: "Oldest Open Invoice - Amount ($)"

  - name: Oldest Open Invoice - Status Description
    expr: MAX_BY(current_status_description, invoice_date) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070') AND invoice_date IS NOT NULL)
    comment: "Status description associated with the oldest positive open invoice."
    display_name: "Oldest Open Invoice - Status Description"

  - name: Median Days Aging
    expr: MEDIAN(aging_days) FILTER (WHERE total_gross_amount > 0 AND invoice_date IS NOT NULL)
    comment: "Median warehouse-published aging days for positive-value invoices."
    display_name: "Median Days Aging"

  - name: Total Invoice Uploads (During Month)
    expr: COUNT(DISTINCT scanman_invoice_uuid)
    comment: "Distinct current invoices; group by Upload Month for monthly intake."
    display_name: "Total Invoice Uploads (During Month)"

  - name: Total Invoice Uploads (During Month, Ignore Page Filters)
    expr: COUNT(DISTINCT scanman_invoice_uuid)
    comment: "Warehouse equivalent of the monthly upload count; group by Upload Month rather than relying on report filter removal."
    display_name: "Total Invoice Uploads (During Month, Ignore Page Filters)"

  - name: Debug - Largest Pending $ (Eligible Max)
    expr: MAX(total_gross_amount) FILTER (WHERE total_gross_amount > 0 AND current_status IS NOT NULL AND current_status NOT IN ('990','999','070'))
    comment: "Diagnostic equivalent of the largest pending amount."
    display_name: "Debug - Largest Pending $ (Eligible Max)"

  - name: Debug Distinct Uploads In Month
    expr: COUNT(DISTINCT scanman_invoice_uuid)
    comment: "Diagnostic distinct-invoice count; group by Upload Month for monthly comparison."
    display_name: "Debug Distinct Uploads In Month"

  - name: Debug Distinct Uploads In Month With Statuses
    expr: COUNT(DISTINCT scanman_invoice_uuid) FILTER (WHERE current_status IN ('050','110','720','740','795','797','990'))
    comment: "Diagnostic distinct-invoice count for the report's explicit upload status set."
    display_name: "Debug Distinct Uploads In Month With Statuses"

  - name: Latest Source Refresh
    expr: MAX(source_etl_gold_timestamp)
    comment: "Latest source refresh timestamp present in the published invoice product. This does not prove every upstream system refreshed simultaneously."
    display_name: "Latest Source Refresh"
$$;
