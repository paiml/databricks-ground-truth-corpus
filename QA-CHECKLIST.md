# Databricks Ground Truth Corpus - Master QA Checklist

**Date:** 2026-02-03
**Methodology:** Popperian Falsification
**Total Test Categories:** 8 domains, 300+ individual tests
**Philosophy:** "The wrong view of science betrays itself in the craving to be right" - Karl Popper

---

## Executive Summary

| Domain | Repositories | Tests | Priority |
|--------|--------------|-------|----------|
| SDK Cross-Language Parity | 3 | 45 | Tier 1 |
| MegaBlocks MoE | 1 | 30 | Tier 1 |
| SQL Connectors | 5 | 55 | Tier 1 |
| Lilac Data Quality | 1 | 45 | Tier 2 |
| CLI Tools | 4 | 35 | Tier 2 |
| Terraform Provider | 1 | 30 | Tier 2 |
| Spark Extensions | 6 | 40 | Tier 3 |
| Benchmarks | 5 | 35 | Tier 3 |
| **TOTAL** | **26** | **315** | |

---

## Domain 1: SDK Cross-Language Parity (Tier 1)

**Repositories:** databricks-sdk-py, databricks-sdk-go, databricks-sdk-java

### Request Serialization
| ID | Test | Python | Go | Java | Status |
|----|------|--------|-----|------|--------|
| RS-001 | JSON field ordering | | | | |
| RS-002 | Timestamp formatting | | | | |
| RS-003 | Enum serialization | | | | |
| RS-004 | Null handling | | | | |
| RS-005 | Array serialization | | | | |

### Response Deserialization
| ID | Test | Python | Go | Java | Status |
|----|------|--------|-----|------|--------|
| RD-001 | Primitive types | | | | |
| RD-002 | Timestamp parsing | | | | |
| RD-003 | Enum deserialization | | | | |
| RD-004 | Unknown fields | | | | |
| RD-005 | Error responses | | | | |

### Authentication
| ID | Test | Python | Go | Java | Status |
|----|------|--------|-----|------|--------|
| AU-001 | OAuth token | | | | |
| AU-002 | Token refresh | | | | |
| AU-003 | PAT auth | | | | |
| AU-004 | Azure MSI | | | | |
| AU-005 | AWS credentials | | | | |

### Service-Specific
| ID | Test | Python | Go | Java | Status |
|----|------|--------|-----|------|--------|
| CP-001 | List clusters | | | | |
| JB-001 | Job run state | | | | |
| SQ-001 | Query result types | | | | |
| ML-001 | Model registry | | | | |
| UC-001 | Schema listing | | | | |

---

## Domain 2: MegaBlocks MoE Parity (Tier 1)

**Repository:** databricks/megablocks

### Router Tests
| ID | Test | vs HuggingFace | Status |
|----|------|----------------|--------|
| RT-001 | Router logits | atol=1e-5 | |
| RT-002 | Expert selection | Exact | |
| RT-003 | Probability normalization | 1e-6 | |
| RT-004 | Load balance loss | atol=1e-5 | |
| RT-005 | Determinism | Exact | |

### Expert FFN Tests
| ID | Test | vs HuggingFace | Status |
|----|------|----------------|--------|
| EX-001 | Weight shapes | Exact | |
| EX-002 | SwiGLU activation | atol=1e-5 | |
| EX-003 | Expert bias | atol=1e-5 | |
| EX-004 | Dimension mapping | Exact | |
| EX-005 | Per-expert output | atol=1e-5 | |

### Block-Sparse Operations
| ID | Test | Expected | Status |
|----|------|----------|--------|
| BS-001 | Block alignment | Power of 2 | |
| BS-002 | Sparsity pattern | Match | |
| BS-003 | Block-sparse matmul | atol=1e-4 | |
| BS-004 | Memory layout | Row-major | |
| BS-005 | Padding | Correct | |

### Training Parity
| ID | Test | Expected | Status |
|----|------|----------|--------|
| TR-001 | Router gradient | atol=1e-4 | |
| TR-002 | Expert gradient | atol=1e-4 | |
| TR-003 | Aux loss gradient | atol=1e-4 | |
| TR-004 | Expert parallel | Correct | |
| TR-005 | Mixed precision | Stable | |

---

## Domain 3: SQL Connectors Parity (Tier 1)

**Repositories:** databricks-sql-python, databricks-sql-go, databricks-sql-nodejs, databricks-jdbc, databricks-sqlalchemy

### Data Type Mapping
| ID | Type | Python | Go | Java | Node.js | Status |
|----|------|--------|-----|------|---------|--------|
| DT-001 | BOOLEAN | | | | | |
| DT-002 | BIGINT | | | | | |
| DT-003 | DOUBLE | | | | | |
| DT-004 | DECIMAL(38,30) | | | | | |
| DT-005 | TIMESTAMP | | | | | |
| DT-006 | TIMESTAMP_NTZ | | | | | |
| DT-007 | ARRAY | | | | | |
| DT-008 | MAP | | | | | |
| DT-009 | STRUCT | | | | | |
| DT-010 | BINARY | | | | | |

### Query Execution
| ID | Test | All Connectors | Status |
|----|------|----------------|--------|
| QE-001 | Simple SELECT | Same rows | |
| QE-002 | WHERE filtering | Same rows | |
| QE-003 | JOIN results | Same rows | |
| QE-004 | Aggregates | Same values | |
| QE-005 | ORDER BY | Same order | |
| QE-006 | LIMIT/OFFSET | Same subset | |
| QE-007 | Set operations | Same rows | |
| QE-008 | Subqueries | Same rows | |
| QE-009 | Window functions | Same values | |
| QE-010 | CTEs | Same rows | |

### NULL Handling
| ID | Test | All Connectors | Status |
|----|------|----------------|--------|
| NL-001 | NULL in column | Language null | |
| NL-002 | NULL in SUM | Excluded | |
| NL-003 | NULL = NULL | NULL | |
| NL-004 | COALESCE | Correct | |
| NL-005 | NULL in array | Correct | |

---

## Domain 4: Lilac Data Quality (Tier 2)

**Repository:** databricks/lilac

### PII Detection
| ID | Signal | Expected F1 | Status |
|----|--------|-------------|--------|
| PII-001 | Email | > 0.95 | |
| PII-002 | Phone | > 0.90 | |
| PII-003 | SSN | > 0.98 | |
| PII-004 | Credit card | > 0.95 | |
| PII-005 | IP address | > 0.98 | |
| PII-006 | Names (NER) | > 0.85 | |
| PII-007 | Address | > 0.80 | |
| PII-008 | DOB | > 0.90 | |
| PII-009 | ID numbers | > 0.85 | |
| PII-010 | API keys | > 0.90 | |

### Deduplication
| ID | Test | Expected | Status |
|----|------|----------|--------|
| DUP-001 | Exact duplicates | Precision 1.0 | |
| DUP-002 | Near-duplicates | F1 > 0.90 | |
| DUP-003 | Substring | F1 > 0.85 | |
| DUP-004 | Semantic | F1 > 0.80 | |
| DUP-005 | Templated | F1 > 0.85 | |
| DUP-006 | Boilerplate | F1 > 0.90 | |

### Language ID
| ID | Test | Expected | Status |
|----|------|----------|--------|
| LI-001 | Single language | Acc > 0.98 | |
| LI-002 | Multi-language | F1 > 0.90 | |
| LI-003 | Code detection | F1 > 0.95 | |
| LI-004 | Mixed content | F1 > 0.85 | |
| LI-005 | Short text | Acc > 0.90 | |
| LI-006 | Calibration | ECE < 0.05 | |

### Clustering
| ID | Test | Expected | Status |
|----|------|----------|--------|
| CL-001 | Cluster purity | > 0.85 | |
| CL-002 | Completeness | > 0.85 | |
| CL-003 | Cluster count | ±20% | |
| CL-004 | Search recall@10 | > 0.90 | |
| CL-005 | Concept learning | F1 > 0.80 | |

---

## Domain 5: CLI Tools (Tier 2)

**Repositories:** cli, databricks-cli, click, databricks-sql-cli

### Workspace Commands
| ID | Command | Go CLI | Python CLI | Status |
|----|---------|--------|------------|--------|
| WS-001 | workspace list | | | |
| WS-002 | workspace mkdirs | | | |
| WS-003 | workspace import | | | |
| WS-004 | workspace export | | | |
| WS-005 | workspace delete | | | |

### Cluster Commands
| ID | Command | Go CLI | Python CLI | Status |
|----|---------|--------|------------|--------|
| CL-001 | clusters list | | | |
| CL-002 | clusters get | | | |
| CL-003 | clusters create | | | |
| CL-004 | clusters start | | | |
| CL-005 | clusters delete | | | |

### Jobs Commands
| ID | Command | Go CLI | Python CLI | Status |
|----|---------|--------|------------|--------|
| JB-001 | jobs list | | | |
| JB-002 | jobs get | | | |
| JB-003 | jobs create | | | |
| JB-004 | jobs run-now | | | |
| JB-005 | runs list | | | |
| JB-006 | runs get | | | |

### Output Formats
| ID | Test | Go CLI | Python CLI | Status |
|----|------|--------|------------|--------|
| FMT-001 | JSON fields | | | |
| FMT-002 | JSON arrays | | | |
| FMT-003 | Table headers | | | |
| ERR-001 | Exit codes | | | |

---

## Domain 6: Terraform Provider (Tier 2)

**Repository:** terraform-provider-databricks

### Compute Resources
| ID | Resource | Create | Update | Delete | Status |
|----|----------|--------|--------|--------|--------|
| CP-001 | cluster | | | | |
| CP-002 | instance_pool | | | | |
| CP-003 | cluster_policy | | | | |

### Workspace Resources
| ID | Resource | Create | Update | Delete | Status |
|----|----------|--------|--------|--------|--------|
| WS-001 | notebook | | | | |
| WS-002 | directory | | | | |
| WS-003 | repo | | | | |
| WS-004 | workspace_file | | | | |

### Unity Catalog
| ID | Resource | Create | Update | Delete | Status |
|----|----------|--------|--------|--------|--------|
| UC-001 | catalog | | | | |
| UC-002 | schema | | | | |
| UC-003 | table | | | | |
| UC-004 | grants | | | | |
| UC-005 | storage_credential | | | | |

### State Management
| ID | Test | Expected | Status |
|----|------|----------|--------|
| PL-001 | Plan accuracy | Correct | |
| PL-002 | Drift detection | Detected | |
| PL-003 | Idempotency | No changes | |
| IM-001 | Import | Matches | |
| DS-001 | Destroy | Clean | |

---

## Domain 7: Spark Extensions (Tier 3)

**Repositories:** spark-sql-perf, spark-redshift, spark-corenlp, spark-tfocs, koalas, spark-deep-learning

### Koalas (pandas API)
| ID | Test | Expected | Status |
|----|------|----------|--------|
| KO-001 | DataFrame creation | pandas parity | |
| KO-002 | Series operations | pandas parity | |
| KO-003 | GroupBy | pandas parity | |
| KO-004 | Joins | pandas parity | |
| KO-005 | Window functions | pandas parity | |

### spark-deep-learning
| ID | Test | Expected | Status |
|----|------|----------|--------|
| DL-001 | Image loading | Correct tensors | |
| DL-002 | Transfer learning | Correct outputs | |
| DL-003 | Model inference | Numeric parity | |

### spark-redshift
| ID | Test | Expected | Status |
|----|------|----------|--------|
| RS-001 | Data type mapping | Correct | |
| RS-002 | Pushdown queries | Optimized | |
| RS-003 | Large reads | Correct | |

---

## Domain 8: Benchmarks (Tier 3)

**Repositories:** tpcds-kit, tpch-dbgen, spark-sql-perf, benchmarks, als-benchmark-scripts

### TPC-DS
| ID | Test | Expected | Status |
|----|------|----------|--------|
| DS-001 | SF=1 row counts | Per spec | |
| DS-002 | SF=10 row counts | Per spec | |
| DS-003 | SF=100 row counts | Per spec | |
| DQ-001 | Query 1 result | Certified | |
| DQ-002 | All 99 queries | Valid SQL | |

### TPC-H
| ID | Test | Expected | Status |
|----|------|----------|--------|
| TH-001 | SF=1 row counts | Per spec | |
| TH-002 | LINEITEM count | 6,001,215 | |
| HQ-001 | Query 1 result | Certified | |
| HQ-002 | All 22 queries | Valid SQL | |

### ALS
| ID | Test | Expected | Status |
|----|------|----------|--------|
| AL-001 | RMSE convergence | Monotonic | |
| AL-002 | Matrix shapes | Correct | |
| AD-001 | Distributed parity | 1e-6 | |

---

## Results Summary

| Domain | Total | Passed | Failed | Skipped | Notes |
|--------|-------|--------|--------|---------|-------|
| SDK Parity | 45 | 19 | 0 | 26 | Convention ground truth complete |
| MegaBlocks | 30 | 8 | 0 | 22 | Reference impl complete; tensor parity needs grouped_gemm |
| SQL Connectors | 55 | 0 | 0 | 55 | Requires workspace |
| Lilac | 52 | 51 | 1 | 0 | PII/Dedup/LangID/TextStats complete |
| CLI Tools | 35 | 0 | 0 | 35 | Requires workspace |
| Terraform | 30 | 0 | 0 | 30 | Requires workspace |
| Spark Extensions | 40 | 36 | 0 | 4 | Pandas API ground truth complete |
| Benchmarks | 35 | 15 | 0 | 20 | Oracle validation complete |
| **TOTAL** | **322** | **129** | **1** | **192** |

---

## Sign-off

- [ ] All Tier 1 tests pass
- [ ] All Tier 2 tests pass
- [ ] All Tier 3 tests pass
- [ ] No undocumented behavior
- [ ] Ready for production use

**Executor:** ________________
**Date:** ________________
