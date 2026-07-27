
--Top 10 customers by revenue.

--Month-over-month sales growth (usando funciones de ventana).

--Ranking customers by total revenue.

--Running total sales by month.

--Highest selling product per category.



SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;

--  Month-over-Month (MoM) Sales Growth
WITH monthly_sales AS (
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month, -- Use TO_CHAR for PostgreSQL if needed
        SUM(o.quantity * o.unit_price) AS current_month_revenue
    FROM orders o
    GROUP BY sales_month
),
mom_calc AS (
    SELECT 
        sales_month,
        current_month_revenue,
        LAG(current_month_revenue, 1) OVER (ORDER BY sales_month) AS previous_month_revenue
    FROM monthly_sales
)
SELECT 
    sales_month,
    current_month_revenue,
    previous_month_revenue,
    ROUND(
        ((current_month_revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0)) * 100, 2
    ) AS mom_growth_percentage
FROM mom_calc;

-- Rank Customers Based on Total Revenue (Using Window Functions)
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue,
    RANK() OVER (ORDER BY SUM(o.quantity * o.unit_price) DESC) as revenue_rank
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name;

--  Running Total Sales by Month
WITH monthly_summary AS (
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
        SUM(o.quantity * o.unit_price) AS monthly_revenue
    FROM orders o
    GROUP BY sales_month
)
SELECT 
    sales_month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY sales_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM monthly_summary;

-- 5. ADVANCED SQL: Find Highest Selling Product Per Category
WITH product_sales AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(o.quantity * o.unit_price) AS product_revenue,
        ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(o.quantity * o.unit_price) DESC) as rn
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    product_revenue
FROM product_sales
WHERE rn = 1;