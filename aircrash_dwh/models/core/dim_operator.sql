{{ config(materialized='table') }}

SELECT DISTINCT
    CASE 
        WHEN location IS NOT NULL AND POSITION(',' IN location) > 0 THEN
            TRIM(REVERSE(SPLIT_PART(REVERSE(location), ',', 1)))
        ELSE NULL
    END AS country,
    operator
FROM {{ ref('stg_airplane_crashes') }}
WHERE operator IS NOT NULL
