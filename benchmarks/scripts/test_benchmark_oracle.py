#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.24",
# ]
# ///
"""Test benchmark oracle correctness.

This script validates that the benchmark oracle golden values match
the official TPC specifications using Popperian falsification methodology.

Tests:
- TPC-DS row counts match specification v3.2.0
- TPC-H row counts match specification v3.0.1
- ALS algorithm properties (convergence, shapes)

Usage:
    uv run benchmarks/scripts/test_benchmark_oracle.py

References:
    - TPC-DS Specification v3.2.0
    - TPC-H Specification v3.0.1
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    message: str
    details: dict = field(default_factory=dict)


# =============================================================================
# TPC-DS Row Count Specification (v3.2.0, Table 3-2)
# =============================================================================

# Official TPC-DS SF=1 row counts from specification
TPCDS_SF1_EXPECTED = {
    "call_center": 6,
    "catalog_page": 11718,
    "catalog_returns": 144067,
    "catalog_sales": 1441548,
    "customer": 100000,
    "customer_address": 50000,
    "customer_demographics": 1920800,
    "date_dim": 73049,
    "household_demographics": 7200,
    "income_band": 20,
    "inventory": 11745000,
    "item": 18000,
    "promotion": 300,
    "reason": 35,
    "ship_mode": 20,
    "store": 12,
    "store_returns": 287514,
    "store_sales": 2880404,
    "time_dim": 86400,
    "warehouse": 5,
    "web_page": 60,
    "web_returns": 71763,
    "web_sales": 719384,
    "web_site": 30,
}


# =============================================================================
# TPC-H Row Count Specification (v3.0.1, Section 4.2.3)
# =============================================================================

# Official TPC-H SF=1 row counts from specification
TPCH_SF1_EXPECTED = {
    "lineitem": 6001215,
    "orders": 1500000,
    "customer": 150000,
    "part": 200000,
    "partsupp": 800000,
    "supplier": 10000,
    "nation": 25,
    "region": 5,
}


# =============================================================================
# TPC-DS Validation
# =============================================================================


def validate_tpcds_oracle(oracle_path: Path) -> list[TestResult]:
    """Validate TPC-DS oracle against specification."""
    results = []

    # Load oracle file
    row_counts_file = oracle_path / "oracle" / "tpcds" / "sf1" / "row_counts.json"

    if not row_counts_file.exists():
        results.append(
            TestResult(
                name="TPC-DS Oracle File Exists",
                passed=False,
                message=f"Oracle file not found: {row_counts_file}",
            )
        )
        return results

    results.append(
        TestResult(
            name="TPC-DS Oracle File Exists",
            passed=True,
            message=f"Found: {row_counts_file}",
        )
    )

    with open(row_counts_file) as f:
        oracle_data = json.load(f)

    # Validate structure
    if "tables" not in oracle_data:
        results.append(
            TestResult(
                name="TPC-DS Oracle Structure",
                passed=False,
                message="Missing 'tables' key in oracle data",
            )
        )
        return results

    results.append(
        TestResult(
            name="TPC-DS Oracle Structure",
            passed=True,
            message="Valid structure with 'tables' key",
        )
    )

    # Validate each table count
    oracle_tables = oracle_data["tables"]
    all_match = True
    mismatches = []

    for table, expected_count in TPCDS_SF1_EXPECTED.items():
        if table not in oracle_tables:
            mismatches.append((table, expected_count, "MISSING"))
            all_match = False
        elif oracle_tables[table] != expected_count:
            mismatches.append((table, expected_count, oracle_tables[table]))
            all_match = False

    results.append(
        TestResult(
            name="TPC-DS Row Counts Match Spec",
            passed=all_match,
            message=f"All {len(TPCDS_SF1_EXPECTED)} tables match specification"
            if all_match
            else f"{len(mismatches)} mismatches found",
            details={"mismatches": mismatches} if mismatches else {},
        )
    )

    # Validate table count
    results.append(
        TestResult(
            name="TPC-DS Table Count",
            passed=len(oracle_tables) == len(TPCDS_SF1_EXPECTED),
            message=f"Oracle has {len(oracle_tables)} tables, spec has {len(TPCDS_SF1_EXPECTED)}",
        )
    )

    return results


# =============================================================================
# TPC-H Validation
# =============================================================================


def validate_tpch_oracle(oracle_path: Path) -> list[TestResult]:
    """Validate TPC-H oracle against specification."""
    results = []

    # Load oracle file
    row_counts_file = oracle_path / "oracle" / "tpch" / "sf1" / "row_counts.json"

    if not row_counts_file.exists():
        results.append(
            TestResult(
                name="TPC-H Oracle File Exists",
                passed=False,
                message=f"Oracle file not found: {row_counts_file}",
            )
        )
        return results

    results.append(
        TestResult(
            name="TPC-H Oracle File Exists",
            passed=True,
            message=f"Found: {row_counts_file}",
        )
    )

    with open(row_counts_file) as f:
        oracle_data = json.load(f)

    # Validate structure
    if "tables" not in oracle_data:
        results.append(
            TestResult(
                name="TPC-H Oracle Structure",
                passed=False,
                message="Missing 'tables' key in oracle data",
            )
        )
        return results

    results.append(
        TestResult(
            name="TPC-H Oracle Structure",
            passed=True,
            message="Valid structure with 'tables' key",
        )
    )

    # Validate each table count
    oracle_tables = oracle_data["tables"]
    all_match = True
    mismatches = []

    for table, expected_count in TPCH_SF1_EXPECTED.items():
        if table not in oracle_tables:
            mismatches.append((table, expected_count, "MISSING"))
            all_match = False
        elif oracle_tables[table] != expected_count:
            mismatches.append((table, expected_count, oracle_tables[table]))
            all_match = False

    results.append(
        TestResult(
            name="TPC-H Row Counts Match Spec",
            passed=all_match,
            message=f"All {len(TPCH_SF1_EXPECTED)} tables match specification"
            if all_match
            else f"{len(mismatches)} mismatches found",
            details={"mismatches": mismatches} if mismatches else {},
        )
    )

    # Validate specific well-known values
    results.append(
        TestResult(
            name="TPC-H LINEITEM Count (6,001,215)",
            passed=oracle_tables.get("lineitem") == 6001215,
            message=f"LINEITEM = {oracle_tables.get('lineitem', 'MISSING')}",
        )
    )

    results.append(
        TestResult(
            name="TPC-H ORDERS Count (1,500,000)",
            passed=oracle_tables.get("orders") == 1500000,
            message=f"ORDERS = {oracle_tables.get('orders', 'MISSING')}",
        )
    )

    return results


# =============================================================================
# ALS Algorithm Validation
# =============================================================================


class SimpleALS:
    """Reference ALS implementation for validation."""

    def __init__(self, n_factors: int = 10, n_iterations: int = 10, reg: float = 0.1):
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.reg = reg
        self.user_factors = None
        self.item_factors = None
        self.rmse_history = []

    def fit(self, ratings: np.ndarray) -> None:
        """Fit ALS model.

        Args:
            ratings: User-item rating matrix (sparse represented as dense with 0s)
        """
        n_users, n_items = ratings.shape

        # Initialize factors randomly
        np.random.seed(42)
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))

        # Get mask of observed ratings
        mask = ratings != 0

        self.rmse_history = []

        for _iteration in range(self.n_iterations):
            # Fix items, solve for users
            for u in range(n_users):
                rated_items = np.where(mask[u])[0]
                if len(rated_items) == 0:
                    continue
                V = self.item_factors[rated_items]
                r = ratings[u, rated_items]
                # Solve: (V^T V + lambda I) U_u = V^T r_u
                A = V.T @ V + self.reg * np.eye(self.n_factors)
                b = V.T @ r
                self.user_factors[u] = np.linalg.solve(A, b)

            # Fix users, solve for items
            for i in range(n_items):
                rated_users = np.where(mask[:, i])[0]
                if len(rated_users) == 0:
                    continue
                U = self.user_factors[rated_users]
                r = ratings[rated_users, i]
                A = U.T @ U + self.reg * np.eye(self.n_factors)
                b = U.T @ r
                self.item_factors[i] = np.linalg.solve(A, b)

            # Compute RMSE
            predictions = self.user_factors @ self.item_factors.T
            errors = (ratings - predictions) * mask
            rmse = np.sqrt(np.sum(errors**2) / np.sum(mask))
            self.rmse_history.append(rmse)

    def predict(self, user_idx: int, item_idx: int) -> float:
        """Predict rating for a user-item pair."""
        return float(self.user_factors[user_idx] @ self.item_factors[item_idx])


def run_als_tests() -> list[TestResult]:
    """Run ALS algorithm property tests."""
    results = []

    # Create small synthetic dataset
    np.random.seed(42)
    n_users, n_items = 50, 30
    true_user_factors = np.random.normal(0, 1, (n_users, 5))
    true_item_factors = np.random.normal(0, 1, (n_items, 5))
    true_ratings = true_user_factors @ true_item_factors.T

    # Clamp to valid rating range and add noise
    true_ratings = np.clip(true_ratings, 1, 5)
    noise = np.random.normal(0, 0.5, (n_users, n_items))
    ratings = np.clip(true_ratings + noise, 1, 5)

    # Make sparse (30% observed)
    mask = np.random.random((n_users, n_items)) < 0.3
    ratings = ratings * mask

    # Test 1: RMSE convergence (should be monotonically decreasing or stable)
    model = SimpleALS(n_factors=10, n_iterations=20, reg=0.1)
    model.fit(ratings)

    # Check convergence - allow small increases (1e-6) due to numerical issues
    is_converging = True
    for i in range(1, len(model.rmse_history)):
        if model.rmse_history[i] > model.rmse_history[i - 1] + 1e-4:
            is_converging = False
            break

    results.append(
        TestResult(
            name="ALS RMSE Convergence",
            passed=is_converging,
            message=f"RMSE: {model.rmse_history[0]:.4f} -> {model.rmse_history[-1]:.4f}",
            details={"rmse_history": [round(x, 4) for x in model.rmse_history]},
        )
    )

    # Test 2: Factor matrix shapes
    correct_shapes = model.user_factors.shape == (n_users, 10) and model.item_factors.shape == (
        n_items,
        10,
    )
    results.append(
        TestResult(
            name="ALS Factor Matrix Shapes",
            passed=correct_shapes,
            message=f"User: {model.user_factors.shape}, Item: {model.item_factors.shape}",
        )
    )

    # Test 3: Regularization effect
    model_low_reg = SimpleALS(n_factors=10, n_iterations=20, reg=0.01)
    model_high_reg = SimpleALS(n_factors=10, n_iterations=20, reg=1.0)
    model_low_reg.fit(ratings)
    model_high_reg.fit(ratings)

    # Lower regularization should allow better fit (lower RMSE) on training data
    results.append(
        TestResult(
            name="ALS Regularization Effect",
            passed=model_low_reg.rmse_history[-1] < model_high_reg.rmse_history[-1],
            message=f"Low reg RMSE: {model_low_reg.rmse_history[-1]:.4f}, "
            f"High reg RMSE: {model_high_reg.rmse_history[-1]:.4f}",
        )
    )

    # Test 4: Rank effect (higher rank = better fit)
    model_low_rank = SimpleALS(n_factors=3, n_iterations=20, reg=0.1)
    model_high_rank = SimpleALS(n_factors=20, n_iterations=20, reg=0.1)
    model_low_rank.fit(ratings)
    model_high_rank.fit(ratings)

    results.append(
        TestResult(
            name="ALS Rank Effect",
            passed=model_high_rank.rmse_history[-1] <= model_low_rank.rmse_history[-1],
            message=f"Rank 3 RMSE: {model_low_rank.rmse_history[-1]:.4f}, "
            f"Rank 20 RMSE: {model_high_rank.rmse_history[-1]:.4f}",
        )
    )

    # Test 5: Determinism with same seed
    model1 = SimpleALS(n_factors=10, n_iterations=5, reg=0.1)
    model2 = SimpleALS(n_factors=10, n_iterations=5, reg=0.1)
    model1.fit(ratings)
    model2.fit(ratings)

    results.append(
        TestResult(
            name="ALS Determinism",
            passed=np.allclose(model1.user_factors, model2.user_factors, atol=1e-10),
            message="Same seed produces identical results",
        )
    )

    # Test 6: Predictions are in valid range
    all_preds = model.user_factors @ model.item_factors.T
    # Predictions should be finite
    results.append(
        TestResult(
            name="ALS Predictions Finite",
            passed=np.all(np.isfinite(all_preds)),
            message=f"All {all_preds.size} predictions are finite",
        )
    )

    return results


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Test benchmark oracle correctness")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    # Find oracle path (relative to this script)
    script_path = Path(__file__).resolve()
    oracle_path = script_path.parent.parent

    print("=== Benchmark Oracle Falsification Tests ===\n")

    # Run TPC-DS tests
    print("TPC-DS Oracle Validation:")
    tpcds_results = validate_tpcds_oracle(oracle_path)
    for result in tpcds_results:
        icon = "+" if result.passed else "x"
        print(f"  {icon} {result.name}: {result.message}")
        if result.details.get("mismatches"):
            for table, expected, actual in result.details["mismatches"][:3]:
                print(f"      {table}: expected {expected}, got {actual}")

    # Run TPC-H tests
    print("\nTPC-H Oracle Validation:")
    tpch_results = validate_tpch_oracle(oracle_path)
    for result in tpch_results:
        icon = "+" if result.passed else "x"
        print(f"  {icon} {result.name}: {result.message}")
        if result.details.get("mismatches"):
            for table, expected, actual in result.details["mismatches"][:3]:
                print(f"      {table}: expected {expected}, got {actual}")

    # Run ALS tests
    print("\nALS Algorithm Property Tests:")
    als_results = run_als_tests()
    for result in als_results:
        icon = "+" if result.passed else "x"
        print(f"  {icon} {result.name}: {result.message}")

    # Summary
    all_results = tpcds_results + tpch_results + als_results
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results if requested
    if args.output:
        output_data = {
            "tpcds_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in tpcds_results
            ],
            "tpch_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in tpch_results
            ],
            "als_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in als_results
            ],
            "summary": {"passed": passed, "total": total},
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
