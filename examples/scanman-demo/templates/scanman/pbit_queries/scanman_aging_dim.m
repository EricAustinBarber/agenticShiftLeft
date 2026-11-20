let
    Source = Databricks.Catalogs("adb-751266416173271.11.azuredatabricks.net", "/sql/1.0/warehouses/467af2fc060984c3", [Catalog="data_governance", Database=null, EnableAutomaticProxyDiscovery=null]),
    data_governance_Database = Source{[Name="data_governance",Kind="Database"]}[Data],
    scanman_Schema = data_governance_Database{[Name="scanman",Kind="Schema"]}[Data],
    scanman_aging_dim_View = scanman_Schema{[Name="scanman_aging_dim",Kind="View"]}[Data],
    RenamedColumns = Table.RenameColumns(scanman_aging_dim_View, {{"aging_bucket", "Aging Bucket"}, {"sort_order", "SortOrder"}}),
    ChangedType = Table.TransformColumnTypes(RenamedColumns, {{"Aging Bucket", type text}, {"SortOrder", Int64.Type}})
in
    ChangedType
