# Databricks Ground Truth Corpus

> *"The wrong view of science betrays itself in the craving to be right"* - Karl Popper

Cross-implementation validation corpus for Databricks open-source projects using **Popperian falsification methodology**.

## Overview

This corpus enables systematic falsification testing of:

- **Cross-language SDK parity** (Python, Go, Java)
- **ML infrastructure correctness** (MegaBlocks MoE)
- **Data connector consistency** (SQL across 5 languages)
- **Data quality signals** (Lilac PII, dedup, clustering)
- **Infrastructure as Code** (Terraform provider)
- **Benchmark reproducibility** (TPC-DS, TPC-H)

## Current Status

| Metric | Value |
|--------|-------|
| **Repositories Analyzed** | 250 (80 active with >10 stars) |
| **Test Coverage** | 322 falsification tests across 8 domains |
| **Current Progress** | 129 tests passing (40% coverage) |
| **Code Coverage** | 100% (1932/1932 lines) |

## Quick Start

```bash
# Clone the corpus
git clone https://github.com/paiml/databricks-ground-truth-corpus
cd databricks-ground-truth-corpus

# Run all tests
uv run run_all_tests.py
```

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
| **Spark Extensions** | koalas, spark-deep-learning | 40 | pandas/DL API parity |
| **Benchmarks** | tpcds-kit, tpch-dbgen | 35 | TPC standard compliance |
