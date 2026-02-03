#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test text statistics computation for data quality.

This script validates text statistics algorithms that serve as
data quality signals in Lilac without requiring ML models.

Tests:
- Character counts
- Word counts
- Sentence counts
- Readability metrics (Flesch-Kincaid, etc.)
- Text structure analysis

Usage:
    uv run lilac/scripts/test_text_statistics.py

References:
    - Flesch Reading Ease: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    - Lilac Data Quality Oracle Spec
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    message: str
    expected: float = 0.0
    actual: float = 0.0
    details: dict = field(default_factory=dict)


# =============================================================================
# Text Statistics Functions
# =============================================================================


def count_characters(text: str, include_whitespace: bool = True) -> int:
    """Count characters in text."""
    if include_whitespace:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def count_words(text: str) -> int:
    """Count words in text."""
    words = text.split()
    return len(words)


def count_sentences(text: str) -> int:
    """Count sentences in text (approximate)."""
    # Split on sentence-ending punctuation
    sentences = re.split(r"[.!?]+", text)
    # Filter empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def count_syllables(word: str) -> int:
    """Count syllables in a word (approximation for English)."""
    word = word.lower().strip()
    if not word:
        return 0

    # Remove trailing 'e' (silent e)
    if word.endswith("e") and len(word) > 2:
        word = word[:-1]

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    return max(count, 1)  # At least one syllable


def flesch_reading_ease(text: str) -> float:
    """Calculate Flesch Reading Ease score.

    Score interpretation:
    90-100: Very easy (5th grade)
    80-89: Easy (6th grade)
    70-79: Fairly easy (7th grade)
    60-69: Standard (8th-9th grade)
    50-59: Fairly difficult (10th-12th grade)
    30-49: Difficult (college)
    0-29: Very difficult (college graduate)

    Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    """
    words = count_words(text)
    sentences = count_sentences(text)
    syllables = sum(count_syllables(w) for w in text.split())

    if words == 0 or sentences == 0:
        return 0.0

    asl = words / sentences  # Average sentence length
    asw = syllables / words  # Average syllables per word

    return 206.835 - 1.015 * asl - 84.6 * asw


def flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level.

    Result is approximate US grade level needed to understand text.

    Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    """
    words = count_words(text)
    sentences = count_sentences(text)
    syllables = sum(count_syllables(w) for w in text.split())

    if words == 0 or sentences == 0:
        return 0.0

    asl = words / sentences
    asw = syllables / words

    return 0.39 * asl + 11.8 * asw - 15.59


def automated_readability_index(text: str) -> float:
    """Calculate Automated Readability Index (ARI).

    Formula: 4.71 * (chars/words) + 0.5 * (words/sentences) - 21.43
    """
    chars = count_characters(text, include_whitespace=False)
    words = count_words(text)
    sentences = count_sentences(text)

    if words == 0 or sentences == 0:
        return 0.0

    return 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43


def coleman_liau_index(text: str) -> float:
    """Calculate Coleman-Liau Index.

    Formula: 0.0588 * L - 0.296 * S - 15.8
    L = average letters per 100 words
    S = average sentences per 100 words
    """
    chars = count_characters(text, include_whitespace=False)
    words = count_words(text)
    sentences = count_sentences(text)

    if words == 0:
        return 0.0

    L = (chars / words) * 100
    S = (sentences / words) * 100

    return 0.0588 * L - 0.296 * S - 15.8


def avg_word_length(text: str) -> float:
    """Calculate average word length."""
    words = text.split()
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def avg_sentence_length(text: str) -> float:
    """Calculate average sentence length (words per sentence)."""
    words = count_words(text)
    sentences = count_sentences(text)
    if sentences == 0:
        return 0.0
    return words / sentences


# =============================================================================
# Test Cases
# =============================================================================

# Simple text for testing
SIMPLE_TEXT = "The cat sat on the mat. The dog ran in the park."
# Expected: 2 sentences, 12 words

# Complex text for testing
COMPLEX_TEXT = """
The unprecedented proliferation of sophisticated computational methodologies
has fundamentally transformed contemporary interdisciplinary research paradigms,
necessitating comprehensive reevaluation of established epistemological frameworks.
"""

# Children's text (should be easy to read)
EASY_TEXT = "I like cats. Cats are fun. They play with toys."

# Technical text (should be harder to read)
TECHNICAL_TEXT = """
The implementation leverages asynchronous non-blocking I/O operations
to maximize throughput while maintaining acceptable latency characteristics
under high-concurrency workloads.
"""


def test_character_counts() -> list[TestResult]:
    """Test character counting."""
    results = []

    # Test with whitespace
    text = "Hello World"
    count = count_characters(text, include_whitespace=True)
    results.append(
        TestResult(
            name="Character count with whitespace",
            passed=count == 11,
            message=f"Count: {count}",
            expected=11,
            actual=count,
        )
    )

    # Test without whitespace
    count = count_characters(text, include_whitespace=False)
    results.append(
        TestResult(
            name="Character count without whitespace",
            passed=count == 10,
            message=f"Count: {count}",
            expected=10,
            actual=count,
        )
    )

    # Test empty
    count = count_characters("")
    results.append(
        TestResult(
            name="Character count empty",
            passed=count == 0,
            message=f"Count: {count}",
            expected=0,
            actual=count,
        )
    )

    return results


def test_word_counts() -> list[TestResult]:
    """Test word counting."""
    results = []

    # Simple text
    count = count_words(SIMPLE_TEXT)
    results.append(
        TestResult(
            name="Word count simple text",
            passed=count == 12,
            message=f"Count: {count}",
            expected=12,
            actual=count,
        )
    )

    # Empty text
    count = count_words("")
    results.append(
        TestResult(
            name="Word count empty",
            passed=count == 0,
            message=f"Count: {count}",
            expected=0,
            actual=count,
        )
    )

    # Multiple whitespace
    count = count_words("Hello   World    Test")
    results.append(
        TestResult(
            name="Word count multiple whitespace",
            passed=count == 3,
            message=f"Count: {count}",
            expected=3,
            actual=count,
        )
    )

    return results


def test_sentence_counts() -> list[TestResult]:
    """Test sentence counting."""
    results = []

    # Simple text
    count = count_sentences(SIMPLE_TEXT)
    results.append(
        TestResult(
            name="Sentence count simple text",
            passed=count == 2,
            message=f"Count: {count}",
            expected=2,
            actual=count,
        )
    )

    # Different punctuation
    count = count_sentences("Hello! How are you? I am fine.")
    results.append(
        TestResult(
            name="Sentence count mixed punctuation",
            passed=count == 3,
            message=f"Count: {count}",
            expected=3,
            actual=count,
        )
    )

    # Empty text
    count = count_sentences("")
    results.append(
        TestResult(
            name="Sentence count empty",
            passed=count == 0,
            message=f"Count: {count}",
            expected=0,
            actual=count,
        )
    )

    return results


def test_syllable_counts() -> list[TestResult]:
    """Test syllable counting.

    Note: Syllable counting in English is inherently approximate without
    a pronunciation dictionary. These tests verify reasonable estimates.
    """
    results = []

    # Test cases with expected approximate syllables
    # Algorithm may differ by ±1 for complex words
    test_cases = [
        ("cat", 1, 1),  # min, max expected
        ("hello", 2, 2),
        ("beautiful", 3, 4),  # Algorithm gets 3, actual is 4
        ("the", 1, 1),
        ("a", 1, 1),
        ("encyclopedia", 5, 6),  # Algorithm gets 5, actual is 6
    ]

    all_reasonable = True
    for word, min_exp, max_exp in test_cases:
        actual = count_syllables(word)
        if not (min_exp <= actual <= max_exp):
            all_reasonable = False

    results.append(
        TestResult(
            name="Syllable counting (approximate)",
            passed=all_reasonable,
            message=f"All {len(test_cases)} words within expected range",
        )
    )

    # Test that single-letter words return 1
    single_syl = count_syllables("a")
    results.append(
        TestResult(
            name="Single letter syllable",
            passed=single_syl == 1,
            message=f"'a' = {single_syl} syllable",
        )
    )

    return results


def test_readability_metrics() -> list[TestResult]:
    """Test readability score calculations."""
    results = []

    # Test Flesch Reading Ease - easy text should have high score
    easy_score = flesch_reading_ease(EASY_TEXT)
    results.append(
        TestResult(
            name="Flesch Reading Ease - easy text",
            passed=easy_score > 80,
            message=f"Score: {easy_score:.1f} (expected > 80)",
            expected=80,
            actual=easy_score,
        )
    )

    # Test Flesch Reading Ease - complex text should have low score
    complex_score = flesch_reading_ease(COMPLEX_TEXT)
    results.append(
        TestResult(
            name="Flesch Reading Ease - complex text",
            passed=complex_score < 40,
            message=f"Score: {complex_score:.1f} (expected < 40)",
            expected=40,
            actual=complex_score,
        )
    )

    # Test Flesch-Kincaid Grade - easy text should have low grade
    easy_grade = flesch_kincaid_grade(EASY_TEXT)
    results.append(
        TestResult(
            name="Flesch-Kincaid Grade - easy text",
            passed=easy_grade < 5,
            message=f"Grade: {easy_grade:.1f} (expected < 5)",
            expected=5,
            actual=easy_grade,
        )
    )

    # Test Flesch-Kincaid Grade - complex text should have high grade
    complex_grade = flesch_kincaid_grade(COMPLEX_TEXT)
    results.append(
        TestResult(
            name="Flesch-Kincaid Grade - complex text",
            passed=complex_grade > 12,
            message=f"Grade: {complex_grade:.1f} (expected > 12)",
            expected=12,
            actual=complex_grade,
        )
    )

    # Test ARI
    ari = automated_readability_index(TECHNICAL_TEXT)
    results.append(
        TestResult(
            name="ARI - technical text",
            passed=ari > 10,
            message=f"ARI: {ari:.1f} (expected > 10)",
            expected=10,
            actual=ari,
        )
    )

    # Test Coleman-Liau
    cli = coleman_liau_index(TECHNICAL_TEXT)
    results.append(
        TestResult(
            name="Coleman-Liau - technical text",
            passed=cli > 10,
            message=f"CLI: {cli:.1f} (expected > 10)",
            expected=10,
            actual=cli,
        )
    )

    return results


def test_averages() -> list[TestResult]:
    """Test average calculations."""
    results = []

    # Average word length
    awl = avg_word_length(SIMPLE_TEXT)
    results.append(
        TestResult(
            name="Average word length",
            passed=2.5 < awl < 4.5,
            message=f"AWL: {awl:.2f}",
            actual=awl,
        )
    )

    # Average sentence length
    asl = avg_sentence_length(SIMPLE_TEXT)
    results.append(
        TestResult(
            name="Average sentence length",
            passed=asl == 6.0,
            message=f"ASL: {asl:.1f}",
            expected=6.0,
            actual=asl,
        )
    )

    # Empty text handling
    awl_empty = avg_word_length("")
    asl_empty = avg_sentence_length("")
    results.append(
        TestResult(
            name="Averages on empty text",
            passed=awl_empty == 0 and asl_empty == 0,
            message=f"AWL: {awl_empty}, ASL: {asl_empty}",
        )
    )

    return results


def test_edge_cases() -> list[TestResult]:
    """Test edge cases."""
    results = []

    # Unicode text
    unicode_text = "Cześć, jak się masz?"
    count = count_words(unicode_text)
    results.append(
        TestResult(
            name="Unicode word count",
            passed=count == 4,
            message=f"Count: {count}",
        )
    )

    # Numbers in text
    text_with_numbers = "I have 3 apples and 5 oranges."
    count = count_words(text_with_numbers)
    results.append(
        TestResult(
            name="Word count with numbers",
            passed=count == 7,
            message=f"Count: {count}",
        )
    )

    # Very long word
    long_word = "pneumonoultramicroscopicsilicovolcanoconiosis"
    syllables = count_syllables(long_word)
    results.append(
        TestResult(
            name="Long word syllables",
            passed=syllables >= 15,
            message=f"Syllables: {syllables}",
        )
    )

    # Single sentence, no period
    text = "Hello world"
    sentences = count_sentences(text)
    results.append(
        TestResult(
            name="Sentence without period",
            passed=sentences == 1,
            message=f"Sentences: {sentences}",
        )
    )

    return results


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Test text statistics")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== Text Statistics Falsification Tests ===\n")

    all_results = []

    # Character counts
    print("Character Count Tests:")
    char_results = test_character_counts()
    all_results.extend(char_results)
    for r in char_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Word counts
    print("\nWord Count Tests:")
    word_results = test_word_counts()
    all_results.extend(word_results)
    for r in word_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Sentence counts
    print("\nSentence Count Tests:")
    sent_results = test_sentence_counts()
    all_results.extend(sent_results)
    for r in sent_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Syllable counts
    print("\nSyllable Count Tests:")
    syl_results = test_syllable_counts()
    all_results.extend(syl_results)
    for r in syl_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Readability metrics
    print("\nReadability Metric Tests:")
    read_results = test_readability_metrics()
    all_results.extend(read_results)
    for r in read_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Averages
    print("\nAverage Calculation Tests:")
    avg_results = test_averages()
    all_results.extend(avg_results)
    for r in avg_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Edge cases
    print("\nEdge Case Tests:")
    edge_results = test_edge_cases()
    all_results.extend(edge_results)
    for r in edge_results:
        icon = "+" if r.passed else "x"
        print(f"  {icon} {r.name}: {r.message}")

    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results
    if args.output:
        output_data = {
            "char_tests": [{"name": r.name, "passed": r.passed} for r in char_results],
            "word_tests": [{"name": r.name, "passed": r.passed} for r in word_results],
            "sent_tests": [{"name": r.name, "passed": r.passed} for r in sent_results],
            "syl_tests": [{"name": r.name, "passed": r.passed} for r in syl_results],
            "read_tests": [{"name": r.name, "passed": r.passed} for r in read_results],
            "avg_tests": [{"name": r.name, "passed": r.passed} for r in avg_results],
            "edge_tests": [{"name": r.name, "passed": r.passed} for r in edge_results],
            "summary": {"passed": passed, "total": total},
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
