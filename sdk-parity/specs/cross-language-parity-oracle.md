# SDK Cross-Language Parity Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification

---

## 1. Overview

Cross-language parity testing for Databricks SDKs ensures that the same API calls produce identical results regardless of which SDK language is used.

### SDKs Under Test

| SDK | Language | Repository | Stars |
|-----|----------|------------|-------|
| databricks-sdk-py | Python | databricks/databricks-sdk-py | 514 |
| databricks-sdk-go | Go | databricks/databricks-sdk-go | 70 |
| databricks-sdk-java | Java | databricks/databricks-sdk-java | 52 |

### Service Coverage

Both Go and Java SDKs expose identical services (code-generated from OpenAPI):

```
agentbricks  apps         billing      catalog      cleanrooms
compute      dashboards   database     dataquality  files
iam          iamv2        jobs         marketplace  ml
oauth2       pipelines    postgres     provisioning qualitymonitorv2
serving      settings     settingsv2   sharing      sql
tags         vectorsearch workspace
```

---

## 2. Parity Test Categories

### 2.1 Request Serialization Parity

Verify that the same logical request produces identical wire format across SDKs.

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| RS-001 | JSON field ordering | Alphabetical or spec-defined | Exact |
| RS-002 | Timestamp formatting | ISO 8601 with timezone | Exact |
| RS-003 | Enum serialization | String values match | Exact |
| RS-004 | Null handling | Omitted vs explicit null | Semantic |
| RS-005 | Array serialization | Order preserved | Exact |
| RS-006 | Nested object flattening | Consistent depth | Exact |

### 2.2 Response Deserialization Parity

Verify that the same API response produces identical SDK objects.

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| RD-001 | Primitive type mapping | int64, float64, string, bool | Exact |
| RD-002 | Timestamp parsing | Same instant in time | 1ms |
| RD-003 | Enum deserialization | Same variant | Exact |
| RD-004 | Unknown field handling | Ignored or preserved | Documented |
| RD-005 | Missing field defaults | SDK-specific or spec default | Documented |
| RD-006 | Error response parsing | Same error code/message | Exact |

### 2.3 Authentication Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| AU-001 | OAuth token acquisition | Same token format | Exact |
| AU-002 | Token refresh timing | Proactive refresh window | 30s |
| AU-003 | PAT authentication | Same header format | Exact |
| AU-004 | Azure MSI detection | Same endpoint discovery | Exact |
| AU-005 | AWS credentials chain | Same precedence order | Exact |
| AU-006 | Error on invalid credentials | Same error type | Semantic |

### 2.4 Retry Behavior Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| RT-001 | Retryable status codes | 429, 503, 500 | Exact |
| RT-002 | Non-retryable codes | 400, 401, 403, 404 | Exact |
| RT-003 | Exponential backoff base | Configurable | 10% |
| RT-004 | Max retry count | Configurable | Exact |
| RT-005 | Retry-After header respect | Honored when present | Exact |
| RT-006 | Idempotency key handling | Consistent generation | Format |

### 2.5 Pagination Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| PG-001 | Page size handling | Same items per page | Exact |
| PG-002 | Token-based pagination | Same token format | Exact |
| PG-003 | Offset pagination | Same offset calculation | Exact |
| PG-004 | Empty page handling | Same empty indicator | Exact |
| PG-005 | Last page detection | Same termination | Exact |

---

## 3. Service-Specific Tests

### 3.1 Compute Service

| ID | Test | Expected |
|----|------|----------|
| CP-001 | List clusters response | Identical cluster objects |
| CP-002 | Cluster state enum | PENDING, RUNNING, TERMINATED, etc. |
| CP-003 | Spark version parsing | Same version struct |
| CP-004 | Node type ID format | Same string format |
| CP-005 | Autoscale config | Same min/max workers |

### 3.2 Jobs Service

| ID | Test | Expected |
|----|------|----------|
| JB-001 | Job run state | Same RunLifeCycleState |
| JB-002 | Task dependencies | Same DAG structure |
| JB-003 | Schedule parsing | Same cron interpretation |
| JB-004 | Run parameters | Same parameter map |
| JB-005 | Output truncation | Same max_bytes behavior |

### 3.3 SQL Service

| ID | Test | Expected |
|----|------|----------|
| SQ-001 | Query result types | Same column type mapping |
| SQ-002 | NULL representation | Same null indicator |
| SQ-003 | Decimal precision | Same scale/precision |
| SQ-004 | Timestamp with timezone | Same UTC conversion |
| SQ-005 | Array/Map columns | Same nested structure |

### 3.4 ML Service

| ID | Test | Expected |
|----|------|----------|
| ML-001 | Model registry listing | Same model objects |
| ML-002 | Model version stages | Same stage enum |
| ML-003 | Run metrics | Same metric values |
| ML-004 | Artifact paths | Same URI format |
| ML-005 | Experiment tags | Same key-value pairs |

### 3.5 Catalog Service (Unity Catalog)

| ID | Test | Expected |
|----|------|----------|
| UC-001 | Schema listing | Same schema objects |
| UC-002 | Table properties | Same property map |
| UC-003 | Column types | Same type strings |
| UC-004 | Permission grants | Same principal format |
| UC-005 | Lineage edges | Same source/target |

---

## 4. Golden Corpus Structure

```
sdk-parity/
├── oracle/
│   ├── requests/           # Captured request payloads
│   │   ├── compute/
│   │   ├── jobs/
│   │   ├── sql/
│   │   └── ...
│   ├── responses/          # Golden API responses
│   │   ├── compute/
│   │   ├── jobs/
│   │   ├── sql/
│   │   └── ...
│   └── manifest.json       # Test inventory
├── specs/
│   └── cross-language-parity-oracle.md
└── scripts/
    ├── capture_golden.py   # Capture from live API
    ├── validate_python.py  # Python SDK validator
    ├── validate_go.go      # Go SDK validator
    └── validate_java.java  # Java SDK validator
```

### Request Corpus Format

```json
{
  "test_id": "CP-001",
  "service": "compute",
  "method": "list",
  "request": {
    "can_use_client": true
  },
  "expected_request_json": "{\"can_use_client\":true}"
}
```

### Response Corpus Format

```json
{
  "test_id": "CP-001",
  "service": "compute",
  "method": "list",
  "response": {
    "clusters": [
      {
        "cluster_id": "0123-456789-abc123",
        "state": "RUNNING",
        "cluster_name": "test-cluster"
      }
    ]
  },
  "expected_python": {
    "cluster_id": "0123-456789-abc123",
    "state": "ClusterState.RUNNING"
  },
  "expected_go": {
    "ClusterId": "0123-456789-abc123",
    "State": "RUNNING"
  },
  "expected_java": {
    "clusterId": "0123-456789-abc123",
    "state": "ClusterState.RUNNING"
  }
}
```

---

## 5. Execution

### 5.1 Prerequisites

```bash
# Python - all scripts use uv inline dependencies (PEP 723)
# No manual installation required - run scripts directly with uv

# Go
go get github.com/databricks/databricks-sdk-go

# Java (Maven)
<dependency>
  <groupId>com.databricks</groupId>
  <artifactId>databricks-sdk-java</artifactId>
</dependency>
```

### 5.2 Running Parity Tests

```bash
# Generate golden corpus from live API
python scripts/capture_golden.py --workspace $DATABRICKS_HOST

# Validate Python SDK
python scripts/validate_python.py --corpus oracle/

# Validate Go SDK
go run scripts/validate_go.go --corpus oracle/

# Validate Java SDK
java -jar scripts/validate_java.jar --corpus oracle/

# Cross-language comparison
python scripts/compare_all.py --corpus oracle/
```

---

## 6. Falsification Checklist

### 6.1 Request Serialization
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| RS-001 | Compare JSON field order | Consistent | | |
| RS-002 | Compare timestamp format | ISO 8601 | | |
| RS-003 | Compare enum string values | Match spec | | |
| RS-004 | Compare null handling | Documented | | |
| RS-005 | Compare array order | Preserved | | |

### 6.2 Response Deserialization
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| RD-001 | Compare int64 values | Exact match | | |
| RD-002 | Compare timestamps | Within 1ms | | |
| RD-003 | Compare enum variants | Same name | | |
| RD-004 | Unknown field behavior | Documented | | |
| RD-005 | Missing field defaults | Consistent | | |

### 6.3 Authentication
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| AU-001 | OAuth token format | RFC 6749 | | |
| AU-002 | Token refresh window | 30s early | | |
| AU-003 | PAT header format | Bearer | | |

### 6.4 Retry Behavior
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| RT-001 | 429 triggers retry | Yes | | |
| RT-002 | 400 no retry | Yes | | |
| RT-003 | Backoff calculation | Exponential | | |

---

## 7. Known Divergences

Document any intentional differences between SDKs:

| Area | Python | Go | Java | Reason |
|------|--------|-----|------|--------|
| Naming | snake_case | PascalCase | camelCase | Language convention |
| Nulls | None | nil | null | Language convention |
| Enums | Enum class | constants | Enum class | Language idiom |

---

## References

- Databricks REST API Spec: https://docs.databricks.com/api/
- OpenAPI Generator: https://openapi-generator.tech/
- IEEE 754 for float comparison
- RFC 6749 for OAuth 2.0
