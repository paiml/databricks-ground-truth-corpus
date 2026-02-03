#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0",
#     "numpy>=1.24",
# ]
# ///
"""Test pandas API behavior for Koalas/PySpark parity validation.

This script validates expected pandas behavior that serves as ground truth
for Koalas (now PySpark pandas API) parity testing.

Tests:
- DataFrame creation and basic operations
- Series operations
- GroupBy operations
- Join operations
- Window functions
- Index operations

Usage:
    uv run spark-extensions/scripts/test_pandas_api_parity.py

References:
    - pandas API: https://pandas.pydata.org/docs/reference/
    - PySpark pandas API: https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class TestResult:
    """Result of a single test case."""
    name: str
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    details: Dict = field(default_factory=dict)


# =============================================================================
# DataFrame Creation Tests
# =============================================================================

def test_dataframe_creation() -> List[TestResult]:
    """Test DataFrame creation patterns."""
    results = []

    # Test 1: Create from dict
    data = {"a": [1, 2, 3], "b": [4, 5, 6]}
    df = pd.DataFrame(data)
    results.append(TestResult(
        name="DataFrame from dict",
        passed=list(df.columns) == ["a", "b"] and len(df) == 3,
        message=f"Columns: {list(df.columns)}, Rows: {len(df)}",
    ))

    # Test 2: Create with index
    df = pd.DataFrame(data, index=["x", "y", "z"])
    results.append(TestResult(
        name="DataFrame with custom index",
        passed=list(df.index) == ["x", "y", "z"],
        message=f"Index: {list(df.index)}",
    ))

    # Test 3: Create from records
    records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    df = pd.DataFrame.from_records(records)
    results.append(TestResult(
        name="DataFrame from records",
        passed=len(df) == 2 and list(df.columns) == ["a", "b"],
        message=f"Shape: {df.shape}",
    ))

    # Test 4: Column dtypes
    df = pd.DataFrame({"int_col": [1, 2], "float_col": [1.0, 2.0], "str_col": ["a", "b"]})
    results.append(TestResult(
        name="DataFrame column dtypes",
        passed=df["int_col"].dtype == np.int64 and df["float_col"].dtype == np.float64,
        message=f"Dtypes: {dict(df.dtypes)}",
    ))

    return results


# =============================================================================
# Series Operations Tests
# =============================================================================

def test_series_operations() -> List[TestResult]:
    """Test Series operations."""
    results = []

    s = pd.Series([1, 2, 3, 4, 5])

    # Test 1: Basic statistics
    results.append(TestResult(
        name="Series mean",
        passed=s.mean() == 3.0,
        message=f"Mean: {s.mean()}",
        expected=3.0,
        actual=s.mean(),
    ))

    results.append(TestResult(
        name="Series sum",
        passed=s.sum() == 15,
        message=f"Sum: {s.sum()}",
        expected=15,
        actual=s.sum(),
    ))

    results.append(TestResult(
        name="Series std",
        passed=abs(s.std() - np.std([1, 2, 3, 4, 5], ddof=1)) < 1e-10,
        message=f"Std: {s.std():.6f}",
    ))

    # Test 2: Vectorized operations
    s2 = s * 2
    results.append(TestResult(
        name="Series multiplication",
        passed=list(s2) == [2, 4, 6, 8, 10],
        message=f"Result: {list(s2)}",
    ))

    # Test 3: Boolean indexing
    filtered = s[s > 3]
    results.append(TestResult(
        name="Series boolean indexing",
        passed=list(filtered) == [4, 5],
        message=f"Filtered: {list(filtered)}",
    ))

    # Test 4: String operations
    s_str = pd.Series(["hello", "world", "test"])
    results.append(TestResult(
        name="Series str.upper()",
        passed=list(s_str.str.upper()) == ["HELLO", "WORLD", "TEST"],
        message=f"Upper: {list(s_str.str.upper())}",
    ))

    # Test 5: NA handling
    s_na = pd.Series([1, 2, None, 4])
    results.append(TestResult(
        name="Series isna()",
        passed=list(s_na.isna()) == [False, False, True, False],
        message=f"isna: {list(s_na.isna())}",
    ))

    results.append(TestResult(
        name="Series fillna()",
        passed=list(s_na.fillna(0)) == [1.0, 2.0, 0.0, 4.0],
        message=f"fillna(0): {list(s_na.fillna(0))}",
    ))

    return results


# =============================================================================
# GroupBy Operations Tests
# =============================================================================

def test_groupby_operations() -> List[TestResult]:
    """Test GroupBy operations."""
    results = []

    df = pd.DataFrame({
        "group": ["A", "A", "B", "B", "C"],
        "value": [1, 2, 3, 4, 5],
        "other": [10, 20, 30, 40, 50],
    })

    # Test 1: GroupBy sum
    grouped_sum = df.groupby("group")["value"].sum()
    expected_sum = {"A": 3, "B": 7, "C": 5}
    results.append(TestResult(
        name="GroupBy sum",
        passed=grouped_sum.to_dict() == expected_sum,
        message=f"Sum: {grouped_sum.to_dict()}",
        expected=expected_sum,
        actual=grouped_sum.to_dict(),
    ))

    # Test 2: GroupBy mean
    grouped_mean = df.groupby("group")["value"].mean()
    expected_mean = {"A": 1.5, "B": 3.5, "C": 5.0}
    results.append(TestResult(
        name="GroupBy mean",
        passed=grouped_mean.to_dict() == expected_mean,
        message=f"Mean: {grouped_mean.to_dict()}",
        expected=expected_mean,
        actual=grouped_mean.to_dict(),
    ))

    # Test 3: GroupBy count
    grouped_count = df.groupby("group")["value"].count()
    expected_count = {"A": 2, "B": 2, "C": 1}
    results.append(TestResult(
        name="GroupBy count",
        passed=grouped_count.to_dict() == expected_count,
        message=f"Count: {grouped_count.to_dict()}",
        expected=expected_count,
        actual=grouped_count.to_dict(),
    ))

    # Test 4: GroupBy agg multiple
    agg_result = df.groupby("group")["value"].agg(["sum", "mean", "count"])
    results.append(TestResult(
        name="GroupBy agg multiple",
        passed=list(agg_result.columns) == ["sum", "mean", "count"],
        message=f"Columns: {list(agg_result.columns)}",
    ))

    # Test 5: GroupBy multiple columns
    multi_group = df.groupby("group").agg({"value": "sum", "other": "mean"})
    results.append(TestResult(
        name="GroupBy multiple columns",
        passed=multi_group.loc["A", "value"] == 3 and multi_group.loc["A", "other"] == 15.0,
        message=f"A: value={multi_group.loc['A', 'value']}, other={multi_group.loc['A', 'other']}",
    ))

    return results


# =============================================================================
# Join Operations Tests
# =============================================================================

def test_join_operations() -> List[TestResult]:
    """Test join/merge operations."""
    results = []

    df1 = pd.DataFrame({"key": ["a", "b", "c"], "val1": [1, 2, 3]})
    df2 = pd.DataFrame({"key": ["b", "c", "d"], "val2": [4, 5, 6]})

    # Test 1: Inner join
    inner = pd.merge(df1, df2, on="key", how="inner")
    results.append(TestResult(
        name="Inner join",
        passed=len(inner) == 2 and list(inner["key"]) == ["b", "c"],
        message=f"Rows: {len(inner)}, Keys: {list(inner['key'])}",
    ))

    # Test 2: Left join
    left = pd.merge(df1, df2, on="key", how="left")
    results.append(TestResult(
        name="Left join",
        passed=len(left) == 3 and pd.isna(left[left["key"] == "a"]["val2"].iloc[0]),
        message=f"Rows: {len(left)}, NA for 'a': {pd.isna(left[left['key'] == 'a']['val2'].iloc[0])}",
    ))

    # Test 3: Right join
    right = pd.merge(df1, df2, on="key", how="right")
    results.append(TestResult(
        name="Right join",
        passed=len(right) == 3 and pd.isna(right[right["key"] == "d"]["val1"].iloc[0]),
        message=f"Rows: {len(right)}, NA for 'd': {pd.isna(right[right['key'] == 'd']['val1'].iloc[0])}",
    ))

    # Test 4: Outer join
    outer = pd.merge(df1, df2, on="key", how="outer")
    results.append(TestResult(
        name="Outer join",
        passed=len(outer) == 4,
        message=f"Rows: {len(outer)}, Keys: {list(outer['key'])}",
    ))

    # Test 5: Concat
    concat = pd.concat([df1[["key"]], df2[["key"]]], ignore_index=True)
    results.append(TestResult(
        name="Concat DataFrames",
        passed=len(concat) == 6,
        message=f"Rows: {len(concat)}",
    ))

    return results


# =============================================================================
# Window Functions Tests
# =============================================================================

def test_window_functions() -> List[TestResult]:
    """Test window function operations."""
    results = []

    df = pd.DataFrame({
        "group": ["A", "A", "A", "B", "B"],
        "value": [1, 2, 3, 4, 5],
    })

    # Test 1: Rolling mean
    rolling = df["value"].rolling(window=2).mean()
    expected_rolling = [np.nan, 1.5, 2.5, 3.5, 4.5]
    results.append(TestResult(
        name="Rolling mean",
        passed=pd.isna(rolling.iloc[0]) and abs(rolling.iloc[1] - 1.5) < 1e-10,
        message=f"Rolling: {list(rolling)}",
    ))

    # Test 2: Cumulative sum
    cumsum = df["value"].cumsum()
    expected_cumsum = [1, 3, 6, 10, 15]
    results.append(TestResult(
        name="Cumulative sum",
        passed=list(cumsum) == expected_cumsum,
        message=f"Cumsum: {list(cumsum)}",
        expected=expected_cumsum,
        actual=list(cumsum),
    ))

    # Test 3: Rank
    rank = df["value"].rank()
    expected_rank = [1.0, 2.0, 3.0, 4.0, 5.0]
    results.append(TestResult(
        name="Rank",
        passed=list(rank) == expected_rank,
        message=f"Rank: {list(rank)}",
    ))

    # Test 4: Shift
    shifted = df["value"].shift(1)
    results.append(TestResult(
        name="Shift",
        passed=pd.isna(shifted.iloc[0]) and shifted.iloc[1] == 1,
        message=f"Shifted: {list(shifted)}",
    ))

    # Test 5: Pct change
    pct = df["value"].pct_change()
    results.append(TestResult(
        name="Percent change",
        passed=pd.isna(pct.iloc[0]) and abs(pct.iloc[1] - 1.0) < 1e-10,
        message=f"Pct change[1]: {pct.iloc[1]}",
    ))

    return results


# =============================================================================
# Index Operations Tests
# =============================================================================

def test_index_operations() -> List[TestResult]:
    """Test index operations."""
    results = []

    df = pd.DataFrame(
        {"a": [1, 2, 3], "b": [4, 5, 6]},
        index=["x", "y", "z"]
    )

    # Test 1: loc (label-based)
    results.append(TestResult(
        name="loc label indexing",
        passed=df.loc["x", "a"] == 1,
        message=f"df.loc['x', 'a'] = {df.loc['x', 'a']}",
    ))

    # Test 2: iloc (position-based)
    results.append(TestResult(
        name="iloc position indexing",
        passed=df.iloc[0, 0] == 1,
        message=f"df.iloc[0, 0] = {df.iloc[0, 0]}",
    ))

    # Test 3: Reset index
    reset = df.reset_index()
    results.append(TestResult(
        name="Reset index",
        passed="index" in reset.columns and len(reset.columns) == 3,
        message=f"Columns after reset: {list(reset.columns)}",
    ))

    # Test 4: Set index
    df2 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df2_indexed = df2.set_index("a")
    results.append(TestResult(
        name="Set index",
        passed=df2_indexed.index.name == "a" and list(df2_indexed.index) == [1, 2],
        message=f"Index: {list(df2_indexed.index)}",
    ))

    # Test 5: MultiIndex
    arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
    tuples = list(zip(*arrays))
    multi_idx = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
    df_multi = pd.DataFrame({"value": [10, 20, 30, 40]}, index=multi_idx)
    results.append(TestResult(
        name="MultiIndex creation",
        passed=df_multi.loc[("A", 1), "value"] == 10,
        message=f"df.loc[('A', 1)] = {df_multi.loc[('A', 1), 'value']}",
    ))

    return results


# =============================================================================
# Data Type Conversion Tests
# =============================================================================

def test_dtype_conversion() -> List[TestResult]:
    """Test data type conversion operations."""
    results = []

    # Test 1: astype int to float
    s = pd.Series([1, 2, 3])
    s_float = s.astype(float)
    results.append(TestResult(
        name="astype int to float",
        passed=s_float.dtype == np.float64,
        message=f"Dtype: {s_float.dtype}",
    ))

    # Test 2: astype to string
    s_str = s.astype(str)
    results.append(TestResult(
        name="astype to string",
        passed=list(s_str) == ["1", "2", "3"],
        message=f"Values: {list(s_str)}",
    ))

    # Test 3: to_datetime
    dates = pd.to_datetime(["2024-01-01", "2024-01-02"])
    results.append(TestResult(
        name="to_datetime",
        passed=dates[0].year == 2024 and dates[0].month == 1,
        message=f"First date: {dates[0]}",
    ))

    # Test 4: Categorical
    s_cat = pd.Series(["a", "b", "a", "c"]).astype("category")
    results.append(TestResult(
        name="Categorical dtype",
        passed=len(s_cat.cat.categories) == 3,
        message=f"Categories: {list(s_cat.cat.categories)}",
    ))

    return results


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Test pandas API for Koalas parity")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== Pandas API Parity Falsification Tests ===")
    print("(Ground truth for Koalas/PySpark pandas API)\n")

    all_results = []

    # DataFrame creation
    print("DataFrame Creation Tests:")
    df_results = test_dataframe_creation()
    all_results.extend(df_results)
    for r in df_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Series operations
    print("\nSeries Operations Tests:")
    series_results = test_series_operations()
    all_results.extend(series_results)
    for r in series_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # GroupBy operations
    print("\nGroupBy Operations Tests:")
    groupby_results = test_groupby_operations()
    all_results.extend(groupby_results)
    for r in groupby_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Join operations
    print("\nJoin Operations Tests:")
    join_results = test_join_operations()
    all_results.extend(join_results)
    for r in join_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Window functions
    print("\nWindow Functions Tests:")
    window_results = test_window_functions()
    all_results.extend(window_results)
    for r in window_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Index operations
    print("\nIndex Operations Tests:")
    index_results = test_index_operations()
    all_results.extend(index_results)
    for r in index_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Data type conversion
    print("\nData Type Conversion Tests:")
    dtype_results = test_dtype_conversion()
    all_results.extend(dtype_results)
    for r in dtype_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results
    if args.output:
        output_data = {
            "dataframe_tests": [{"name": r.name, "passed": r.passed} for r in df_results],
            "series_tests": [{"name": r.name, "passed": r.passed} for r in series_results],
            "groupby_tests": [{"name": r.name, "passed": r.passed} for r in groupby_results],
            "join_tests": [{"name": r.name, "passed": r.passed} for r in join_results],
            "window_tests": [{"name": r.name, "passed": r.passed} for r in window_results],
            "index_tests": [{"name": r.name, "passed": r.passed} for r in index_results],
            "dtype_tests": [{"name": r.name, "passed": r.passed} for r in dtype_results],
            "summary": {"passed": passed, "total": total},
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
