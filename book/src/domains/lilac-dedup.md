# Deduplication Detection

Ground truth tests for Lilac's near-duplicate detection using MinHash/Jaccard similarity.

## Test Coverage: 8/9 (89%)

One test requires Lilac infrastructure and is skipped in standalone mode.

## MinHash Algorithm

MinHash provides efficient approximate Jaccard similarity:

```python
import hashlib
from typing import Set

def minhash_signature(text: str, num_hashes: int = 128) -> list[int]:
    """Generate MinHash signature for text."""
    shingles = _get_shingles(text, k=3)
    signature = []

    for i in range(num_hashes):
        min_hash = float('inf')
        for shingle in shingles:
            # Hash with seed
            h = int(hashlib.md5(f"{i}:{shingle}".encode()).hexdigest(), 16)
            min_hash = min(min_hash, h)
        signature.append(min_hash)

    return signature

def _get_shingles(text: str, k: int = 3) -> Set[str]:
    """Extract k-shingles (character n-grams) from text."""
    text = text.lower().strip()
    return {text[i:i+k] for i in range(len(text) - k + 1)}
```

## Jaccard Similarity

```python
def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0
```

## Test Cases

### Exact Duplicates (2 tests)

| Test | Text A | Text B | Expected |
|------|--------|--------|----------|
| DEDUP-001 | "Hello world" | "Hello world" | 1.0 |
| DEDUP-002 | "Test string" | "Test string" | 1.0 |

### Near Duplicates (3 tests)

| Test | Text A | Text B | Similarity |
|------|--------|--------|------------|
| DEDUP-003 | "The quick brown fox" | "The quick brown dog" | ~0.75 |
| DEDUP-004 | "Machine learning is great" | "Machine learning is amazing" | ~0.70 |
| DEDUP-005 | "Python programming" | "Python programming language" | ~0.80 |

### Non-Duplicates (3 tests)

| Test | Text A | Text B | Expected |
|------|--------|--------|----------|
| DEDUP-006 | "Hello world" | "Goodbye universe" | < 0.3 |
| DEDUP-007 | "Data science" | "Web development" | < 0.2 |
| DEDUP-008 | "Machine learning" | "Quantum physics" | < 0.2 |

## Similarity Thresholds

| Threshold | Interpretation |
|-----------|---------------|
| ≥ 0.95 | Exact duplicate (whitespace/punctuation diff) |
| ≥ 0.80 | Near duplicate (minor edits) |
| ≥ 0.50 | Related content |
| < 0.30 | Distinct documents |

## Running Tests

```bash
uv run lilac/scripts/test_dedup_detection.py
```

## Example Output

```
=== Lilac Deduplication Ground Truth Tests ===

Section 1: Exact Duplicate Detection
  [PASS] DEDUP-001: Exact match similarity = 1.0
  [PASS] DEDUP-002: Identical strings similarity = 1.0

Section 2: Near-Duplicate Detection
  [PASS] DEDUP-003: Similar sentences similarity = 0.76
  ...

Summary: 8/9 tests passed (1 skipped - requires infrastructure)
```

## Limitations

The standalone tests use a simplified MinHash implementation. Production Lilac uses:
- Larger signature sizes (256+)
- LSH (Locality Sensitive Hashing) for efficient search
- Configurable shingle sizes
- Unicode normalization
