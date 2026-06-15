import duckdb
import os

DB_PATH   = "data/airline.duckdb"
GOLD_PATH = "data/gold"

con = duckdb.connect(DB_PATH)

marts = [
    "mart_merger_impact",
    "mart_otp_monthly",
    "mart_seasonality",
]

print("\n" + "="*60)
print("EXPORT MARTS → PARQUET")
print("="*60)

for mart in marts:
    dest = f"{GOLD_PATH}/{mart}.parquet"

    print(f"\n[{mart}]")

    # Compter les lignes
    nb = con.execute(f"SELECT COUNT(*) FROM main.{mart}").fetchone()[0]
    print(f"  lignes    : {nb:,}")

    # Aperçu des colonnes
    cols = con.execute(f"DESCRIBE main.{mart}").df()["column_name"].tolist()
    print(f"  colonnes  : {cols}")

    # Export Parquet
    con.execute(f"""
        COPY main.{mart}
        TO '{dest}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    taille = round(os.path.getsize(dest) / 1024 / 1024, 2)
    print(f"  ✅ exporté : {dest} ({taille} MB)")

print("\n" + "="*60)
print("✅  Export terminé — fichiers dans data/gold/")
print("="*60)