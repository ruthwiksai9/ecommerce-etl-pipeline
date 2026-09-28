-- Staging tables mirror source schema exactly (no transformations)

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id                        VARCHAR(50) PRIMARY KEY,
    customer_id                     VARCHAR(50) NOT NULL,
    order_status                    VARCHAR(20),
    order_purchase_timestamp        TIMESTAMP,
    order_approved_at               TIMESTAMP,
    order_delivered_carrier_date    TIMESTAMP,
    order_delivered_customer_date   TIMESTAMP,
    order_estimated_delivery_date   TIMESTAMP,
    loaded_at                       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_id            VARCHAR(50) NOT NULL,
    order_item_id       INTEGER NOT NULL,
    product_id          VARCHAR(50) NOT NULL,
    seller_id           VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price               NUMERIC(10, 2),
    freight_value       NUMERIC(10, 2),
    loaded_at           TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id             VARCHAR(50) PRIMARY KEY,
    customer_unique_id      VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city           VARCHAR(100),
    customer_state          VARCHAR(5),
    loaded_at               TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id                  VARCHAR(50) PRIMARY KEY,
    product_category_name       VARCHAR(100),
    product_name_lenght         INTEGER,
    product_description_lenght  INTEGER,
    product_photos_qty          INTEGER,
    product_weight_g            NUMERIC(10, 2),
    product_length_cm           NUMERIC(10, 2),
    product_height_cm           NUMERIC(10, 2),
    product_width_cm            NUMERIC(10, 2),
    loaded_at                   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.sellers (
    seller_id               VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix  VARCHAR(10),
    seller_city             VARCHAR(100),
    seller_state            VARCHAR(5),
    loaded_at               TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.order_payments (
    order_id                VARCHAR(50) NOT NULL,
    payment_sequential      INTEGER NOT NULL,
    payment_type            VARCHAR(30),
    payment_installments    INTEGER,
    payment_value           NUMERIC(10, 2),
    loaded_at               TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (order_id, payment_sequential)
);
