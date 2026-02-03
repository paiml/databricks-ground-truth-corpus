# CLI Tools Parity Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification

---

## 1. Overview

Databricks provides CLI tools in multiple languages. This oracle validates command behavior parity.

### CLIs Under Test

| CLI | Language | Repository | Stars | Status |
|-----|----------|------------|-------|--------|
| cli | Go | databricks/cli | 290 | Active |
| databricks-cli | Python | databricks/databricks-cli | 396 | Legacy |
| click | Rust | databricks/click | 1508 | K8s controller |
| databricks-sql-cli | Python | databricks/databricks-sql-cli | 44 | SQL-focused |

---

## 2. Command Parity Tests

### 2.1 Workspace Commands

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| WS-001 | `workspace list /` | Same directory listing | Exact |
| WS-002 | `workspace mkdirs /test` | Same result | Exact |
| WS-003 | `workspace import` | Same imported file | Exact |
| WS-004 | `workspace export` | Same exported file | Exact |
| WS-005 | `workspace delete` | Same deletion | Exact |

### 2.2 Cluster Commands

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| CL-001 | `clusters list` | Same cluster list | Exact |
| CL-002 | `clusters get` | Same cluster details | Exact |
| CL-003 | `clusters create` | Same cluster created | Exact |
| CL-004 | `clusters start` | Same state change | Exact |
| CL-005 | `clusters delete` | Same deletion | Exact |

### 2.3 Jobs Commands

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| JB-001 | `jobs list` | Same job list | Exact |
| JB-002 | `jobs get` | Same job details | Exact |
| JB-003 | `jobs create` | Same job created | Exact |
| JB-004 | `jobs run-now` | Same run triggered | Exact |
| JB-005 | `runs list` | Same run list | Exact |
| JB-006 | `runs get` | Same run details | Exact |

### 2.4 DBFS Commands

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| DF-001 | `fs ls dbfs:/` | Same file listing | Exact |
| DF-002 | `fs cp local dbfs:/` | Same file uploaded | Exact |
| DF-003 | `fs cp dbfs:/ local` | Same file downloaded | Exact |
| DF-004 | `fs rm dbfs:/file` | Same deletion | Exact |
| DF-005 | `fs mkdirs dbfs:/dir` | Same directory | Exact |

### 2.5 Secrets Commands

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| SC-001 | `secrets list-scopes` | Same scope list | Exact |
| SC-002 | `secrets create-scope` | Same scope created | Exact |
| SC-003 | `secrets put` | Same secret stored | Exact |
| SC-004 | `secrets list` | Same secret list | Exact |
| SC-005 | `secrets delete` | Same deletion | Exact |

### 2.6 SQL Commands (databricks-sql-cli)

| ID | Command | Expected Output | Tolerance |
|----|---------|-----------------|-----------|
| SQ-001 | `query "SELECT 1"` | Same result | Exact |
| SQ-002 | `query --format csv` | Same CSV output | Exact |
| SQ-003 | `query --format json` | Same JSON output | Exact |
| SQ-004 | `warehouses list` | Same warehouse list | Exact |

---

## 3. Output Format Parity

### 3.1 JSON Output

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| FMT-001 | Field names | Same casing | Exact |
| FMT-002 | Array ordering | Same order | Exact |
| FMT-003 | NULL representation | `null` | Exact |
| FMT-004 | Number formatting | Same precision | Exact |
| FMT-005 | Timestamp format | ISO 8601 | Exact |

### 3.2 Table Output

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| TBL-001 | Column headers | Same names | Exact |
| TBL-002 | Column alignment | Consistent | Visual |
| TBL-003 | Truncation | Same behavior | Configurable |
| TBL-004 | Unicode handling | Same rendering | Exact |

### 3.3 Error Output

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| ERR-001 | Error codes | Same exit code | Exact |
| ERR-002 | Error messages | Similar text | Semantic |
| ERR-003 | Stack traces | Optional | Documented |

---

## 4. Golden Corpus Structure

```
cli-tools/
├── oracle/
│   ├── commands/
│   │   ├── workspace/
│   │   ├── clusters/
│   │   ├── jobs/
│   │   ├── dbfs/
│   │   └── secrets/
│   ├── expected/
│   │   ├── workspace_list.json
│   │   ├── clusters_list.json
│   │   └── ...
│   └── manifest.json
├── specs/
│   └── cli-parity-oracle.md
└── scripts/
    ├── capture_golden.sh
    ├── validate_go_cli.sh
    └── validate_python_cli.sh
```

---

## 5. Falsification Checklist

### 5.1 Workspace Commands
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| WS-001 | workspace list | Same output | | |
| WS-002 | workspace mkdirs | Same result | | |
| WS-003 | workspace import | Same file | | |
| WS-004 | workspace export | Same file | | |
| WS-005 | workspace delete | Same result | | |

### 5.2 Cluster Commands
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| CL-001 | clusters list | Same output | | |
| CL-002 | clusters get | Same details | | |
| CL-003 | clusters create | Same cluster | | |
| CL-004 | clusters start | Same state | | |
| CL-005 | clusters delete | Same result | | |

### 5.3 Jobs Commands
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| JB-001 | jobs list | Same output | | |
| JB-002 | jobs get | Same details | | |
| JB-003 | jobs create | Same job | | |
| JB-004 | jobs run-now | Same run | | |
| JB-005 | runs list | Same output | | |
| JB-006 | runs get | Same details | | |

### 5.4 DBFS Commands
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DF-001 | fs ls | Same listing | | |
| DF-002 | fs cp upload | Same file | | |
| DF-003 | fs cp download | Same file | | |
| DF-004 | fs rm | Same result | | |
| DF-005 | fs mkdirs | Same dir | | |

### 5.5 Output Formats
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| FMT-001 | JSON field names | Same casing | | |
| FMT-002 | JSON arrays | Same order | | |
| FMT-003 | Table headers | Same names | | |
| ERR-001 | Exit codes | Same code | | |

---

## References

- Databricks CLI Documentation: https://docs.databricks.com/dev-tools/cli/
- Go CLI: https://github.com/databricks/cli
- Python CLI: https://github.com/databricks/databricks-cli
