-- Monthly category performance
-- Joins fact_order_items → dim_products → fact_orders for full context

INSERT INTO metrics.category_performance (
    report_month,
    category_name,
    total_orders,
    units_sold,
    gross_revenue,
    avg_price,
    avg_freight_ratio
)
SELECT
    DATE_TRUNC('month', d.full_date)::DATE          AS report_month,
    dp.category_name,
    COUNT(DISTINCT foi.order_id)                    AS total_orders,
    COUNT(foi.item_key)                             AS units_sold,
    ROUND(SUM(foi.total_value), 2)                  AS gross_revenue,
    ROUND(AVG(foi.price), 2)                        AS avg_price,
    ROUND(AVG(foi.freight_value / NULLIF(foi.total_value, 0)), 4) AS avg_freight_ratio
FROM warehouse.fact_order_items foi
JOIN warehouse.dim_products dp ON dp.product_key = foi.product_key
JOIN warehouse.fact_orders fo ON fo.order_id = foi.order_id
JOIN warehouse.dim_date d ON d.date_key = fo.order_date_key
WHERE fo.order_status = 'delivered'
GROUP BY DATE_TRUNC('month', d.full_date), dp.category_name
ON CONFLICT (report_month, category_name) DO UPDATE SET
    total_orders        = EXCLUDED.total_orders,
    units_sold          = EXCLUDED.units_sold,
    gross_revenue       = EXCLUDED.gross_revenue,
    avg_price           = EXCLUDED.avg_price,
    avg_freight_ratio   = EXCLUDED.avg_freight_ratio;
