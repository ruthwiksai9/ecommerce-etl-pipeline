from typing import Tuple

import pandas as pd

from src.utils.logger import get_logger

log = get_logger("transformer")


def clean_orders(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Clean and standardize orders dataset."""
    stats = {"input_rows": len(df), "dropped_rows": 0, "nulls_filled": 0}

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    datetime_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    initial_len = len(df)
    df = df.dropna(subset=["order_id", "customer_id"])
    stats["dropped_rows"] = initial_len - len(df)

    df["order_status"] = df["order_status"].str.lower().str.strip()

    if "order_purchase_timestamp" in df.columns:
        df["order_year"] = df["order_purchase_timestamp"].dt.year
        df["order_month"] = df["order_purchase_timestamp"].dt.month
        df["order_day_of_week"] = df["order_purchase_timestamp"].dt.dayofweek
        df["order_hour"] = df["order_purchase_timestamp"].dt.hour

    stats["output_rows"] = len(df)
    log.info(f"Orders cleaned: {stats}")
    return df, stats


def clean_order_items(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Clean order items and compute derived metrics."""
    stats = {"input_rows": len(df)}

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce").fillna(0)

    df["total_item_value"] = df["price"] + df["freight_value"]
    df["freight_ratio"] = (df["freight_value"] / df["total_item_value"]).round(4)

    df = df.dropna(subset=["order_id", "product_id"])
    df = df[df["price"] >= 0]

    stats["output_rows"] = len(df)
    log.info(f"Order items cleaned: {stats}")
    return df, stats


def clean_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Clean customer data."""
    stats = {"input_rows": len(df)}

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    for col in ["customer_city", "customer_state"]:
        if col in df.columns:
            df[col] = df[col].str.lower().str.strip()

    df["customer_zip_code_prefix"] = (
        df["customer_zip_code_prefix"].astype(str).str.zfill(5)
    )

    df = df.dropna(subset=["customer_id", "customer_unique_id"])
    df = df.drop_duplicates(subset=["customer_id"])

    stats["output_rows"] = len(df)
    log.info(f"Customers cleaned: {stats}")
    return df, stats


def clean_products(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Clean product catalog data."""
    stats = {"input_rows": len(df)}

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    numeric_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["product_category_name"] = (
        df["product_category_name"].fillna("unknown").str.lower().str.strip()
    )

    df["product_volume_cm3"] = (
        df.get("product_length_cm", 0)
        * df.get("product_height_cm", 0)
        * df.get("product_width_cm", 0)
    )

    df = df.drop_duplicates(subset=["product_id"])

    stats["output_rows"] = len(df)
    log.info(f"Products cleaned: {stats}")
    return df, stats


def transform_all(dataframes: dict) -> Tuple[dict, dict]:
    """Run all transforms, return cleaned dataframes and stats."""
    log.info("Starting transformation phase")

    cleaners = {
        "orders": clean_orders,
        "order_items": clean_order_items,
        "customers": clean_customers,
        "products": clean_products,
    }

    cleaned = {}
    all_stats = {}

    for name, cleaner in cleaners.items():
        if name in dataframes:
            try:
                cleaned[name], all_stats[name] = cleaner(dataframes[name])
            except Exception as e:
                log.error(f"Transform failed for {name}: {e}")
                raise

    for name in dataframes:
        if name not in cleaned:
            df = dataframes[name].copy()
            df.columns = df.columns.str.lower().str.strip()
            cleaned[name] = df

    log.info(f"Transformation complete: {len(cleaned)} datasets processed")
    return cleaned, all_stats
