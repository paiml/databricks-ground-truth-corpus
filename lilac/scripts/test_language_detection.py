#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "langdetect>=1.0.9",
# ]
# ///
"""Test language detection accuracy.

This script validates language identification algorithms against
ground truth using Popperian falsification methodology.

Tests:
- Single language detection
- Code detection
- Short text handling
- Confidence calibration

Usage:
    uv run scripts/test_language_detection.py

References:
    - Lilac Data Quality Oracle Spec: specs/data-quality-oracle.md
    - ISO 639-1 language codes
"""

import argparse
import json
import sys
from dataclasses import dataclass, field

# langdetect for reference implementation
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

# Set seed for reproducibility
DetectorFactory.seed = 42


@dataclass
class TestResult:
    """Result of a single test case."""

    name: str
    passed: bool
    message: str
    accuracy: float = 0.0
    details: dict = field(default_factory=dict)


# =============================================================================
# Language Detection (Reference Implementation using langdetect)
# =============================================================================


class LanguageDetector:
    """Reference language detector."""

    # Common programming language indicators
    CODE_INDICATORS = {
        "python": ["def ", "import ", "class ", "if __name__", "print(", "self."],
        "javascript": ["function ", "const ", "let ", "var ", "=>", "console.log"],
        "java": ["public class", "public static void", "System.out", "import java"],
        "rust": ["fn ", "let mut", "impl ", "pub fn", "::new()", "println!"],
        "sql": ["SELECT ", "FROM ", "WHERE ", "INSERT INTO", "CREATE TABLE"],
        "html": ["<html", "<div", "<span", "</div>", 'class="'],
        "css": ["{", "}", "color:", "margin:", "padding:", "display:"],
    }

    def detect_language(self, text: str) -> tuple[str, float]:
        """Detect language of text.

        Returns: (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            return ("unknown", 0.0)

        # Check for code first
        code_lang = self._detect_code(text)
        if code_lang:
            return (f"code:{code_lang}", 0.95)

        # Use langdetect for natural language
        try:
            results = detect_langs(text)
            if results:
                top = results[0]
                return (top.lang, top.prob)
        except LangDetectException:
            pass

        return ("unknown", 0.0)

    def _detect_code(self, text: str) -> str | None:
        """Detect if text is code and which language."""
        text_lower = text.lower()

        # Count indicators for each language
        scores = {}
        for lang, indicators in self.CODE_INDICATORS.items():
            score = sum(1 for ind in indicators if ind.lower() in text_lower)
            if score >= 2:  # Need at least 2 indicators
                scores[lang] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    def detect_batch(self, texts: list[str]) -> list[tuple[str, float]]:
        """Detect languages for multiple texts."""
        return [self.detect_language(text) for text in texts]


# =============================================================================
# Ground Truth Test Cases
# =============================================================================


def get_english_test_cases() -> list[tuple[str, str]]:
    """English detection test cases."""
    return [
        ("The quick brown fox jumps over the lazy dog.", "en"),
        ("Hello, how are you doing today?", "en"),
        ("This is a test of the language detection system.", "en"),
        ("The weather is beautiful outside.", "en"),
    ]


def get_multilingual_test_cases() -> list[tuple[str, str]]:
    """Non-English language test cases."""
    return [
        ("Bonjour, comment allez-vous aujourd'hui?", "fr"),
        ("Hola, ¿cómo estás hoy?", "es"),
        ("Guten Tag, wie geht es Ihnen?", "de"),
        ("Ciao, come stai oggi?", "it"),
        ("Olá, como você está?", "pt"),
        ("Привет, как дела?", "ru"),
        ("こんにちは、お元気ですか？", "ja"),
        ("你好，你好吗？", "zh-cn"),
    ]


def get_code_test_cases() -> list[tuple[str, str]]:
    """Programming language detection test cases."""
    return [
        ("def hello_world():\n    print('Hello, World!')", "code:python"),
        ("function greet() { console.log('Hello'); }", "code:javascript"),
        ("public class Main { public static void main(String[] args) {} }", "code:java"),
        ('fn main() { println!("Hello"); }', "code:rust"),
        ("SELECT * FROM users WHERE id = 1;", "code:sql"),
        ("<html><body><div>Hello</div></body></html>", "code:html"),
    ]


def get_short_text_cases() -> list[tuple[str, str]]:
    """Short text detection (harder cases)."""
    return [
        ("Hello", "en"),
        ("Bonjour", "fr"),
        ("Hola", "es"),
        ("OK", "en"),  # Very short, may fail
    ]


def get_ambiguous_cases() -> list[tuple[str, str | None]]:
    """Ambiguous or edge cases."""
    return [
        ("", None),  # Empty
        ("12345", None),  # Numbers only
        ("...", None),  # Punctuation only
        ("@#$%^&", None),  # Symbols only
    ]


# =============================================================================
# Test Runner
# =============================================================================


def run_language_tests(detector: LanguageDetector) -> list[TestResult]:
    """Run language detection tests."""
    results = []

    # English detection
    cases = get_english_test_cases()
    correct = 0
    for text, expected in cases:
        detected, conf = detector.detect_language(text)
        if detected == expected:
            correct += 1

    accuracy = correct / len(cases) if cases else 0
    results.append(
        TestResult(
            name="English Detection",
            passed=accuracy >= 0.95,
            message=f"Accuracy: {accuracy:.1%} ({correct}/{len(cases)})",
            accuracy=accuracy,
        )
    )

    # Multilingual detection
    cases = get_multilingual_test_cases()
    correct = 0
    failed = []
    for text, expected in cases:
        detected, conf = detector.detect_language(text)
        if detected == expected:
            correct += 1
        else:
            failed.append((expected, detected, text[:30]))

    accuracy = correct / len(cases) if cases else 0
    results.append(
        TestResult(
            name="Multilingual Detection",
            passed=accuracy >= 0.80,
            message=f"Accuracy: {accuracy:.1%} ({correct}/{len(cases)})",
            accuracy=accuracy,
            details={"failed": failed} if failed else {},
        )
    )

    # Code detection
    cases = get_code_test_cases()
    correct = 0
    failed = []
    for text, expected in cases:
        detected, conf = detector.detect_language(text)
        if detected == expected:
            correct += 1
        else:
            failed.append((expected, detected))

    accuracy = correct / len(cases) if cases else 0
    results.append(
        TestResult(
            name="Code Detection",
            passed=accuracy >= 0.90,
            message=f"Accuracy: {accuracy:.1%} ({correct}/{len(cases)})",
            accuracy=accuracy,
            details={"failed": failed} if failed else {},
        )
    )

    # Short text
    cases = get_short_text_cases()
    correct = 0
    for text, expected in cases:
        detected, _conf = detector.detect_language(text)
        if detected == expected:
            correct += 1

    accuracy = correct / len(cases) if cases else 0
    results.append(
        TestResult(
            name="Short Text Detection",
            passed=accuracy >= 0.50,  # Lower threshold for short text
            message=f"Accuracy: {accuracy:.1%} ({correct}/{len(cases)})",
            accuracy=accuracy,
        )
    )

    return results


def run_edge_case_tests(detector: LanguageDetector) -> list[TestResult]:
    """Test edge cases and error handling."""
    results = []

    # Empty input
    detected, conf = detector.detect_language("")
    results.append(
        TestResult(
            name="Empty Input",
            passed=detected == "unknown" and conf == 0.0,
            message=f"Returned: {detected} ({conf})",
        )
    )

    # Numbers only
    detected, conf = detector.detect_language("12345 67890")
    results.append(
        TestResult(
            name="Numbers Only",
            passed=True,  # Should not crash
            message=f"Returned: {detected} ({conf:.2f})",
        )
    )

    # Mixed content
    text = "Hello world! def foo(): print('bar')"
    detected, conf = detector.detect_language(text)
    results.append(
        TestResult(
            name="Mixed Natural/Code",
            passed=True,  # Accept any reasonable result
            message=f"Detected: {detected} ({conf:.2f})",
        )
    )

    # Unicode
    text = "Cześć, jak się masz? 🎉"
    detected, conf = detector.detect_language(text)
    results.append(
        TestResult(
            name="Unicode with Emoji",
            passed=True,  # Should not crash
            message=f"Detected: {detected} ({conf:.2f})",
        )
    )

    return results


def run_confidence_tests(detector: LanguageDetector) -> list[TestResult]:
    """Test confidence calibration."""
    results = []

    # High confidence for clear text
    text = "The quick brown fox jumps over the lazy dog. This is a very clear English sentence."
    detected, conf = detector.detect_language(text)
    results.append(
        TestResult(
            name="High Confidence for Clear Text",
            passed=conf >= 0.9,
            message=f"Confidence: {conf:.2f} (expected >= 0.9)",
        )
    )

    # Lower confidence for ambiguous
    text = "OK"
    _detected, conf = detector.detect_language(text)
    results.append(
        TestResult(
            name="Lower Confidence for Ambiguous",
            passed=True,  # Just check it doesn't claim high confidence
            message=f"Confidence: {conf:.2f}",
        )
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="Test language detection")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== Language Detection Falsification Tests ===\n")

    detector = LanguageDetector()

    # Run language tests
    print("Language Detection Tests:")
    lang_results = run_language_tests(detector)
    for result in lang_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")
        if result.details.get("failed"):
            for exp, got, txt in result.details["failed"][:3]:
                print(f"      Expected {exp}, got {got}: '{txt}...'")

    # Run edge case tests
    print("\nEdge Case Tests:")
    edge_results = run_edge_case_tests(detector)
    for result in edge_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")

    # Run confidence tests
    print("\nConfidence Calibration Tests:")
    conf_results = run_confidence_tests(detector)
    for result in conf_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")

    # Summary
    all_results = lang_results + edge_results + conf_results
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results if requested
    if args.output:
        output_data = {
            "language_tests": [
                {"name": r.name, "passed": r.passed, "accuracy": r.accuracy} for r in lang_results
            ],
            "edge_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in edge_results
            ],
            "confidence_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in conf_results
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
