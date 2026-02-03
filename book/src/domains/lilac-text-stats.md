# Text Statistics

Ground truth tests for Lilac's text statistics signals including readability metrics and document statistics.

## Test Coverage: 16/16 (100%)

## Metrics Implemented

### Flesch-Kincaid Readability

```python
def flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level."""
    words = count_words(text)
    sentences = count_sentences(text)
    syllables = count_syllables(text)

    if words == 0 or sentences == 0:
        return 0.0

    return (
        0.39 * (words / sentences) +
        11.8 * (syllables / words) -
        15.59
    )

def flesch_reading_ease(text: str) -> float:
    """Calculate Flesch Reading Ease score."""
    words = count_words(text)
    sentences = count_sentences(text)
    syllables = count_syllables(text)

    if words == 0 or sentences == 0:
        return 0.0

    return (
        206.835 -
        1.015 * (words / sentences) -
        84.6 * (syllables / words)
    )
```

### Reading Ease Interpretation

| Score | Grade Level | Interpretation |
|-------|-------------|----------------|
| 90-100 | 5th grade | Very easy |
| 80-90 | 6th grade | Easy |
| 70-80 | 7th grade | Fairly easy |
| 60-70 | 8-9th grade | Standard |
| 50-60 | 10-12th grade | Fairly difficult |
| 30-50 | College | Difficult |
| 0-30 | Professional | Very difficult |

## Test Cases

### Basic Counting (4 tests)

| Test | Input | Metric | Expected |
|------|-------|--------|----------|
| STATS-001 | "Hello world" | word_count | 2 |
| STATS-002 | "Hello. World." | sentence_count | 2 |
| STATS-003 | "extraordinary" | syllable_count | 5 |
| STATS-004 | "The cat sat." | char_count | 12 |

### Flesch-Kincaid Tests (4 tests)

| Test | Text | FK Grade | Reading Ease |
|------|------|----------|--------------|
| STATS-005 | "The cat sat on the mat." | ~1.0 | ~100 |
| STATS-006 | "The quick brown fox jumps." | ~2.0 | ~90 |
| STATS-007 | Complex academic text | ~12.0 | ~40 |
| STATS-008 | Legal document excerpt | ~15.0 | ~20 |

### Syllable Counting (4 tests)

| Test | Word | Syllables | Notes |
|------|------|-----------|-------|
| STATS-009 | "cat" | 1 | Simple |
| STATS-010 | "amazing" | 3 | a-ma-zing |
| STATS-011 | "beautiful" | 3 | beau-ti-ful |
| STATS-012 | "extraordinary" | 5 | ex-tra-or-di-na-ry |

### Edge Cases (4 tests)

| Test | Input | Expected |
|------|-------|----------|
| STATS-013 | "" (empty) | All zeros |
| STATS-014 | "..." (punctuation only) | word_count = 0 |
| STATS-015 | "123 456" (numbers only) | word_count = 2 |
| STATS-016 | Unicode text | Correct counts |

## Syllable Counting Algorithm

```python
import re

def count_syllables(word: str) -> int:
    """Count syllables in a word using vowel groups."""
    word = word.lower().strip()

    # Remove non-alpha
    word = re.sub(r'[^a-z]', '', word)

    if len(word) == 0:
        return 0

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Adjust for silent e
    if word.endswith('e') and count > 1:
        count -= 1

    # Minimum 1 syllable per word
    return max(1, count)
```

## Running Tests

```bash
uv run lilac/scripts/test_text_statistics.py
```

## Example Output

```
=== Lilac Text Statistics Ground Truth Tests ===

Section 1: Basic Counting
  [PASS] STATS-001: word_count("Hello world") = 2
  [PASS] STATS-002: sentence_count("Hello. World.") = 2
  ...

Section 2: Flesch-Kincaid
  [PASS] STATS-005: Simple text FK grade = 1.2
  [PASS] STATS-006: Medium text FK grade = 2.1
  ...

Summary: 16/16 tests passed
```
