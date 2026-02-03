# TPC-H Benchmark

TPC-H is an ad-hoc decision support benchmark that measures database performance for complex business queries.

## Specification

- **Version**: 3.0.1
- **Tables**: 8
- **Queries**: 22
- **Scale Factors**: 1, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000

## Scale Factor 1 Row Counts

Ground truth row counts from TPC-H specification:

| Table | Rows | Description |
|-------|------|-------------|
| customer | 150,000 | Customer records |
| lineitem | 6,001,215 | Order line items |
| nation | 25 | Nations (fixed) |
| orders | 1,500,000 | Customer orders |
| part | 200,000 | Parts catalog |
| partsupp | 800,000 | Part-supplier relationships |
| region | 5 | Regions (fixed) |
| supplier | 10,000 | Suppliers |

## Schema

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  REGION  │────<│  NATION  │────<│ SUPPLIER │
└──────────┘     └──────────┘     └────┬─────┘
     │                                  │
     │           ┌──────────┐           │
     └──────────<│ CUSTOMER │           │
                 └────┬─────┘           │
                      │                 │
                 ┌────┴─────┐     ┌─────┴────┐
                 │  ORDERS  │     │ PARTSUPP │
                 └────┬─────┘     └────┬─────┘
                      │                │
                 ┌────┴─────┐     ┌────┴─────┐
                 │ LINEITEM │────<│   PART   │
                 └──────────┘     └──────────┘
```

## Validation Code

```python
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

def validate_tpch_row_counts(actual_counts: dict) -> list[str]:
    """Validate row counts against TPC-H specification."""
    errors = []
    for table, expected in TPCH_SF1_ROW_COUNTS.items():
        if table not in actual_counts:
            errors.append(f"Missing table: {table}")
        elif actual_counts[table] != expected:
            errors.append(
                f"{table}: expected {expected:,}, got {actual_counts[table]:,}"
            )
    return errors
```

## Scale Factor Scaling

```python
def get_tpch_row_count(table: str, scale_factor: int) -> int:
    """Get expected row count for given scale factor."""
    # Fixed dimension tables
    if table == "nation":
        return 25
    if table == "region":
        return 5

    # Scaled tables
    base_counts = {
        "customer": 150_000,
        "lineitem": 6_001_215,
        "orders": 1_500_000,
        "part": 200_000,
        "partsupp": 800_000,
        "supplier": 10_000,
    }

    return base_counts[table] * scale_factor
```

## Query Examples

### Q1: Pricing Summary Report

```sql
SELECT
    l_returnflag,
    l_linestatus,
    SUM(l_quantity) AS sum_qty,
    SUM(l_extendedprice) AS sum_base_price,
    SUM(l_extendedprice * (1 - l_discount)) AS sum_disc_price,
    SUM(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
    AVG(l_quantity) AS avg_qty,
    AVG(l_extendedprice) AS avg_price,
    AVG(l_discount) AS avg_disc,
    COUNT(*) AS count_order
FROM lineitem
WHERE l_shipdate <= DATE '1998-12-01' - INTERVAL '90' DAY
GROUP BY l_returnflag, l_linestatus
ORDER BY l_returnflag, l_linestatus;
```

### Q6: Forecasting Revenue Change

```sql
SELECT SUM(l_extendedprice * l_discount) AS revenue
FROM lineitem
WHERE
    l_shipdate >= DATE '1994-01-01'
    AND l_shipdate < DATE '1994-01-01' + INTERVAL '1' YEAR
    AND l_discount BETWEEN 0.06 - 0.01 AND 0.06 + 0.01
    AND l_quantity < 24;
```

## Lineitem Row Count Formula

The lineitem table has a variable number of rows per order:

```python
def estimate_lineitem_rows(scale_factor: int) -> int:
    """
    Lineitem rows = orders * avg_items_per_order

    Average items per order: ~4 (range 1-7)
    SF1: 1,500,000 orders * ~4 = 6,001,215 lineitems
    """
    orders = 1_500_000 * scale_factor
    avg_items = 4.00081  # Empirically determined
    return int(orders * avg_items)
```

## References

- [TPC-H Specification v3.0.1](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v3.0.1.pdf)
- [dbgen Data Generator](https://github.com/databricks/tpch-dbgen)
