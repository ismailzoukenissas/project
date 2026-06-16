SELECT
    f.MONTH,
    f.DAY_OF_WEEK,
    f.dep_hour,
    f.season,

    COUNT(*)                                                      AS total_flights,

    -- OTP
    ROUND(
        AVG(CASE WHEN f.CANCELLED = 0 THEN 1 - f.ARR_DEL15 END) * 100
    , 2)                                                          AS otp_pct,

    -- Retard moyen sur vols retardés
    ROUND(
        AVG(CASE WHEN f.ARR_DELAY > 0 THEN f.ARR_DELAY END)
    , 2)                                                          AS avg_delay_when_late,

    -- Part météo vs NAS (saisonnalité des causes)
    ROUND(
        SUM(COALESCE(f.WEATHER_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)), 0)
    , 2)                                                          AS pct_weather,

    ROUND(
        SUM(COALESCE(f.NAS_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)), 0)
    , 2)                                                          AS pct_nas,

    ROUND(
        SUM(COALESCE(f.CARRIER_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)), 0)
    , 2)                                                          AS pct_carrier

FROM {{ ref('int_flights_enriched') }} f
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3