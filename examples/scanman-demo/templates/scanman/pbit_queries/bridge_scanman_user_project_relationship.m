let
    Source = Databricks.Catalogs("adb-751266416173271.11.azuredatabricks.net", "/sql/1.0/warehouses/467af2fc060984c3", [Catalog="data_governance", Database=null, EnableAutomaticProxyDiscovery=null]),
    data_governance_Database = Source{[Name="data_governance",Kind="Database"]}[Data],
    scanman_Schema = data_governance_Database{[Name="scanman",Kind="Schema"]}[Data],
    bridge_scanman_user_project_relationship_Table = scanman_Schema{[Name="bridge_scanman_user_project_relationship",Kind="Table"]}[Data]
in
    bridge_scanman_user_project_relationship_Table
