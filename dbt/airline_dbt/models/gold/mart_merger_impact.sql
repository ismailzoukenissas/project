SELECT
    f.OP_UNIQUE_CARRIER                                          AS carrier_key,
    f.YEAR,
    f.QUARTER,
    f.fusion_periode,
    f.carrier_group,

    COUNT(*)                                                     AS total_flights,

    -- OTP : % vols arrivés à l'heure (vols non annulés uniquement)
    ROUND(
        AVG(CASE WHEN f.CANCELLED = 0 THEN 1 - f.ARR_DEL15 END) * 100
    , 2)                                                         AS otp_pct,

    -- Retard moyen sur vols retardés uniquement
    ROUND(
        AVG(CASE WHEN f.ARR_DELAY > 0 THEN f.ARR_DELAY END)
    , 2)                                                         AS avg_arr_delay,

    -- Taux d'annulation
    ROUND(
        SUM(f.CANCELLED) * 100.0 / COUNT(*)
    , 2)                                                         AS cancellation_rate,

    -- Minutes totales par cause
    SUM(COALESCE(f.CARRIER_DELAY, 0))                           AS min_carrier,
    SUM(COALESCE(f.LATE_AIRCRAFT_DELAY, 0))                     AS min_late_aircraft,
    SUM(COALESCE(f.NAS_DELAY, 0))                               AS min_nas,
    SUM(COALESCE(f.WEATHER_DELAY, 0))                           AS min_weather,
    SUM(COALESCE(f.SECURITY_DELAY, 0))                          AS min_security,

    -- Part de chaque cause en % du total minutes retard
    ROUND(
        SUM(COALESCE(f.CARRIER_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.SECURITY_DELAY, 0)), 0)
    , 2)                                                         AS pct_carrier,

    ROUND(
        SUM(COALESCE(f.LATE_AIRCRAFT_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.SECURITY_DELAY, 0)), 0)
    , 2)                                                         AS pct_late_aircraft,

    ROUND(
        SUM(COALESCE(f.NAS_DELAY, 0)) * 100.0 /
        NULLIF(SUM(COALESCE(f.CARRIER_DELAY, 0)
             + COALESCE(f.LATE_AIRCRAFT_DELAY, 0)
             + COALESCE(f.NAS_DELAY, 0)
             + COALESCE(f.WEATHER_DELAY, 0)
             + COALESCE(f.SECURITY_DELAY, 0)), 0)
    , 2)                                                         AS pct_nas

FROM {{ ref('int_flights_enriched') }} f
WHERE f.fusion_periode != 'not_merged'
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 2, 3