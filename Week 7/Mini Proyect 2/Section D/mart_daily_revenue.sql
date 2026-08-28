WITH staging AS (
    SELECT * FROM {{ ref('stg_coffee_sales') }}
)
SELECT 
    sale_date,
    SUM(revenue) AS total_daily_revenue,
    COUNT(*) AS total_transactions
FROM staging
GROUP BY sale_date