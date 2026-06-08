# Cutover Runbook — SQL Server to Azure SQL Database

## Pre-conditions
- Azure SQL Database provisioned and accessible
- Schema migrated via EF Core migrations
- Data migrated and validation passed (zero mismatches)
- App container built and tested locally
- Firewall rules configured on Azure SQL DB

## T-60 min — Pre-cutover checks
sqlcmd -S dbmig-sqlsrv2024.database.windows.net -U sqladmin -P password -C -Q "SELECT @@VERSION, DB_NAME()"

## T-30 min — Final backup
docker exec onprem-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P password -C -d eShopOnWeb -Q "BACKUP DATABASE eShopOnWeb TO DISK='/var/opt/mssql/backup/final.bak' WITH COMPRESSION, CHECKSUM, STATS=10;"

## T-0 — Freeze source writes
docker exec onprem-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P password -C -Q "ALTER DATABASE eShopOnWeb SET RESTRICTED_USER WITH ROLLBACK IMMEDIATE;"

## T+5 — Run final validation
python3 validation/reconciliation.py

## T+10 — Switch app connection string
Update ConnectionStrings__CatalogConnection to:
Server=dbmig-sqlsrv2024.database.windows.net,1433;Database=eShopOnWeb;User Id=sqladmin;Encrypt=True;

## T+15 — Smoke test
curl -s -o /dev/null -w "HTTP Status: %{http_code}" http://localhost:8082

## Rollback trigger
If smoke tests fail OR error rate greater than 5 percent:
- ALTER DATABASE eShopOnWeb SET MULTI_USER
- Revert ConnectionStrings to source

## Post-cutover hypercare 72 hours
- Hour 1:  Verify Azure SQL DB metrics CPU DTU connections
- Hour 4:  Review slow query log
- Hour 24: Confirm automated backup ran
- Hour 72: Decommission source SQL Server container
- Hour 72: Remove SAS token and rotate passwords
