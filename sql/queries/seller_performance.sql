-- Monthly seller performance scorecard

INSERT INTO metrics.seller_performance (
    report_month,
    seller_key,
    total_orders,
    total_revenue,
    avg_delivery_days,
    on_time_rate
)
SELECT
    DATE_TRUNC('month', d.full_date)::DATE              AS report_month,
    ds.seller_key,
    COUNT(DISTINCT fo.order_id)                         AS total_orders,
    ROUND(SUM(foi.total_value), 2)                      AS total_revenue,
    ROUND(AVG(fo.delivery_days), 2)                     AS avg_delivery_days,
    ROUND(
        COUNT(fo.order_key) FILTER (WHERE fo.is_delivered_on_time = TRUE)::NUMERIC
        / NULLIF(COUNT(fo.order_key), 0),
        4
    )                                                   AS on_time_rate
FROM warehouse.fact_order_items foi
JOIN warehouse.dim_sellers ds ON ds.seller_key = foi.seller_key
JOIN warehouse.fact_orders fo ON fo.order_id = foi.order_id
JOIN warehouse.dim_date d ON d.date_key = fo.order_date_key
WHERE fo.order_status = 'delivered'
GROUP BY DATE_TRUNC('month', d.full_date), ds.seller_key
ON CONFLICT (report_month, seller_key) DO UPDATE SET
    total_orders        = EXCLUDED.total_orders,
    total_revenue       = EXCLUDED.total_revenue,
    avg_delivery_days   = EXCLUDED.avg_delivery_days,
    on_time_rate        = EXCLUDED.on_time_rate;
