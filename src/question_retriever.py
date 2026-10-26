"""
Question retrieval module using scikit-learn TF-IDF and Cosine Similarity.
Retrieves relevant dataset records and enforces evidence thresholding.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.dataset_loader import DatasetRecord


@dataclass
class RetrievedRecord:
    record: DatasetRecord
    similarity_score: float
    source_id: str
    source_file: str
    row_index: int


@dataclass
class RetrievalResult:
    query: str
    top_records: List[RetrievedRecord]
    best_similarity: float
    min_similarity_threshold: float
    has_sufficient_evidence: bool
    status: str  # "sufficient_evidence", "limited_evidence", "insufficient_evidence"
    message: str
    searched_records_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "best_similarity": round(self.best_similarity, 4),
            "threshold": self.min_similarity_threshold,
            "has_sufficient_evidence": self.has_sufficient_evidence,
            "status": self.status,
            "message": self.message,
            "searched_records_count": self.searched_records_count,
            "top_sources": [
                {
                    "source_id": r.source_id,
                    "similarity": round(r.similarity_score, 4),
                    "file": r.source_file,
                    "row": r.row_index,
                    "question_snippet": r.record.question[:120] + "..." if len(r.record.question) > 120 else r.record.question
                }
                for r in self.top_records
            ]
        }


class QuestionRetriever:
    def __init__(
        self,
        records: List[DatasetRecord],
        min_similarity_threshold: float = 0.25,
        limited_similarity_threshold: float = 0.45,
        top_k: int = 4
    ):
        self.records = records
        self.min_similarity_threshold = float(min_similarity_threshold)
        self.limited_similarity_threshold = float(limited_similarity_threshold)
        self.top_k = top_k
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """Constructs and caches the TF-IDF index across all dataset records."""
        if not self.records:
            return

        corpus = []
        for r in self.records:
            # Combine question and answer keywords to give highest weight to the question text
            # Repeating question 2x strengthens exact question relevance
            text = f"{r.question} {r.question} {r.answer[:400]}"
            if r.keywords:
                text += f" {r.keywords}"
            corpus.append(text)

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=50000,
            stop_words="english",
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str) -> RetrievalResult:
        query_clean = str(query).strip()
        if not query_clean or not self.records or self.vectorizer is None or self.tfidf_matrix is None:
            return RetrievalResult(
                query=query_clean,
                top_records=[],
                best_similarity=0.0,
                min_similarity_threshold=self.min_similarity_threshold,
                has_sufficient_evidence=False,
                status="insufficient_evidence",
                message="No search query provided or dataset is empty.",
                searched_records_count=len(self.records) if self.records else 0
            )

        query_vec = self.vectorizer.transform([query_clean])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(similarities)[::-1][:self.top_k]
        top_records: List[RetrievedRecord] = []

        for idx in top_indices:
            score = float(similarities[idx])
            rec = self.records[idx]
            top_records.append(
                RetrievedRecord(
                    record=rec,
                    similarity_score=score,
                    source_id=rec.source_id,
                    source_file=rec.source_file,
                    row_index=rec.row_index
                )
            )

        best_score = top_records[0].similarity_score if top_records else 0.0

        if best_score < self.min_similarity_threshold:
            status = "insufficient_evidence"
            has_sufficient = False
            msg = (
                f"Insufficient dataset evidence: Closest match similarity is {best_score:.2f}, "
                f"which is below the minimum required threshold of {self.min_similarity_threshold:.2f}. "
                f"The question is not adequately covered by the local dataset."
            )
        elif best_score < self.limited_similarity_threshold:
            status = "limited_evidence"
            has_sufficient = True
            msg = (
                f"Limited dataset evidence: Moderate similarity ({best_score:.2f}). "
                f"Evaluation is grounded only in partially matching records."
            )
        else:
            status = "sufficient_evidence"
            has_sufficient = True
            msg = (
                f"Sufficient dataset evidence: Strong similarity match ({best_score:.2f}) "
                f"found in local dataset records."
            )

        return RetrievalResult(
            query=query_clean,
            top_records=top_records,
            best_similarity=best_score,
            min_similarity_threshold=self.min_similarity_threshold,
            has_sufficient_evidence=has_sufficient,
            status=status,
            message=msg,
            searched_records_count=len(self.records)
        )
