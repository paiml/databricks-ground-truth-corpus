# Benchmark Reproducibility - Falsification QA Checklist

**Date:** 2026-02-03
**Methodology:** Popperian Falsification (attempt to break, not verify)
**Philosophy:** "The wrong view of science betrays itself in the craving to be right"

---

## 1. TPC-DS Oracle Validation

### 1.1 Oracle Structure
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| TPCDS-001 | Oracle file exists | Present | Present | + |
| TPCDS-002 | Oracle structure valid | 'tables' key | Valid | + |
| TPCDS-003 | Table count | 24 tables | 24 tables | + |

### 1.2 Row Count Compliance (SF=1)
| ID | Table | TPC-DS Spec | Oracle Value | Pass |
|----|-------|-------------|--------------|------|
| TPCDS-004 | call_center | 6 | 6 | + |
| TPCDS-005 | catalog_page | 11,718 | 11,718 | + |
| TPCDS-006 | catalog_returns | 144,067 | 144,067 | + |
| TPCDS-007 | catalog_sales | 1,441,548 | 1,441,548 | + |
| TPCDS-008 | customer | 100,000 | 100,000 | + |
| TPCDS-009 | customer_address | 50,000 | 50,000 | + |
| TPCDS-010 | customer_demographics | 1,920,800 | 1,920,800 | + |
| TPCDS-011 | date_dim | 73,049 | 73,049 | + |
| TPCDS-012 | household_demographics | 7,200 | 7,200 | + |
| TPCDS-013 | income_band | 20 | 20 | + |
| TPCDS-014 | inventory | 11,745,000 | 11,745,000 | + |
| TPCDS-015 | item | 18,000 | 18,000 | + |
| TPCDS-016 | promotion | 300 | 300 | + |
| TPCDS-017 | reason | 35 | 35 | + |
| TPCDS-018 | ship_mode | 20 | 20 | + |
| TPCDS-019 | store | 12 | 12 | + |
| TPCDS-020 | store_returns | 287,514 | 287,514 | + |
| TPCDS-021 | store_sales | 2,880,404 | 2,880,404 | + |
| TPCDS-022 | time_dim | 86,400 | 86,400 | + |
| TPCDS-023 | warehouse | 5 | 5 | + |
| TPCDS-024 | web_page | 60 | 60 | + |
| TPCDS-025 | web_returns | 71,763 | 71,763 | + |
| TPCDS-026 | web_sales | 719,384 | 719,384 | + |
| TPCDS-027 | web_site | 30 | 30 | + |

---

## 2. TPC-H Oracle Validation

### 2.1 Oracle Structure
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| TPCH-001 | Oracle file exists | Present | Present | + |
| TPCH-002 | Oracle structure valid | 'tables' key | Valid | + |
| TPCH-003 | Table count | 8 tables | 8 tables | + |

### 2.2 Row Count Compliance (SF=1)
| ID | Table | TPC-H Spec | Oracle Value | Pass |
|----|-------|------------|--------------|------|
| TPCH-004 | lineitem | 6,001,215 | 6,001,215 | + |
| TPCH-005 | orders | 1,500,000 | 1,500,000 | + |
| TPCH-006 | customer | 150,000 | 150,000 | + |
| TPCH-007 | part | 200,000 | 200,000 | + |
| TPCH-008 | partsupp | 800,000 | 800,000 | + |
| TPCH-009 | supplier | 10,000 | 10,000 | + |
| TPCH-010 | nation | 25 | 25 | + |
| TPCH-011 | region | 5 | 5 | + |

---

## 3. ALS Algorithm Property Tests

### 3.1 Algorithm Properties
| ID | Property | Expected | Actual | Pass |
|----|----------|----------|--------|------|
| ALS-001 | RMSE Convergence | Monotonically decreasing | 0.3898 -> 0.0286 | + |
| ALS-002 | Factor Matrix Shapes | (n_users, k), (n_items, k) | (50,10), (30,10) | + |
| ALS-003 | Regularization Effect | Lower reg = lower RMSE | 0.0145 < 0.2174 | + |
| ALS-004 | Rank Effect | Higher rank = better fit | 0.0185 < 0.3483 | + |
| ALS-005 | Determinism | Same seed = same result | Identical | + |
| ALS-006 | Predictions Finite | All predictions valid | 1500/1500 finite | + |

---

## 4. Execution Log

```
Date: 2026-02-03
Executor: Claude Code
Command: uv run benchmarks/scripts/test_benchmark_oracle.py
```

### Results Summary

| Category | Total | Passed | Failed |
|----------|-------|--------|--------|
| TPC-DS Oracle | 4 | 4 | 0 |
| TPC-H Oracle | 5 | 5 | 0 |
| ALS Properties | 6 | 6 | 0 |
| **TOTAL** | **15** | **15** | **0** |

---

## 5. Standards Validated

### 5.1 TPC-DS
- **Specification:** TPC-DS v3.2.0
- **Scale Factor:** SF=1
- **Source:** Table 3-2 (Row Counts)

### 5.2 TPC-H
- **Specification:** TPC-H v3.0.1
- **Scale Factor:** SF=1
- **Source:** Section 4.2.3 (Database Population)

### 5.3 ALS
- **Algorithm:** Alternating Least Squares
- **Reference:** Spark MLlib implementation
- **Regularization:** Tikhonov (L2)

---

## Sign-off

- [x] All 15 falsification tests pass
- [x] TPC-DS row counts match specification v3.2.0
- [x] TPC-H row counts match specification v3.0.1
- [x] ALS algorithm properties validated

**Verdict: COMPLETE** - Benchmark oracle validation passes all tests.
