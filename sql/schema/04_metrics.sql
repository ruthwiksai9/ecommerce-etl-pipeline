-- Metrics schema: pre-aggregated reporting tables for BI/dashboards

-- Daily revenue summary
CREATE TABLE IF NOT EXISTS metrics.daily_revenue (
    report_date         DATE PRIMARY KEY,
    total_orders        INTEGER,
    delivered_orders    INTEGER,
    cancelled_orders    INTEGER,
    gross_revenue       NUMERIC(14, 2),
    total_freight       NUMERIC(14, 2),
    net_revenue         NUMERIC(14, 2),
    avg_order_value     NUMERIC(10, 2),
    unique_customers    INTEGER,
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- Product category performance
CREATE TABLE IF NOT EXISTS metrics.category_performance (
    report_month        DATE,
    category_name       VARCHAR(100),
    total_orders        INTEGER,
    units_sold          INTEGER,
    gross_revenue       NUMERIC(14, 2),
    avg_price           NUMERIC(10, 2),
    avg_freight_ratio   NUMERIC(6, 4),
    PRIMARY KEY (report_month, category_name)
);

-- Customer cohort retention
CREATE TABLE IF NOT EXISTS metrics.customer_cohort (
    cohort_month        DATE,
    order_month         DATE,
    cohort_size         INTEGER,
    active_customers    INTEGER,
    retention_rate      NUMERIC(6, 4),
    cohort_revenue      NUMERIC(14, 2),
    PRIMARY KEY (cohort_month, order_month)
);

-- Seller performance
CREATE TABLE IF NOT EXISTS metrics.seller_performance (
    report_month        DATE,
    seller_key          INTEGER REFERENCES warehouse.dim_sellers(seller_key),
    total_orders        INTEGER,
    total_revenue       NUMERIC(14, 2),
    avg_delivery_days   NUMERIC(6, 2),
    on_time_rate        NUMERIC(6, 4),
    PRIMARY KEY (report_month, seller_key)
);

CREATE INDEX IF NOT EXISTS idx_metrics_daily_revenue_date ON metrics.daily_revenue(report_date);
CREATE INDEX IF NOT EXISTS idx_metrics_category_month ON metrics.category_performance(report_month);
CREATE INDEX IF NOT EXISTS idx_metrics_cohort ON metrics.customer_cohort(cohort_month, order_month);
