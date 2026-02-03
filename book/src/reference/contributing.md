# Contributing

Guidelines for contributing to the Databricks Ground Truth Corpus.

## Adding New Tests

### 1. Choose the Right Domain

| Domain | Use For |
|--------|---------|
| `lilac/` | Data quality signals (PII, dedup, language) |
| `megablocks/` | MoE model validation |
| `spark-extensions/` | pandas API parity |
| `sdk-parity/` | Cross-language SDK behavior |
| `sql-connectors/` | SQL result parity |
| `cli-tools/` | CLI command behavior |
| `terraform/` | Infrastructure state validation |
| `benchmarks/` | TPC and algorithm validation |

### 2. Create Test File

Use PEP 723 inline script metadata for dependencies:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.24",
#     "pandas>=2.0",
# ]
# ///
"""Test description."""
```

### 3. Follow Test ID Convention

```
DOMAIN-NNN: Description

Examples:
CC-001: Valid Visa card detection
TPCDS-005: Item table row count
ALS-003: Factor matrix shape
```

### 4. Implement Falsification Pattern

```python
def test_something():
    """
    Falsification test: describe what would falsify the implementation.

    Ground Truth: [specification or reference]
    """
    # Arrange
    input_data = create_test_input()

    # Act
    result = implementation_under_test(input_data)

    # Assert
    assert result == expected, f"Expected {expected}, got {result}"
```

### 5. Update Checklist

Add test IDs to the appropriate checklist:

- Domain-specific: `{domain}/specs/{domain}-qa-checklist.md`
- Master: `QA-CHECKLIST.md`

## Code Standards

### Python

- Python 3.11+
- ruff for linting and formatting
- ty for type checking
- 100% code coverage target

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
ty check .

# Coverage
python3 -m trace --count script.py
```

### Docstrings

```python
def function_name(param: type) -> return_type:
    """Short description.

    Longer description if needed.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this happens.
    """
```

## Pull Request Process

### 1. Create Branch (if applicable)

```bash
git checkout -b feature/add-new-domain-tests
```

### 2. Make Changes

- Add test files
- Update checklists
- Update book documentation

### 3. Run Validation

```bash
# All tests pass
uv run run_all_tests.py

# Lint passes
ruff check .

# Format correct
ruff format --check .
```

### 4. Submit PR

Include in PR description:
- Test IDs added
- Domain(s) affected
- Coverage change

## Oracle Integration

Tests may be indexed by batuta's oracle RAG system:

```bash
# In batuta repo
batuta oracle --rag-index

# Query
batuta oracle --rag "PII detection patterns"
```

Ensure test files include clear docstrings for good RAG retrieval.

## Ground Truth Sources

When adding tests, document the ground truth source:

| Source Type | Examples |
|-------------|----------|
| Specification | TPC-DS v3.2.0, IEEE 754 |
| Reference Implementation | pandas, HuggingFace |
| Standard | ISO 8601, RFC 5322 |
| Algorithm | Luhn, MinHash, Flesch-Kincaid |

## Questions?

- Open an issue on GitHub
- Check existing tests for patterns
- Review methodology documentation
