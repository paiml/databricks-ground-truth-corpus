# QA Checklist

Master checklist of all 322 falsification tests across 8 domains.

## Summary

| Domain | Passing | Total | Coverage |
|--------|---------|-------|----------|
| SDK Parity | 19 | 45 | 42% |
| MegaBlocks MoE | 8 | 30 | 27% |
| Lilac Data Quality | 51 | 52 | 98% |
| SQL Connectors | 0 | 55 | 0% |
| CLI Tools | 0 | 35 | 0% |
| Terraform | 0 | 30 | 0% |
| Spark Extensions | 36 | 40 | 90% |
| Benchmarks | 15 | 35 | 43% |
| **Total** | **129** | **322** | **40%** |

## By Domain

### SDK Parity (19/45)

```
[x] SDK-001: Python snake_case validation
[x] SDK-002: Go PascalCase validation
[x] SDK-003: Java camelCase validation
[x] SDK-004: Python→Go name mapping
[x] SDK-005: Python→Java name mapping
[x] SDK-006: Bidirectional name mapping
[x] SDK-007: int → int64 → Long type mapping
[x] SDK-008: str → string → String type mapping
[x] SDK-009: bool → bool → Boolean type mapping
[x] SDK-010: list → slice → List type mapping
[x] SDK-011: dict → map → Map type mapping
[x] SDK-012: ISO 8601 timestamp format
[x] SDK-013: Unix epoch milliseconds format
[x] SDK-014: Cross-language timestamp conversion
[x] SDK-015: Python enum SCREAMING_SNAKE
[x] SDK-016: Go enum PascalCase
[x] SDK-017: Java enum convention
[x] SDK-018: None/nil/null handling
[x] SDK-019: Optional field handling
[ ] SDK-020 - SDK-045: Require SDK infrastructure
```

### MegaBlocks MoE (8/30)

```
[x] MOE-001: Top-k selection correctness
[x] MOE-002: Router weight normalization
[x] MOE-003: Load balancing auxiliary loss
[x] MOE-004: Expert capacity enforcement
[x] MOE-011: Single expert forward
[x] MOE-012: Multi-expert parallel forward
[x] MOE-021: HuggingFace Mixtral parity
[x] MOE-022: fp32 tolerance compliance
[ ] MOE-005 - MOE-030: Require GPU + grouped_gemm
```

### Lilac Data Quality (51/52)

```
[x] CC-001 - CC-005: Credit card detection (5/5)
[x] SSN-001 - SSN-005: SSN detection (5/5)
[x] EMAIL-001 - EMAIL-004: Email detection (4/4)
[x] PHONE-001 - PHONE-004: Phone detection (4/4)
[x] DEDUP-001 - DEDUP-008: Deduplication (8/9)
[ ] DEDUP-009: Lilac infrastructure required
[x] LANG-001 - LANG-009: Language detection (9/10)
[ ] LANG-010: Short text unreliable (known limitation)
[x] STATS-001 - STATS-016: Text statistics (16/16)
```

### Spark Extensions (36/40)

```
[x] DF-001 - DF-008: DataFrame operations (8/8)
[x] S-001 - S-008: Series operations (8/8)
[x] GB-001 - GB-008: GroupBy operations (8/8)
[x] J-001 - J-006: Join operations (6/6)
[x] W-001 - W-006: Window functions (6/6)
[ ] SP-001 - SP-004: Require Spark cluster
```

### Benchmarks (15/35)

```
[x] TPCDS-001 - TPCDS-005: TPC-DS row counts (5/5)
[x] TPCH-001 - TPCH-005: TPC-H row counts (5/5)
[x] ALS-001 - ALS-005: ALS algorithm properties (5/5)
[ ] TPCDS-006 - TPCDS-020: Query validation (requires data)
[ ] TPCH-006 - TPCH-020: Query validation (requires data)
```

### SQL Connectors (0/55)

```
[ ] SQL-001 - SQL-055: Require Databricks workspace
```

### CLI Tools (0/35)

```
[ ] CLI-001 - CLI-035: Require CLI installation
```

### Terraform (0/30)

```
[ ] TF-001 - TF-030: Require Terraform + Databricks
```

## Running All Tests

```bash
# Run all standalone tests
uv run run_all_tests.py

# Run specific domain
uv run lilac/scripts/test_pii_detection.py
uv run lilac/scripts/test_dedup_detection.py
uv run lilac/scripts/test_language_detection.py
uv run lilac/scripts/test_text_statistics.py
uv run benchmarks/scripts/test_benchmark_oracle.py
uv run spark-extensions/scripts/test_pandas_api_parity.py
uv run sdk-parity/scripts/test_sdk_conventions.py
```

## Test Output Format

All tests produce standardized output:

```
=== [Domain] Ground Truth Tests ===

Section N: [Category]
  [PASS] TEST-001: Description
  [PASS] TEST-002: Description
  [FAIL] TEST-003: Description - expected X, got Y
  [SKIP] TEST-004: Description - reason

Summary: X/Y tests passed
```
