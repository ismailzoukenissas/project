import duckdb
import pandas as pd
import os

con = duckdb.connect()

DATA_PATH = "data/raw"
YEARS = range(2009, 2019)

# Colonnes REELLES trouvées dans le dataset (noms exacts Kaggle)
COLONNES_REQUISES = [
    "OP_CARRIER",        # = OP_UNIQUE_CARRIER dans d'autres versions
    "FL_DATE",           # contient année/mois/jour à extraire
    "ARR_DELAY",
    "DEP_DELAY",
    "CANCELLED",
    "CANCELLATION_CODE",
    "CARRIER_DELAY",
    "LATE_AIRCRAFT_DELAY",
    "NAS_DELAY",
    "WEATHER_DELAY",
    "SECURITY_DELAY",
    "CRS_DEP_TIME",
    "DISTANCE",
    "DIVERTED",
]

print("\n" + "="*60)
print("ETAPE 1 — Colonnes disponibles par année")
print("="*60)

rapport_lines = ["# Rapport d'audit schémas\n\n"]

for year in YEARS:
    path = f"{DATA_PATH}/{year}.csv"
    if not os.path.exists(path):
        print(f"[{year}] ❌ Fichier introuvable")
        rapport_lines.append(f"## {year}\n- fichier manquant\n\n")
        continue

    cols_dispo = con.execute(f"""
        SELECT column_name
        FROM (DESCRIBE SELECT * FROM read_csv_auto('{path}') LIMIT 0)
    """).df()["column_name"].tolist()

    manquantes = [c for c in COLONNES_REQUISES if c not in cols_dispo]
    statut = "✅" if not manquantes else "⚠️ "
    print(f"[{year}] {statut}  {len(cols_dispo)} colonnes | manquantes : {manquantes if manquantes else 'aucune'}")

    rapport_lines.append(f"## {year}\n")
    rapport_lines.append(f"- colonnes totales : {len(cols_dispo)}\n")
    rapport_lines.append(f"- toutes colonnes  : {cols_dispo}\n")
    rapport_lines.append(f"- manquantes       : {manquantes}\n\n")

print("\n" + "="*60)
print("ETAPE 2 — Codes IATA par année (extraction depuis FL_DATE)")
print("="*60)

# FL_DATE contient l'année → on l'extrait avec YEAR()
iata = con.execute(f"""
    SELECT
        YEAR(CAST(FL_DATE AS DATE))   AS annee,
        OP_CARRIER                    AS code,
        COUNT(*)                      AS nb_vols
    FROM read_csv_auto('{DATA_PATH}/*.csv', union_by_name=true)
    GROUP BY 1, 2
    ORDER BY 2, 1
""").df()

pivot = iata.pivot(index="code", columns="annee", values="nb_vols").fillna(0).astype(int)
print("\n", pivot.to_string())

print("\n--- Carriers fusionnés détectés ---")
for code in pivot.index:
    annees_actives = [y for y in pivot.columns if pivot.loc[code, y] > 0]
    if annees_actives and max(annees_actives) < 2018:
        print(f"  {code} : actif {min(annees_actives)} → {max(annees_actives)}  ← fusion probable")

rapport_lines.append("## Transitions IATA\n")
rapport_lines.append(pivot.to_string() + "\n\n")

print("\n" + "="*60)
print("ETAPE 3 — Volumétrie par année")
print("="*60)

volumes = con.execute(f"""
    SELECT
        YEAR(CAST(FL_DATE AS DATE))       AS annee,
        COUNT(*)                          AS total_vols,
        SUM(CANCELLED)                    AS vols_annules,
        COUNT(DISTINCT OP_CARRIER)        AS nb_carriers
    FROM read_csv_auto('{DATA_PATH}/*.csv', union_by_name=true)
    GROUP BY 1
    ORDER BY 1
""").df()

print(volumes.to_string(index=False))
rapport_lines.append("## Volumétrie\n")
rapport_lines.append(volumes.to_string(index=False) + "\n\n")

print("\n" + "="*60)
print("ETAPE 4 — Taux de nulls (2015 comme référence)")
print("="*60)

path_2015 = f"{DATA_PATH}/2015.csv"
if os.path.exists(path_2015):
    null_check = con.execute(f"""
        SELECT
            COUNT(*)                                                       AS total,
            SUM(CASE WHEN ARR_DELAY           IS NULL THEN 1 ELSE 0 END)  AS null_arr_delay,
            SUM(CASE WHEN CARRIER_DELAY       IS NULL THEN 1 ELSE 0 END)  AS null_carrier_delay,
            SUM(CASE WHEN LATE_AIRCRAFT_DELAY IS NULL THEN 1 ELSE 0 END)  AS null_late_aircraft,
            SUM(CASE WHEN NAS_DELAY           IS NULL THEN 1 ELSE 0 END)  AS null_nas_delay,
            SUM(CASE WHEN WEATHER_DELAY       IS NULL THEN 1 ELSE 0 END)  AS null_weather_delay,
            SUM(CASE WHEN CRS_DEP_TIME        IS NULL THEN 1 ELSE 0 END)  AS null_dep_time,
            SUM(CASE WHEN CANCELLED           IS NULL THEN 1 ELSE 0 END)  AS null_cancelled
        FROM read_csv_auto('{path_2015}')
    """).df()

    total = null_check["total"].iloc[0]
    print(f"  Total vols 2015 : {total:,}\n")
    rapport_lines.append("## Nulls sur 2015\n")
    for col in null_check.columns[1:]:
        n   = null_check[col].iloc[0]
        pct = round(n / total * 100, 2)
        normal = pct > 50 and "delay" in col.lower() and col != "null_arr_delay"
        flag = "✅ normal" if normal else ("⚠️  PROBLEME" if pct > 5 else "✅")
        print(f"  {col.replace('null_',''):<25} : {pct:>6}%  {flag}")
        rapport_lines.append(f"- {col.replace('null_','')} : {pct}%\n")

print("\n" + "="*60)
print("ETAPE 5 — Décisions à documenter")
print("="*60)

decisions = """
## Décisions suite à l'audit

### Renommages à appliquer dans stg_flights.sql
- OP_CARRIER           → renommer en OP_UNIQUE_CARRIER
- FL_DATE              → extraire YEAR, MONTH, QUARTER, DAY_OF_WEEK via fonctions date
- ARR_DEL15            → à calculer : CASE WHEN ARR_DELAY >= 15 THEN 1 ELSE 0 END
- DEP_DEL15            → à calculer : CASE WHEN DEP_DELAY >= 15 THEN 1 ELSE 0 END

### Notes fusions (à compléter après lecture étape 2)
- CO (Continental) : actif jusqu'à ____  → merged_into = UA
- FL (AirTran)     : actif jusqu'à ____  → merged_into = WN
- US (US Airways)  : actif jusqu'à ____  → merged_into = AA
"""

rapport_lines.append(decisions)

with open("DECISIONS.md", "w", encoding="utf-8") as f:
    f.writelines(rapport_lines)

print(decisions)
print("="*60)
print("✅  Audit terminé — résultats dans DECISIONS.md")
print("="*60)