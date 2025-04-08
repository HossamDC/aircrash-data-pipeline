{{ config(materialized='table') }}

SELECT
    crash_date,
    location,
    CASE 
        WHEN location IS NOT NULL AND POSITION(',' IN location) > 0 THEN
            TRIM(REVERSE(SPLIT_PART(REVERSE(location), ',', 1)))
        ELSE NULL
    END AS country,
    operator,
    aircraft_type_full AS aircraft_type ,
    aboard,
    fatalities,
    ground,
    survivors,
    is_fatal,
    crash_severity,
    year
FROM {{ ref('stg_airplane_crashes') }}
-- WHERE year >=2008 