# Lilac Data Quality Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification
**Purpose:** Validate Lilac's data curation signals against ground truth

---

## 1. Overview

Lilac provides automated data quality signals for LLM training data curation:
- PII Detection
- Near-Duplicate Detection
- Language Identification
- Text Quality Metrics
- Semantic Clustering

This oracle validates these signals against manually curated ground truth.

---

## 2. Signal Categories

### 2.1 PII Detection

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| PII-001 | Email detection | Regex + ML | F1 > 0.95 |
| PII-002 | Phone number detection | Regex + format | F1 > 0.90 |
| PII-003 | SSN detection | 9-digit pattern | F1 > 0.98 |
| PII-004 | Credit card detection | Luhn + pattern | F1 > 0.95 |
| PII-005 | IP address detection | IPv4/IPv6 | F1 > 0.98 |
| PII-006 | Name detection (NER) | SpaCy/HF NER | F1 > 0.85 |
| PII-007 | Address detection | Multi-line | F1 > 0.80 |
| PII-008 | Date of birth | Multiple formats | F1 > 0.90 |
| PII-009 | Passport/ID numbers | Country-specific | F1 > 0.85 |
| PII-010 | API keys/secrets | Pattern matching | F1 > 0.90 |

### 2.2 Near-Duplicate Detection

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| DUP-001 | Exact duplicates | Hash match | Precision 1.0 |
| DUP-002 | Near-duplicates (>90% similar) | MinHash/SimHash | F1 > 0.90 |
| DUP-003 | Substring duplicates | Containment | F1 > 0.85 |
| DUP-004 | Semantic duplicates | Embedding distance | F1 > 0.80 |
| DUP-005 | Templated content | Pattern detection | F1 > 0.85 |
| DUP-006 | Boilerplate detection | Common prefix/suffix | F1 > 0.90 |

### 2.3 Language Identification

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| LI-001 | Single language detection | ISO 639-1 code | Acc > 0.98 |
| LI-002 | Multi-language detection | All languages present | F1 > 0.90 |
| LI-003 | Code detection | Programming languages | F1 > 0.95 |
| LI-004 | Mixed content | Code + natural language | F1 > 0.85 |
| LI-005 | Short text classification | <50 chars | Acc > 0.90 |
| LI-006 | Confidence calibration | P(correct) matches | ECE < 0.05 |

### 2.4 Text Quality Metrics

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| TQ-001 | Perplexity scoring | Relative ranking | Spearman > 0.90 |
| TQ-002 | Readability (Flesch-Kincaid) | Score calculation | Exact |
| TQ-003 | Toxicity detection | HateBERT/Perspective | F1 > 0.85 |
| TQ-004 | Coherence scoring | Sentence flow | Spearman > 0.80 |
| TQ-005 | Factuality markers | Hedging language | F1 > 0.80 |
| TQ-006 | Repetition detection | N-gram patterns | Exact |

### 2.5 Clustering & Conceptual Search

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| CL-001 | Cluster purity | Known categories | Purity > 0.85 |
| CL-002 | Cluster completeness | Same category together | Completeness > 0.85 |
| CL-003 | Cluster count | Reasonable granularity | ±20% of expected |
| CL-004 | Semantic search recall | Top-10 results | Recall > 0.90 |
| CL-005 | Concept learning | Few-shot examples | F1 > 0.80 |

---

## 3. Golden Corpus Structure

```
lilac/
├── oracle/
│   ├── pii/
│   │   ├── emails/
│   │   │   ├── positive.jsonl     # Known PII
│   │   │   ├── negative.jsonl     # Clean text
│   │   │   └── manifest.json
│   │   ├── phones/
│   │   ├── ssn/
│   │   ├── credit_cards/
│   │   └── names/
│   ├── dedup/
│   │   ├── exact/
│   │   ├── near/
│   │   └── semantic/
│   ├── language/
│   │   ├── monolingual/
│   │   ├── multilingual/
│   │   └── code/
│   ├── quality/
│   │   ├── toxic/
│   │   ├── coherent/
│   │   └── repetitive/
│   └── clustering/
│       ├── known_categories/
│       └── semantic_search/
├── specs/
│   └── data-quality-oracle.md
└── scripts/
    ├── generate_pii_corpus.py
    ├── validate_lilac.py
    └── compute_metrics.py
```

### Ground Truth Format

```json
{
  "id": "pii-email-001",
  "text": "Contact me at john.doe@example.com for details",
  "annotations": [
    {
      "type": "email",
      "start": 14,
      "end": 34,
      "value": "john.doe@example.com",
      "confidence": 1.0
    }
  ],
  "metadata": {
    "source": "synthetic",
    "annotator": "expert",
    "difficulty": "easy"
  }
}
```

---

## 4. Test Execution

### 4.1 PII Validation

```python
import lilac as ll
from lilac.signals import pii

# Load ground truth
with open('oracle/pii/emails/positive.jsonl') as f:
    ground_truth = [json.loads(line) for line in f]

# Run Lilac PII detector
ds = ll.Dataset('test_pii')
ds.compute_signal(pii.PIISignal())

# Compare predictions to ground truth
results = validate_predictions(ds, ground_truth)
assert results['f1'] > 0.95, f"Email F1: {results['f1']}"
```

### 4.2 Dedup Validation

```python
import lilac as ll
from lilac.signals import near_dup

# Known duplicate pairs
known_dups = load_duplicate_pairs('oracle/dedup/near/')

# Run Lilac near-dup detection
ds = ll.Dataset('test_dedup')
ds.compute_signal(near_dup.NearDuplicateSignal())

# Validate detection
precision, recall = compute_dup_metrics(ds, known_dups)
assert precision > 0.95, f"Precision: {precision}"
assert recall > 0.90, f"Recall: {recall}"
```

### 4.3 Language ID Validation

```python
import lilac as ll
from lilac.signals import lang_id

# Load labeled corpus
corpus = load_language_corpus('oracle/language/')

# Run Lilac language detection
ds = ll.Dataset('test_lang')
ds.compute_signal(lang_id.LanguageSignal())

# Compute accuracy
accuracy = compute_accuracy(ds, corpus)
assert accuracy > 0.98, f"Accuracy: {accuracy}"
```

---

## 5. Falsification Checklist

### 5.1 PII Detection
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| PII-001 | Email F1 score | > 0.95 | | |
| PII-002 | Phone F1 score | > 0.90 | | |
| PII-003 | SSN F1 score | > 0.98 | | |
| PII-004 | Credit card F1 | > 0.95 | | |
| PII-005 | IP address F1 | > 0.98 | | |
| PII-006 | Name NER F1 | > 0.85 | | |
| PII-007 | Address F1 | > 0.80 | | |
| PII-008 | DOB F1 | > 0.90 | | |
| PII-009 | ID numbers F1 | > 0.85 | | |
| PII-010 | API keys F1 | > 0.90 | | |

### 5.2 Near-Duplicate Detection
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DUP-001 | Exact dup precision | 1.0 | | |
| DUP-002 | Near-dup F1 | > 0.90 | | |
| DUP-003 | Substring F1 | > 0.85 | | |
| DUP-004 | Semantic dup F1 | > 0.80 | | |
| DUP-005 | Template F1 | > 0.85 | | |
| DUP-006 | Boilerplate F1 | > 0.90 | | |

### 5.3 Language ID
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| LI-001 | Single lang accuracy | > 0.98 | | |
| LI-002 | Multi-lang F1 | > 0.90 | | |
| LI-003 | Code detection F1 | > 0.95 | | |
| LI-004 | Mixed content F1 | > 0.85 | | |
| LI-005 | Short text accuracy | > 0.90 | | |
| LI-006 | Calibration ECE | < 0.05 | | |

### 5.4 Text Quality
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| TQ-001 | Perplexity Spearman | > 0.90 | | |
| TQ-002 | Flesch-Kincaid | Exact | | |
| TQ-003 | Toxicity F1 | > 0.85 | | |
| TQ-004 | Coherence Spearman | > 0.80 | | |
| TQ-005 | Factuality F1 | > 0.80 | | |
| TQ-006 | Repetition | Exact | | |

### 5.5 Clustering
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| CL-001 | Cluster purity | > 0.85 | | |
| CL-002 | Completeness | > 0.85 | | |
| CL-003 | Cluster count | ±20% | | |
| CL-004 | Search recall@10 | > 0.90 | | |
| CL-005 | Concept F1 | > 0.80 | | |

---

## 6. Edge Cases

### 6.1 PII Edge Cases
- Obfuscated emails: `john[dot]doe[at]example[dot]com`
- International phone formats: +44, +81, +91
- Fictional SSNs in examples: 000-00-0000
- Partial PII: truncated emails, masked cards

### 6.2 Dedup Edge Cases
- Whitespace variations
- Unicode normalization differences
- Case sensitivity
- Punctuation differences
- Translated duplicates

### 6.3 Language Edge Cases
- Transliterated text (Romanized Japanese, Pinyin)
- Code-switching within sentences
- Technical jargon (SQL, regex)
- Very short strings (<10 chars)

---

## 7. Benchmark Datasets

Reference datasets for validation:

| Dataset | Purpose | Size | Source |
|---------|---------|------|--------|
| PII-Benchmark | PII detection | 10K samples | Synthetic |
| DedupBench | Near-duplicate | 100K pairs | Crawl data |
| UDHR | Language ID | 500 languages | UN |
| ToxiGen | Toxicity | 274K samples | Academic |
| 20 Newsgroups | Clustering | 20K docs | UCI |

---

## References

- Databricks Lilac: https://github.com/databricks/lilac
- Presidio PII Detection: https://microsoft.github.io/presidio/
- MinHash LSH: Broder (1997)
- FastText Language ID: Joulin et al. (2016)
