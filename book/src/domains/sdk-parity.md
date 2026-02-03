# SDK Parity

Ground truth tests for cross-language SDK consistency (Python, Go, Java).

## Test Coverage: 19/19 (100%)

## Overview

The Databricks SDK exists in multiple languages. These tests validate that naming conventions, type mappings, and behaviors are consistent across implementations.

## Test Categories

### Naming Conventions (6 tests)

| Test | Convention | Example |
|------|------------|---------|
| SDK-001 | Python snake_case | `create_job`, `list_clusters` |
| SDK-002 | Go PascalCase | `CreateJob`, `ListClusters` |
| SDK-003 | Java camelCase | `createJob`, `listClusters` |
| SDK-004 | Python→Go mapping | `create_job` → `CreateJob` |
| SDK-005 | Python→Java mapping | `create_job` → `createJob` |
| SDK-006 | Bidirectional mapping | Verify round-trip |

### Type Mappings (5 tests)

| Test | Python Type | Go Type | Java Type |
|------|-------------|---------|-----------|
| SDK-007 | `int` | `int64` | `Long` |
| SDK-008 | `str` | `string` | `String` |
| SDK-009 | `bool` | `bool` | `Boolean` |
| SDK-010 | `list` | `[]T` (slice) | `List<T>` |
| SDK-011 | `dict` | `map[K]V` | `Map<K,V>` |

### Timestamp Formats (3 tests)

| Test | Format | Example |
|------|--------|---------|
| SDK-012 | ISO 8601 | `2024-01-15T10:30:00Z` |
| SDK-013 | Unix epoch ms | `1705315800000` |
| SDK-014 | Cross-language conversion | Bidirectional |

### Enum Conventions (3 tests)

| Test | Description | Example |
|------|-------------|---------|
| SDK-015 | Python: SCREAMING_SNAKE | `JOB_STATUS_RUNNING` |
| SDK-016 | Go: PascalCase const | `JobStatusRunning` |
| SDK-017 | Java: enum member | `JobStatus.RUNNING` |

### Null Handling (2 tests)

| Test | Python | Go | Java |
|------|--------|-----|------|
| SDK-018 | `None` | `nil` | `null` |
| SDK-019 | Optional fields | Omitted | Omitted | `Optional<T>` |

## Implementation

```python
def to_snake_case(name: str) -> str:
    """Convert PascalCase/camelCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper():
            if i > 0 and (name[i-1].islower() or
                         (i < len(name)-1 and name[i+1].islower())):
                result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result)

def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))

def to_camel_case(name: str) -> str:
    """Convert snake_case to camelCase."""
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ''
```

## Ground Truth Validation

```python
NAMING_GROUND_TRUTH = {
    # Python snake_case → Go PascalCase → Java camelCase
    "create_job": ("CreateJob", "createJob"),
    "list_clusters": ("ListClusters", "listClusters"),
    "get_run_output": ("GetRunOutput", "getRunOutput"),
    "submit_run": ("SubmitRun", "submitRun"),
    "delete_workspace_object": ("DeleteWorkspaceObject", "deleteWorkspaceObject"),
}

def test_naming_conventions():
    for python_name, (go_name, java_name) in NAMING_GROUND_TRUTH.items():
        assert to_pascal_case(python_name) == go_name
        assert to_camel_case(python_name) == java_name
        assert to_snake_case(go_name) == python_name
```

## Running Tests

```bash
uv run sdk-parity/scripts/test_sdk_conventions.py
```

## Example Output

```
=== SDK Parity Ground Truth Tests ===

Section 1: Naming Conventions
  [PASS] SDK-001: Python snake_case validation
  [PASS] SDK-002: Go PascalCase validation
  [PASS] SDK-003: Java camelCase validation
  ...

Section 2: Type Mappings
  [PASS] SDK-007: int → int64 → Long
  [PASS] SDK-008: str → string → String
  ...

Summary: 19/19 tests passed
```

## Cross-Language Gotchas

| Issue | Python | Go | Java |
|-------|--------|-----|------|
| Empty list | `[]` | `nil` or `[]T{}` | `Collections.emptyList()` |
| Empty dict | `{}` | `nil` or `map[K]V{}` | `Collections.emptyMap()` |
| Zero values | Explicit | Default | Null or default |
| Optional | `Optional[T]` | Pointer `*T` | `Optional<T>` |
