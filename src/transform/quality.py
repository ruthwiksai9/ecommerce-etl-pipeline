from dataclasses import dataclass, field
from typing import List

import pandas as pd

from src.utils.logger import get_logger

log = get_logger("quality")


@dataclass
class QualityResult:
    dataset: str
    passed: bool
    checks: List[dict] = field(default_factory=list)
    total_rows: int = 0
    failed_checks: int = 0

    def add_check(self, name: str, passed: bool, details: str = ""):
        self.checks.append({"check": name, "passed": passed, "details": details})
        if not passed:
            self.failed_checks += 1
            self.passed = False


def check_nulls(
    df: pd.DataFrame, critical_cols: List[str], threshold_pct: float = 5.0
) -> dict:
    """Fail if critical columns exceed null threshold."""
    results = {}
    for col in critical_cols:
        if col not in df.columns:
            results[col] = {
                "null_pct": None,
                "passed": False,
                "reason": "column missing",
            }
            continue
        null_pct = (df[col].isna().sum() / len(df)) * 100
        results[col] = {
            "null_pct": round(null_pct, 2),
            "passed": null_pct <= threshold_pct,
        }
    return results


def check_duplicates(df: pd.DataFrame, key_cols: List[str]) -> dict:
    """Check for duplicate primary keys."""
    dup_count = df.duplicated(subset=key_cols).sum()
    return {
        "duplicate_count": int(dup_count),
        "passed": dup_count == 0,
        "duplicate_pct": round((dup_count / len(df)) * 100, 2),
    }


def check_referential_integrity(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    child_key: str,
    parent_key: str,
) -> dict:
    """Verify all FK values exist in parent table."""
    orphan_count = (~child_df[child_key].isin(parent_df[parent_key])).sum()
    return {
        "orphan_count": int(orphan_count),
        "passed": orphan_count == 0,
        "orphan_pct": round((orphan_count / len(child_df)) * 100, 2),
    }


def check_value_ranges(df: pd.DataFrame, col: str, min_val=None, max_val=None) -> dict:
    """Validate numeric columns stay within expected bounds."""
    series = pd.to_numeric(df[col], errors="coerce")
    violations = 0
    if min_val is not None:
        violations += (series < min_val).sum()
    if max_val is not None:
        violations += (series > max_val).sum()
    return {
        "violations": int(violations),
        "passed": violations == 0,
        "min": float(series.min()) if not series.empty else None,
        "max": float(series.max()) if not series.empty else None,
    }


def run_quality_checks(dataframes: dict) -> List[QualityResult]:
    """Run all quality checks across datasets."""
    log.info("Running data quality checks")
    results = []

    if "orders" in dataframes:
        df = dataframes["orders"]
        result = QualityResult(dataset="orders", passed=True, total_rows=len(df))

        nulls = check_nulls(df, ["order_id", "customer_id"])
        for col, r in nulls.items():
            result.add_check(f"null_{col}", r["passed"], str(r))

        dups = check_duplicates(df, ["order_id"])
        result.add_check("duplicate_order_id", dups["passed"], str(dups))

        results.append(result)

    if "order_items" in dataframes:
        df = dataframes["order_items"]
        result = QualityResult(dataset="order_items", passed=True, total_rows=len(df))

        nulls = check_nulls(df, ["order_id", "product_id"])
        for col, r in nulls.items():
            result.add_check(f"null_{col}", r["passed"], str(r))

        if "price" in df.columns:
            price_check = check_value_ranges(df, "price", min_val=0)
            result.add_check(
                "price_non_negative", price_check["passed"], str(price_check)
            )

        if "orders" in dataframes:
            ref_check = check_referential_integrity(
                df, dataframes["orders"], "order_id", "order_id"
            )
            result.add_check(
                "order_items_fk_orders", ref_check["passed"], str(ref_check)
            )

        results.append(result)

    for r in results:
        status = "PASSED" if r.passed else "FAILED"
        log.info(
            f"Quality check [{r.dataset}]: {status} ({r.failed_checks} failures, {r.total_rows:,} rows)"
        )

    return results
