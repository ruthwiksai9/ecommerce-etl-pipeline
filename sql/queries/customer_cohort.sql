-- Customer cohort retention analysis
-- Classic cohort: group customers by first-order month, track activity each subsequent month

WITH customer_first_order AS (
    -- Assign each unique customer their acquisition cohort month
    SELECT
        dc.customer_unique_id,
        dc.customer_key,
        DATE_TRUNC('month', MIN(d.full_date))::DATE AS cohort_month
    FROM warehouse.fact_orders fo
    JOIN warehouse.dim_customers dc ON dc.customer_key = fo.customer_key
    JOIN warehouse.dim_date d ON d.date_key = fo.order_date_key
    GROUP BY dc.customer_unique_id, dc.customer_key
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM customer_first_order
    GROUP BY cohort_month
),
monthly_activity AS (
    -- Find all months each customer was active
    SELECT
        cfo.customer_key,
        cfo.cohort_month,
        DATE_TRUNC('month', d.full_date)::DATE AS order_month,
        SUM(fo.total_revenue) AS cohort_revenue
    FROM customer_first_order cfo
    JOIN warehouse.fact_orders fo ON fo.customer_key = cfo.customer_key
    JOIN warehouse.dim_date d ON d.date_key = fo.order_date_key
    GROUP BY cfo.customer_key, cfo.cohort_month, DATE_TRUNC('month', d.full_date)
)
INSERT INTO metrics.customer_cohort (
    cohort_month,
    order_month,
    cohort_size,
    active_customers,
    retention_rate,
    cohort_revenue
)
SELECT
    ma.cohort_month,
    ma.order_month,
    cs.cohort_size,
    COUNT(DISTINCT ma.customer_key)                                             AS active_customers,
    ROUND(COUNT(DISTINCT ma.customer_key)::NUMERIC / cs.cohort_size, 4)         AS retention_rate,
    ROUND(SUM(ma.cohort_revenue), 2)                                            AS cohort_revenue
FROM monthly_activity ma
JOIN cohort_sizes cs ON cs.cohort_month = ma.cohort_month
GROUP BY ma.cohort_month, ma.order_month, cs.cohort_size
ON CONFLICT (cohort_month, order_month) DO UPDATE SET
    cohort_size         = EXCLUDED.cohort_size,
    active_customers    = EXCLUDED.active_customers,
    retention_rate      = EXCLUDED.retention_rate,
    cohort_revenue      = EXCLUDED.cohort_revenue;
