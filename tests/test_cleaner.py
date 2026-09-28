import pandas as pd

from src.transform.cleaner import clean_customers, clean_order_items, clean_orders, clean_products


@pytest.fixture
def sample_orders():
    return pd.DataFrame({
        "order_id": ["o1", "o2", "o3", None],
        "customer_id": ["c1", "c2", None, "c4"],
        "order_status": ["DELIVERED", "shipped", "canceled", "delivered"],
        "order_purchase_timestamp": [
            "2021-01-15 10:00:00",
            "2021-03-22 14:30:00",
            "2021-06-01 09:15:00",
            "2021-09-10 17:45:00",
        ],
        "order_approved_at": [None, "2021-03-22 15:00:00", None, None],
        "order_delivered_carrier_date": [None, None, None, None],
        "order_delivered_customer_date": [None, None, None, None],
        "order_estimated_delivery_date": [None, None, None, None],
    })


@pytest.fixture
def sample_order_items():
    return pd.DataFrame({
        "order_id": ["o1", "o1", "o2"],
        "order_item_id": [1, 2, 1],
        "product_id": ["p1", "p2", "p3"],
        "seller_id": ["s1", "s1", "s2"],
        "shipping_limit_date": ["2021-01-20", "2021-01-20", "2021-03-28"],
        "price": ["29.99", "49.99", "-5.00"],
        "freight_value": ["5.00", "8.50", "3.00"],
    })


def test_clean_orders_drops_null_ids(sample_orders):
    cleaned, stats = clean_orders(sample_orders)
    assert len(cleaned) == 2  # rows with both order_id and customer_id
    assert stats["dropped_rows"] == 2


def test_clean_orders_lowercases_status(sample_orders):
    cleaned, _ = clean_orders(sample_orders)
    assert all(cleaned["order_status"].str.islower())


def test_clean_orders_adds_time_columns(sample_orders):
    cleaned, _ = clean_orders(sample_orders)
    for col in ["order_year", "order_month", "order_day_of_week", "order_hour"]:
        assert col in cleaned.columns


def test_clean_orders_parses_timestamps(sample_orders):
    cleaned, _ = clean_orders(sample_orders)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["order_purchase_timestamp"])


def test_clean_order_items_removes_negative_prices(sample_order_items):
    cleaned, _ = clean_order_items(sample_order_items)
    assert (cleaned["price"] >= 0).all()


def test_clean_order_items_adds_derived_columns(sample_order_items):
    cleaned, _ = clean_order_items(sample_order_items)
    assert "total_item_value" in cleaned.columns
    assert "freight_ratio" in cleaned.columns


def test_clean_customers_deduplicates():
    df = pd.DataFrame({
        "customer_id": ["c1", "c1", "c2"],
        "customer_unique_id": ["u1", "u1", "u2"],
        "customer_zip_code_prefix": ["12345", "12345", "67890"],
        "customer_city": ["São Paulo", "São Paulo", "Rio"],
        "customer_state": ["SP", "SP", "RJ"],
    })
    cleaned, _ = clean_customers(df)
    assert len(cleaned) == 2


def test_clean_products_fills_unknown_category():
    df = pd.DataFrame({
        "product_id": ["p1", "p2"],
        "product_category_name": [None, "Electronics"],
        "product_name_lenght": [10, 15],
        "product_description_lenght": [100, 200],
        "product_photos_qty": [3, 5],
        "product_weight_g": [500.0, 1000.0],
        "product_length_cm": [20.0, 30.0],
        "product_height_cm": [10.0, 15.0],
        "product_width_cm": [5.0, 10.0],
    })
    cleaned, _ = clean_products(df)
    assert cleaned.loc[cleaned["product_id"] == "p1", "product_category_name"].values[0] == "unknown"
