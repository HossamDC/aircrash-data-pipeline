{{ config(materialized='table') }}
SELECT
  crash_date,
  location,
  operator,
  type AS aircraft_type_full,
  TRIM(SPLIT_PART(type, ' ', 1)) AS aircraft_maker,
  aboard,
  fatalities,
  ground,
  survivors,
  is_fatal,
  crash_severity,
  year
FROM {{ source('spectrum_schema', 'airplane_crashes_parquet') }}
--WHERE year >= 2008
WHERE year IS NOT NULL
