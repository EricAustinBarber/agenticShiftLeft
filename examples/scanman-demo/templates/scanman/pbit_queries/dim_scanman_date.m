let
    Source = Databricks.Catalogs("adb-751266416173271.11.azuredatabricks.net", "/sql/1.0/warehouses/467af2fc060984c3", [Catalog="data_governance", Database=null, EnableAutomaticProxyDiscovery=null]),
    data_governance_Database = Source{[Name="data_governance",Kind="Database"]}[Data],
    scanman_Schema = data_governance_Database{[Name="scanman",Kind="Schema"]}[Data],
    dim_scanman_date_Table = scanman_Schema{[Name="dim_scanman_date",Kind="Table"]}[Data],
    #"Renamed Columns" = Table.RenameColumns(dim_scanman_date_Table, {{"year_month_label", "YearMonth Label"}}),
    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"YearMonth", Int64.Type}, {"YearMonth Label", type text}, {"MonthStart", type date}, {"MonthEnd", type date}})
in
    #"Changed Type"
