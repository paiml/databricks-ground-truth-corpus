#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "torch>=2.0",
#     "safetensors>=0.4",
#     "numpy>=1.24",
# ]
# ///
"""Validate MegaBlocks parity against HuggingFace golden outputs.

This script implements Popperian falsification testing for MoE layers,
comparing MegaBlocks outputs against HuggingFace Mixtral reference.

Usage:
    uv run scripts/validate_parity.py \
        --reference oracle/mixtral-8x7b/v1 \
        --candidate oracle/megablocks-dmoe/v1 \
        --tolerance fp32

References:
    - IEEE 754: Floating-point tolerance standards
    - Goldberg, D. (1991). What Every Computer Scientist Should Know About FP
"""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from safetensors.torch import load_file


@dataclass
class Tolerance:
    """IEEE 754-based tolerance for floating-point comparison."""

    atol: float
    rtol: float
    name: str

    @classmethod
    def fp32(cls) -> "Tolerance":
        return cls(atol=1e-5, rtol=1e-4, name="fp32")

    @classmethod
    def fp16(cls) -> "Tolerance":
        return cls(atol=1e-3, rtol=1e-2, name="fp16")

    @classmethod
    def bf16(cls) -> "Tolerance":
        return cls(atol=1e-2, rtol=1e-1, name="bf16")

    def is_close(self, a: float, b: float) -> bool:
        """NumPy-style allclose criterion."""
        return abs(a - b) <= self.atol + self.rtol * abs(b)


@dataclass
class TensorDiff:
    """Statistics about tensor differences."""

    max_diff: float
    mean_diff: float
    max_diff_idx: tuple[int, ...]
    mismatch_ratio: float
    shape_match: bool
    within_tolerance: bool


def compare_tensors(
    reference: torch.Tensor,
    candidate: torch.Tensor,
    tolerance: Tolerance,
    mismatch_threshold: float = 0.01,
) -> TensorDiff:
    """Compare two tensors with detailed statistics."""

    # Check shapes
    if reference.shape != candidate.shape:
        return TensorDiff(
            max_diff=float("inf"),
            mean_diff=float("inf"),
            max_diff_idx=(),
            mismatch_ratio=1.0,
            shape_match=False,
            within_tolerance=False,
        )

    # Convert to float64 for comparison
    ref = reference.double().flatten()
    cand = candidate.double().flatten()

    # Compute differences
    diff = torch.abs(ref - cand)
    max_diff = diff.max().item()
    mean_diff = diff.mean().item()
    max_diff_idx = diff.argmax().item()

    # Convert index back to original shape
    max_diff_idx_tuple = np.unravel_index(max_diff_idx, reference.shape)

    # Check tolerance element-wise
    close = torch.abs(ref - cand) <= tolerance.atol + tolerance.rtol * torch.abs(cand)
    mismatch_ratio = 1.0 - close.float().mean().item()

    # Within tolerance if mismatch ratio is below threshold
    within_tolerance = mismatch_ratio <= mismatch_threshold

    return TensorDiff(
        max_diff=max_diff,
        mean_diff=mean_diff,
        max_diff_idx=max_diff_idx_tuple,
        mismatch_ratio=mismatch_ratio,
        shape_match=True,
        within_tolerance=within_tolerance,
    )


def detect_systematic_bias(
    reference: torch.Tensor,
    candidate: torch.Tensor,
) -> str | None:
    """Detect systematic biases in the difference."""

    if reference.shape != candidate.shape:
        return "Shape mismatch"

    ref = reference.double().flatten()
    cand = candidate.double().flatten()
    diff = cand - ref

    mean_diff = diff.mean().item()
    std_diff = diff.std().item()
    ref_std = ref.std().item()

    # Detect mean shift (bias)
    if ref_std > 0 and abs(mean_diff) > 3 * std_diff:
        return f"Mean shift detected: {mean_diff:.6f} (3σ = {3 * std_diff:.6f})"

    # Detect scale drift
    cand_std = cand.std().item()
    if ref_std > 0:
        scale_ratio = cand_std / ref_std
        if abs(scale_ratio - 1.0) > 0.1:
            return f"Scale drift detected: ratio = {scale_ratio:.4f}"

    return None


def load_test_data(
    manifest_path: Path,
) -> list[dict]:
    """Load test data from manifest."""
    with open(manifest_path) as f:
        manifest = json.load(f)

    tests = []
    base_dir = manifest_path.parent

    for test in manifest.get("tests", []):
        tensor_file = base_dir / test["file"]
        json_file = base_dir / f"{test['name']}_{test['hash']}.json"

        if tensor_file.exists():
            tensors = load_file(str(tensor_file))
            with open(json_file) as f:
                metadata = json.load(f)

            tests.append(
                {
                    "name": test["name"],
                    "hash": test["hash"],
                    "tensors": tensors,
                    "metadata": metadata,
                }
            )

    return tests


def run_parity_test(
    ref_dir: Path,
    cand_dir: Path,
    tolerance: Tolerance,
) -> dict:
    """Run full parity test suite."""

    # Load manifests
    ref_manifest = ref_dir / "manifest.json"
    cand_manifest = cand_dir / "manifest.json"

    if not ref_manifest.exists():
        return {"error": f"Reference manifest not found: {ref_manifest}"}

    if not cand_manifest.exists():
        return {"error": f"Candidate manifest not found: {cand_manifest}"}

    ref_tests = load_test_data(ref_manifest)
    cand_tests = load_test_data(cand_manifest)

    # Match tests by hash
    cand_by_hash = {t["hash"]: t for t in cand_tests}

    results = {
        "tolerance": tolerance.name,
        "reference_dir": str(ref_dir),
        "candidate_dir": str(cand_dir),
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
        },
    }

    for ref_test in ref_tests:
        test_hash = ref_test["hash"]
        test_name = ref_test["name"]

        results["summary"]["total"] += 1

        if test_hash not in cand_by_hash:
            results["tests"].append(
                {
                    "name": test_name,
                    "hash": test_hash,
                    "status": "SKIPPED",
                    "reason": "No matching candidate",
                }
            )
            results["summary"]["skipped"] += 1
            continue

        cand_test = cand_by_hash[test_hash]

        # Compare each tensor
        tensor_results = []
        all_passed = True

        for tensor_name, ref_tensor in ref_test["tensors"].items():
            if tensor_name not in cand_test["tensors"]:
                tensor_results.append(
                    {
                        "tensor": tensor_name,
                        "status": "MISSING",
                    }
                )
                all_passed = False
                continue

            cand_tensor = cand_test["tensors"][tensor_name]

            # Compare tensors
            diff = compare_tensors(ref_tensor, cand_tensor, tolerance)

            # Check for bias
            bias = detect_systematic_bias(ref_tensor, cand_tensor)

            tensor_result = {
                "tensor": tensor_name,
                "shape_match": diff.shape_match,
                "within_tolerance": diff.within_tolerance,
                "max_diff": diff.max_diff,
                "mean_diff": diff.mean_diff,
                "mismatch_ratio": diff.mismatch_ratio,
                "bias": bias,
                "status": "PASS" if diff.within_tolerance and diff.shape_match else "FAIL",
            }

            tensor_results.append(tensor_result)

            if not (diff.within_tolerance and diff.shape_match):
                all_passed = False

        results["tests"].append(
            {
                "name": test_name,
                "hash": test_hash,
                "status": "PASS" if all_passed else "FAIL",
                "tensors": tensor_results,
            }
        )

        if all_passed:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    return results


def print_results(results: dict):
    """Print results in human-readable format."""

    if "error" in results:
        print(f"ERROR: {results['error']}")
        return

    print("=== MegaBlocks Parity Validation ===")
    print(f"Reference: {results['reference_dir']}")
    print(f"Candidate: {results['candidate_dir']}")
    print(f"Tolerance: {results['tolerance']}")
    print()

    summary = results["summary"]
    print(
        f"Summary: {summary['passed']}/{summary['total']} passed, "
        f"{summary['failed']} failed, {summary['skipped']} skipped"
    )
    print()

    for test in results["tests"]:
        status_icon = "✓" if test["status"] == "PASS" else "✗" if test["status"] == "FAIL" else "○"
        print(f"  {status_icon} {test['name']} [{test['hash']}]: {test['status']}")

        if test["status"] == "FAIL" and "tensors" in test:
            for tensor in test["tensors"]:
                if tensor["status"] != "PASS":
                    print(f"      {tensor['tensor']}: {tensor['status']}")
                    if "max_diff" in tensor:
                        print(f"        max_diff: {tensor['max_diff']:.6e}")
                        print(f"        mismatch_ratio: {tensor['mismatch_ratio']:.4f}")
                    if tensor.get("bias"):
                        print(f"        bias: {tensor['bias']}")

    print()
    if summary["failed"] == 0 and summary["skipped"] == 0:
        print("All parity tests PASSED")
    elif summary["failed"] > 0:
        print(f"FAILED: {summary['failed']} tests did not meet tolerance")


def main():
    parser = argparse.ArgumentParser(description="Validate MegaBlocks parity")
    parser.add_argument("--reference", required=True, help="Reference golden directory")
    parser.add_argument("--candidate", required=True, help="Candidate golden directory")
    parser.add_argument("--tolerance", choices=["fp32", "fp16", "bf16"], default="fp32")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    # Set tolerance
    tolerance_map = {
        "fp32": Tolerance.fp32(),
        "fp16": Tolerance.fp16(),
        "bf16": Tolerance.bf16(),
    }
    tolerance = tolerance_map[args.tolerance]

    # Run parity test
    results = run_parity_test(
        Path(args.reference),
        Path(args.candidate),
        tolerance,
    )

    # Print results
    print_results(results)

    # Save JSON if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    # Exit with appropriate code
    if results.get("error"):
        exit(1)
    if results["summary"]["failed"] > 0:
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
