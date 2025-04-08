{{ config(materialized='table') }}

SELECT DISTINCT
    crash_date AS date,
    EXTRACT(year FROM crash_date) AS year,
    EXTRACT(month FROM crash_date) AS month,
    EXTRACT(day FROM crash_date) AS day
FROM {{ ref('stg_airplane_crashes') }}
WHERE crash_date IS NOT NULL
