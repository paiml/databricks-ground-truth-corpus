# Popperian Falsification

Karl Popper's philosophy of science emphasizes **falsification** over verification. A scientific theory can never be proven true, only proven false. This corpus applies these principles to software testing.

## Core Principles

### 1. Severe Testing

Design tests that have a **high probability of failing** if the implementation is wrong.

```python
# Bad: Tests that rarely fail
def test_pii_detects_something():
    result = detect_pii("some text")
    assert result is not None  # Always passes

# Good: Tests designed to catch specific failures
def test_pii_luhn_validation():
    """Luhn checksum must validate correctly - rejects invalid cards."""
    valid_card = "4532015112830366"    # Valid Luhn checksum
    invalid_card = "4532015112830367"   # Invalid (off by 1)

    assert detect_credit_card(valid_card) == True
    assert detect_credit_card(invalid_card) == False
```

### 2. Corroboration, Not Verification

Passing tests provide **corroboration**, not proof. Each passing test only means the implementation survived one attempt to falsify it.

```python
# Each test is an attempted falsification
FALSIFICATION_ATTEMPTS = [
    ("boundary", "1234567890123456"),     # Exact 16 digits
    ("overflow", "12345678901234567890"), # Too many digits
    ("unicode", "４５３２０１５１１２８３０３６６"),  # Full-width digits
    ("separator", "4532-0151-1283-0366"), # With dashes
]
```

### 3. Independent Reference

Compare against **independent implementations**, not the same codebase.

| Domain | Reference Implementation |
|--------|-------------------------|
| MegaBlocks MoE | HuggingFace Mixtral |
| pandas API | Official pandas library |
| TPC Benchmarks | TPC specification documents |
| PII Detection | Industry-standard regex patterns |

### 4. Bias Detection

Look for **systematic deviations**, not just point failures.

```python
def test_systematic_bias():
    """Detect if implementation consistently underreports."""
    results = [detect_pii(text) for text in TEST_CORPUS]

    # Check for systematic bias
    false_negative_rate = sum(1 for r in results if r.missed) / len(results)

    # Systematic bias threshold
    assert false_negative_rate < 0.05, f"Systematic under-detection: {false_negative_rate:.1%}"
```

## Falsification vs Verification

| Aspect | Verification (Bad) | Falsification (Good) |
|--------|-------------------|---------------------|
| **Goal** | Prove correctness | Find failures |
| **Mindset** | "Does it work?" | "How can I break it?" |
| **Test Design** | Happy path | Edge cases, boundaries |
| **Success** | Tests pass | Tests reveal bugs |
| **Confidence** | False security | Calibrated uncertainty |

## Application to This Corpus

Every test in this corpus is designed as a **falsification attempt**:

1. **PII Detection**: Tests include near-misses (invalid Luhn checksums, malformed SSNs)
2. **Deduplication**: Tests include similar-but-different texts that should NOT match
3. **Benchmarks**: Tests validate exact row counts against TPC specifications
4. **SDK Parity**: Tests verify cross-language type conversions maintain semantics
