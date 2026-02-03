# Tolerance Standards

Numerical comparisons require explicit tolerance specifications based on data types and IEEE 754 standards.

## Standard Tolerances

| Data Type | Absolute Tolerance | Relative Tolerance | Standard |
|-----------|-------------------|-------------------|----------|
| `fp32` | `1e-5` | `1e-4` | IEEE 754-2019 |
| `fp16` | `1e-3` | `1e-2` | IEEE 754-2019 |
| `int8` | `1e-1` | N/A | Quantization |
| `int4` | `5e-1` | N/A | Quantization |
| `int64` | Exact | N/A | None |
| `string` | Exact | N/A | Unicode NFC |
| `timestamp` | 1ms | N/A | ISO 8601 |

## IEEE 754 Floating-Point Comparison

```python
import numpy as np

def assert_fp32_equal(actual: float, expected: float) -> None:
    """Assert floating-point equality within IEEE 754 fp32 tolerances."""
    np.testing.assert_allclose(
        actual,
        expected,
        atol=1e-5,  # Absolute tolerance
        rtol=1e-4,  # Relative tolerance
    )
```

### Why These Tolerances?

**fp32 (float32)**:
- Machine epsilon: ~1.19e-7
- Practical tolerance: ~1e-5 (accounts for accumulated error)
- Relative tolerance: ~1e-4 (allows 0.01% deviation)

**fp16 (float16)**:
- Machine epsilon: ~9.77e-4
- Practical tolerance: ~1e-3
- Common in ML inference workloads

## Quantization Tolerances

Quantized models trade precision for speed/memory:

```python
# Int8 quantization: 256 discrete levels
# Expected error: ~1/256 ≈ 0.004 per value
INT8_TOLERANCE = 0.1  # Accounts for accumulated error

# Int4 quantization: 16 discrete levels
# Expected error: ~1/16 ≈ 0.0625 per value
INT4_TOLERANCE = 0.5  # Accounts for accumulated error
```

## String Comparisons

All string comparisons use **Unicode NFC normalization**:

```python
import unicodedata

def normalize_string(s: str) -> str:
    """Normalize to Unicode NFC form."""
    return unicodedata.normalize("NFC", s)

def assert_string_equal(actual: str, expected: str) -> None:
    """Assert string equality with NFC normalization."""
    assert normalize_string(actual) == normalize_string(expected)
```

### Why NFC?

Different Unicode representations can look identical:
- `é` (U+00E9, precomposed) vs `e` + `́` (U+0065 + U+0301, decomposed)
- NFC normalizes to the precomposed form

## Timestamp Comparisons

```python
from datetime import datetime, timedelta

TIMESTAMP_TOLERANCE = timedelta(milliseconds=1)

def assert_timestamp_equal(actual: datetime, expected: datetime) -> None:
    """Assert timestamp equality within 1ms tolerance."""
    diff = abs(actual - expected)
    assert diff <= TIMESTAMP_TOLERANCE, f"Timestamp diff: {diff}"
```

## Cross-Implementation Validation

When comparing outputs across implementations:

```python
def validate_cross_implementation(
    impl_a: np.ndarray,
    impl_b: np.ndarray,
    dtype: str = "fp32",
) -> bool:
    """Validate outputs match within dtype-specific tolerances."""
    tolerances = {
        "fp32": {"atol": 1e-5, "rtol": 1e-4},
        "fp16": {"atol": 1e-3, "rtol": 1e-2},
        "int8": {"atol": 1e-1, "rtol": 0},
    }

    tol = tolerances.get(dtype, tolerances["fp32"])
    return np.allclose(impl_a, impl_b, **tol)
```
