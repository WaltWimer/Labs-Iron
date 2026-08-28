USE WAREHOUSE lab_wh_WWH;
USE DATABASE retail_db_WWH;

-- Lab 4: Combine structured CSV and semi-structured JSON orders into a single view
CREATE OR REPLACE VIEW analytics.v_all_line_items AS
SELECT
  order_id, customer_name, product, quantity AS qty,
  unit_price, order_date, region, 'csv' AS source
FROM raw.orders
UNION ALL
SELECT
  data:order_id::INT, data:customer.name::STRING,
  f.value:product::STRING, f.value:qty::INT,
  f.value:price::NUMBER(10,2), CURRENT_DATE(),
  data:customer.city::STRING, 'json' AS source
FROM raw.orders_json, LATERAL FLATTEN(input => data:items) f;

-- Check revenue by region
SELECT
  region,
  SUM(qty * unit_price) AS revenue,
  COUNT(DISTINCT order_id) AS orders
FROM analytics.v_all_line_items
GROUP BY region
ORDER BY revenue DESC;


-- Lab 5: Time travel and cloning
-- Test accidental deletion and recovery
DELETE FROM raw.orders WHERE region = 'North';

-- Restore table using time travel
CREATE OR REPLACE TABLE raw.orders AS
SELECT * FROM raw.orders BEFORE(STATEMENT => LAST_QUERY_ID());

-- Create a zero-copy clone for safe testing
CREATE OR REPLACE TABLE raw.orders_backup CLONE raw.orders;


-- Lab 6: Role-Based Access Control (RBAC)
CREATE OR REPLACE ROLE analyst_WWH;
GRANT USAGE ON WAREHOUSE lab_wh_WWH TO ROLE analyst_WWH;
GRANT USAGE ON DATABASE retail_db_WWH TO ROLE analyst_WWH;
GRANT USAGE ON SCHEMA retail_db_WWH.analytics TO ROLE analyst_WWH;
GRANT SELECT ON ALL VIEWS IN SCHEMA retail_db_WWH.analytics TO ROLE analyst_WWH;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA retail_db_WWH.analytics TO ROLE analyst_WWH;


-- Lab 7: Performance testing with sample data
SELECT
  o.o_orderpriority,
  COUNT(*)               AS order_count,
  SUM(o.o_totalprice)    AS total_value
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF100.ORDERS o
JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF100.CUSTOMER c
  ON o.o_custkey = c.c_custkey
GROUP BY o.o_orderpriority
ORDER BY total_value DESC;

-- Adjust warehouse size for testing
ALTER WAREHOUSE lab_wh_WWH SET WAREHOUSE_SIZE = 'SMALL';
ALTER WAREHOUSE lab_wh_WWH SET WAREHOUSE_SIZE = 'XSMALL';


-- Lab 8: Streams and Tasks (Change Data Capture)
CREATE OR REPLACE STREAM raw.orders_stream ON TABLE raw.orders;

-- Insert a new record to trigger the stream
INSERT INTO raw.orders VALUES
  (2001, 'Meera Nair', 'Webcam', 'Electronics', 1, 2499.00, CURRENT_DATE(), 'West');

-- Create target table and scheduled task
CREATE OR REPLACE TABLE analytics.new_orders_log (
  order_id INT, customer_name STRING, product STRING,
  logged_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TASK raw.process_new_orders
  WAREHOUSE = lab_wh_WWH
  SCHEDULE = '1 MINUTE'
WHEN
  SYSTEM$STREAM_HAS_DATA('raw.orders_stream')
AS
  INSERT INTO analytics.new_orders_log (order_id, customer_name, product)
  SELECT order_id, customer_name, product
  FROM raw.orders_stream
  WHERE METADATA$ACTION = 'INSERT';

-- Resume and suspend the task
ALTER TASK raw.process_new_orders RESUME;
-- Remember to suspend it when finished to avoid extra credit consumption
ALTER TASK raw.process_new_orders SUSPEND;