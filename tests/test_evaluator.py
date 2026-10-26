"""
Unit tests for EvaluatorOrchestrator and end-to-end evaluation flow.
Includes mocks for Gemini API calls to ensure reproducible unit testing without network calls.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.evaluator import EvaluatorOrchestrator
from src.ai_reference_generator import (
    GeminiReferenceGenerator,
    GeminiReferenceResult,
    ExpectedConcept,
    GeminiAPIError,
    GeminiParsingError
)


@pytest.fixture
def orchestrator():
    return EvaluatorOrchestrator(data_dir="data")


def test_evaluator_insufficient_evidence_question(orchestrator):
    unrelated_question = "What is the cellular structure of eukaryotic plant mitochondria?"
    student_ans = "Plant mitochondria generate ATP through oxidative phosphorylation."

    res = orchestrator.evaluate(
        question=unrelated_question,
        student_answer=student_ans,
        max_marks=5.0
    )

    assert res["status"] == "insufficient_evidence"
    assert res["awarded_marks"] == 0.0
    assert len(res["concept_scores"]) == 0
    assert "Insufficient dataset evidence" in res["status_message"]
    assert len(res["strengths"]) == 0


def test_evaluator_valid_networking_question_with_mocked_gemini(orchestrator):
    mock_gemini_result = GeminiReferenceResult(
        status="sufficient_evidence",
        reference_answer="A firewall is a network security device that monitors and filters traffic.",
        concepts=[
            ExpectedConcept(
                concept="Monitors and filters network traffic",
                keywords=["firewall", "filter", "traffic"],
                marks_weight=2.5,
                evidence_sources=["test_networking.parquet:row-0"]
            ),
            ExpectedConcept(
                concept="Operates based on predetermined security rules",
                keywords=["security rules", "predetermined"],
                marks_weight=2.5,
                evidence_sources=["test_networking.parquet:row-0"]
            )
        ],
        source_ids=["test_networking.parquet:row-0"],
        limitations=[]
    )

    with patch.object(
        GeminiReferenceGenerator,
        "generate_reference_and_rubric",
        return_value=mock_gemini_result
    ):
        question = "What is a firewall and what are its primary types and functions in network security?"
        student_answer = (
            "A firewall is a security barrier that monitors and filters incoming and outgoing network traffic. "
            "It enforces predetermined security rules to protect internal networks."
        )

        res = orchestrator.evaluate(
            question=question,
            student_answer=student_answer,
            max_marks=5.0
        )

        assert res["status"] == "sufficient_evidence"
        assert res["awarded_marks"] >= 3.5  # High score for accurate answer
        assert res["max_marks"] == 5.0
        assert len(res["concept_scores"]) == 2
        assert len(res["strengths"]) > 0
        assert res["reference_answer"] != ""
        assert len(res["source_files"]) > 0


def test_evaluator_gemini_failure_fallback(orchestrator):
    # Test that if Gemini raises an API error or timeout, direct dataset extraction fallback takes over seamlessly
    with patch.object(
        GeminiReferenceGenerator,
        "generate_reference_and_rubric",
        side_effect=GeminiAPIError("API rate limit or connection timeout")
    ):
        question = "What is a firewall and what are its primary types and functions in network security?"
        student_answer = "A firewall filters packets based on security rules."

        res = orchestrator.evaluate(
            question=question,
            student_answer=student_answer,
            max_marks=5.0
        )

        # Fallback should succeed without throwing an uncaught exception
        assert res["status"] in ("sufficient_evidence", "limited_evidence")
        assert res["awarded_marks"] > 0.0
        assert res["reference_answer"] != ""
