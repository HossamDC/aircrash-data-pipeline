{{ config(materialized='table') }}

SELECT DISTINCT
    aircraft_type_full AS full_type,
    aircraft_maker,
    SPLIT_PART(aircraft_type_full, ' ', 1) AS model_prefix
FROM {{ ref('stg_airplane_crashes') }}
WHERE aircraft_type_full IS NOT NULL

