#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.24",
#     "pandas>=2.0",
#     "langdetect>=1.0.9",
#     "coverage>=7.0",
# ]
# ///
"""Run all tests with coverage measurement."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run all test scripts and aggregate results."""
    scripts = [
        "lilac/scripts/test_pii_detection.py",
        "lilac/scripts/test_dedup_detection.py",
        "lilac/scripts/test_language_detection.py",
        "lilac/scripts/test_text_statistics.py",
        "benchmarks/scripts/test_benchmark_oracle.py",
        "spark-extensions/scripts/test_pandas_api_parity.py",
        "sdk-parity/scripts/test_sdk_conventions.py",
    ]

    total_passed = 0
    total_tests = 0
    all_passed = True

    print("=" * 60)
    print("Running all Databricks Ground Truth Corpus tests")
    print("=" * 60)

    for script in scripts:
        path = Path(script)
        if not path.exists():
            print(f"\nSKIP: {script} (not found)")
            continue

        print(f"\n>>> {script}")
        result = subprocess.run(
            ["uv", "run", script],
            capture_output=True,
            text=True,
        )

        # Extract summary line
        for line in result.stdout.split("\n"):
            if "Summary:" in line:
                print(f"    {line.strip()}")
                # Parse "Summary: X/Y tests passed"
                parts = line.split()
                for part in parts:
                    if "/" in part:
                        passed, total = part.split("/")
                        total_passed += int(passed)
                        total_tests += int(total)
                        break

        if result.returncode != 0:
            all_passed = False
            print(f"    FAILED (exit code {result.returncode})")

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
