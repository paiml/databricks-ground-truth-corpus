# TPC-DS Benchmark

TPC-DS (Transaction Processing Performance Council - Decision Support) is the industry standard benchmark for decision support systems.

## Specification

- **Version**: 3.2.0
- **Tables**: 24
- **Queries**: 99
- **Scale Factors**: 1, 10, 100, 1000, 10000, 30000, 100000

## Scale Factor 1 Row Counts

Ground truth row counts from TPC-DS specification:

| Table | Rows | Description |
|-------|------|-------------|
| call_center | 6 | Call center dimension |
| catalog_page | 11,718 | Catalog page dimension |
| catalog_returns | 144,067 | Catalog return facts |
| catalog_sales | 1,441,548 | Catalog sales facts |
| customer | 100,000 | Customer dimension |
| customer_address | 50,000 | Customer address dimension |
| customer_demographics | 1,920,800 | Customer demographics |
| date_dim | 73,049 | Date dimension |
| household_demographics | 7,200 | Household demographics |
| income_band | 20 | Income band dimension |
| inventory | 11,745,000 | Inventory facts |
| item | 18,000 | Item dimension |
| promotion | 300 | Promotion dimension |
| reason | 35 | Return reason dimension |
| ship_mode | 20 | Ship mode dimension |
| store | 12 | Store dimension |
| store_returns | 287,514 | Store return facts |
| store_sales | 2,880,404 | Store sales facts |
| time_dim | 86,400 | Time dimension |
| warehouse | 5 | Warehouse dimension |
| web_page | 60 | Web page dimension |
| web_returns | 71,763 | Web return facts |
| web_sales | 719,384 | Web sales facts |
| web_site | 30 | Web site dimension |

## Validation Code

```python
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

def validate_tpcds_row_counts(actual_counts: dict) -> list[str]:
    """Validate row counts against TPC-DS specification."""
    errors = []
    for table, expected in TPCDS_SF1_ROW_COUNTS.items():
        if table not in actual_counts:
            errors.append(f"Missing table: {table}")
        elif actual_counts[table] != expected:
            errors.append(
                f"{table}: expected {expected:,}, got {actual_counts[table]:,}"
            )
    return errors
```

## Scale Factor Scaling

Row counts scale linearly with scale factor:

```python
def get_tpcds_row_count(table: str, scale_factor: int) -> int:
    """Get expected row count for given scale factor."""
    base_count = TPCDS_SF1_ROW_COUNTS[table]

    # Dimension tables don't scale linearly
    dimension_tables = {
        "call_center", "catalog_page", "customer_demographics",
        "date_dim", "household_demographics", "income_band",
        "promotion", "reason", "ship_mode", "time_dim",
        "warehouse", "web_page", "web_site"
    }

    if table in dimension_tables:
        # Dimension scaling is more complex - see spec
        return base_count  # Simplified

    # Fact tables scale linearly
    return base_count * scale_factor
```

## Query Validation

TPC-DS queries must return deterministic results for validation:

```sql
-- Query 1 example (simplified)
SELECT
    c_customer_id,
    c_salutation,
    c_first_name,
    c_last_name
FROM customer
WHERE c_customer_sk IN (
    SELECT ss_customer_sk
    FROM store_sales
    WHERE ss_sold_date_sk BETWEEN 2451180 AND 2451270
)
ORDER BY c_customer_id
LIMIT 100;
```

## References

- [TPC-DS Specification v3.2.0](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v3.2.0.pdf)
- [dsdgen Data Generator](https://github.com/databricks/tpcds-kit)
