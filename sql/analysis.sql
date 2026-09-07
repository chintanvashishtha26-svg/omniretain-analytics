

WITH clean_orders AS (
    SELECT 
        "Customer ID" AS customer_id,
        "Order ID" AS order_id,
        TO_DATE("Order Date", 'YYYY-MM-DD') AS order_date,
        CAST("Sales" AS NUMERIC(10, 2)) AS sales_amount
    FROM superstore_orders
    WHERE "Sales" > 0
),

snapshot AS (
    
    SELECT MAX(order_date) + INTERVAL '1 day' AS ref_date
    FROM clean_orders
),

customer_metrics AS (
    SELECT 
        c.customer_id,
        (s.ref_date - MAX(c.order_date)) AS recency_days,
        COUNT(DISTINCT c.order_id) AS total_orders,
        ROUND(SUM(c.sales_amount)::NUMERIC, 2) AS total_spent,
        ROUND(AVG(c.sales_amount)::NUMERIC, 2) AS avg_order_value
    FROM clean_orders c
    CROSS JOIN snapshot s
    GROUP BY c.customer_id, s.ref_date
),

rfm_ranks AS (
    SELECT 
        customer_id,
        recency_days,
        total_orders,
        total_spent,
        avg_order_value,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY total_spent ASC) AS m_score
    FROM customer_metrics
)

SELECT 
    customer_id,
    recency_days,
    total_orders AS frequency,
    total_spent AS monetary,
    avg_order_value,
    r_score,
    f_score,
    m_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 3 AND f_score < 3 THEN 'Promising'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score < 3 THEN 'Lost'
        ELSE 'Regular'
    END AS segment
FROM rfm_ranks
ORDER BY total_spent DESC;
