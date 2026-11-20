CREATE OR REPLACE VIEW data_governance.scanman.scanman_invoice_aging_asof_report AS
SELECT
  as_of_date,
  AVG(aging_days_as_of) AS avg_days_aging_as_of,
  COUNT(*) AS invoice_rows_as_of,
  SUM(total_gross_amount) AS gross_amount_as_of
FROM data_governance.scanman.fact_scanman_invoice_aging_snapshot
GROUP BY as_of_date;

CREATE OR REPLACE VIEW data_governance.scanman.scanman_invoice_aging_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1

source: data_governance.scanman.fact_scanman_invoice_aging_snapshot

comment: "Historical as-of aging metrics from daily current-state invoice snapshots."

dimensions:
  - name: As Of Date
    expr: as_of_date
    display_name: "As Of Date"
    format:
      type: date
      date_format: year_month_day

  - name: Status
    expr: current_status
    display_name: "Current Status"

measures:
  - name: Avg Days Aging (As of Month End - include 990/999, exclude 070/blanks)
    expr: AVG(aging_days_as_of)
    comment: "Average invoice age at the selected snapshot date. The snapshot should be selected at month end for month-end reporting."
    display_name: "Avg Days Aging (As of Month End - include 990/999, exclude 070/blanks)"

  - name: Invoice Rows As Of
    expr: COUNT(1)
    comment: "Positive-value, non-070 invoice rows present at the selected snapshot date."
    display_name: "Invoice Rows As Of"

  - name: Gross Amount As Of
    expr: SUM(total_gross_amount)
    comment: "Gross amount represented by the selected as-of snapshot."
    display_name: "Gross Amount As Of"
$$;
