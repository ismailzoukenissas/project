SELECT
    f.OP_UNIQUE_CARRIER                                          AS carrier_key,
    f.YEAR,
    f.MONTH,
    f.season,

    COUNT(*)                                                     AS total_flights,

    -- OTP mensuel
    ROUND(
        AVG(CASE WHEN f.CANCELLED = 0 THEN 1 - f.ARR_DEL15 END) * 100
    , 2)                                                         AS otp_pct,

    -- Retard moyen
    ROUND(
        AVG(CASE WHEN f.ARR_DELAY > 0 THEN f.ARR_DELAY END)
    , 2)                                                         AS avg_arr_delay,

    -- Taux annulation
    ROUND(
        SUM(f.CANCELLED) * 100.0 / COUNT(*)
    , 2)                                                         AS cancellation_rate,

    -- Causes en minutes
    SUM(COALESCE(f.CARRIER_DELAY, 0))                           AS min_carrier,
    SUM(COALESCE(f.WEATHER_DELAY, 0))                           AS min_weather,
    SUM(COALESCE(f.NAS_DELAY, 0))                               AS min_nas,
    SUM(COALESCE(f.LATE_AIRCRAFT_DELAY, 0))                     AS min_late_aircraft

FROM {{ ref('int_flights_enriched') }} f
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3