# Benchmarks

Ground truth tests for benchmark reproducibility including TPC-DS, TPC-H, and ALS algorithm validation.

## Test Coverage: 15/15 (100%)

## Overview

These tests validate that benchmark implementations produce results matching official specifications.

## Test Categories

### TPC-DS Validation (5 tests)

TPC-DS is a decision support benchmark with 24 tables and 99 queries.

| Test | Table | Scale Factor 1 Rows | Status |
|------|-------|---------------------|--------|
| TPCDS-001 | store_sales | 2,880,404 | Pass |
| TPCDS-002 | catalog_sales | 1,441,548 | Pass |
| TPCDS-003 | web_sales | 719,384 | Pass |
| TPCDS-004 | customer | 100,000 | Pass |
| TPCDS-005 | item | 18,000 | Pass |

### TPC-H Validation (5 tests)

TPC-H is an ad-hoc decision support benchmark with 8 tables and 22 queries.

| Test | Table | Scale Factor 1 Rows | Status |
|------|-------|---------------------|--------|
| TPCH-001 | lineitem | 6,001,215 | Pass |
| TPCH-002 | orders | 1,500,000 | Pass |
| TPCH-003 | customer | 150,000 | Pass |
| TPCH-004 | part | 200,000 | Pass |
| TPCH-005 | supplier | 10,000 | Pass |

### ALS Algorithm (5 tests)

Alternating Least Squares for collaborative filtering.

| Test | Property | Expected |
|------|----------|----------|
| ALS-001 | Convergence | RMSE decreases |
| ALS-002 | User factors shape | (n_users, rank) |
| ALS-003 | Item factors shape | (n_items, rank) |
| ALS-004 | Regularization effect | Higher λ → lower factor norms |
| ALS-005 | Prediction range | Within [min, max] ratings |

## TPC Specifications

### Row Count Formulas

```python
# TPC-DS Scale Factor 1 row counts
TPCDS_SF1_ROW_COUNTS = {
    "call_center": 6,
    "catalog_page": 11_718,
    "catalog_returns": 144_067,
    "catalog_sales": 1_441_548,
    "customer": 100_000,
    "customer_address": 50_000,
    "customer_demographics": 1_920_800,
    "date_dim": 73_049,
    "household_demographics": 7_200,
    "income_band": 20,
    "inventory": 11_745_000,
    "item": 18_000,
    "promotion": 300,
    "reason": 35,
    "ship_mode": 20,
    "store": 12,
    "store_returns": 287_514,
    "store_sales": 2_880_404,
    "time_dim": 86_400,
    "warehouse": 5,
    "web_page": 60,
    "web_returns": 71_763,
    "web_sales": 719_384,
    "web_site": 30,
}

# TPC-H Scale Factor 1 row counts
TPCH_SF1_ROW_COUNTS = {
    "customer": 150_000,
    "lineitem": 6_001_215,
    "nation": 25,
    "orders": 1_500_000,
    "part": 200_000,
    "partsupp": 800_000,
    "region": 5,
    "supplier": 10_000,
}
```

## ALS Algorithm Properties

```python
def test_als_convergence():
    """ALS must converge: RMSE should decrease over iterations."""
    model = ALS(rank=10, max_iter=20, reg_param=0.1)

    rmse_history = []
    for iteration in range(20):
        model.fit_iteration(ratings)
        rmse = model.evaluate(test_ratings)
        rmse_history.append(rmse)

    # Convergence: each RMSE should be <= previous (with tolerance)
    for i in range(1, len(rmse_history)):
        assert rmse_history[i] <= rmse_history[i-1] + 1e-6

def test_als_factor_shapes():
    """Factor matrices must have correct shapes."""
    model = ALS(rank=10)
    model.fit(ratings)

    assert model.user_factors.shape == (n_users, 10)
    assert model.item_factors.shape == (n_items, 10)
```

## Running Tests

```bash
uv run benchmarks/scripts/test_benchmark_oracle.py
```

## Example Output

```
=== Benchmark Oracle Ground Truth Tests ===

Section 1: TPC-DS Row Counts
  [PASS] TPCDS-001: store_sales = 2,880,404 rows
  [PASS] TPCDS-002: catalog_sales = 1,441,548 rows
  ...

Section 2: TPC-H Row Counts
  [PASS] TPCH-001: lineitem = 6,001,215 rows
  ...

Section 3: ALS Algorithm Properties
  [PASS] ALS-001: Convergence verified (RMSE: 0.95 → 0.82)
  [PASS] ALS-002: User factors shape correct
  ...

Summary: 15/15 tests passed
```

## References

- [TPC-DS Specification v3.2.0](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v3.2.0.pdf)
- [TPC-H Specification v3.0.1](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v3.0.1.pdf)
- [ALS for Collaborative Filtering](https://dl.acm.org/doi/10.1109/MC.2009.263)
