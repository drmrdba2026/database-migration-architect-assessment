#!/usr/bin/env python3
import os, json, sys
from datetime import datetime

def validate(host, port, user, password, db, label):
    import pymssql
    print(f"\n{'='*50}")
    print(f"Validating: {label.upper()} — {host}/{db}")
    print(f"{'='*50}")
    conn = pymssql.connect(server=host, port=int(port), user=user, password=password, database=db)
    cursor = conn.cursor()
    result = {"label": label, "host": host, "database": db, "timestamp": str(datetime.utcnow()), "tables": [], "aggregates": {}}
    print("\n--- Row counts ---")
    cursor.execute("""SELECT t.name, p.rows FROM sys.tables t JOIN sys.partitions p ON t.object_id = p.object_id WHERE p.index_id IN (0,1) AND t.name NOT LIKE '%_CT' AND t.name NOT IN ('captured_columns','change_tables','ddl_history','index_columns','lsn_time_mapping','systranschemas') ORDER BY t.name""")
    for row in cursor.fetchall():
        result["tables"].append({"table": row[0], "row_count": int(row[1])})
        print(f"  {row[0]}: {int(row[1]):,} rows")
    print("\n--- Aggregates ---")
    for key, query in {"Catalog_count": "SELECT COUNT(*) FROM Catalog", "Catalog_sum_price": "SELECT CAST(SUM(Price) AS DECIMAL(10,2)) FROM Catalog", "CatalogBrands_count": "SELECT COUNT(*) FROM CatalogBrands", "CatalogTypes_count": "SELECT COUNT(*) FROM CatalogTypes"}.items():
        try:
            cursor.execute(query)
            val = cursor.fetchone()[0]
            result["aggregates"][key] = float(val) if val else 0
            print(f"  {key}: {val}")
        except Exception as e:
            result["aggregates"][key] = f"ERROR: {e}"
    conn.close()
    return result

def compare(src, tgt):
    print(f"\n{'='*50}\nRECONCILIATION DIFF\n{'='*50}")
    src_map = {t["table"]: t["row_count"] for t in src["tables"]}
    tgt_map = {t["table"]: t["row_count"] for t in tgt["tables"]}
    mismatches = []
    for table in sorted(set(src_map) | set(tgt_map)):
        s = src_map.get(table, "MISSING")
        t = tgt_map.get(table, "MISSING")
        icon = "✓" if s == t else "✗"
        if s != t: mismatches.append({"table": table, "source": s, "target": t})
        print(f"  {icon} {table}: src={s}  tgt={t}")
    print(f"\nAggregates:")
    for key in sorted(set(src["aggregates"]) | set(tgt["aggregates"])):
        s = src["aggregates"].get(key, "MISSING")
        t = tgt["aggregates"].get(key, "MISSING")
        icon = "✓" if s == t else "✗"
        if s != t: mismatches.append({"check": key, "source": s, "target": t})
        print(f"  {icon} {key}: src={s}  tgt={t}")
    print(f"\nTotal mismatches: {len(mismatches)}")
    return mismatches

if __name__ == "__main__":
    try:
        import pymssql
    except ImportError:
        import subprocess
        subprocess.run(["pip3", "install", "pymssql", "-q"])
        import pymssql
    output = {"generated": str(datetime.utcnow())}
    src = validate(os.getenv("SRC_SQL_HOST","localhost"), os.getenv("SRC_SQL_PORT","1433"), os.getenv("SRC_SQL_USER","sa"), os.getenv("SRC_SQL_PASSWORD","SqlPass!2024"), os.getenv("SRC_SQL_DB","eShopOnWeb"), "source-onprem-docker")
    output["source"] = src
    tgt = validate(os.getenv("TGT_SQL_HOST","dbmig-sqlsrv2024.database.windows.net"), "1433", os.getenv("TGT_SQL_USER","sqladmin"), os.getenv("TGT_SQL_PASSWORD","SqlMiPass!2024"), os.getenv("TGT_SQL_DB","eShopOnWeb"), "target-azure-sqldb")
    output["target"] = tgt
    output["mismatches"] = compare(src, tgt)
    output["passed"] = len(output["mismatches"]) == 0
    os.makedirs("validation", exist_ok=True)
    with open("validation/sqlserver_reconciliation.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nReport: validation/sqlserver_reconciliation.json")
    print(f"Passed: {output['passed']}")
