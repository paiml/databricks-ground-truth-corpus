# Databricks Repository Catalog for Falsification QA

**Analysis Date:** 2026-02-03
**Total Repositories:** 250 (80 active with >10 stars)
**Methodology:** Popperian Falsification

---

## Category 1: ML/AI Infrastructure (High Priority)

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **megablocks** | 1523 | Python | MoE sparse training | Tensor parity vs HuggingFace Mixtral |
| **spark-deep-learning** | 1993 | Python | DL pipelines for Spark | Inference parity testing |
| **koalas** | 3370 | Python | pandas API on Spark | DataFrame operation parity |
| **tensorframes** | 744 | Scala | TensorFlow on Spark | Tensor operation validation |
| **diviner** | 39 | Python | Time series forecasting | Forecast accuracy validation |
| **automl** | 28 | Python | AutoML | Model selection validation |
| **compose-rl** | 59 | Python | Reinforcement learning | Policy gradient validation |
| **databricks-ai-bridge** | 67 | Python | AI integration | API contract testing |

## Category 2: Data Quality & Curation

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **lilac** | 1067 | Python | LLM data curation | PII/dedup/clustering accuracy |
| **drunken-data-quality-1** | 25 | Scala | Data quality checks | Quality rule validation |
| **officeqa** | 60 | Python | Office QA benchmark | Benchmark accuracy |

## Category 3: SDKs & APIs (Cross-Language Parity)

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **databricks-sdk-py** | 514 | Python | Python SDK | API contract testing |
| **databricks-sdk-go** | 70 | Go | Go SDK | Cross-language parity |
| **databricks-sdk-java** | 52 | Java | Java SDK | Cross-language parity |
| **databricks-sql-python** | 220 | Python | SQL connector | Query result parity |
| **databricks-sql-go** | 44 | Go | Go SQL driver | Cross-language SQL parity |
| **databricks-sql-nodejs** | 31 | TypeScript | Node.js SQL connector | Cross-language SQL parity |
| **databricks-jdbc** | 30 | Java | JDBC driver | JDBC compliance testing |
| **databricks-sqlalchemy** | 19 | Python | SQLAlchemy adapter | ORM parity testing |
| **zerobus-sdk-py** | 31 | Python | Zerobus Python SDK | Event streaming parity |
| **zerobus-sdk-rs** | 21 | Rust | Zerobus Rust SDK | Cross-language parity |
| **zerobus-sdk-java** | 16 | Java | Zerobus Java SDK | Cross-language parity |
| **zerobus-sdk-go** | 5 | Go | Zerobus Go SDK | Cross-language parity |

## Category 4: CLI Tools

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **cli** | 290 | Go | Databricks CLI (new) | Command behavior validation |
| **databricks-cli** | 396 | Python | Legacy CLI | Migration parity testing |
| **click** | 1508 | Rust | K8s CLI controller | Command validation |
| **databricks-sql-cli** | 44 | Python | SQL CLI | Query execution parity |

## Category 5: Terraform & Infrastructure

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **terraform-provider-databricks** | 569 | Go | Terraform provider | Resource state validation |
| **terraform-databricks-sra** | 172 | HCL | Security ref arch | Security config validation |
| **terraform-databricks-examples** | 307 | HCL | TF examples | Example correctness |
| **terraform-databricks-lakehouse-blueprints** | 90 | Python | Lakehouse blueprints | Blueprint validation |

## Category 6: Spark Extensions

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **spark-sql-perf** | 619 | Scala | SQL performance | Benchmark reproducibility |
| **spark-redshift** | 610 | Scala | Redshift connector | Data type parity |
| **spark-corenlp** | 422 | Scala | CoreNLP wrapper | NLP result validation |
| **spark-tfocs** | 89 | Scala | TFOCS optimization | Solver accuracy |
| **spark-perf** | 383 | Scala | Performance tests | Benchmark validation |
| **spark-integration-tests** | 68 | Scala | Integration tests | Test oracle validation |

## Category 7: Data Connectors & Formats

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **iceberg-kafka-connect** | 278 | Java | Iceberg Kafka connector | Message delivery parity |
| **iceberg-rest-image** | 153 | Java | Iceberg REST catalog | REST API compliance |
| **dbt-databricks** | 322 | Python | dbt adapter | SQL transformation parity |
| **pgsqlite** | 131 | Python | SQLite to Postgres | Data migration accuracy |
| **pg-text-query** | 91 | Python | Postgres text queries | Query generation accuracy |

## Category 8: Benchmarks & Testing

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **benchmarks** | 108 | Python | Reproducible benchmarks | Benchmark reproducibility |
| **tpcds-kit** | 105 | C | TPC-DS benchmark | Standard compliance |
| **tpch-dbgen** | 32 | C | TPC-H data generator | Data generation accuracy |
| **als-benchmark-scripts** | 22 | Scala | ALS benchmarks | Algorithm accuracy |

## Category 9: IDE & Developer Tools

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **databricks-vscode** | 171 | TypeScript | VS Code extension | Extension behavior validation |
| **intellij-jsonnet** | 90 | Java | IntelliJ Jsonnet | Parser accuracy |
| **sjsonnet** | 306 | Jsonnet | Jsonnet implementation | Spec compliance |

## Category 10: MLOps & Pipelines

| Repo | Stars | Lang | Description | QA Opportunity |
|------|-------|------|-------------|----------------|
| **mlops-stacks** | 647 | Python | MLOps templates | Template correctness |
| **delta-live-tables-notebooks** | 403 | Python | DLT notebooks | Pipeline validation |
| **genai-cookbook** | 160 | Python | GenAI recipes | Recipe accuracy |
| **notebook-best-practices** | 150 | Python | Notebook practices | Best practice validation |

---

## Prioritized QA Domains

### Tier 1: Core Infrastructure (Highest Impact)
1. **MegaBlocks** - MoE training parity
2. **SDK Cross-Language** - Python/Go/Java/Rust API parity
3. **SQL Connectors** - Query result parity across languages
4. **Terraform Provider** - Infrastructure state validation

### Tier 2: Data Quality & ML
1. **Lilac** - Data curation signal accuracy
2. **Koalas** - pandas API compatibility
3. **spark-deep-learning** - Inference parity
4. **diviner** - Forecasting accuracy

### Tier 3: Tooling & Developer Experience
1. **CLI tools** - Command behavior parity
2. **VS Code extension** - Extension functionality
3. **dbt-databricks** - SQL transformation parity

### Tier 4: Benchmarks & Compliance
1. **TPC-DS/TPC-H** - Standard compliance
2. **Spark SQL perf** - Benchmark reproducibility
3. **Iceberg connectors** - Format compliance

---

## Cross-Cutting QA Opportunities

### 1. Cross-Language SDK Parity Matrix
```
                 Python  Go    Java  Rust  Node.js
Workspace API      ✓     ✓      ✓     -      -
SQL Connector      ✓     ✓      ✓     -      ✓
Zerobus SDK        ✓     ✓      ✓     ✓      -
CLI                ✓     ✓      -     ✓      -
```

### 2. Data Type Parity Testing
- Timestamp handling across connectors
- Decimal precision across languages
- NULL semantics consistency
- Array/Map type handling

### 3. Authentication Parity
- OAuth flows across SDKs
- Token refresh behavior
- Error handling consistency

### 4. Query Result Parity
- Same query, same results across:
  - databricks-sql-python
  - databricks-sql-go
  - databricks-sql-nodejs
  - databricks-jdbc
