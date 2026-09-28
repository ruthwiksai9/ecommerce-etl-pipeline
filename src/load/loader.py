import pandas as pd
from sqlalchemy import text

from src.utils.db import get_engine
from src.utils.logger import get_logger

log = get_logger("loader")


def truncate_and_load(
    df: pd.DataFrame,
    schema: str,
    table: str,
    batch_size: int = 10000,
    if_exists: str = "append",
) -> int:
    """Load DataFrame to PostgreSQL with batching."""
    engine = get_engine()
    full_table = f"{schema}.{table}"
    total_rows = len(df)

    if total_rows == 0:
        log.warning(f"Empty DataFrame for {full_table}, skipping load")
        return 0

    rows_loaded = 0
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i : i + batch_size]
        batch.to_sql(
            name=table,
            schema=schema,
            con=engine,
            if_exists=if_exists if i == 0 else "append",
            index=False,
            method="multi",
        )
        rows_loaded += len(batch)
        log.debug(
            f"Loaded batch {i // batch_size + 1}: {rows_loaded:,}/{total_rows:,} rows -> {full_table}"
        )

    log.info(f"Load complete: {rows_loaded:,} rows -> {full_table}")
    return rows_loaded


def upsert(
    df: pd.DataFrame,
    schema: str,
    table: str,
    conflict_cols: list,
    batch_size: int = 10000,
) -> int:
    """Upsert rows using INSERT ... ON CONFLICT DO UPDATE."""
    engine = get_engine()
    full_table = f"{schema}.{table}"
    cols = list(df.columns)
    col_names = ", ".join(cols)
    placeholders = ", ".join([f":{c}" for c in cols])
    update_set = ", ".join(
        [f"{c} = EXCLUDED.{c}" for c in cols if c not in conflict_cols]
    )
    conflict_target = ", ".join(conflict_cols)

    sql = text(f"""
        INSERT INTO {full_table} ({col_names})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_target})
        DO UPDATE SET {update_set}
    """)

    rows_upserted = 0
    with engine.begin() as conn:
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]
            conn.execute(sql, batch.to_dict(orient="records"))
            rows_upserted += len(batch)

    log.info(f"Upsert complete: {rows_upserted:,} rows -> {full_table}")
    return rows_upserted


def load_all(dataframes: dict, batch_size: int = 10000) -> dict:
    """Load all cleaned datasets to raw schema."""
    log.info("Starting load phase")
    load_stats = {}

    table_map = {
        "orders": "orders",
        "order_items": "order_items",
        "customers": "customers",
        "products": "products",
        "sellers": "sellers",
        "order_payments": "order_payments",
    }

    for name, table in table_map.items():
        if name in dataframes:
            try:
                rows = truncate_and_load(
                    dataframes[name],
                    schema="raw",
                    table=table,
                    batch_size=batch_size,
                    if_exists="replace",
                )
                load_stats[name] = {"rows_loaded": rows, "status": "success"}
            except Exception as e:
                log.error(f"Load failed for {name}: {e}")
                load_stats[name] = {
                    "rows_loaded": 0,
                    "status": "failed",
                    "error": str(e),
                }

    log.info(
        f"Load phase complete: {sum(v['rows_loaded'] for v in load_stats.values()):,} total rows"
    )
    return load_stats
