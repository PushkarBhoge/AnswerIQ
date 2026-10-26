"""
Unit tests for QuestionRetriever: TF-IDF indexing, query matching,
relevance thresholds, and insufficient evidence detection.
"""

import pytest
from src.dataset_loader import DatasetRecord
from src.question_retriever import QuestionRetriever


@pytest.fixture
def sample_records():
    return [
        DatasetRecord(
            source_id="test.parquet:row-0",
            source_file="test.parquet",
            row_index=0,
            question="What is a firewall and what are its types?",
            answer="A firewall filters incoming and outgoing network traffic using security rules. Types include packet filtering and proxy.",
            keywords="firewall, packet filtering, security rules"
        ),
        DatasetRecord(
            source_id="test.parquet:row-1",
            source_file="test.parquet",
            row_index=1,
            question="Explain DNS and resolution steps.",
            answer="DNS translates domain names to IP addresses over port 53 using root, TLD, and authoritative servers.",
            keywords="DNS, domain name, IP address, port 53"
        )
    ]


def test_question_retriever_exact_match(sample_records):
    retriever = QuestionRetriever(records=sample_records, min_similarity_threshold=0.25)
    result = retriever.retrieve("What is a firewall and its functions?")

    assert result.has_sufficient_evidence is True
    assert result.status in ("sufficient_evidence", "limited_evidence")
    assert len(result.top_records) > 0
    assert result.top_records[0].source_id == "test.parquet:row-0"
    assert result.best_similarity > 0.35


def test_question_retriever_insufficient_evidence(sample_records):
    retriever = QuestionRetriever(records=sample_records, min_similarity_threshold=0.25)
    # Completely unrelated question not covered in networking sample records
    result = retriever.retrieve("How do plants perform photosynthesis in daylight?")

    assert result.has_sufficient_evidence is False
    assert result.status == "insufficient_evidence"
    assert "Insufficient dataset evidence" in result.message
    assert result.best_similarity < 0.25


def test_question_retriever_empty_query(sample_records):
    retriever = QuestionRetriever(records=sample_records, min_similarity_threshold=0.25)
    result = retriever.retrieve("")

    assert result.has_sufficient_evidence is False
    assert result.status == "insufficient_evidence"
    assert result.best_similarity == 0.0
