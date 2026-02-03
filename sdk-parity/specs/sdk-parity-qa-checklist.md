# SDK Cross-Language Parity - Falsification QA Checklist

**Date:** 2026-02-03
**Methodology:** Popperian Falsification (attempt to break, not verify)
**Philosophy:** "The wrong view of science betrays itself in the craving to be right"

---

## 1. Naming Convention Tests

### 1.1 Case Transformations
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| NC-001 | snake_case to camelCase | clusterId | clusterId | + |
| NC-002 | snake_case to PascalCase | ClusterId | ClusterId | + |
| NC-003 | camelCase to snake_case | cluster_id | cluster_id | + |

### 1.2 Test Cases Validated
| snake_case | camelCase | PascalCase |
|------------|-----------|------------|
| cluster_id | clusterId | ClusterId |
| spark_version | sparkVersion | SparkVersion |
| num_workers | numWorkers | NumWorkers |
| autoscale_config | autoscaleConfig | AutoscaleConfig |
| can_use_client | canUseClient | CanUseClient |
| cluster_name | clusterName | ClusterName |
| run_life_cycle_state | runLifeCycleState | RunLifeCycleState |
| max_bytes | maxBytes | MaxBytes |
| access_token | accessToken | AccessToken |
| workspace_id | workspaceId | WorkspaceId |

---

## 2. Type Mapping Tests

### 2.1 JSON to Language Types
| ID | JSON Type | Python | Go | Java | Pass |
|----|-----------|--------|-----|------|------|
| TM-001 | string | str | string | String | + |
| TM-002 | integer | int | int64 | Long | + |
| TM-003 | number | float | float64 | Double | + |
| TM-004 | boolean | bool | bool | Boolean | + |
| TM-005 | array | list | []T | List<T> | + |
| TM-006 | object | dict | map[string]T | Map<String, T> | + |
| TM-007 | null | None | nil | null | + |

### 2.2 API-Specific Types
| ID | Field | Python | Go | Java | Pass |
|----|-------|--------|-----|------|------|
| AT-001 | cluster_id | str | string | String | + |
| AT-002 | num_workers | int | int32 | Integer | + |
| AT-003 | memory_mb | int | int64 | Long | + |
| AT-004 | start_time | int | int64 | Long | + |
| AT-005 | timeout_seconds | int | int32 | Integer | + |
| AT-006 | enable_elastic_disk | bool | bool | Boolean | + |
| AT-007 | spot_bid_max_price | float | float64 | Double | + |

---

## 3. Timestamp Format Tests

### 3.1 ISO 8601 Formats
| ID | Format | Example | Parsed | Pass |
|----|--------|---------|--------|------|
| TS-001 | UTC with Z | 2024-01-15T10:30:00Z | Yes | + |
| TS-002 | UTC with offset | 2024-01-15T10:30:00+00:00 | Yes | + |
| TS-003 | Milliseconds | 2024-01-15T10:30:00.123Z | Yes | + |
| TS-004 | Microseconds | 2024-01-15T10:30:00.123456Z | Yes | + |

### 3.2 Unix Timestamps
| ID | Format | Example | Pass |
|----|--------|---------|------|
| TS-005 | Unix milliseconds | 1705315800123 | + |

---

## 4. Enum Convention Tests

### 4.1 Enum Format Validation
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| EN-001 | SCREAMING_SNAKE_CASE | All match | All match | + |
| EN-002 | ClusterState count | 8 values | 8 values | + |
| EN-003 | RunLifeCycleState count | 8 values | 8 values | + |
| EN-004 | PermissionLevel count | 7 values | 7 values | + |

### 4.2 Enum Values Documented
**ClusterState:** PENDING, RUNNING, RESTARTING, RESIZING, TERMINATING, TERMINATED, ERROR, UNKNOWN

**RunLifeCycleState:** PENDING, RUNNING, TERMINATING, TERMINATED, SKIPPED, INTERNAL_ERROR, BLOCKED, WAITING_FOR_RETRY

**PermissionLevel:** CAN_MANAGE, CAN_RESTART, CAN_ATTACH_TO, CAN_READ, CAN_RUN, CAN_EDIT, CAN_VIEW

---

## 5. Null Handling Tests

| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| NH-001 | Python None to JSON null | {"field": null} | Correct | + |
| NH-002 | JSON null to Python None | field=None | Correct | + |
| NH-003 | Optional field omission | Not in JSON | Correct | + |

---

## 6. Error Format Tests

### 6.1 Error Code Format
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| EF-001 | SCREAMING_SNAKE_CASE | All match | All match | + |
| EF-002 | Error response schema | error_code, message | Correct | + |

### 6.2 Error Codes Documented
- INVALID_PARAMETER_VALUE
- RESOURCE_DOES_NOT_EXIST
- PERMISSION_DENIED
- RESOURCE_ALREADY_EXISTS
- QUOTA_EXCEEDED
- TEMPORARILY_UNAVAILABLE
- INTERNAL_ERROR
- REQUEST_LIMIT_EXCEEDED

---

## 7. JSON Serialization Tests

| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| JS-001 | Sorted JSON consistency | Identical output | Correct | + |
| JS-002 | Nested object roundtrip | Preserved | Correct | + |
| JS-003 | Array order preservation | Maintained | Correct | + |

---

## 8. Execution Log

```
Date: 2026-02-03
Executor: Claude Code
Command: uv run sdk-parity/scripts/test_sdk_conventions.py
```

### Results Summary

| Category | Total | Passed | Failed |
|----------|-------|--------|--------|
| Naming Conventions | 3 | 3 | 0 |
| Type Mappings | 2 | 2 | 0 |
| Timestamp Formats | 2 | 2 | 0 |
| Enum Conventions | 4 | 4 | 0 |
| Null Handling | 3 | 3 | 0 |
| Error Formats | 2 | 2 | 0 |
| JSON Serialization | 3 | 3 | 0 |
| **TOTAL** | **19** | **19** | **0** |

---

## 9. Next Steps (Requires Workspace)

| Test | Status | Notes |
|------|--------|-------|
| Live API request parity | PENDING | Needs Databricks workspace |
| Response deserialization | PENDING | Needs live responses |
| Authentication flows | PENDING | Needs credentials |

---

## Sign-off

- [x] All 19 SDK convention ground truth tests pass
- [x] Naming conventions documented (snake_case, camelCase, PascalCase)
- [x] Type mappings documented (Python, Go, Java)
- [x] Enum values documented (ClusterState, RunLifeCycleState, PermissionLevel)
- [x] Error codes documented

**Verdict: PARTIAL COMPLETE** - Convention ground truth established. Live API parity requires workspace.
