# Language Detection

Ground truth tests for Lilac's language detection signal using the `langdetect` library.

## Test Coverage: 9/10 (90%)

One edge case (very short text) has known detection limitations.

## Algorithm

Language detection uses n-gram frequency profiles compared against known language models:

```python
from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException

def detect_language(text: str) -> str | None:
    """Detect language of text."""
    try:
        return detect(text)
    except LangDetectException:
        return None

def detect_language_with_confidence(text: str) -> list[tuple[str, float]]:
    """Detect language with confidence scores."""
    try:
        results = detect_langs(text)
        return [(r.lang, r.prob) for r in results]
    except LangDetectException:
        return []
```

## Test Cases

### Unambiguous Detection (6 tests)

| Test | Text | Expected | Notes |
|------|------|----------|-------|
| LANG-001 | "Hello, how are you today?" | `en` | English |
| LANG-002 | "Bonjour, comment allez-vous?" | `fr` | French |
| LANG-003 | "Hola, cómo estás?" | `es` | Spanish |
| LANG-004 | "Guten Tag, wie geht es Ihnen?" | `de` | German |
| LANG-005 | "Ciao, come stai?" | `it` | Italian |
| LANG-006 | "Olá, como você está?" | `pt` | Portuguese |

### Mixed/Ambiguous Content (2 tests)

| Test | Text | Expected | Notes |
|------|------|----------|-------|
| LANG-007 | "Hello monde" | `en` or `fr` | Mixed English/French |
| LANG-008 | "JavaScript Python code" | `en` | Technical terms |

### Edge Cases (2 tests)

| Test | Text | Expected | Notes |
|------|------|----------|-------|
| LANG-009 | "12345 67890" | None/Unknown | Numbers only |
| LANG-010 | "Hi" | Unreliable | Too short |

## Confidence Thresholds

```python
CONFIDENCE_THRESHOLDS = {
    "high": 0.90,      # Very confident detection
    "medium": 0.70,    # Reasonably confident
    "low": 0.50,       # Uncertain, multiple possibilities
}

def is_confident_detection(text: str, min_confidence: float = 0.70) -> bool:
    """Check if language detection is confident."""
    results = detect_language_with_confidence(text)
    if not results:
        return False
    return results[0][1] >= min_confidence
```

## Running Tests

```bash
uv run lilac/scripts/test_language_detection.py
```

## Example Output

```
=== Lilac Language Detection Ground Truth Tests ===

Section 1: Unambiguous Languages
  [PASS] LANG-001: English detected correctly (confidence: 0.99)
  [PASS] LANG-002: French detected correctly (confidence: 0.99)
  [PASS] LANG-003: Spanish detected correctly (confidence: 0.99)
  ...

Section 2: Mixed/Ambiguous Content
  [PASS] LANG-007: Mixed content detected as en or fr
  [PASS] LANG-008: Technical text detected as en

Section 3: Edge Cases
  [PASS] LANG-009: Numbers-only returns None
  [SKIP] LANG-010: Short text detection unreliable

Summary: 9/10 tests passed (1 skipped - known limitation)
```

## Known Limitations

1. **Short text**: Less than 20 characters produces unreliable results
2. **Mixed languages**: May detect dominant language only
3. **Similar languages**: e.g., Norwegian/Danish/Swedish confusion
4. **Technical content**: Code/math may skew detection
5. **Transliteration**: Romanized text may misdetect
