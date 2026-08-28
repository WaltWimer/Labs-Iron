WITH raw_source AS (
    SELECT * FROM {{ source('brewbeats_raw', 'coffee_sales') }}
)
SELECT 
    CAST(date AS DATE) AS sale_date,
    CAST(datetime AS TIMESTAMP) AS sale_timestamp,
    cash_type AS payment_method,
    card AS card_details,
    CAST(money AS DECIMAL(10,2)) AS revenue,
    coffee_name
FROM raw_source