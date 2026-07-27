-- 1. Find top 10 customers by revenue.
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Find month-over-month sales growth.
WITH monthly_sales AS (
    SELECT 
        strftime('%Y-%m', order_date) AS sales_month,
        SUM(quantity * unit_price) AS current_month_revenue
    FROM orders
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
        ((current_month_revenue - previous_month_revenue) * 100.0) / NULLIF(previous_month_revenue, 0), 2
    ) AS mom_growth_percentage
FROM mom_calc;

-- 3. Find customers who ordered in consecutive months.
WITH monthly_orders AS (
    SELECT DISTINCT 
        c.customer_id, 
        c.customer_name, 
        strftime('%Y-%m', o.order_date) AS order_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
),
month_diffs AS (
    SELECT 
        customer_name,
        order_month,
        LAG(order_month) OVER (PARTITION BY customer_id ORDER BY order_month) AS prev_month
    FROM monthly_orders
)
SELECT DISTINCT customer_name
FROM month_diffs
WHERE prev_month = strftime('%Y-%m', date(order_month || '-01', '-1 month'));

-- 4. Find products never ordered.
SELECT 
    p.product_id, 
    p.product_name 
FROM products p 
LEFT JOIN orders o ON p.product_id = o.product_id 
WHERE o.order_id IS NULL;

-- 5. Find revenue contribution percentage by category.
WITH category_revenue AS (
    SELECT 
        p.category, 
        SUM(o.quantity * o.unit_price) AS rev
    FROM orders o 
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
),
total_revenue AS (
    SELECT SUM(rev) AS total FROM category_revenue
)
SELECT 
    category,
    ROUND((rev / total) * 100, 2) AS contribution_percentage
FROM category_revenue, total_revenue;



-- SECTION B: Q2. Advanced SQL


-- 1. Rank customers based on total revenue.
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_revenue,
    RANK() OVER (ORDER BY SUM(o.quantity * o.unit_price) DESC) AS revenue_rank
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name;

-- 2. Find running total sales by month.
WITH monthly_summary AS (
    SELECT 
        strftime('%Y-%m', order_date) AS sales_month,
        SUM(quantity * unit_price) AS monthly_revenue
    FROM orders
    GROUP BY sales_month
)
SELECT 
    sales_month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY sales_month) AS running_total_revenue
FROM monthly_summary;

-- 3. Find the highest selling product per category.
WITH product_sales AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(o.quantity * o.unit_price) AS total_revenue,
        ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(o.quantity * o.unit_price) DESC) as rn
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue
FROM product_sales
WHERE rn = 1;

-- 4. Find 7-day rolling average sales.
WITH daily_sales AS (
    SELECT 
        order_date, 
        SUM(quantity * unit_price) AS daily_revenue
    FROM orders
    GROUP BY order_date
)
SELECT 
    order_date,
    daily_revenue,
    AVG(daily_revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_avg
FROM daily_sales;