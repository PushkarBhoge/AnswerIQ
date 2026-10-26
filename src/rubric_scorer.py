"""
Rubric scoring module.
Calculates concept-level and overall scores based on semantic similarity,
keyword evidence, and dataset rubrics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.ai_reference_generator import ExpectedConcept
from src.keyword_matcher import KeywordMatchResult


@dataclass
class ConceptScore:
    concept: str
    max_marks: float
    awarded_marks: float
    semantic_score: float
    keyword_score: float
    combined_score: float
    status: str  # "Full Credit", "Partial Credit", "Minimal Credit", "Not Addressed"
    matched_keywords: List[str]
    missing_keywords: List[str]
    evidence_snippet: str
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept,
            "max_marks": round(self.max_marks, 2),
            "awarded_marks": round(self.awarded_marks, 2),
            "semantic_score": round(self.semantic_score, 4),
            "keyword_score": round(self.keyword_score, 4),
            "combined_score": round(self.combined_score, 4),
            "status": self.status,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "evidence_snippet": self.evidence_snippet,
            "explanation": self.explanation
        }


@dataclass
class RubricScoreResult:
    max_marks: float
    total_awarded_marks: float
    percentage_score: float
    concept_scores: List[ConceptScore]
    is_conclusive: bool
    scoring_note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_marks": round(self.max_marks, 2),
            "total_awarded_marks": round(self.total_awarded_marks, 2),
            "percentage_score": round(self.percentage_score, 2),
            "concept_scores": [c.to_dict() for c in self.concept_scores],
            "is_conclusive": self.is_conclusive,
            "scoring_note": self.scoring_note
        }


class RubricScorer:
    def __init__(
        self,
        semantic_weight: float = 0.65,
        keyword_weight: float = 0.35,
        full_credit_threshold: float = 0.68,
        partial_credit_threshold: float = 0.42,
        minimal_credit_threshold: float = 0.25
    ):
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.full_credit_threshold = full_credit_threshold
        self.partial_credit_threshold = partial_credit_threshold
        self.minimal_credit_threshold = minimal_credit_threshold

    def score_answer(
        self,
        concepts: List[ExpectedConcept],
        semantic_matches: Dict[str, Dict[str, Any]],
        keyword_matches: Dict[str, KeywordMatchResult],
        max_marks: float,
        evidence_status: str
    ) -> RubricScoreResult:
        max_marks = float(max(0.1, max_marks))

        if evidence_status == "insufficient_evidence" or not concepts:
            return RubricScoreResult(
                max_marks=max_marks,
                total_awarded_marks=0.0,
                percentage_score=0.0,
                concept_scores=[],
                is_conclusive=False,
                scoring_note="Marks cannot be awarded because there is insufficient dataset evidence to verify the answer."
            )

        # Normalize concept weights to sum to max_marks
        total_concept_weights = sum(max(0.1, c.marks_weight) for c in concepts)
        if total_concept_weights <= 0:
            total_concept_weights = float(len(concepts))

        evaluated_concepts: List[ConceptScore] = []
        running_total_score = 0.0

        for c in concepts:
            c_name = c.concept
            # Proportion of total marks
            concept_max = (max(0.1, c.marks_weight) / total_concept_weights) * max_marks

            sem_info = semantic_matches.get(c_name, {"similarity_score": 0.0, "best_matching_sentence": ""})
            kw_info = keyword_matches.get(c_name, KeywordMatchResult([], [], [], 0.0))

            sem_score = float(sem_info.get("similarity_score", 0.0))
            kw_score = float(kw_info.match_ratio)
            evidence_snippet = str(sem_info.get("best_matching_sentence", ""))

            # Calculate combined score
            if kw_info.expected_keywords:
                combined = (self.semantic_weight * sem_score) + (self.keyword_weight * kw_score)
            else:
                combined = sem_score

            # Credit classification and mark assignment
            if combined >= self.full_credit_threshold:
                status = "Full Credit"
                awarded = concept_max
                expl = "Concept clearly articulated with supporting networking terminology."
            elif combined >= self.partial_credit_threshold:
                status = "Partial Credit"
                # Proportional sliding award between 45% and 80% of concept max
                factor = 0.45 + (0.35 * ((combined - self.partial_credit_threshold) / (self.full_credit_threshold - self.partial_credit_threshold)))
                awarded = concept_max * factor
                expl = "Core concept partially addressed; some elaboration or key technical terms are missing."
            elif combined >= self.minimal_credit_threshold:
                status = "Minimal Credit"
                awarded = concept_max * 0.25
                expl = "Brief mention or vague reference; lacks technical depth and required terminology."
            else:
                status = "Not Addressed"
                awarded = 0.0
                expl = "Concept missing or unsupported by the provided answer."

            # Ensure awarded marks do not exceed concept maximum or drop below 0
            awarded = max(0.0, min(concept_max, awarded))
            running_total_score += awarded

            evaluated_concepts.append(
                ConceptScore(
                    concept=c_name,
                    max_marks=concept_max,
                    awarded_marks=awarded,
                    semantic_score=sem_score,
                    keyword_score=kw_score,
                    combined_score=combined,
                    status=status,
                    matched_keywords=kw_info.matched_keywords,
                    missing_keywords=kw_info.missing_keywords,
                    evidence_snippet=evidence_snippet,
                    explanation=expl
                )
            )

        # Normalize total awarded marks strictly between 0 and max_marks
        final_total = max(0.0, min(max_marks, round(running_total_score, 2)))
        percentage = round((final_total / max_marks) * 100.0, 2)

        note = "Estimated score based on local dataset evidence. Not an official exam grade."
        if evidence_status == "limited_evidence":
            note += " Evaluated under limited dataset coverage; score may be conservative."

        return RubricScoreResult(
            max_marks=max_marks,
            total_awarded_marks=final_total,
            percentage_score=percentage,
            concept_scores=evaluated_concepts,
            is_conclusive=True,
            scoring_note=note
        )
