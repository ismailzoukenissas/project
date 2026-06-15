import duckdb
import os
import time

con = duckdb.connect()

DATA_RAW     = "data/raw"
DATA_PARQUET = "data/parquet"
YEARS = range(2009, 2019)

print("\n" + "="*60)
print("CONVERSION CSV → PARQUET (10 années)")
print("="*60)

total_debut = time.time()

for year in YEARS:
    src  = f"{DATA_RAW}/{year}.csv"
    dest = f"{DATA_PARQUET}/{year}.parquet"

    if not os.path.exists(src):
        print(f"[{year}] ❌ CSV introuvable — ignoré")
        continue

    if os.path.exists(dest):
        print(f"[{year}] ⏭️  Parquet déjà existant — ignoré")
        continue

    print(f"[{year}] ⏳ Conversion en cours...", end=" ", flush=True)
    debut = time.time()

    con.execute(f"""
        COPY (
            SELECT
                -- Identifiants
                FL_DATE,
                OP_CARRIER                                     AS OP_UNIQUE_CARRIER,
                OP_CARRIER_FL_NUM,

                -- Temporalité extraite depuis FL_DATE
                YEAR(CAST(FL_DATE AS DATE))                    AS YEAR,
                MONTH(CAST(FL_DATE AS DATE))                   AS MONTH,
                QUARTER(CAST(FL_DATE AS DATE))                 AS QUARTER,
                DAYOFWEEK(CAST(FL_DATE AS DATE))               AS DAY_OF_WEEK,

                -- Aéroports
                ORIGIN,
                DEST,

                -- Horaires départ
                CRS_DEP_TIME,
                DEP_TIME,
                DEP_DELAY,
                CASE
                    WHEN CANCELLED = 1 THEN NULL
                    WHEN ARR_DELAY >= 15 THEN 1
                    ELSE 0
                END                                            AS ARR_DEL15,
                CASE
                    WHEN CANCELLED = 1 THEN NULL
                    WHEN DEP_DELAY >= 15 THEN 1
                    ELSE 0
                END                                            AS DEP_DEL15,
                TAXI_OUT,
                WHEELS_OFF,

                -- Horaires arrivée
                WHEELS_ON,
                TAXI_IN,
                CRS_ARR_TIME,
                ARR_TIME,
                ARR_DELAY,

                -- Statut du vol
                CANCELLED,
                CANCELLATION_CODE,
                DIVERTED,

                -- Durées
                CRS_ELAPSED_TIME,
                ACTUAL_ELAPSED_TIME,
                AIR_TIME,
                DISTANCE,

                -- Causes de retard
                CARRIER_DELAY,
                WEATHER_DELAY,
                NAS_DELAY,
                SECURITY_DELAY,
                LATE_AIRCRAFT_DELAY

                -- Unnamed: 27 ignorée volontairement

            FROM read_csv_auto('{src}')
        )
        TO '{dest}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    duree  = round(time.time() - debut, 1)
    taille = round(os.path.getsize(dest) / 1024 / 1024, 1)
    print(f"✅  {duree}s  →  {taille} MB")

# ─────────────────────────────────────────────
# Vérification finale
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("VERIFICATION — Comptage des vols par fichier Parquet")
print("="*60)

verif = con.execute(f"""
    SELECT
        YEAR,
        COUNT(*)                                                    AS total_vols,
        COUNT(DISTINCT OP_UNIQUE_CARRIER)                           AS nb_carriers,
        ROUND(AVG(CASE WHEN ARR_DEL15 = 1 THEN 100.0 ELSE 0 END), 2) AS pct_retardes
    FROM read_parquet('{DATA_PARQUET}/*.parquet')
    GROUP BY 1
    ORDER BY 1
""").df()

print(verif.to_string(index=False))

duree_totale = round(time.time() - total_debut, 1)
print(f"\n✅  Conversion terminée en {duree_totale}s")
print("="*60)