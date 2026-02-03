# Spark Extensions Parity Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification

---

## 1. Overview

Databricks maintains several Spark extensions. This oracle validates API parity and behavior correctness.

### Projects Under Test

| Project | Repository | Stars | Purpose |
|---------|------------|-------|---------|
| Koalas | databricks/koalas | 3.3k | pandas API on Spark (now in PySpark) |
| spark-deep-learning | databricks/spark-deep-learning | 2.0k | Deep learning on Spark |
| spark-redshift | databricks/spark-redshift | 589 | Redshift connector |
| spark-corenlp | databricks/spark-corenlp | 462 | NLP on Spark |
| spark-tfocs | databricks/spark-tfocs | 170 | Optimization on Spark |

---

## 2. Pandas API Parity Tests (Koalas/PySpark pandas)

### 2.1 DataFrame Creation
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| DF-001 | DataFrame from dict | Columns preserved | Exact |
| DF-002 | DataFrame with index | Index preserved | Exact |
| DF-003 | DataFrame.from_records | Same shape | Exact |
| DF-004 | Column dtypes | Same types | Exact |

### 2.2 Series Operations
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| SR-001 | Series.mean() | Arithmetic mean | 1e-10 |
| SR-002 | Series.sum() | Sum | Exact |
| SR-003 | Series.std() | Sample std dev | 1e-10 |
| SR-004 | Series * scalar | Element-wise | Exact |
| SR-005 | Boolean indexing | Filter | Exact |
| SR-006 | str.upper() | Uppercase | Exact |
| SR-007 | isna() | NA detection | Exact |
| SR-008 | fillna() | NA replacement | Exact |

### 2.3 GroupBy Operations
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| GB-001 | groupby().sum() | Group sum | Exact |
| GB-002 | groupby().mean() | Group mean | 1e-10 |
| GB-003 | groupby().count() | Group count | Exact |
| GB-004 | groupby().agg() | Multiple aggs | Exact |
| GB-005 | Multi-column agg | Dict-based | Exact |

### 2.4 Join Operations
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| JN-001 | Inner join | Intersection | Exact |
| JN-002 | Left join | Left + matched | Exact |
| JN-003 | Right join | Right + matched | Exact |
| JN-004 | Outer join | Union | Exact |
| JN-005 | Concat | Row-wise union | Exact |

### 2.5 Window Functions
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| WN-001 | rolling().mean() | Moving average | 1e-10 |
| WN-002 | cumsum() | Cumulative sum | Exact |
| WN-003 | rank() | Rank | Exact |
| WN-004 | shift() | Lag | Exact |
| WN-005 | pct_change() | Percent change | 1e-10 |

### 2.6 Index Operations
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| IX-001 | loc[] | Label indexing | Exact |
| IX-002 | iloc[] | Position indexing | Exact |
| IX-003 | reset_index() | Index to column | Exact |
| IX-004 | set_index() | Column to index | Exact |
| IX-005 | MultiIndex | Hierarchical | Exact |

### 2.7 Data Type Conversion
| ID | Operation | pandas Behavior | Tolerance |
|----|-----------|-----------------|-----------|
| DT-001 | astype(float) | Int to float | Exact |
| DT-002 | astype(str) | To string | Exact |
| DT-003 | to_datetime() | Parse dates | Exact |
| DT-004 | Categorical | Category dtype | Exact |

---

## 3. Golden Corpus Structure

```
spark-extensions/
├── oracle/
│   ├── pandas_api/
│   │   ├── dataframe_creation.json
│   │   ├── series_operations.json
│   │   ├── groupby_operations.json
│   │   └── ...
│   └── deep_learning/
│       └── transfer_learning.json
├── specs/
│   ├── spark-extensions-oracle.md
│   └── spark-extensions-qa-checklist.md
└── scripts/
    ├── test_pandas_api_parity.py
    └── validate_koalas.py
```

---

## 4. Falsification Checklist

### 4.1 Pandas API - DataFrame
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DF-001 | DataFrame from dict | Cols preserved | Correct | + |
| DF-002 | DataFrame with index | Index preserved | Correct | + |
| DF-003 | DataFrame.from_records | Same shape | Correct | + |
| DF-004 | Column dtypes | Same types | Correct | + |

### 4.2 Pandas API - Series
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| SR-001 | mean() | 3.0 | 3.0 | + |
| SR-002 | sum() | 15 | 15 | + |
| SR-003 | std() | 1.581139 | 1.581139 | + |
| SR-004 | multiplication | [2,4,6,8,10] | Correct | + |
| SR-005 | boolean indexing | [4, 5] | Correct | + |
| SR-006 | str.upper() | Uppercase | Correct | + |
| SR-007 | isna() | NA mask | Correct | + |
| SR-008 | fillna() | NA replaced | Correct | + |

### 4.3 Pandas API - GroupBy
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| GB-001 | sum | {A:3, B:7, C:5} | Correct | + |
| GB-002 | mean | {A:1.5, B:3.5, C:5.0} | Correct | + |
| GB-003 | count | {A:2, B:2, C:1} | Correct | + |
| GB-004 | agg multiple | 3 columns | Correct | + |
| GB-005 | multi-col agg | Dict-based | Correct | + |

### 4.4 Pandas API - Joins
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| JN-001 | inner | 2 rows | Correct | + |
| JN-002 | left | 3 rows, NA | Correct | + |
| JN-003 | right | 3 rows, NA | Correct | + |
| JN-004 | outer | 4 rows | Correct | + |
| JN-005 | concat | 6 rows | Correct | + |

### 4.5 Pandas API - Window
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| WN-001 | rolling mean | [NA, 1.5, ...] | Correct | + |
| WN-002 | cumsum | [1,3,6,10,15] | Correct | + |
| WN-003 | rank | [1,2,3,4,5] | Correct | + |
| WN-004 | shift | [NA, 1, 2, ...] | Correct | + |
| WN-005 | pct_change | 1.0 at [1] | Correct | + |

### 4.6 Pandas API - Index
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| IX-001 | loc['x','a'] | 1 | 1 | + |
| IX-002 | iloc[0,0] | 1 | 1 | + |
| IX-003 | reset_index | 3 cols | Correct | + |
| IX-004 | set_index | Col as index | Correct | + |
| IX-005 | MultiIndex | Hierarchical | Correct | + |

### 4.7 Pandas API - Dtypes
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DT-001 | int to float | float64 | float64 | + |
| DT-002 | to string | str values | Correct | + |
| DT-003 | to_datetime | datetime | Correct | + |
| DT-004 | categorical | 3 cats | Correct | + |

---

## References

- pandas documentation: https://pandas.pydata.org/docs/
- PySpark pandas API: https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/
- Koalas: https://github.com/databricks/koalas
