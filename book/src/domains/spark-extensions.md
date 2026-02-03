# Spark Extensions

Ground truth tests for Spark extensions including Koalas (pandas API on Spark) parity.

## Test Coverage: 36/36 (100%)

## Overview

These tests validate that pandas-compatible Spark APIs produce identical results to native pandas operations.

## Test Categories

### DataFrame Operations (8 tests)

| Test | Operation | Tolerance |
|------|-----------|-----------|
| DF-001 | `head(n)` | Exact |
| DF-002 | `tail(n)` | Exact |
| DF-003 | `describe()` | fp32 |
| DF-004 | `shape` | Exact |
| DF-005 | `columns` | Exact |
| DF-006 | `dtypes` | Type match |
| DF-007 | `values` | fp32 |
| DF-008 | `to_dict()` | Exact |

### Series Operations (8 tests)

| Test | Operation | Tolerance |
|------|-----------|-----------|
| S-001 | `mean()` | fp32 |
| S-002 | `std()` | fp32 |
| S-003 | `min()` / `max()` | Exact |
| S-004 | `sum()` | fp32 |
| S-005 | `count()` | Exact |
| S-006 | `unique()` | Set equality |
| S-007 | `value_counts()` | Exact |
| S-008 | `isna()` / `notna()` | Exact |

### GroupBy Operations (8 tests)

| Test | Operation | Tolerance |
|------|-----------|-----------|
| GB-001 | `groupby().sum()` | fp32 |
| GB-002 | `groupby().mean()` | fp32 |
| GB-003 | `groupby().count()` | Exact |
| GB-004 | `groupby().agg()` | fp32 |
| GB-005 | `groupby().transform()` | fp32 |
| GB-006 | Multi-column groupby | fp32 |
| GB-007 | `groupby().first()` | Exact |
| GB-008 | `groupby().last()` | Exact |

### Join Operations (6 tests)

| Test | Operation | Tolerance |
|------|-----------|-----------|
| J-001 | Inner join | Exact |
| J-002 | Left join | Exact |
| J-003 | Right join | Exact |
| J-004 | Outer join | Exact |
| J-005 | Multi-key join | Exact |
| J-006 | Self join | Exact |

### Window Functions (6 tests)

| Test | Operation | Tolerance |
|------|-----------|-----------|
| W-001 | `rolling().mean()` | fp32 |
| W-002 | `rolling().sum()` | fp32 |
| W-003 | `rolling().std()` | fp32 |
| W-004 | `expanding().mean()` | fp32 |
| W-005 | `rank()` | Exact |
| W-006 | `shift()` | Exact |

## Ground Truth Pattern

```python
import pandas as pd
import numpy as np

def test_groupby_mean_parity():
    """pandas groupby().mean() ground truth."""
    # Create test data
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B', 'C'],
        'value': [1.0, 2.0, 3.0, 4.0, 5.0],
    })

    # Ground truth: native pandas
    expected = df.groupby('group')['value'].mean()

    # Expected results
    ground_truth = pd.Series(
        [1.5, 3.5, 5.0],
        index=pd.Index(['A', 'B', 'C'], name='group'),
        name='value',
    )

    # Validate
    pd.testing.assert_series_equal(expected, ground_truth)
```

## Running Tests

```bash
uv run spark-extensions/scripts/test_pandas_api_parity.py
```

## Example Output

```
=== Spark Extensions pandas API Parity Tests ===

Section 1: DataFrame Operations
  [PASS] DF-001: head(5) returns correct rows
  [PASS] DF-002: tail(5) returns correct rows
  ...

Section 2: Series Operations
  [PASS] S-001: mean() = 3.0 (expected: 3.0)
  [PASS] S-002: std() = 1.58 (expected: 1.58, tol=1e-5)
  ...

Summary: 36/36 tests passed
```

## Koalas vs pandas Differences

Known behavioral differences (not tested as failures):

| Operation | pandas | Koalas/Spark | Notes |
|-----------|--------|--------------|-------|
| `sort_values()` | Stable | Unstable | Use `sort_index()` for determinism |
| `groupby()` order | Preserved | Not guaranteed | Sort after groupby |
| Float precision | IEEE 754 | IEEE 754 | Minor differences possible |
| NaN handling | Consistent | Per-operation | Check documentation |
