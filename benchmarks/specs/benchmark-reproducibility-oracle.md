# Benchmark Reproducibility Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification
**Purpose:** Validate benchmark reproducibility and standard compliance

---

## 1. Overview

Databricks maintains several benchmark implementations. This oracle validates reproducibility and compliance with industry standards.

### Benchmarks Under Test

| Benchmark | Repository | Stars | Standard |
|-----------|------------|-------|----------|
| tpcds-kit | databricks/tpcds-kit | 105 | TPC-DS |
| tpch-dbgen | databricks/tpch-dbgen | 32 | TPC-H |
| spark-sql-perf | databricks/spark-sql-perf | 619 | TPC-DS/TPC-H |
| benchmarks | databricks/benchmarks | 108 | Various |
| als-benchmark-scripts | databricks/als-benchmark-scripts | 22 | ALS |

---

## 2. TPC-DS Compliance Tests

### 2.1 Data Generation

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| DS-001 | Scale factor 1 row counts | TPC-DS spec | Exact |
| DS-002 | Scale factor 10 row counts | TPC-DS spec | Exact |
| DS-003 | Scale factor 100 row counts | TPC-DS spec | Exact |
| DS-004 | Data distribution | Zipfian/Uniform | Statistical |
| DS-005 | Null ratio | Per column spec | ±0.1% |
| DS-006 | String lengths | Per column spec | Exact |
| DS-007 | Date ranges | Per column spec | Exact |

### 2.2 Query Compliance

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| DQ-001 | Query 1 syntax | Valid SQL | Exact |
| DQ-002 | Query 1 result count | Certified result | Exact |
| DQ-003 | All 99 queries parse | Valid SQL | Exact |
| DQ-004 | Query result ordering | Deterministic | Exact |
| DQ-005 | Decimal precision | Per spec | Exact |

### 2.3 Performance Metrics

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| DP-001 | Query throughput metric | QphDS@SF | Formula |
| DP-002 | Load time metric | LT | Documented |
| DP-003 | Power test | PT | Documented |
| DP-004 | Throughput test | TT | Documented |

---

## 3. TPC-H Compliance Tests

### 3.1 Data Generation

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| TH-001 | Scale factor 1 row counts | TPC-H spec | Exact |
| TH-002 | Scale factor 10 row counts | TPC-H spec | Exact |
| TH-003 | LINEITEM rows at SF=1 | 6,001,215 | Exact |
| TH-004 | ORDERS rows at SF=1 | 1,500,000 | Exact |
| TH-005 | Data skew | Per spec | Statistical |

### 3.2 Query Compliance

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| HQ-001 | Query 1 result | Certified | Exact |
| HQ-002 | All 22 queries parse | Valid SQL | Exact |
| HQ-003 | Refresh functions | RF1, RF2 | Functional |

---

## 4. Spark SQL Performance Tests

### 4.1 Benchmark Coverage

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| SP-001 | TPC-DS queries run | All 99 | Exact |
| SP-002 | TPC-H queries run | All 22 | Exact |
| SP-003 | Custom queries run | Per config | Exact |

### 4.2 Reproducibility

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| SR-001 | Same config, same results | Deterministic | Exact |
| SR-002 | Same data, same timing | ±5% variance | Statistical |
| SR-003 | Warm cache vs cold | Documented diff | Documented |

---

## 5. ALS Benchmark Tests

### 5.1 Algorithm Correctness

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| AL-001 | RMSE convergence | Decreasing | Monotonic |
| AL-002 | Factor matrix shapes | m×k, n×k | Exact |
| AL-003 | Regularization effect | Lower RMSE | Statistical |
| AL-004 | Rank effect | Higher rank, better fit | Statistical |

### 5.2 Distributed Correctness

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| AD-001 | Single vs multi-node | Same result | 1e-6 |
| AD-002 | Partitioning effect | No semantic diff | Exact |
| AD-003 | Checkpoint recovery | Same result | Exact |

---

## 6. Golden Corpus Structure

```
benchmarks/
├── oracle/
│   ├── tpcds/
│   │   ├── sf1/
│   │   │   ├── row_counts.json
│   │   │   ├── query_results/
│   │   │   └── timing_baseline.json
│   │   └── sf10/
│   ├── tpch/
│   │   ├── sf1/
│   │   │   ├── row_counts.json
│   │   │   └── query_results/
│   │   └── sf10/
│   └── als/
│       ├── movielens_100k/
│       └── movielens_1m/
├── specs/
│   └── benchmark-reproducibility-oracle.md
└── scripts/
    ├── validate_tpcds.py
    ├── validate_tpch.py
    └── validate_als.py
```

### Row Count Golden Format

```json
{
  "benchmark": "tpcds",
  "scale_factor": 1,
  "tables": {
    "call_center": 6,
    "catalog_page": 11718,
    "catalog_returns": 144067,
    "catalog_sales": 1441548,
    "customer": 100000,
    "customer_address": 50000,
    "customer_demographics": 1920800,
    "date_dim": 73049,
    "household_demographics": 7200,
    "income_band": 20,
    "inventory": 11745000,
    "item": 18000,
    "promotion": 300,
    "reason": 35,
    "ship_mode": 20,
    "store": 12,
    "store_returns": 287514,
    "store_sales": 2880404,
    "time_dim": 86400,
    "warehouse": 5,
    "web_page": 60,
    "web_returns": 71763,
    "web_sales": 719384,
    "web_site": 30
  }
}
```

---

## 7. Falsification Checklist

### 7.1 TPC-DS Data Generation
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DS-001 | SF=1 row counts | Per spec | | |
| DS-002 | SF=10 row counts | Per spec | | |
| DS-003 | SF=100 row counts | Per spec | | |
| DS-004 | Data distribution | Zipfian | | |
| DS-005 | Null ratios | Per spec | | |

### 7.2 TPC-DS Query Compliance
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DQ-001 | Query 1 syntax | Valid | | |
| DQ-002 | Query 1 result | Certified | | |
| DQ-003 | All 99 parse | Valid | | |
| DQ-004 | Result ordering | Deterministic | | |
| DQ-005 | Decimal precision | Per spec | | |

### 7.3 TPC-H Data Generation
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| TH-001 | SF=1 row counts | Per spec | | |
| TH-002 | SF=10 row counts | Per spec | | |
| TH-003 | LINEITEM count | 6,001,215 | | |
| TH-004 | ORDERS count | 1,500,000 | | |
| TH-005 | Data skew | Per spec | | |

### 7.4 TPC-H Query Compliance
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| HQ-001 | Query 1 result | Certified | | |
| HQ-002 | All 22 parse | Valid | | |
| HQ-003 | Refresh functions | Correct | | |

### 7.5 ALS Algorithm
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| AL-001 | RMSE convergence | Monotonic | | |
| AL-002 | Matrix shapes | Correct | | |
| AL-003 | Regularization | Effective | | |
| AD-001 | Distributed parity | 1e-6 | | |

---

## 8. Standard References

- TPC-DS Specification v3.2.0
- TPC-H Specification v3.0.1
- Spark MLlib ALS Implementation
- IEEE 754 Floating Point Standard

---

## References

- TPC-DS: http://www.tpc.org/tpcds/
- TPC-H: http://www.tpc.org/tpch/
- Databricks benchmarks: https://github.com/databricks/benchmarks
