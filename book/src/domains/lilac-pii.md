# PII Detection

Ground truth tests for Lilac's PII (Personally Identifiable Information) detection signals.

## Test Coverage: 18/18 (100%)

### Credit Card Detection (5 tests)

| Test | Pattern | Expected |
|------|---------|----------|
| Valid Visa | `4532015112830366` | Detect |
| Invalid Luhn | `4532015112830367` | No detect |
| With separators | `4532-0151-1283-0366` | Detect |
| Too short | `453201511283` | No detect |
| Too long | `45320151128303661234` | No detect |

### Luhn Algorithm

Credit card validation uses the Luhn checksum (ISO/IEC 7812-1):

```python
def luhn_checksum(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    total = sum(odd_digits)
    for digit in even_digits:
        doubled = digit * 2
        total += doubled if doubled < 10 else doubled - 9

    return total % 10 == 0
```

### SSN Detection (5 tests)

| Test | Pattern | Expected |
|------|---------|----------|
| Standard format | `123-45-6789` | Detect |
| No separators | `123456789` | Detect |
| Invalid area | `000-45-6789` | No detect |
| Invalid group | `123-00-6789` | No detect |
| Too short | `123-45-678` | No detect |

### SSN Validation Rules

Per Social Security Administration:
- Area number: 001-899 (excluding 666)
- Group number: 01-99
- Serial number: 0001-9999

```python
SSN_INVALID_PATTERNS = [
    r"^000",           # Area 000 invalid
    r"^666",           # Area 666 reserved
    r"^9\d{2}",        # Area 900-999 reserved
    r"^\d{3}-00-",     # Group 00 invalid
    r"-0000$",         # Serial 0000 invalid
]
```

### Email Detection (4 tests)

| Test | Pattern | Expected |
|------|---------|----------|
| Standard | `user@example.com` | Detect |
| With subdomain | `user@mail.example.com` | Detect |
| Invalid TLD | `user@example` | No detect |
| Missing @ | `user.example.com` | No detect |

### Phone Detection (4 tests)

| Test | Pattern | Expected |
|------|---------|----------|
| US format | `(555) 123-4567` | Detect |
| International | `+1-555-123-4567` | Detect |
| Too short | `555-1234` | No detect |
| Letters | `555-CALL-NOW` | No detect |

## Running Tests

```bash
uv run lilac/scripts/test_pii_detection.py
```

## Example Test Output

```
=== Lilac PII Detection Ground Truth Tests ===

Section 1: Credit Card Detection
  [PASS] CC-001: Valid Visa card number detected
  [PASS] CC-002: Invalid Luhn checksum rejected
  [PASS] CC-003: Card with separators detected
  [PASS] CC-004: Short number rejected
  [PASS] CC-005: Long number rejected

Section 2: SSN Detection
  [PASS] SSN-001: Standard SSN format detected
  ...

Summary: 18/18 tests passed
```
