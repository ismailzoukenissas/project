import duckdb
import pandas as pd
from ydata_profiling import ProfileReport
import os

BASE         = r"C:\Users\izouk\OneDrive\Desktop\projet aeroport\airline_performance"
PARQUET_2015 = f"{BASE}/data/parquet/2015.parquet"
OUTPUT       = f"{BASE}/rapport/profiling_2015.html"

print("="*60)
print("CHARGEMENT 2015...")
print("="*60)

con = duckdb.connect()

# On prend un échantillon de 200k lignes pour que le rapport
# soit rapide à générer (le fichier complet = 5.8M lignes)
df = con.execute(f"""
    SELECT *
    FROM read_parquet('{PARQUET_2015}')
    USING SAMPLE 200000
""").df()

print(f"Lignes chargées  : {len(df):,}")
print(f"Colonnes         : {list(df.columns)}")

print("\n" + "="*60)
print("GÉNÉRATION DU RAPPORT (2-5 minutes)...")
print("="*60)

profile = ProfileReport(
    df,
    title="Profiling — Airline Performance 2015",
    explorative=True,
    correlations={
        "pearson" : {"calculate": True},
        "spearman": {"calculate": False},
        "kendall" : {"calculate": False},
        "phi_k"   : {"calculate": False},
    },
    missing_diagrams={
        "bar"    : True,
        "matrix" : False,
        "heatmap": False,
    },
    interactions={"continuous": False},
    vars={
        "num": {"low_categorical_threshold": 0},
    },
)

profile.to_file(OUTPUT)

print(f"\n✅  Rapport généré : {OUTPUT}")
print("="*60)