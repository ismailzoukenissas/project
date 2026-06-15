SELECT
    -- Toutes les colonnes du staging
    f.*,

    -- AX4 : heure de départ arrondie
    FLOOR(CRS_DEP_TIME / 100)                        AS dep_hour,

    -- AX4 : saison
    CASE
        WHEN MONTH IN (12, 1, 2) THEN 'Winter'
        WHEN MONTH IN (3, 4, 5)  THEN 'Spring'
        WHEN MONTH IN (6, 7, 8)  THEN 'Summer'
        ELSE                          'Fall'
    END                                              AS season,

    -- AX3 : période de fusion par carrier
    CASE
        -- United + Continental (fusion oct. 2010)
        WHEN f.OP_UNIQUE_CARRIER IN ('UA', 'CO')
             AND (f.YEAR < 2010 OR (f.YEAR = 2010 AND f.QUARTER < 4))
             THEN 'pre'
        WHEN f.OP_UNIQUE_CARRIER IN ('UA', 'CO')
             AND f.YEAR IN (2010, 2011, 2012)
             THEN 'during'
        WHEN f.OP_UNIQUE_CARRIER = 'UA'
             AND f.YEAR >= 2013
             THEN 'post'

        -- Southwest + AirTran (fusion mai 2011)
        WHEN f.OP_UNIQUE_CARRIER IN ('WN', 'FL')
             AND (f.YEAR < 2011 OR (f.YEAR = 2011 AND f.QUARTER < 2))
             THEN 'pre'
        WHEN f.OP_UNIQUE_CARRIER IN ('WN', 'FL')
             AND f.YEAR IN (2011, 2012, 2013)
             THEN 'during'
        WHEN f.OP_UNIQUE_CARRIER = 'WN'
             AND f.YEAR >= 2014
             THEN 'post'

        -- American + US Airways (fusion déc. 2013)
        WHEN f.OP_UNIQUE_CARRIER IN ('AA', 'US')
             AND f.YEAR < 2013
             THEN 'pre'
        WHEN f.OP_UNIQUE_CARRIER IN ('AA', 'US')
             AND f.YEAR IN (2013, 2014, 2015)
             THEN 'during'
        WHEN f.OP_UNIQUE_CARRIER = 'AA'
             AND f.YEAR >= 2016
             THEN 'post'

        ELSE 'not_merged'
    END                                              AS fusion_periode,

    -- AX3 : groupe post-fusion pour comparer avant/après
    CASE
        WHEN f.OP_UNIQUE_CARRIER IN ('UA', 'CO') THEN 'United Group'
        WHEN f.OP_UNIQUE_CARRIER IN ('WN', 'FL') THEN 'Southwest Group'
        WHEN f.OP_UNIQUE_CARRIER IN ('AA', 'US') THEN 'American Group'
        WHEN f.OP_UNIQUE_CARRIER IN ('DL', 'NW') THEN 'Delta Group'
        WHEN f.OP_UNIQUE_CARRIER IN ('AS', 'VX') THEN 'Alaska Group'
        ELSE 'Independent'
    END                                              AS carrier_group

FROM {{ ref('stg_flights') }} f