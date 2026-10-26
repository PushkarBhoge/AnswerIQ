"""
Unit tests for KeywordMatcher, SemanticMatcher, and RubricScorer bounds and rules.
"""

import pytest
from src.keyword_matcher import KeywordMatcher
from src.semantic_matcher import SemanticMatcher
from src.ai_reference_generator import ExpectedConcept
from src.rubric_scorer import RubricScorer


def test_keyword_matcher_boundaries_and_case():
    matcher = KeywordMatcher()
    student_text = "The firewall performs packet filtering and inspects TCP port numbers."
    expected_kws = ["Firewall", "packet filtering", "UDP", "stateful inspection"]

    res = matcher.match_keywords(student_text, expected_kws)
    assert "Firewall" in res.matched_keywords
    assert "packet filtering" in res.matched_keywords
    assert "UDP" in res.missing_keywords
    assert "stateful inspection" in res.missing_keywords
    assert res.match_ratio == 0.5


def test_keyword_matcher_no_substring_false_positives():
    matcher = KeywordMatcher()
    # "cat" should not match "certificate", "port" should match
    student_text = "We configured port forwarding and validated the certificate."
    res = matcher.match_keywords(student_text, ["cat", "port"])
    assert "port" in res.matched_keywords
    assert "cat" in res.missing_keywords


def test_semantic_matcher_empty():
    matcher = SemanticMatcher.get_instance()
    sim = matcher.compute_similarity("", "TCP protocol")
    assert sim == 0.0

    eval_res = matcher.evaluate_concept_match("TCP protocol", "")
    assert eval_res["similarity_score"] == 0.0
    assert eval_res["is_covered"] is False


def test_rubric_scorer_bounds_and_proportions():
    scorer = RubricScorer()
    concepts = [
        ExpectedConcept("Packet filtering", ["packet", "filtering"], 2.0),
        ExpectedConcept("Stateful inspection", ["stateful", "inspection"], 3.0),
    ]

    semantic_matches = {
        "Packet filtering": {"similarity_score": 0.85, "best_matching_sentence": "packet filtering works"},
        "Stateful inspection": {"similarity_score": 0.20, "best_matching_sentence": ""}
    }

    kw_matcher = KeywordMatcher()
    kw_matches = {
        "Packet filtering": kw_matcher.match_keywords("packet filtering", ["packet", "filtering"]),
        "Stateful inspection": kw_matcher.match_keywords("packet filtering", ["stateful", "inspection"])
    }

    res = scorer.score_answer(
        concepts=concepts,
        semantic_matches=semantic_matches,
        keyword_matches=kw_matches,
        max_marks=10.0,
        evidence_status="sufficient_evidence"
    )

    # Max marks must be respected (<= 10.0 and >= 0.0)
    assert 0.0 <= res.total_awarded_marks <= 10.0
    assert 0.0 <= res.percentage_score <= 100.0
    assert len(res.concept_scores) == 2

    # First concept should have high marks (approx 4.0 out of normalized 4.0)
    c1 = res.concept_scores[0]
    assert c1.status == "Full Credit"
    assert c1.awarded_marks > 3.0

    # Second concept should have low/no marks
    c2 = res.concept_scores[1]
    assert c2.status in ("Minimal Credit", "Not Addressed")
    assert c2.awarded_marks < 1.5


def test_rubric_scorer_insufficient_evidence():
    scorer = RubricScorer()
    res = scorer.score_answer(
        concepts=[],
        semantic_matches={},
        keyword_matches={},
        max_marks=5.0,
        evidence_status="insufficient_evidence"
    )

    assert res.total_awarded_marks == 0.0
    assert res.is_conclusive is False
    assert "insufficient" in res.scoring_note.lower()
