# Architecture — SQL Server On-Prem to Azure SQL Database

## On-premises state (Docker Compose simulation)

nginx:8080 → eshop-app:8082 → onprem-sqlserver:1433

- eShopOnWeb .NET 8 container
- SQL Server 2022 Developer Edition
- CDC enabled on 7 business tables
- Connection strings from environment variables (never hardcoded)

## Azure target state

Azure App Service for Containers
  → Azure SQL Database (Standard S3)
    Server:   dbmig-sqlsrv2024.database.windows.net
    Database: eShopOnWeb
    Location: Southeast Asia
    TLS:      1.2 minimum
    Backup:   Geo-redundant automated

## Migration method

1. CDC enabled on source SQL Server (7 tables)
2. Full backup taken and uploaded to Azure Blob Storage
3. Schema migrated via EF Core migrations
4. Data migrated via sqlcmd INSERT scripts
5. Validation confirmed zero mismatches source vs target

## CDC tables enabled

dbo_Catalog, dbo_CatalogBrands, dbo_CatalogTypes,
dbo_Orders, dbo_OrderItems, dbo_Baskets, dbo_BasketItems

## Validation results

| Table         | Source | Target | Match |
|---------------|--------|--------|-------|
| Catalog       | 12     | 12     | pass  |
| CatalogBrands | 5      | 5      | pass  |
| CatalogTypes  | 4      | 4      | pass  |
| Orders        | 0      | 0      | pass  |
| Baskets       | 0      | 0      | pass  |

Catalog sum price: 137.50 = 137.50 — pass

## Azure resources

| Resource       | Name                  | Location       |
|----------------|-----------------------|----------------|
| Resource Group | dbmig-rg              | Southeast Asia |
| Storage Account| dbmigstorage2024      | Southeast Asia |
| SQL Server     | dbmig-sqlsrv2024      | Southeast Asia |
| SQL Database   | eShopOnWeb (S3)       | Southeast Asia |

## Target selection rationale

Azure SQL Database chosen over Azure SQL Managed Instance:
- Free subscription quota restrictions on SQL MI in all tested regions
- eShopOnWeb has no SQL Agent jobs or linked servers requiring SQL MI
- Full SQL MI Bicep IaC provided in infra/bicep/sqlmi.bicep

## Assumptions

1. Docker Compose simulates on-prem VMware environment
2. Azure SQL DB used instead of SQL MI due to quota restrictions
3. EF Core migrations handle schema creation on target
4. All credentials in environment variables — never in repo
