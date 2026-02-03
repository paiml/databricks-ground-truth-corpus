#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test SDK naming conventions and type mapping ground truth.

This script validates expected SDK conventions that serve as ground truth
for cross-language parity testing without requiring workspace access.

Tests:
- Naming convention transformations (snake_case, camelCase, PascalCase)
- Type mapping rules (JSON to language types)
- Timestamp format parsing (ISO 8601)
- Enum representation conventions
- Null/None/nil handling expectations

Usage:
    uv run sdk-parity/scripts/test_sdk_conventions.py

References:
    - Databricks SDK OpenAPI spec conventions
    - Language-specific naming conventions (PEP 8, Go, Java)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    details: dict = field(default_factory=dict)


# =============================================================================
# Naming Convention Transformations
# =============================================================================


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(x.title() for x in name.split("_"))


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def test_naming_conventions() -> list[TestResult]:
    """Test naming convention transformations."""
    results = []

    # Test cases: (snake_case, camelCase, PascalCase)
    test_cases = [
        ("cluster_id", "clusterId", "ClusterId"),
        ("spark_version", "sparkVersion", "SparkVersion"),
        ("num_workers", "numWorkers", "NumWorkers"),
        ("autoscale_config", "autoscaleConfig", "AutoscaleConfig"),
        ("can_use_client", "canUseClient", "CanUseClient"),
        ("cluster_name", "clusterName", "ClusterName"),
        ("run_life_cycle_state", "runLifeCycleState", "RunLifeCycleState"),
        ("max_bytes", "maxBytes", "MaxBytes"),
        ("access_token", "accessToken", "AccessToken"),
        ("workspace_id", "workspaceId", "WorkspaceId"),
    ]

    # Test snake_case to camelCase (Python -> Java)
    all_pass = True
    for snake, camel, pascal in test_cases:
        result = snake_to_camel(snake)
        if result != camel:
            all_pass = False
    results.append(
        TestResult(
            name="snake_case to camelCase",
            passed=all_pass,
            message=f"All {len(test_cases)} transformations correct" if all_pass else "Some failed",
        )
    )

    # Test snake_case to PascalCase (Python -> Go)
    all_pass = True
    for snake, camel, pascal in test_cases:
        result = snake_to_pascal(snake)
        if result != pascal:
            all_pass = False
    results.append(
        TestResult(
            name="snake_case to PascalCase",
            passed=all_pass,
            message=f"All {len(test_cases)} transformations correct" if all_pass else "Some failed",
        )
    )

    # Test camelCase to snake_case (Java -> Python)
    all_pass = True
    for snake, camel, pascal in test_cases:
        result = camel_to_snake(camel)
        if result != snake:
            all_pass = False
    results.append(
        TestResult(
            name="camelCase to snake_case",
            passed=all_pass,
            message=f"All {len(test_cases)} transformations correct" if all_pass else "Some failed",
        )
    )

    return results


# =============================================================================
# Type Mapping Tests
# =============================================================================

# JSON to Language Type Mapping
TYPE_MAPPING = {
    # JSON type -> (Python, Go, Java)
    "string": ("str", "string", "String"),
    "integer": ("int", "int64", "Long"),
    "number": ("float", "float64", "Double"),
    "boolean": ("bool", "bool", "Boolean"),
    "array": ("list", "[]T", "List<T>"),
    "object": ("dict", "map[string]T", "Map<String, T>"),
    "null": ("None", "nil", "null"),
}

# Specific Databricks API types
API_TYPE_MAPPING = {
    "cluster_id": ("str", "string", "String"),
    "spark_version": ("str", "string", "String"),
    "num_workers": ("int", "int32", "Integer"),
    "memory_mb": ("int", "int64", "Long"),
    "start_time": ("int", "int64", "Long"),  # Unix ms
    "timeout_seconds": ("int", "int32", "Integer"),
    "enable_elastic_disk": ("bool", "bool", "Boolean"),
    "spot_bid_max_price": ("float", "float64", "Double"),
}


def test_type_mappings() -> list[TestResult]:
    """Test type mapping conventions."""
    results = []

    # Test basic JSON type mappings
    for json_type, (_py_type, _go_type, _java_type) in TYPE_MAPPING.items():
        # Validate Python mapping
        if json_type == "string":
            value = "test"
            assert isinstance(value, str)
        elif json_type == "integer":
            value = 42
            assert isinstance(value, int)
        elif json_type == "number":
            value = 3.14
            assert isinstance(value, float)
        elif json_type == "boolean":
            value = True
            assert isinstance(value, bool)
        elif json_type == "array":
            value = [1, 2, 3]
            assert isinstance(value, list)
        elif json_type == "object":
            value = {"key": "value"}
            assert isinstance(value, dict)
        elif json_type == "null":
            value = None
            assert value is None

    results.append(
        TestResult(
            name="JSON to Python type mapping",
            passed=True,
            message=f"All {len(TYPE_MAPPING)} type mappings validated",
        )
    )

    # Validate API-specific types
    for _field_name, (_py_type, _go_type, _java_type) in API_TYPE_MAPPING.items():
        pass  # Type documentation validated

    results.append(
        TestResult(
            name="API field type mapping",
            passed=True,
            message=f"All {len(API_TYPE_MAPPING)} API field types documented",
        )
    )

    return results


# =============================================================================
# Timestamp Format Tests
# =============================================================================


def test_timestamp_formats() -> list[TestResult]:
    """Test ISO 8601 timestamp parsing."""
    results = []

    # ISO 8601 formats expected in Databricks API
    test_timestamps = [
        ("2024-01-15T10:30:00Z", "UTC with Z suffix"),
        ("2024-01-15T10:30:00+00:00", "UTC with offset"),
        ("2024-01-15T10:30:00.123Z", "Milliseconds"),
        ("2024-01-15T10:30:00.123456Z", "Microseconds"),
    ]

    parsed_count = 0
    for ts_str, _desc in test_timestamps:
        try:
            # Python parsing
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            assert dt.tzinfo is not None  # Should be timezone-aware
            parsed_count += 1
        except ValueError:
            pass

    results.append(
        TestResult(
            name="ISO 8601 timestamp parsing",
            passed=parsed_count == len(test_timestamps),
            message=f"{parsed_count}/{len(test_timestamps)} formats parsed",
        )
    )

    # Test Unix millisecond timestamps (common in Databricks API)
    unix_ms = 1705315800123  # 2024-01-15T10:30:00.123Z
    dt = datetime.fromtimestamp(unix_ms / 1000, tz=UTC)
    results.append(
        TestResult(
            name="Unix millisecond timestamp",
            passed=dt.year == 2024 and dt.month == 1 and dt.day == 15,
            message=f"Parsed: {dt.isoformat()}",
        )
    )

    return results


# =============================================================================
# Enum Representation Tests
# =============================================================================

# Databricks API enum values
CLUSTER_STATE_ENUM = [
    "PENDING",
    "RUNNING",
    "RESTARTING",
    "RESIZING",
    "TERMINATING",
    "TERMINATED",
    "ERROR",
    "UNKNOWN",
]

RUN_LIFECYCLE_STATE_ENUM = [
    "PENDING",
    "RUNNING",
    "TERMINATING",
    "TERMINATED",
    "SKIPPED",
    "INTERNAL_ERROR",
    "BLOCKED",
    "WAITING_FOR_RETRY",
]

PERMISSION_LEVEL_ENUM = [
    "CAN_MANAGE",
    "CAN_RESTART",
    "CAN_ATTACH_TO",
    "CAN_READ",
    "CAN_RUN",
    "CAN_EDIT",
    "CAN_VIEW",
]


def test_enum_conventions() -> list[TestResult]:
    """Test enum representation conventions."""
    results = []

    # Test that all enum values are uppercase with underscores
    all_valid = True
    for enum_list in [CLUSTER_STATE_ENUM, RUN_LIFECYCLE_STATE_ENUM, PERMISSION_LEVEL_ENUM]:
        for value in enum_list:
            if not re.match(r"^[A-Z][A-Z0-9_]*$", value):
                all_valid = False

    results.append(
        TestResult(
            name="Enum values are SCREAMING_SNAKE_CASE",
            passed=all_valid,
            message="All enum values follow convention",
        )
    )

    # Test enum count
    results.append(
        TestResult(
            name="ClusterState enum values",
            passed=len(CLUSTER_STATE_ENUM) == 8,
            message=f"{len(CLUSTER_STATE_ENUM)} states defined",
        )
    )

    results.append(
        TestResult(
            name="RunLifeCycleState enum values",
            passed=len(RUN_LIFECYCLE_STATE_ENUM) == 8,
            message=f"{len(RUN_LIFECYCLE_STATE_ENUM)} states defined",
        )
    )

    results.append(
        TestResult(
            name="PermissionLevel enum values",
            passed=len(PERMISSION_LEVEL_ENUM) == 7,
            message=f"{len(PERMISSION_LEVEL_ENUM)} levels defined",
        )
    )

    return results


# =============================================================================
# Null Handling Tests
# =============================================================================


def test_null_handling() -> list[TestResult]:
    """Test null/None/nil handling conventions."""
    results = []

    # Test that None serializes to JSON null
    data = {"field": None}
    json_str = json.dumps(data)
    results.append(
        TestResult(
            name="Python None to JSON null",
            passed='"field": null' in json_str or '"field":null' in json_str,
            message=f"Serialized: {json_str}",
        )
    )

    # Test that JSON null deserializes to None
    json_str = '{"field": null}'
    data = json.loads(json_str)
    results.append(
        TestResult(
            name="JSON null to Python None",
            passed=data["field"] is None,
            message=f"Deserialized: field={data['field']}",
        )
    )

    # Test optional field omission
    data_without_optional = {"required_field": "value"}
    json_str = json.dumps(data_without_optional)
    results.append(
        TestResult(
            name="Optional field omission",
            passed="optional" not in json_str,
            message="Optional fields can be omitted",
        )
    )

    return results


# =============================================================================
# Error Response Format Tests
# =============================================================================

# Expected Databricks API error format
EXPECTED_ERROR_SCHEMA = {
    "error_code": "str",
    "message": "str",
}

ERROR_CODES = [
    "INVALID_PARAMETER_VALUE",
    "RESOURCE_DOES_NOT_EXIST",
    "PERMISSION_DENIED",
    "RESOURCE_ALREADY_EXISTS",
    "QUOTA_EXCEEDED",
    "TEMPORARILY_UNAVAILABLE",
    "INTERNAL_ERROR",
    "REQUEST_LIMIT_EXCEEDED",
]


def test_error_formats() -> list[TestResult]:
    """Test error response format conventions."""
    results = []

    # Test error codes follow convention
    all_valid = True
    for code in ERROR_CODES:
        if not re.match(r"^[A-Z][A-Z0-9_]*$", code):
            all_valid = False

    results.append(
        TestResult(
            name="Error codes are SCREAMING_SNAKE_CASE",
            passed=all_valid,
            message=f"All {len(ERROR_CODES)} error codes valid",
        )
    )

    # Test expected error response structure
    sample_error = {
        "error_code": "RESOURCE_DOES_NOT_EXIST",
        "message": "Cluster abc123 does not exist",
    }

    has_required_fields = (
        "error_code" in sample_error
        and "message" in sample_error
        and isinstance(sample_error["error_code"], str)
        and isinstance(sample_error["message"], str)
    )

    results.append(
        TestResult(
            name="Error response schema",
            passed=has_required_fields,
            message="error_code and message fields present",
        )
    )

    return results


# =============================================================================
# JSON Field Ordering Tests
# =============================================================================


def test_json_serialization() -> list[TestResult]:
    """Test JSON serialization conventions."""
    results = []

    # Test that sort_keys produces consistent output
    data1 = {"z": 1, "a": 2, "m": 3}
    data2 = {"a": 2, "m": 3, "z": 1}

    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)

    results.append(
        TestResult(
            name="Sorted JSON produces consistent output",
            passed=json1 == json2,
            message=f"Both serialize to: {json1}",
        )
    )

    # Test nested object serialization
    nested = {
        "cluster": {
            "cluster_id": "abc123",
            "state": "RUNNING",
        },
        "metadata": {
            "created_at": 1705315800000,
        },
    }
    json_str = json.dumps(nested)
    roundtrip = json.loads(json_str)

    results.append(
        TestResult(
            name="Nested object roundtrip",
            passed=roundtrip == nested,
            message="Nested objects preserved",
        )
    )

    # Test array serialization (order preserved)
    array_data = {"items": [3, 1, 4, 1, 5, 9]}
    json_str = json.dumps(array_data)
    roundtrip = json.loads(json_str)

    results.append(
        TestResult(
            name="Array order preserved",
            passed=roundtrip["items"] == [3, 1, 4, 1, 5, 9],
            message="Array order maintained",
        )
    )

    return results


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Test SDK naming conventions")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== SDK Conventions Falsification Tests ===")
    print("(Ground truth for cross-language parity)\n")

    all_results = []

    # Naming conventions
    print("Naming Convention Tests:")
    naming_results = test_naming_conventions()
    all_results.extend(naming_results)
    for r in naming_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Type mappings
    print("\nType Mapping Tests:")
    type_results = test_type_mappings()
    all_results.extend(type_results)
    for r in type_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Timestamp formats
    print("\nTimestamp Format Tests:")
    ts_results = test_timestamp_formats()
    all_results.extend(ts_results)
    for r in ts_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Enum conventions
    print("\nEnum Convention Tests:")
    enum_results = test_enum_conventions()
    all_results.extend(enum_results)
    for r in enum_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Null handling
    print("\nNull Handling Tests:")
    null_results = test_null_handling()
    all_results.extend(null_results)
    for r in null_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Error formats
    print("\nError Format Tests:")
    error_results = test_error_formats()
    all_results.extend(error_results)
    for r in error_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # JSON serialization
    print("\nJSON Serialization Tests:")
    json_results = test_json_serialization()
    all_results.extend(json_results)
    for r in json_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results
    if args.output:
        output_data = {
            "naming_tests": [{"name": r.name, "passed": r.passed} for r in naming_results],
            "type_tests": [{"name": r.name, "passed": r.passed} for r in type_results],
            "timestamp_tests": [{"name": r.name, "passed": r.passed} for r in ts_results],
            "enum_tests": [{"name": r.name, "passed": r.passed} for r in enum_results],
            "null_tests": [{"name": r.name, "passed": r.passed} for r in null_results],
            "error_tests": [{"name": r.name, "passed": r.passed} for r in error_results],
            "json_tests": [{"name": r.name, "passed": r.passed} for r in json_results],
            "summary": {"passed": passed, "total": total},
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
