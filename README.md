# Database Migration Architect Assessment

## SQL Server on-prem to Azure SQL Managed Instance

### Tracks covered
- SQL Server (eShopOnWeb → Azure SQL Managed Instance) — primary track
- MySQL (PetClinic → Azure Database for MySQL Flexible Server) — dry-run scripts
- PostgreSQL (FastAPI → Azure Database for PostgreSQL Flexible Server) — dry-run scripts

### Minimum proof points
- [x] Working container image — eShopOnWeb + SQL Server 2022
- [x] Migrated database path — native backup + dry-run restore to Azure SQL MI
- [x] Validation script — reconciliation.py with row counts and FK checks
- [x] CI/CD run — GitHub Actions pipeline
- [x] Architecture + runbook — docs/architecture.md + docs/cutover-runbook.md

### Repo structure
- apps/          — forked application repos (submodules)
- docker/        — Dockerfiles and docker-compose
- discovery/     — inventory scripts and crawler output
- migration/     — migration scripts for all three tracks
- validation/    — reconciliation and smoke test scripts
- cicd/          — GitHub Actions pipeline
- infra/         — Bicep IaC templates
- docs/          — architecture, runbook, evidence files
