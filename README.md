# Databricks Ground Truth Corpus

<div align="center">

![Databricks Ground Truth Corpus](https://img.shields.io/badge/Popperian-Falsification-red?style=for-the-badge&logo=databricks)
![Tests](https://img.shields.io/badge/Tests-129%2F322%20Passing-brightgreen?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Domains-8-blue?style=for-the-badge)

**Cross-implementation validation corpus using Popperian falsification methodology**

*"The wrong view of science betrays itself in the craving to be right"* - Karl Popper

</div>

---

| | |
|---|---|
| **Methodology** | Popperian Falsification (attempt to break, not verify) |
| **Analysis Date** | 2026-02-03 |
| **Repositories Analyzed** | 250 (80 active with >10 stars) |
| **Test Coverage** | 322 falsification tests across 8 domains |
| **Current Progress** | 129 tests passing (40% coverage) |

---

## Overview

Cross-implementation validation corpus for Databricks open-source projects. This corpus enables systematic falsification testing of:

- **Cross-language SDK parity** (Python, Go, Java)
- **ML infrastructure correctness** (MegaBlocks MoE)
- **Data connector consistency** (SQL across 5 languages)
- **Data quality signals** (Lilac PII, dedup, clustering)
- **Infrastructure as Code** (Terraform provider)
- **Benchmark reproducibility** (TPC-DS, TPC-H)

---

## Repository Structure

```
databricks-ground-truth-corpus/
├── README.md                 # This file
├── CATALOG.md               # Full repository analysis (250 repos)
├── QA-CHECKLIST.md          # Master 315-test falsification checklist
│
├── sdk-parity/              # Cross-language SDK validation
│   ├── specs/
│   │   └── cross-language-parity-oracle.md
│   └── oracle/              # Request/response golden outputs
│
├── megablocks/              # MoE training parity
│   ├── specs/
│   │   └── moe-parity-oracle.md
│   └── oracle/              # Tensor outputs vs HuggingFace
│
├── lilac/                   # Data quality signal validation
│   ├── specs/
│   │   └── data-quality-oracle.md
│   └── oracle/              # PII, dedup, clustering ground truth
│
├── sql-connectors/          # SQL result parity
│   ├── specs/
│   │   └── sql-parity-oracle.md
│   └── oracle/              # Query results across languages
│
├── cli-tools/               # CLI behavior validation
│   ├── specs/
│   │   └── cli-parity-oracle.md
│   └── oracle/              # Command output golden files
│
├── terraform/               # Terraform provider validation
│   ├── specs/
│   │   └── terraform-provider-oracle.md
│   └── oracle/              # State and plan golden files
│
├── spark-extensions/        # Spark extension validation
│   └── specs/
│
└── benchmarks/              # Benchmark reproducibility
    ├── specs/
    │   └── benchmark-reproducibility-oracle.md
    └── oracle/              # TPC-DS/TPC-H golden results
```

---

## Priority Tiers

### Tier 1: Core Infrastructure (Highest Impact)

| Domain | Repositories | Tests | Purpose |
|--------|--------------|-------|---------|
| **SDK Parity** | databricks-sdk-{py,go,java} | 45 | API contract consistency |
| **MegaBlocks** | megablocks | 30 | MoE numerical correctness |
| **SQL Connectors** | databricks-sql-{python,go,nodejs,jdbc} | 55 | Query result parity |

### Tier 2: Data Quality & Tooling

| Domain | Repositories | Tests | Purpose |
|--------|--------------|-------|---------|
| **Lilac** | lilac | 45 | Data curation signal accuracy |
| **CLI Tools** | cli, databricks-cli, click | 35 | Command behavior parity |
| **Terraform** | terraform-provider-databricks | 30 | Infrastructure state validation |

### Tier 3: Extensions & Benchmarks

| Domain | Repositories | Tests | Purpose |
|--------|--------------|-------|---------|
| **Spark Extensions** | koalas, spark-deep-learning, etc. | 40 | pandas/DL API parity |
| **Benchmarks** | tpcds-kit, tpch-dbgen, etc. | 35 | TPC standard compliance |

---

## Quick Start

### 1. Clone the corpus

```bash
git clone https://github.com/paiml/databricks-ground-truth-corpus
cd databricks-ground-truth-corpus
```

### 2. Run SDK parity tests

```bash
# Python SDK
python sdk-parity/scripts/validate_python.py --corpus sdk-parity/oracle/

# Go SDK
go run sdk-parity/scripts/validate_go.go --corpus sdk-parity/oracle/

# Java SDK
java -jar sdk-parity/scripts/validate_java.jar --corpus sdk-parity/oracle/
```

### 3. Run MegaBlocks parity

```bash
# Compare MegaBlocks vs HuggingFace Mixtral
python megablocks/scripts/validate_parity.py \
    --reference megablocks/oracle/mixtral-8x7b/v1 \
    --candidate megablocks/oracle/megablocks-dmoe/v1 \
    --tolerance fp32
```

### 4. Run SQL connector parity

```bash
# Generate golden outputs (requires Databricks connection)
python sql-connectors/scripts/capture_golden.py --workspace $DATABRICKS_HOST

# Validate each connector
python sql-connectors/scripts/validate_python.py
go run sql-connectors/scripts/validate_go.go
node sql-connectors/scripts/validate_nodejs.ts
java -jar sql-connectors/scripts/validate_java.jar
```

### 5. Run Lilac validation

```bash
# Run all Lilac falsification tests (PII, dedup, language detection)
uv run lilac/scripts/test_pii_detection.py
uv run lilac/scripts/test_dedup_detection.py
uv run lilac/scripts/test_language_detection.py
```

### 6. Run Benchmark oracle validation

```bash
# Validate TPC-DS/TPC-H row counts and ALS algorithm properties
uv run benchmarks/scripts/test_benchmark_oracle.py
```

---

## Falsification Principles

1. **Severe Testing**: Design tests that have high probability of failing if implementation is wrong
2. **Corroboration, Not Verification**: Passing tests provide corroboration, not proof
3. **Cross-Implementation**: Compare against independent implementations (HuggingFace, pandas, TPC)
4. **Tolerance Documentation**: IEEE 754 tolerances for floating-point, exact for integers/strings
5. **Bias Detection**: Look for systematic deviations, not just point failures

---

## Tolerance Standards

| Data Type | Tolerance | Standard |
|-----------|-----------|----------|
| fp32 | atol=1e-5, rtol=1e-4 | IEEE 754 |
| fp16 | atol=1e-3, rtol=1e-2 | IEEE 754 |
| int8 | atol=1e-1 | Quantization |
| int4 | atol=5e-1 | Quantization |
| int64 | Exact | None |
| string | Exact | Unicode NFC |
| timestamp | 1ms | ISO 8601 |

---

## Contributing

1. Add golden outputs to appropriate `oracle/` directory
2. Update corresponding spec in `specs/`
3. Add test IDs to `QA-CHECKLIST.md`
4. Run full validation suite
5. Submit PR with test results

---

## Repository Coverage Summary

| Category | Repos | Description |
|----------|-------|-------------|
| ML/AI | 8 | megablocks, spark-deep-learning, koalas, etc. |
| SDKs | 12 | Python, Go, Java, Rust SDKs + Zerobus |
| CLI | 4 | Go CLI, Python CLI, SQL CLI, click |
| Data | 7 | SQL connectors, Iceberg, dbt |
| Infra | 5 | Terraform, Docker, Containers |
| Benchmarks | 5 | TPC-DS, TPC-H, Spark SQL perf |
| MLOps | 4 | mlops-stacks, Delta Live Tables |

See [CATALOG.md](CATALOG.md) for complete analysis of all 250 repositories.

---

## References

- Popper, K. (1959). The Logic of Scientific Discovery
- Goldberg, D. (1991). What Every Computer Scientist Should Know About FP
- IEEE 754-2019: Floating-Point Arithmetic
- TPC-DS Specification v3.2.0
- TPC-H Specification v3.0.1
- Gale, T. et al. (2023). MegaBlocks: Efficient Sparse Training with MoE

---

## License

Apache 2.0 - See LICENSE file
