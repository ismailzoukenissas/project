import duckdb

print("Génération de la table mart_carrier_monthly en cours...")
con = duckdb.connect()

con.execute("""
    COPY (
        SELECT
            YEAR,
            MONTH,
            DAY_OF_WEEK,
            OP_UNIQUE_CARRIER,
            ROUND(AVG(CASE WHEN CANCELLED=0 THEN 1-ARR_DEL15 END)*100,2) AS otp_pct,
            SUM(COALESCE(NAS_DELAY,0))         AS min_nas,
            SUM(COALESCE(CARRIER_DELAY,0))     AS min_carrier,
            SUM(COALESCE(WEATHER_DELAY,0))     AS min_weather,
            COUNT(*) AS total_vols
        FROM read_parquet('data/parquet/*.parquet')
        GROUP BY 1,2,3,4
        ORDER BY 1,2,3,4
    ) TO 'data/gold/mart_carrier_monthly.parquet' (FORMAT PARQUET);
""")

print("Succès ! Fichier data/gold/mart_carrier_monthly.parquet créé avec succès.")