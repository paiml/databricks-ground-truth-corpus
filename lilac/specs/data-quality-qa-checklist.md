# Lilac Data Quality - Falsification QA Checklist

**Date:** 2026-02-03
**Methodology:** Popperian Falsification (attempt to break, not verify)
**Philosophy:** "The wrong view of science betrays itself in the craving to be right"

---

## 1. PII Detection Tests

### 1.1 PII Type Detection
| ID | PII Type | Min F1 | Actual F1 | Pass |
|----|----------|--------|-----------|------|
| PII-001 | Email | 0.95 | 1.000 | ✓ |
| PII-002 | Phone (US) | 0.90 | 1.000 | ✓ |
| PII-003 | SSN | 0.98 | 1.000 | ✓ |
| PII-004 | Credit Card | 0.95 | 1.000 | ✓ |
| PII-005 | IP Address | 0.98 | 1.000 | ✓ |
| PII-006 | API Keys | 0.90 | 1.000 | ✓ |

### 1.2 Edge Cases
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| EC-001 | Obfuscated email (negative) | No match | No match | ✓ |
| EC-002 | Empty input | No crash | Handles OK | ✓ |
| EC-003 | Unicode in email | Graceful | 0 matches | ✓ |
| EC-004 | Multiple PII types | All detected | All found | ✓ |

---

## 2. Duplicate Detection Tests

### 2.1 Duplicate Types
| ID | Type | Min F1 | Actual | Pass |
|----|------|--------|--------|------|
| DUP-001 | Exact duplicates | 1.00 (P) | P=1.00 | ✓ |
| DUP-002 | Near-duplicates | 0.80 | F1=0.80 | ✓ |
| DUP-003 | Substring containment | 0.80 | F1=1.00 | ✓ |
| DUP-004 | No false positives | 0 FP | 0 FP | ✓ |

### 2.2 MinHash Properties
| ID | Property | Expected | Actual | Pass |
|----|----------|----------|--------|------|
| MH-001 | Determinism | Same output | Identical | ✓ |
| MH-002 | Identical similarity | 1.0 | 1.0 | ✓ |
| MH-003 | Different text low sim | < 0.5 | 0.055 | ✓ |
| MH-004 | Empty input handling | No crash | OK | ✓ |

---

## 3. Language Detection Tests

### 3.1 Natural Language Detection
| ID | Test | Min Accuracy | Actual | Pass |
|----|------|--------------|--------|------|
| LANG-001 | English Detection | 0.95 | 1.000 | ✓ |
| LANG-002 | Multilingual Detection | 0.80 | 0.875 | ✓ |
| LANG-003 | Code Detection | 0.90 | 1.000 | ✓ |
| LANG-004 | Short Text Detection | 0.50 | 0.000 | ✗* |

*Known limitation: langdetect struggles with very short text (<5 words)

### 3.2 Edge Cases
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| LEC-001 | Empty Input | "unknown" | "unknown" | ✓ |
| LEC-002 | Numbers Only | No crash | OK | ✓ |
| LEC-003 | Mixed Natural/Code | Reasonable | Detected | ✓ |
| LEC-004 | Unicode with Emoji | No crash | OK | ✓ |

### 3.3 Confidence Calibration
| ID | Test | Expected | Actual | Pass |
|----|------|----------|--------|------|
| CC-001 | High Confidence Clear Text | >= 0.9 | 0.99+ | ✓ |
| CC-002 | Lower Confidence Ambiguous | Reported | Reported | ✓ |

---

## 4. Execution Log

```
Date: 2026-02-03
Executor: Claude Code
Commands:
  uv run lilac/scripts/test_pii_detection.py
  uv run lilac/scripts/test_dedup_detection.py
  uv run lilac/scripts/test_language_detection.py
```

### Results Summary

| Category | Total | Passed | Failed |
|----------|-------|--------|--------|
| PII Detection | 10 | 10 | 0 |
| Dedup Detection | 8 | 8 | 0 |
| Language Detection | 10 | 9 | 1* |
| **TOTAL** | **28** | **27** | **1** |

*Short text detection failure is a known limitation of langdetect

---

## 5. Algorithms Validated

### 5.1 PII Detection Patterns
- **Email**: RFC 5322 simplified regex
- **Phone**: US formats (+1, parens, dashes)
- **SSN**: 9-digit with validation (excludes 9xx, 666, 000)
- **Credit Card**: Major brands + Luhn checksum
- **IP**: IPv4 (full validation), IPv6 (simplified)
- **API Keys**: OpenAI, AWS, GitHub, Slack patterns

### 5.2 Duplicate Detection
- **Exact**: SHA-256 hash comparison
- **Near**: MinHash signatures + Jaccard similarity
- **Containment**: Substring matching (min 10 chars)

### 5.3 Language Detection
- **Natural Language**: langdetect library (n-gram based)
- **Code Detection**: Keyword pattern matching (Python, JS, Java, Rust, SQL, HTML)
- **Confidence**: Probability scores from detector

---

## 6. Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Obfuscated PII not detected | FN for `[at]`, `[dot]` | Could add pattern variants |
| Unicode emails not matched | FN for non-ASCII | Could use IDN-aware pattern |
| Short containment ignored | FN for <10 char | Configurable threshold |
| MinHash approximation | ~5% variance | Use exact Jaccard for verification |
| Short text lang detection | FN for <5 words | Use fasttext or character-level models |

---

## 7. Next Steps (Not Yet Implemented)

| Test | Status | Notes |
|------|--------|-------|
| Language ID | ✓ COMPLETE | 9/10 tests pass (short text is known limitation) |
| Clustering | PENDING | Need embeddings |
| Toxicity | PENDING | Need classifier model |
| Lilac integration | PENDING | Test actual Lilac library |

---

## Sign-off

- [x] 27/28 falsification tests pass (1 known limitation)
- [x] PII detection achieves required F1 scores
- [x] Duplicate detection handles all cases
- [x] Language detection validates core use cases
- [x] Known limitations documented

**Verdict: PARTIAL COMPLETE** - Reference implementations pass 27/28 tests. Short text language detection is a known limitation. Lilac library integration pending.
