{{ config(materialized='table') }}

SELECT
  crash_date,
  location,
  operator,
  type,
  aircraft_maker,
  aboard,
  fatalities,
  ground,
  survivors,
  is_fatal,
  crash_severity,
  year,
  month
FROM {{ source('spectrum_schema', 'airplane_crashes_parquet') }}
