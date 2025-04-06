WITH distinct_operators AS (
    SELECT DISTINCT operator
    FROM {{ ref('stg_airplane_crashes') }}
    WHERE operator IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY operator) AS operator_id,
    operator
FROM distinct_operators
