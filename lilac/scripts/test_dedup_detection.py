#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.24",
# ]
# ///
"""Test near-duplicate detection accuracy.

This script validates duplicate detection algorithms against
ground truth using Popperian falsification methodology.

Dedup Types Tested:
- Exact duplicates (hash-based)
- Near-duplicates (MinHash/Jaccard similarity)
- Substring containment

Usage:
    uv run scripts/test_dedup_detection.py

References:
    - Broder, A. (1997). On the resemblance and containment of documents
    - Lilac Data Quality Oracle Spec: specs/data-quality-oracle.md
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field

import numpy as np


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    message: str
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    details: dict = field(default_factory=dict)


# =============================================================================
# Duplicate Detection Algorithms (Reference Implementation)
# =============================================================================


class DuplicateDetector:
    """Reference duplicate detector using multiple algorithms."""

    def __init__(self, num_hashes: int = 128, ngram_size: int = 3):
        self.num_hashes = num_hashes
        self.ngram_size = ngram_size
        # Generate hash functions for MinHash
        np.random.seed(42)
        self.hash_a = np.random.randint(1, 2**31, size=num_hashes)
        self.hash_b = np.random.randint(0, 2**31, size=num_hashes)
        self.prime = 2**31 - 1

    def exact_hash(self, text: str) -> str:
        """SHA-256 hash for exact duplicate detection."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get_ngrams(self, text: str) -> set[str]:
        """Extract character n-grams from text."""
        text = text.lower().strip()
        if len(text) < self.ngram_size:
            return {text}
        return {text[i : i + self.ngram_size] for i in range(len(text) - self.ngram_size + 1)}

    def minhash_signature(self, ngrams: set[str]) -> np.ndarray:
        """Compute MinHash signature for a set of n-grams."""
        if not ngrams:
            return np.full(self.num_hashes, np.inf)

        # Convert ngrams to hash values
        ngram_hashes = np.array([hash(ng) % self.prime for ng in ngrams])

        # Compute MinHash for each hash function
        signature = np.full(self.num_hashes, np.inf)
        for _i, ng_hash in enumerate(ngram_hashes):
            h = (self.hash_a * ng_hash + self.hash_b) % self.prime
            signature = np.minimum(signature, h)

        return signature

    def jaccard_similarity(self, set1: set[str], set2: set[str]) -> float:
        """Exact Jaccard similarity."""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union

    def minhash_similarity(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """Estimated Jaccard similarity from MinHash signatures."""
        return np.mean(sig1 == sig2)

    def containment(self, text1: str, text2: str) -> float:
        """Check if one text contains the other (substring).

        Returns 1.0 if either text is a complete substring of the other,
        with a minimum length requirement to avoid trivial matches.
        """
        if not text1 or not text2:
            return 0.0

        min_length = 10  # Minimum substring length to be considered
        t1_lower = text1.lower()
        t2_lower = text2.lower()

        # Check if shorter text is contained in longer
        shorter, longer = (
            (t1_lower, t2_lower) if len(t1_lower) < len(t2_lower) else (t2_lower, t1_lower)
        )

        if len(shorter) >= min_length and shorter in longer:
            return 1.0  # Full containment

        return 0.0

    def find_duplicates(
        self,
        documents: list[str],
        threshold: float = 0.9,
    ) -> list[tuple[int, int, float, str]]:
        """Find all duplicate pairs above threshold.

        Returns: List of (idx1, idx2, similarity, method)
        """
        duplicates = []
        n = len(documents)

        # Precompute hashes and signatures
        exact_hashes = [self.exact_hash(doc) for doc in documents]
        ngrams = [self.get_ngrams(doc) for doc in documents]
        signatures = [self.minhash_signature(ng) for ng in ngrams]

        for i in range(n):
            for j in range(i + 1, n):
                # Check exact duplicate
                if exact_hashes[i] == exact_hashes[j]:
                    duplicates.append((i, j, 1.0, "exact"))
                    continue

                # Check near-duplicate via MinHash
                mh_sim = self.minhash_similarity(signatures[i], signatures[j])
                if mh_sim >= threshold:
                    # Verify with exact Jaccard
                    exact_sim = self.jaccard_similarity(ngrams[i], ngrams[j])
                    if exact_sim >= threshold:
                        duplicates.append((i, j, exact_sim, "near"))
                        continue

                # Check containment
                cont = self.containment(documents[i], documents[j])
                if cont >= threshold:
                    duplicates.append((i, j, cont, "containment"))

        return duplicates


# =============================================================================
# Ground Truth Test Cases
# =============================================================================


def get_exact_duplicate_cases() -> tuple[list[str], list[tuple[int, int]]]:
    """Test cases for exact duplicate detection."""
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "The quick brown fox jumps over the lazy dog.",  # Exact dup of 0
        "A completely different sentence.",
        "The quick brown fox jumps over the lazy dog.",  # Exact dup of 0, 1
        "Another unique document here.",
    ]
    expected_pairs = [(0, 1), (0, 3), (1, 3)]
    return documents, expected_pairs


def get_near_duplicate_cases() -> tuple[list[str], list[tuple[int, int]]]:
    """Test cases for near-duplicate detection."""
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "The quick brown fox jumps over a lazy dog.",  # Near dup (1 word diff) - Jaccard ~0.86
        "A completely different sentence about cats.",
        "The quick brown fox jumps over the lazy dogs.",  # Near dup (1 char diff) - should be ~0.9+
        "Something entirely unrelated to animals.",
    ]
    # With threshold 0.8, expect (0,1) and (0,3)
    expected_pairs = [(0, 1), (0, 3)]
    return documents, expected_pairs


def get_containment_cases() -> tuple[list[str], list[tuple[int, int]]]:
    """Test cases for substring containment detection.

    Note: Containment cases need low Jaccard similarity but high containment.
    This means short substrings of much longer documents.
    """
    documents = [
        "This is a very long document with many different words and phrases that make it quite unique in its content and structure.",
        "long document",  # Short substring of 0 (low Jaccard, high containment)
        "Completely different text about something else.",
        "many different words",  # Short substring of 0
    ]
    expected_pairs = [(0, 1), (0, 3)]
    return documents, expected_pairs


def get_no_duplicate_cases() -> tuple[list[str], list[tuple[int, int]]]:
    """Test cases that should have no duplicates."""
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "How vexingly quick daft zebras jump.",
        "The five boxing wizards jump quickly.",
    ]
    expected_pairs = []  # No duplicates
    return documents, expected_pairs


# =============================================================================
# Test Runner
# =============================================================================


def compute_metrics(
    predicted_pairs: set[tuple[int, int]],
    ground_truth_pairs: set[tuple[int, int]],
) -> tuple[float, float, float]:
    """Compute precision, recall, F1 for duplicate pairs."""
    if not predicted_pairs and not ground_truth_pairs:
        return 1.0, 1.0, 1.0

    # Normalize pairs (always smaller index first)
    pred_normalized = {(min(a, b), max(a, b)) for a, b in predicted_pairs}
    gt_normalized = {(min(a, b), max(a, b)) for a, b in ground_truth_pairs}

    true_positives = len(pred_normalized & gt_normalized)

    precision = true_positives / len(pred_normalized) if pred_normalized else 0.0
    recall = true_positives / len(gt_normalized) if gt_normalized else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def run_dedup_tests(detector: DuplicateDetector) -> list[TestResult]:
    """Run all duplicate detection tests."""
    results = []

    # Test exact duplicates
    docs, expected = get_exact_duplicate_cases()
    duplicates = detector.find_duplicates(docs, threshold=1.0)
    pred_pairs = {(d[0], d[1]) for d in duplicates if d[3] == "exact"}
    gt_pairs = set(expected)
    precision, recall, f1 = compute_metrics(pred_pairs, gt_pairs)
    results.append(
        TestResult(
            name="Exact Duplicate Detection",
            passed=precision == 1.0,  # Require perfect precision
            message=f"P={precision:.3f} R={recall:.3f} F1={f1:.3f}",
            precision=precision,
            recall=recall,
            f1=f1,
            details={"predicted": list(pred_pairs), "expected": list(gt_pairs)},
        )
    )

    # Test near duplicates
    docs, expected = get_near_duplicate_cases()
    duplicates = detector.find_duplicates(docs, threshold=0.8)
    pred_pairs = {(d[0], d[1]) for d in duplicates}
    gt_pairs = set(expected)
    precision, recall, f1 = compute_metrics(pred_pairs, gt_pairs)
    results.append(
        TestResult(
            name="Near-Duplicate Detection",
            passed=f1 >= 0.8,
            message=f"P={precision:.3f} R={recall:.3f} F1={f1:.3f}"
            if f1 >= 0.8
            else f"F1={f1:.3f} < 0.8 required",
            precision=precision,
            recall=recall,
            f1=f1,
            details={"predicted": list(pred_pairs), "expected": list(gt_pairs)},
        )
    )

    # Test containment
    docs, expected = get_containment_cases()
    duplicates = detector.find_duplicates(docs, threshold=0.5)
    pred_pairs = {(d[0], d[1]) for d in duplicates if d[3] == "containment"}
    gt_pairs = set(expected)
    precision, recall, f1 = compute_metrics(pred_pairs, gt_pairs)
    results.append(
        TestResult(
            name="Substring Containment",
            passed=f1 >= 0.8,
            message=f"P={precision:.3f} R={recall:.3f} F1={f1:.3f}"
            if f1 >= 0.8
            else f"F1={f1:.3f} < 0.8 required",
            precision=precision,
            recall=recall,
            f1=f1,
        )
    )

    # Test no false positives
    docs, expected = get_no_duplicate_cases()
    duplicates = detector.find_duplicates(docs, threshold=0.9)
    pred_pairs = {(d[0], d[1]) for d in duplicates}
    results.append(
        TestResult(
            name="No False Positives",
            passed=len(pred_pairs) == 0,
            message="No false positives"
            if len(pred_pairs) == 0
            else f"Found {len(pred_pairs)} false positive pairs",
            details={"false_positives": list(pred_pairs)},
        )
    )

    return results


def run_minhash_property_tests(detector: DuplicateDetector) -> list[TestResult]:
    """Test MinHash algorithm properties."""
    results = []

    # Test: MinHash is deterministic
    text = "The quick brown fox"
    ngrams = detector.get_ngrams(text)
    sig1 = detector.minhash_signature(ngrams)
    sig2 = detector.minhash_signature(ngrams)
    results.append(
        TestResult(
            name="MinHash Determinism",
            passed=np.array_equal(sig1, sig2),
            message="MinHash is deterministic",
        )
    )

    # Test: Identical texts have similarity 1.0
    ngrams1 = detector.get_ngrams("Hello world")
    ngrams2 = detector.get_ngrams("Hello world")
    sig1 = detector.minhash_signature(ngrams1)
    sig2 = detector.minhash_signature(ngrams2)
    sim = detector.minhash_similarity(sig1, sig2)
    results.append(
        TestResult(
            name="Identical Text Similarity",
            passed=sim == 1.0,
            message=f"Similarity = {sim}",
        )
    )

    # Test: Completely different texts have low similarity
    ngrams1 = detector.get_ngrams("The quick brown fox jumps over the lazy dog")
    ngrams2 = detector.get_ngrams("Pack my box with five dozen liquor jugs")
    sig1 = detector.minhash_signature(ngrams1)
    sig2 = detector.minhash_signature(ngrams2)
    sim = detector.minhash_similarity(sig1, sig2)
    results.append(
        TestResult(
            name="Different Text Low Similarity",
            passed=sim < 0.5,
            message=f"Similarity = {sim:.3f} (expected < 0.5)",
        )
    )

    # Test: Empty input handling
    ngrams = detector.get_ngrams("")
    detector.minhash_signature(ngrams)
    results.append(
        TestResult(
            name="Empty Input Handling",
            passed=True,  # Should not crash
            message="Signature computed for empty input",
        )
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="Test duplicate detection")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== Duplicate Detection Falsification Tests ===\n")

    detector = DuplicateDetector()

    # Run dedup tests
    print("Duplicate Detection Tests:")
    dedup_results = run_dedup_tests(detector)
    for result in dedup_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")

    # Run MinHash property tests
    print("\nMinHash Property Tests:")
    minhash_results = run_minhash_property_tests(detector)
    for result in minhash_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")

    # Summary
    all_results = dedup_results + minhash_results
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results if requested
    if args.output:
        output_data = {
            "dedup_tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "precision": r.precision,
                    "recall": r.recall,
                    "f1": r.f1,
                }
                for r in dedup_results
            ],
            "minhash_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in minhash_results
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
