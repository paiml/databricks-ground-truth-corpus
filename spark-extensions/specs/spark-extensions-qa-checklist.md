# Spark Extensions - Falsification QA Checklist

**Date:** 2026-02-03
**Methodology:** Popperian Falsification (attempt to break, not verify)
**Philosophy:** "The wrong view of science betrays itself in the craving to be right"

---

## 1. Pandas API Ground Truth Tests

### 1.1 DataFrame Creation
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| DF-001 | DataFrame from dict | Columns preserved | ['a', 'b'] | + |
| DF-002 | DataFrame with custom index | Index preserved | ['x', 'y', 'z'] | + |
| DF-003 | DataFrame from records | Shape (2, 2) | (2, 2) | + |
| DF-004 | Column dtypes | int64, float64 | Correct | + |

### 1.2 Series Operations
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| SR-001 | Series mean | 3.0 | 3.0 | + |
| SR-002 | Series sum | 15 | 15 | + |
| SR-003 | Series std | 1.581139 | 1.581139 | + |
| SR-004 | Series multiplication | [2,4,6,8,10] | Correct | + |
| SR-005 | Boolean indexing | [4, 5] | [4, 5] | + |
| SR-006 | str.upper() | UPPERCASE | Correct | + |
| SR-007 | isna() | [F,F,T,F] | Correct | + |
| SR-008 | fillna() | NA replaced | Correct | + |

### 1.3 GroupBy Operations
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| GB-001 | GroupBy sum | {A:3, B:7, C:5} | Correct | + |
| GB-002 | GroupBy mean | {A:1.5, B:3.5, C:5.0} | Correct | + |
| GB-003 | GroupBy count | {A:2, B:2, C:1} | Correct | + |
| GB-004 | GroupBy agg multiple | [sum, mean, count] | Correct | + |
| GB-005 | GroupBy multiple columns | Dict-based | Correct | + |

### 1.4 Join Operations
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| JN-001 | Inner join | 2 rows, keys [b, c] | Correct | + |
| JN-002 | Left join | 3 rows, NA for 'a' | Correct | + |
| JN-003 | Right join | 3 rows, NA for 'd' | Correct | + |
| JN-004 | Outer join | 4 rows | Correct | + |
| JN-005 | Concat DataFrames | 6 rows | Correct | + |

### 1.5 Window Functions
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| WN-001 | Rolling mean | [NA, 1.5, 2.5, 3.5, 4.5] | Correct | + |
| WN-002 | Cumulative sum | [1, 3, 6, 10, 15] | Correct | + |
| WN-003 | Rank | [1.0, 2.0, 3.0, 4.0, 5.0] | Correct | + |
| WN-004 | Shift | [NA, 1, 2, 3, 4] | Correct | + |
| WN-005 | Percent change | 1.0 at index 1 | Correct | + |

### 1.6 Index Operations
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| IX-001 | loc label indexing | 1 | 1 | + |
| IX-002 | iloc position indexing | 1 | 1 | + |
| IX-003 | Reset index | 3 columns | Correct | + |
| IX-004 | Set index | Column as index | Correct | + |
| IX-005 | MultiIndex creation | Hierarchical access | Correct | + |

### 1.7 Data Type Conversion
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| DT-001 | astype int to float | float64 | float64 | + |
| DT-002 | astype to string | ['1', '2', '3'] | Correct | + |
| DT-003 | to_datetime | datetime64 | Correct | + |
| DT-004 | Categorical dtype | 3 categories | Correct | + |

---

## 2. Execution Log

```
Date: 2026-02-03
Executor: Claude Code
Command: uv run spark-extensions/scripts/test_pandas_api_parity.py
```

### Results Summary

| Category | Total | Passed | Failed |
|----------|-------|--------|--------|
| DataFrame Creation | 4 | 4 | 0 |
| Series Operations | 8 | 8 | 0 |
| GroupBy Operations | 5 | 5 | 0 |
| Join Operations | 5 | 5 | 0 |
| Window Functions | 5 | 5 | 0 |
| Index Operations | 5 | 5 | 0 |
| Data Type Conversion | 4 | 4 | 0 |
| **TOTAL** | **36** | **36** | **0** |

---

## 3. Algorithms Validated

### 3.1 pandas API Coverage
- **DataFrame**: Creation, indexing, selection
- **Series**: Arithmetic, string ops, NA handling
- **GroupBy**: Aggregations (sum, mean, count, agg)
- **Joins**: Inner, left, right, outer, concat
- **Window**: Rolling, cumsum, rank, shift, pct_change
- **Index**: loc, iloc, reset, set, MultiIndex
- **Dtypes**: Type conversion, datetime, categorical

### 3.2 Test Methodology
- Ground truth established via pandas 2.0+
- All operations tested in isolation
- Results captured as reference for Koalas/PySpark validation

---

## 4. Next Steps (Requires Spark)

| Test | Status | Notes |
|------|--------|-------|
| Koalas vs pandas | PENDING | Requires PySpark |
| spark-deep-learning | PENDING | Requires Spark + TF |
| spark-redshift | PENDING | Requires Redshift |

---

## Sign-off

- [x] All 36 pandas API ground truth tests pass
- [x] Coverage spans 7 major pandas API categories
- [x] Reference values documented for Koalas validation

**Verdict: COMPLETE** - Pandas API ground truth established. Koalas validation requires PySpark.
