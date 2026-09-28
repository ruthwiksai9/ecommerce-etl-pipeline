import pandas as pd
import pytest

from src.transform.quality import check_duplicates, check_nulls, check_referential_integrity, check_value_ranges


def test_check_nulls_passes_under_threshold():
    df = pd.DataFrame({"id": ["a", "b", None, "d", "e", "f", "g", "h", "i", "j"]})
    result = check_nulls(df, ["id"], threshold_pct=15.0)
    assert result["id"]["passed"] is True


def test_check_nulls_fails_over_threshold():
    df = pd.DataFrame({"id": ["a", None, None, None]})
    result = check_nulls(df, ["id"], threshold_pct=5.0)
    assert result["id"]["passed"] is False


def test_check_nulls_missing_column():
    df = pd.DataFrame({"id": ["a", "b"]})
    result = check_nulls(df, ["nonexistent"])
    assert result["nonexistent"]["passed"] is False


def test_check_duplicates_clean():
    df = pd.DataFrame({"order_id": ["o1", "o2", "o3"]})
    result = check_duplicates(df, ["order_id"])
    assert result["passed"] is True
    assert result["duplicate_count"] == 0


def test_check_duplicates_detects_dupes():
    df = pd.DataFrame({"order_id": ["o1", "o1", "o3"]})
    result = check_duplicates(df, ["order_id"])
    assert result["passed"] is False
    assert result["duplicate_count"] == 1


def test_referential_integrity_passes():
    parent = pd.DataFrame({"order_id": ["o1", "o2", "o3"]})
    child = pd.DataFrame({"order_id": ["o1", "o2"], "item_id": [1, 2]})
    result = check_referential_integrity(child, parent, "order_id", "order_id")
    assert result["passed"] is True


def test_referential_integrity_detects_orphans():
    parent = pd.DataFrame({"order_id": ["o1", "o2"]})
    child = pd.DataFrame({"order_id": ["o1", "o99"], "item_id": [1, 2]})
    result = check_referential_integrity(child, parent, "order_id", "order_id")
    assert result["passed"] is False
    assert result["orphan_count"] == 1


def test_value_range_passes():
    df = pd.DataFrame({"price": [10.0, 20.0, 30.0]})
    result = check_value_ranges(df, "price", min_val=0)
    assert result["passed"] is True


def test_value_range_detects_negatives():
    df = pd.DataFrame({"price": [10.0, -5.0, 30.0]})
    result = check_value_ranges(df, "price", min_val=0)
    assert result["passed"] is False
    assert result["violations"] == 1
