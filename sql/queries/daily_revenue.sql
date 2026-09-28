-- Daily revenue aggregation
-- Populates metrics.daily_revenue from warehouse.fact_orders

INSERT INTO metrics.daily_revenue (
    report_date,
    total_orders,
    delivered_orders,
    cancelled_orders,
    gross_revenue,
    total_freight,
    net_revenue,
    avg_order_value,
    unique_customers,
    updated_at
)
SELECT
    d.full_date                                             AS report_date,
    COUNT(fo.order_key)                                     AS total_orders,
    COUNT(fo.order_key) FILTER (WHERE fo.order_status = 'delivered')    AS delivered_orders,
    COUNT(fo.order_key) FILTER (WHERE fo.order_status = 'canceled')     AS cancelled_orders,
    COALESCE(SUM(fo.total_revenue), 0)                     AS gross_revenue,
    COALESCE(SUM(fo.total_freight), 0)                     AS total_freight,
    COALESCE(SUM(fo.total_revenue - fo.total_freight), 0)  AS net_revenue,
    ROUND(AVG(fo.total_order_value), 2)                    AS avg_order_value,
    COUNT(DISTINCT fo.customer_key)                        AS unique_customers,
    NOW()                                                  AS updated_at
FROM warehouse.dim_date d
LEFT JOIN warehouse.fact_orders fo ON fo.order_date_key = d.date_key
WHERE d.full_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY d.full_date
ON CONFLICT (report_date) DO UPDATE SET
    total_orders        = EXCLUDED.total_orders,
    delivered_orders    = EXCLUDED.delivered_orders,
    cancelled_orders    = EXCLUDED.cancelled_orders,
    gross_revenue       = EXCLUDED.gross_revenue,
    total_freight       = EXCLUDED.total_freight,
    net_revenue         = EXCLUDED.net_revenue,
    avg_order_value     = EXCLUDED.avg_order_value,
    unique_customers    = EXCLUDED.unique_customers,
    updated_at          = NOW();
