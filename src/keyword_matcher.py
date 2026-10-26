"""
Keyword matching module for evaluating student networking terminology.
Utilizes regex word boundaries and case-insensitive normalization.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set


@dataclass
class KeywordMatchResult:
    expected_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    match_ratio: float  # Value between 0.0 and 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_count": len(self.expected_keywords),
            "matched_count": len(self.matched_keywords),
            "missing_count": len(self.missing_keywords),
            "match_ratio": round(self.match_ratio, 4),
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords
        }


class KeywordMatcher:
    def __init__(self):
        pass

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase, replace non-standard dashes/quotes, normalize whitespace
        text = text.lower()
        text = re.sub(r"[\u2018\u2019]", "'", text)
        text = re.sub(r"[\u201c\u201d]", '"', text)
        text = re.sub(r"[\u2013\u2014]", "-", text)
        return " ".join(text.split())

    def match_keywords(self, student_text: str, expected_keywords: List[str]) -> KeywordMatchResult:
        normalized_student_text = self._normalize_text(student_text)

        # Remove duplicates while preserving order
        unique_expected: List[str] = []
        seen: Set[str] = set()
        for kw in expected_keywords:
            clean_kw = kw.strip()
            clean_kw_lower = clean_kw.lower()
            if clean_kw_lower and clean_kw_lower not in seen:
                seen.add(clean_kw_lower)
                unique_expected.append(clean_kw)

        if not unique_expected or not normalized_student_text:
            return KeywordMatchResult(
                expected_keywords=unique_expected,
                matched_keywords=[],
                missing_keywords=unique_expected,
                match_ratio=0.0
            )

        matched: List[str] = []
        missing: List[str] = []

        for kw in unique_expected:
            clean_kw = self._normalize_text(kw)
            # Create regex with word boundaries
            # If the keyword contains special symbols like +, -, /, escape them safely
            pattern = r"\b" + re.escape(clean_kw) + r"\b"
            if re.search(pattern, normalized_student_text):
                matched.append(kw)
            else:
                missing.append(kw)

        ratio = len(matched) / len(unique_expected) if unique_expected else 0.0

        return KeywordMatchResult(
            expected_keywords=unique_expected,
            matched_keywords=matched,
            missing_keywords=missing,
            match_ratio=ratio
        )
