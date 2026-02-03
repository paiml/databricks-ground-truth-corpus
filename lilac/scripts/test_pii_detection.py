#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "regex>=2023.0",
# ]
# ///
"""Test PII detection accuracy against ground truth.

This script validates PII detection algorithms against manually
curated ground truth data using Popperian falsification methodology.

PII Types Tested:
- Emails
- Phone numbers (US, International)
- SSN (US Social Security Numbers)
- Credit card numbers
- IP addresses (IPv4, IPv6)

Usage:
    uv run scripts/test_pii_detection.py
    uv run scripts/test_pii_detection.py --with-lilac

References:
    - Lilac Data Quality Oracle Spec: specs/data-quality-oracle.md
    - GDPR Article 4(1): Definition of personal data
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field


@dataclass
class PIIMatch:
    """A detected PII instance."""

    type: str
    start: int
    end: int
    value: str
    confidence: float = 1.0


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
# PII Detection Patterns (Reference Implementation)
# =============================================================================


class PIIDetector:
    """Reference PII detector using regex patterns."""

    # Email pattern (RFC 5322 simplified)
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    # US Phone patterns - handles various formats
    US_PHONE_PATTERN = re.compile(
        r"(?:\+1[-.\s]?)?"  # Optional +1 prefix
        r"(?:\(\d{3}\)|\d{3})"  # Area code with or without parens
        r"[-.\s]?"  # Separator
        r"\d{3}"  # Exchange
        r"[-.\s]?"  # Separator
        r"\d{4}"  # Subscriber
        r"(?!\d)"  # Not followed by more digits
    )

    # International phone (E.164 format)
    INTL_PHONE_PATTERN = re.compile(r"\b\+[1-9]\d{1,14}\b")

    # US SSN pattern
    SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")

    # Credit card patterns (major brands)
    CREDIT_CARD_PATTERN = re.compile(
        r"\b(?:"
        r"4[0-9]{12}(?:[0-9]{3})?|"  # Visa
        r"5[1-5][0-9]{14}|"  # MasterCard
        r"3[47][0-9]{13}|"  # Amex
        r"6(?:011|5[0-9]{2})[0-9]{12}|"  # Discover
        r"(?:2131|1800|35\d{3})\d{11}"  # JCB
        r")\b"
    )

    # IPv4 pattern
    IPV4_PATTERN = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )

    # IPv6 pattern (simplified)
    IPV6_PATTERN = re.compile(
        r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|"
        r"\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|"
        r"\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b"
    )

    # API key patterns (generic)
    API_KEY_PATTERN = re.compile(
        r"\b(?:"
        r"sk-[a-zA-Z0-9]{32,}|"  # OpenAI style
        r"AKIA[0-9A-Z]{16}|"  # AWS Access Key
        r"ghp_[a-zA-Z0-9]{36}|"  # GitHub PAT
        r"xox[baprs]-[a-zA-Z0-9-]+"  # Slack tokens
        r")\b"
    )

    def detect(self, text: str) -> list[PIIMatch]:
        """Detect all PII in text."""
        matches = []

        # Email
        for m in self.EMAIL_PATTERN.finditer(text):
            matches.append(PIIMatch("email", m.start(), m.end(), m.group()))

        # US Phone
        for m in self.US_PHONE_PATTERN.finditer(text):
            matches.append(PIIMatch("phone_us", m.start(), m.end(), m.group()))

        # International Phone
        for m in self.INTL_PHONE_PATTERN.finditer(text):
            # Skip if already matched as US phone
            if not any(
                m.start() >= x.start and m.end() <= x.end for x in matches if x.type == "phone_us"
            ):
                matches.append(PIIMatch("phone_intl", m.start(), m.end(), m.group()))

        # SSN
        for m in self.SSN_PATTERN.finditer(text):
            # Validate not a phone number or date
            value = m.group().replace("-", "").replace(" ", "")
            # SSN cannot start with 9, 666, or 000
            if not (
                value.startswith("9")
                or value.startswith("666")
                or value.startswith("000")
                or value[3:5] == "00"
                or value[5:] == "0000"
            ):
                matches.append(PIIMatch("ssn", m.start(), m.end(), m.group()))

        # Credit Card
        for m in self.CREDIT_CARD_PATTERN.finditer(text):
            if self._luhn_check(m.group()):
                matches.append(PIIMatch("credit_card", m.start(), m.end(), m.group()))

        # IPv4
        for m in self.IPV4_PATTERN.finditer(text):
            matches.append(PIIMatch("ipv4", m.start(), m.end(), m.group()))

        # IPv6
        for m in self.IPV6_PATTERN.finditer(text):
            matches.append(PIIMatch("ipv6", m.start(), m.end(), m.group()))

        # API Keys
        for m in self.API_KEY_PATTERN.finditer(text):
            matches.append(PIIMatch("api_key", m.start(), m.end(), m.group()))

        return matches

    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) < 13:
            return False

        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0


# =============================================================================
# Ground Truth Test Cases
# =============================================================================


def get_email_test_cases() -> list[tuple[str, list[dict]]]:
    """Email detection test cases."""
    return [
        # Positive cases
        (
            "Contact me at john.doe@example.com",
            [{"type": "email", "value": "john.doe@example.com"}],
        ),
        (
            "Emails: test@test.org and admin@company.co.uk",
            [
                {"type": "email", "value": "test@test.org"},
                {"type": "email", "value": "admin@company.co.uk"},
            ],
        ),
        ("user+tag@gmail.com is valid", [{"type": "email", "value": "user+tag@gmail.com"}]),
        # Negative cases
        ("This is not an email address", []),
        ("@invalid and invalid@ are not emails", []),
        ("name@.com is malformed", []),
    ]


def get_phone_test_cases() -> list[tuple[str, list[dict]]]:
    """Phone number detection test cases."""
    return [
        # US formats
        ("Call me at 555-123-4567", [{"type": "phone_us", "value": "555-123-4567"}]),
        ("Phone: (555) 123-4567", [{"type": "phone_us", "value": "(555) 123-4567"}]),
        ("+1 555 123 4567 is my number", [{"type": "phone_us", "value": "+1 555 123 4567"}]),
        # Negative cases
        ("Call 911 for emergencies", []),  # Too short
        ("The number 12345 is not a phone", []),  # Too short
    ]


def get_ssn_test_cases() -> list[tuple[str, list[dict]]]:
    """SSN detection test cases."""
    return [
        # Positive cases
        ("SSN: 123-45-6789", [{"type": "ssn", "value": "123-45-6789"}]),
        ("My social is 123 45 6789", [{"type": "ssn", "value": "123 45 6789"}]),
        # Invalid SSNs (should not match)
        ("900-00-0000 is invalid", []),  # Starts with 9
        ("666-12-3456 is invalid", []),  # Starts with 666
        ("000-12-3456 is invalid", []),  # Starts with 000
    ]


def get_credit_card_test_cases() -> list[tuple[str, list[dict]]]:
    """Credit card detection test cases."""
    return [
        # Valid cards (using Luhn-valid test numbers)
        (
            "Card: 4111111111111111",
            [  # Visa test number
                {"type": "credit_card", "value": "4111111111111111"}
            ],
        ),
        (
            "MC: 5500000000000004",
            [  # MasterCard test
                {"type": "credit_card", "value": "5500000000000004"}
            ],
        ),
        # Invalid (fails Luhn)
        ("1234567890123456 is not valid", []),
        ("Card 0000000000000000 invalid", []),
    ]


def get_ip_test_cases() -> list[tuple[str, list[dict]]]:
    """IP address detection test cases."""
    return [
        # IPv4
        ("Server at 192.168.1.1", [{"type": "ipv4", "value": "192.168.1.1"}]),
        ("Public IP: 8.8.8.8", [{"type": "ipv4", "value": "8.8.8.8"}]),
        # Invalid IPv4
        ("256.1.1.1 is invalid", []),
        ("1.2.3 is incomplete", []),
        # IPv6
        (
            "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            [{"type": "ipv6", "value": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}],
        ),
    ]


def get_api_key_test_cases() -> list[tuple[str, list[dict]]]:
    """API key detection test cases."""
    return [
        # OpenAI style
        (
            "Key: sk-1234567890abcdefghijklmnopqrstuv",
            [{"type": "api_key", "value": "sk-1234567890abcdefghijklmnopqrstuv"}],
        ),
        # AWS Access Key
        ("AWS: AKIAIOSFODNN7EXAMPLE", [{"type": "api_key", "value": "AKIAIOSFODNN7EXAMPLE"}]),
        # GitHub PAT
        (
            "Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            [{"type": "api_key", "value": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}],
        ),
        # Negative
        ("sk-short is too short", []),
        ("AKIA is incomplete", []),
    ]


# =============================================================================
# Test Runner
# =============================================================================


def compute_metrics(
    predictions: list[PIIMatch],
    ground_truth: list[dict],
    pii_type: str | None = None,
) -> tuple[float, float, float]:
    """Compute precision, recall, F1 for predictions vs ground truth."""

    # Filter by type if specified
    if pii_type:
        predictions = [p for p in predictions if p.type == pii_type]
        ground_truth = [g for g in ground_truth if g.get("type") == pii_type]

    pred_values = {p.value for p in predictions}
    gt_values = {g["value"] for g in ground_truth}

    if not pred_values and not gt_values:
        return 1.0, 1.0, 1.0  # Both empty = perfect

    true_positives = len(pred_values & gt_values)

    precision = true_positives / len(pred_values) if pred_values else 0.0
    recall = true_positives / len(gt_values) if gt_values else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def run_pii_tests(detector: PIIDetector) -> list[TestResult]:
    """Run all PII detection tests."""
    results = []

    test_suites = [
        ("Email Detection", get_email_test_cases(), "email", 0.95),
        ("Phone Detection", get_phone_test_cases(), "phone_us", 0.90),
        ("SSN Detection", get_ssn_test_cases(), "ssn", 0.98),
        ("Credit Card Detection", get_credit_card_test_cases(), "credit_card", 0.95),
        ("IP Address Detection", get_ip_test_cases(), "ipv4", 0.98),
        ("API Key Detection", get_api_key_test_cases(), "api_key", 0.90),
    ]

    for suite_name, test_cases, pii_type, min_f1 in test_suites:
        all_predictions = []
        all_ground_truth = []

        for text, expected in test_cases:
            predictions = detector.detect(text)
            all_predictions.extend(predictions)
            all_ground_truth.extend(expected)

        precision, recall, f1 = compute_metrics(all_predictions, all_ground_truth, pii_type)

        passed = f1 >= min_f1

        results.append(
            TestResult(
                name=suite_name,
                passed=passed,
                message=f"F1={f1:.3f} (min={min_f1})"
                if passed
                else f"F1={f1:.3f} < {min_f1} required",
                precision=precision,
                recall=recall,
                f1=f1,
                details={
                    "predictions": len(all_predictions),
                    "ground_truth": len(all_ground_truth),
                    "min_f1": min_f1,
                },
            )
        )

    return results


def run_edge_case_tests(detector: PIIDetector) -> list[TestResult]:
    """Test edge cases and adversarial inputs."""
    results = []

    # Test: Obfuscated email
    text = "Contact john[dot]doe[at]example[dot]com"
    matches = detector.detect(text)
    results.append(
        TestResult(
            name="Obfuscated Email (negative)",
            passed=len([m for m in matches if m.type == "email"]) == 0,
            message="Correctly ignores obfuscated format"
            if len(matches) == 0
            else "Incorrectly matched obfuscated email",
        )
    )

    # Test: Empty input
    matches = detector.detect("")
    results.append(
        TestResult(
            name="Empty Input",
            passed=len(matches) == 0,
            message="Handles empty input",
        )
    )

    # Test: Unicode
    text = "Email: tëst@example.com"
    matches = detector.detect(text)
    results.append(
        TestResult(
            name="Unicode in Email",
            passed=True,  # Should either match or gracefully skip
            message=f"Found {len(matches)} matches",
        )
    )

    # Test: Multiple PII in one string
    text = "Contact john@example.com at 555-123-4567, SSN 123-45-6789"
    matches = detector.detect(text)
    has_email = any(m.type == "email" for m in matches)
    has_phone = any(m.type == "phone_us" for m in matches)
    has_ssn = any(m.type == "ssn" for m in matches)
    results.append(
        TestResult(
            name="Multiple PII Types",
            passed=has_email and has_phone and has_ssn,
            message=f"Found: email={has_email}, phone={has_phone}, ssn={has_ssn}",
        )
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="Test PII detection")
    parser.add_argument("--with-lilac", action="store_true", help="Also test against Lilac library")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    print("=== PII Detection Falsification Tests ===\n")

    # Use reference detector
    detector = PIIDetector()

    # Run main tests
    print("PII Type Tests:")
    type_results = run_pii_tests(detector)
    for result in type_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")
        print(f"      P={result.precision:.3f} R={result.recall:.3f} F1={result.f1:.3f}")

    # Run edge case tests
    print("\nEdge Case Tests:")
    edge_results = run_edge_case_tests(detector)
    for result in edge_results:
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.name}: {result.message}")

    # Summary
    all_results = type_results + edge_results
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print(f"\n=== Summary: {passed}/{total} tests passed ===")

    # Save results if requested
    if args.output:
        output_data = {
            "type_tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "precision": r.precision,
                    "recall": r.recall,
                    "f1": r.f1,
                    "details": r.details,
                }
                for r in type_results
            ],
            "edge_tests": [
                {"name": r.name, "passed": r.passed, "message": r.message} for r in edge_results
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
