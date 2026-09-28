-- Star schema: fact_orders at center, dimension tables around it

CREATE TABLE IF NOT EXISTS warehouse.dim_customers (
    customer_key        SERIAL PRIMARY KEY,
    customer_id         VARCHAR(50) UNIQUE NOT NULL,
    customer_unique_id  VARCHAR(50),
    zip_code_prefix     VARCHAR(10),
    city                VARCHAR(100),
    state               VARCHAR(5),
    valid_from          TIMESTAMP DEFAULT NOW(),
    valid_to            TIMESTAMP,
    is_current          BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_products (
    product_key             SERIAL PRIMARY KEY,
    product_id              VARCHAR(50) UNIQUE NOT NULL,
    category_name           VARCHAR(100),
    weight_g                NUMERIC(10, 2),
    volume_cm3              NUMERIC(12, 2),
    photos_qty              INTEGER,
    valid_from              TIMESTAMP DEFAULT NOW(),
    valid_to                TIMESTAMP,
    is_current              BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_sellers (
    seller_key          SERIAL PRIMARY KEY,
    seller_id           VARCHAR(50) UNIQUE NOT NULL,
    zip_code_prefix     VARCHAR(10),
    city                VARCHAR(100),
    state               VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key        INTEGER PRIMARY KEY,  -- YYYYMMDD
    full_date       DATE NOT NULL,
    year            INTEGER,
    quarter         INTEGER,
    month           INTEGER,
    month_name      VARCHAR(10),
    week            INTEGER,
    day_of_month    INTEGER,
    day_of_week     INTEGER,
    day_name        VARCHAR(10),
    is_weekend      BOOLEAN,
    is_holiday      BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS warehouse.fact_orders (
    order_key               SERIAL PRIMARY KEY,
    order_id                VARCHAR(50) UNIQUE NOT NULL,
    customer_key            INTEGER REFERENCES warehouse.dim_customers(customer_key),
    order_date_key          INTEGER REFERENCES warehouse.dim_date(date_key),
    delivery_date_key       INTEGER REFERENCES warehouse.dim_date(date_key),
    order_status            VARCHAR(20),
    total_items             INTEGER,
    total_revenue           NUMERIC(12, 2),
    total_freight           NUMERIC(12, 2),
    total_order_value       NUMERIC(12, 2),
    delivery_days           INTEGER,
    is_delivered_on_time    BOOLEAN,
    loaded_at               TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS warehouse.fact_order_items (
    item_key        SERIAL PRIMARY KEY,
    order_id        VARCHAR(50) NOT NULL,
    order_item_id   INTEGER NOT NULL,
    product_key     INTEGER REFERENCES warehouse.dim_products(product_key),
    seller_key      INTEGER REFERENCES warehouse.dim_sellers(seller_key),
    price           NUMERIC(10, 2),
    freight_value   NUMERIC(10, 2),
    total_value     NUMERIC(10, 2),
    loaded_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE (order_id, order_item_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON warehouse.fact_orders(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON warehouse.fact_orders(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_status ON warehouse.fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_fact_items_product ON warehouse.fact_order_items(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_items_seller ON warehouse.fact_order_items(seller_key);
