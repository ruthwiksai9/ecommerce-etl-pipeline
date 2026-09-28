from pathlib import Path

from sqlalchemy import text

from src.utils.db import get_engine
from src.utils.logger import get_logger

log = get_logger("metrics")

QUERIES_DIR = Path(__file__).parent.parent.parent / "sql" / "queries"

METRIC_QUERIES = [
    "daily_revenue.sql",
    "category_performance.sql",
    "customer_cohort.sql",
    "seller_performance.sql",
]


def run_metric(query_file: str) -> dict:
    """Execute single metric aggregation query."""
    path = QUERIES_DIR / query_file
    if not path.exists():
        return {"query": query_file, "status": "failed", "error": "file not found"}

    sql = path.read_text()
    engine = get_engine()

    try:
        with engine.begin() as conn:
            result = conn.execute(text(sql))
        rows = result.rowcount if result.rowcount >= 0 else -1
        log.info(f"Metric [{query_file}]: {rows} rows affected")
        return {"query": query_file, "status": "success", "rows_affected": rows}
    except Exception as e:
        log.error(f"Metric [{query_file}] failed: {e}")
        return {"query": query_file, "status": "failed", "error": str(e)}


def run_all_metrics() -> list:
    """Run all metric aggregations in dependency order."""
    log.info("Running metrics aggregation layer")
    results = [run_metric(q) for q in METRIC_QUERIES]
    failed = [r for r in results if r["status"] == "failed"]
    if failed:
        log.warning(f"{len(failed)} metric(s) failed: {[r['query'] for r in failed]}")
    else:
        log.info(f"All {len(results)} metrics computed successfully")
    return results
