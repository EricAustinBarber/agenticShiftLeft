let
    Source = Databricks.Catalogs("adb-751266416173271.11.azuredatabricks.net", "/sql/1.0/warehouses/467af2fc060984c3", [Catalog="data_governance", Database=null, EnableAutomaticProxyDiscovery=null]),
    data_governance_Database = Source{[Name="data_governance",Kind="Database"]}[Data],
    scanman_Schema = data_governance_Database{[Name="scanman",Kind="Schema"]}[Data],
    scanman_refresh_audit_View = scanman_Schema{[Name="scanman_refresh_audit",Kind="View"]}[Data]
in
    scanman_refresh_audit_View
