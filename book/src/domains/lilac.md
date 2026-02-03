# Lilac Data Quality

[Lilac](https://github.com/lilacai/lilac) is a data curation tool from Databricks that provides data quality signals including PII detection, deduplication, language detection, and text statistics.

## Test Coverage: 51/52 (98%)

| Signal | Tests | Status |
|--------|-------|--------|
| PII Detection | 18/18 | Pass |
| Deduplication | 8/9 | Pass (1 infrastructure-dependent) |
| Language Detection | 9/10 | Pass (1 edge case) |
| Text Statistics | 16/16 | Pass |

## Running Tests

```bash
# Run all Lilac tests
uv run lilac/scripts/test_pii_detection.py
uv run lilac/scripts/test_dedup_detection.py
uv run lilac/scripts/test_language_detection.py
uv run lilac/scripts/test_text_statistics.py
```

## Ground Truth Philosophy

Lilac's data quality signals are tested against **independent reference implementations**:

| Signal | Reference |
|--------|-----------|
| Credit Card | Luhn algorithm (ISO/IEC 7812-1) |
| SSN | US Social Security Administration format |
| Email | RFC 5322 regex pattern |
| Phone | E.164 format patterns |
| Deduplication | MinHash/Jaccard similarity |
| Language | langdetect library |
| Text Stats | Flesch-Kincaid standard formulas |

## Architecture

```
lilac/
├── scripts/
│   ├── test_pii_detection.py      # 18 tests
│   ├── test_dedup_detection.py    # 9 tests
│   ├── test_language_detection.py # 10 tests
│   └── test_text_statistics.py    # 16 tests
├── specs/
│   ├── data-quality-oracle.md     # Signal specifications
│   └── data-quality-qa-checklist.md
└── oracle/
    └── (golden outputs)
```

## Key Falsification Patterns

### Near-Miss Testing

Tests include inputs that are **almost** valid but should fail:

```python
# Valid credit card (passes Luhn)
"4532015112830366"  # Should detect

# Invalid credit card (fails Luhn by 1 digit)
"4532015112830367"  # Should NOT detect
```

### Boundary Testing

Tests exercise boundary conditions:

```python
# Minimum valid SSN
"001-01-0001"

# Maximum valid SSN (excluding special ranges)
"899-99-9999"

# Invalid: Group 00
"123-00-4567"  # Should NOT detect
```

### Unicode Handling

Tests verify correct Unicode behavior:

```python
# Full-width digits (should not match credit card pattern)
"４５３２０１５１１２８３０３６６"

# Mixed scripts
"Call me at ٠١٢٣٤٥٦٧٨٩"  # Arabic-Indic digits
```
