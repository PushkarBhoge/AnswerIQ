"""
Evaluation Orchestrator.
Coordinates dataset retrieval, AI reference generation, keyword matching,
semantic similarity scoring, rubric calculation, and feedback generation.
"""

import os
from typing import Dict, Any, Optional, List

from src.dataset_loader import DatasetLoader, DatasetRecord, DatasetLoaderError
from src.question_retriever import QuestionRetriever, RetrievalResult
from src.ai_reference_generator import (
    GeminiReferenceGenerator,
    GeminiReferenceResult,
    ExpectedConcept,
    GeminiConfigError,
    GeminiError
)
from src.keyword_matcher import KeywordMatcher, KeywordMatchResult
from src.semantic_matcher import SemanticMatcher
from src.rubric_scorer import RubricScorer, RubricScoreResult
from src.feedback_generator import FeedbackGenerator, FeedbackResult


class EvaluatorOrchestrator:
    _instance = None

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.loader = DatasetLoader(data_dir=self.data_dir)
        self.records: List[DatasetRecord] = []
        self.retriever: Optional[QuestionRetriever] = None
        self.keyword_matcher = KeywordMatcher()
        self.semantic_matcher = SemanticMatcher.get_instance()
        self.rubric_scorer = RubricScorer()
        self.feedback_generator = FeedbackGenerator()
        self.reference_generator: Optional[GeminiReferenceGenerator] = None
        self._init_components()

    @classmethod
    def get_instance(cls, data_dir: str = "data") -> "EvaluatorOrchestrator":
        if cls._instance is None:
            cls._instance = cls(data_dir=data_dir)
        return cls._instance

    def _init_components(self):
        """Loads dataset and initializes retriever and AI components."""
        try:
            self.records = self.loader.load_dataset()
            min_sim = float(os.getenv("RETRIEVAL_MIN_SIMILARITY", "0.25"))
            self.retriever = QuestionRetriever(
                records=self.records,
                min_similarity_threshold=min_sim,
                limited_similarity_threshold=0.45,
                top_k=int(os.getenv("MAX_RETRIEVAL_RESULTS", "4"))
            )
        except DatasetLoaderError as e:
            print(f"[EvaluatorOrchestrator] Dataset initialization warning: {e}")
            self.records = []
            self.retriever = None

        try:
            self.reference_generator = GeminiReferenceGenerator()
        except GeminiConfigError as e:
            print(f"[EvaluatorOrchestrator] Notice: Gemini API not configured ({e}). Direct dataset fallback will be active.")
            self.reference_generator = None

    def _direct_dataset_reference_fallback(
        self,
        question: str,
        retrieval_result: RetrievalResult,
        max_marks: float
    ) -> GeminiReferenceResult:
        """
        Direct dataset extraction fallback when Gemini API is unconfigured or unavailable.
        Strictly preserves the dataset-only policy without hallucination.
        """
        if not retrieval_result.top_records:
            return GeminiReferenceResult(
                status="insufficient_evidence",
                reference_answer="",
                concepts=[],
                source_ids=[],
                limitations=["No dataset records matched the query."]
            )

        top_rec = retrieval_result.top_records[0].record
        ref_answer = top_rec.answer

        # Extract concepts from record if available, else derive key clauses from the answer
        concepts: List[ExpectedConcept] = []
        if top_rec.expected_concepts:
            raw_items = [c.strip() for c in top_rec.expected_concepts.split(";") if c.strip()]
        else:
            # Fallback: break answer into main descriptive clauses
            raw_items = [s.strip() for s in ref_answer.split(".") if len(s.strip()) > 15][:5]

        weight_per_concept = max_marks / max(1, len(raw_items))

        # Keywords from record
        record_kws = [k.strip() for k in top_rec.keywords.split(",")] if top_rec.keywords else []

        for item in raw_items:
            # Match subset of keywords relevant to this concept
            concept_kws = [kw for kw in record_kws if kw.lower() in item.lower()]
            if not concept_kws and record_kws:
                concept_kws = record_kws[:2]

            concepts.append(
                ExpectedConcept(
                    concept=item,
                    keywords=concept_kws,
                    marks_weight=weight_per_concept,
                    evidence_sources=[top_rec.source_id]
                )
            )

        return GeminiReferenceResult(
            status=retrieval_result.status,
            reference_answer=ref_answer,
            concepts=concepts,
            source_ids=[top_rec.source_id],
            limitations=[
                "Extracted directly from local dataset record without Gemini generative processing."
            ]
        )

    def evaluate(self, question: str, student_answer: str, max_marks: float) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation of a student answer.
        """
        q_clean = str(question).strip()
        ans_clean = str(student_answer).strip()
        max_m = float(max_marks)

        # 1. Dataset Retrieval
        if not self.retriever or not self.records:
            # Attempt to reload if previously empty
            self._init_components()

        if not self.retriever or not self.records:
            return {
                "status": "insufficient_evidence",
                "question": q_clean,
                "student_answer": ans_clean,
                "max_marks": max_m,
                "awarded_marks": 0.0,
                "percentage_score": 0.0,
                "status_message": "Evaluation impossible: No usable dataset found in data/ directory.",
                "retrieval_info": {"status": "insufficient_evidence", "searched_records_count": 0, "top_sources": []},
                "reference_answer": "",
                "concept_scores": [],
                "strengths": [],
                "missing_concepts": ["No dataset available to evaluate concepts."],
                "potential_errors": ["Cannot verify correctness."],
                "recommendations": ["Ensure .parquet dataset files exist in data/."],
                "improved_answer": "",
                "source_files": [],
                "source_ids": [],
                "scoring_note": "Inconclusive due to missing dataset.",
                "limitations": ["No local dataset found."]
            }

        retrieval_result = self.retriever.retrieve(q_clean)

        # 2. Reference & Rubric Generation (Gemini with Dataset Fallback)
        ref_result: Optional[GeminiReferenceResult] = None
        if retrieval_result.status == "insufficient_evidence":
            ref_result = GeminiReferenceResult(
                status="insufficient_evidence",
                reference_answer="",
                concepts=[],
                source_ids=[r.source_id for r in retrieval_result.top_records],
                limitations=[retrieval_result.message]
            )
        else:
            if self.reference_generator:
                try:
                    ref_result = self.reference_generator.generate_reference_and_rubric(
                        question=q_clean,
                        retrieved_records=retrieval_result.top_records,
                        max_marks=max_m
                    )
                except GeminiError as ge:
                    print(f"[Evaluator] Gemini call failed ({ge}), using dataset fallback.")
                    ref_result = self._direct_dataset_reference_fallback(q_clean, retrieval_result, max_m)
            else:
                ref_result = self._direct_dataset_reference_fallback(q_clean, retrieval_result, max_m)

        # 3. Matching & Scoring
        semantic_matches: Dict[str, Dict[str, Any]] = {}
        keyword_matches: Dict[str, KeywordMatchResult] = {}

        if ref_result.status != "insufficient_evidence":
            for concept_obj in ref_result.concepts:
                c_text = concept_obj.concept
                # Semantic match
                sem_eval = self.semantic_matcher.evaluate_concept_match(c_text, ans_clean)
                semantic_matches[c_text] = sem_eval

                # Keyword match
                kw_eval = self.keyword_matcher.match_keywords(ans_clean, concept_obj.keywords)
                keyword_matches[c_text] = kw_eval

        # 4. Rubric Scoring
        score_result: RubricScoreResult = self.rubric_scorer.score_answer(
            concepts=ref_result.concepts,
            semantic_matches=semantic_matches,
            keyword_matches=keyword_matches,
            max_marks=max_m,
            evidence_status=ref_result.status
        )

        # 5. Feedback Generation
        feedback_result: FeedbackResult = self.feedback_generator.generate_feedback(
            student_answer=ans_clean,
            score_result=score_result,
            reference_result=ref_result,
            evidence_status=ref_result.status
        )

        # 6. Extract source files and IDs for traceability
        source_files = list(set(r.source_file for r in retrieval_result.top_records))
        source_ids = [r.source_id for r in retrieval_result.top_records]

        return {
            "status": ref_result.status,
            "question": q_clean,
            "student_answer": ans_clean,
            "max_marks": score_result.max_marks,
            "awarded_marks": score_result.total_awarded_marks,
            "percentage_score": score_result.percentage_score,
            "status_message": retrieval_result.message,
            "retrieval_info": retrieval_result.to_dict(),
            "reference_answer": feedback_result.reference_answer,
            "concept_scores": [c.to_dict() for c in score_result.concept_scores],
            "strengths": feedback_result.strengths,
            "missing_concepts": feedback_result.missing_concepts,
            "potential_errors": feedback_result.potential_errors,
            "recommendations": feedback_result.recommendations,
            "improved_answer": feedback_result.improved_student_answer,
            "source_files": source_files,
            "source_ids": source_ids,
            "scoring_note": score_result.scoring_note,
            "limitations": feedback_result.limitations
        }
