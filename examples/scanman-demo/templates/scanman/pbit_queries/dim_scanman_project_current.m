let
    Source = Databricks.Catalogs("adb-751266416173271.11.azuredatabricks.net", "/sql/1.0/warehouses/467af2fc060984c3", [Catalog="data_governance", Database=null, EnableAutomaticProxyDiscovery=null]),
    data_governance_Database = Source{[Name="data_governance",Kind="Database"]}[Data],
    scanman_Schema = data_governance_Database{[Name="scanman",Kind="Schema"]}[Data],
    dim_scanman_project_current_Table = scanman_Schema{[Name="dim_scanman_project_current",Kind="Table"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(dim_scanman_project_current_Table, {{"project_number-int", Int64.Type}})
in
    #"Changed Type"
