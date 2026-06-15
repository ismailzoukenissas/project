import duckdb
import os

BASE      = r"C:\Users\izouk\OneDrive\Desktop\projet aeroport\airline_performance"
GOLD      = f"{BASE}/data/gold"
TABLEAU   = f"{BASE}/dashboard/tableau_data"

os.makedirs(TABLEAU, exist_ok=True)

con = duckdb.connect()

exports = [
    "mart_merger_impact",
    "mart_otp_monthly",
    "mart_seasonality",
]

print("="*60)
print("EXPORT → CSV pour Tableau")
print("="*60)

for mart in exports:
    src  = f"{GOLD}/{mart}.parquet"
    dest = f"{TABLEAU}/{mart}.csv"

    df = con.execute(f"SELECT * FROM read_parquet('{src}')").df()
    df.to_csv(dest, index=False)

    print(f"✅  {mart}.csv  ({len(df):,} lignes)")

# Copier aussi dim_carrier
import shutil
shutil.copy(
    f"{BASE}/dbt/airline_dbt/seeds/dim_carrier.csv",
    f"{TABLEAU}/dim_carrier.csv"
)
print(f"✅  dim_carrier.csv")

print("="*60)
print(f"✅  Fichiers prêts dans : {TABLEAU}")
print("="*60)