"""
Feedback generation module.
Produces strengths, missing concepts, potential errors, personalized recommendations,
and an improved student answer strictly grounded in dataset evidence.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.rubric_scorer import RubricScoreResult, ConceptScore
from src.ai_reference_generator import GeminiReferenceResult


@dataclass
class FeedbackResult:
    strengths: List[str]
    missing_concepts: List[str]
    potential_errors: List[str]
    recommendations: List[str]
    reference_answer: str
    improved_student_answer: str
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strengths": self.strengths,
            "missing_concepts": self.missing_concepts,
            "potential_errors": self.potential_errors,
            "recommendations": self.recommendations,
            "reference_answer": self.reference_answer,
            "improved_student_answer": self.improved_student_answer,
            "limitations": self.limitations
        }


class FeedbackGenerator:
    def __init__(self):
        pass

    def generate_feedback(
        self,
        student_answer: str,
        score_result: RubricScoreResult,
        reference_result: GeminiReferenceResult,
        evidence_status: str
    ) -> FeedbackResult:
        if evidence_status == "insufficient_evidence":
            return FeedbackResult(
                strengths=[],
                missing_concepts=["Unable to identify expected concepts due to insufficient dataset evidence."],
                potential_errors=["Answer could not be verified against the local dataset."],
                recommendations=[
                    "Consult your networking course syllabus or add relevant question-answer records to data/.",
                    "Verify your question phrasing or try a more specific networking query."
                ],
                reference_answer="",
                improved_student_answer="",
                limitations=["No authoritative records found in the local dataset matching this question."]
            )

        strengths: List[str] = []
        missing_concepts: List[str] = []
        recommendations: List[str] = []
        potential_errors: List[str] = []

        # 1. Analyze concept breakdown
        for cs in score_result.concept_scores:
            if cs.status == "Full Credit":
                detail = f"Strong grasp of: **{cs.concept}**."
                if cs.matched_keywords:
                    detail += f" (Correctly used terminology: {', '.join(cs.matched_keywords)})"
                strengths.append(detail)
            elif cs.status == "Partial Credit":
                strengths.append(f"Partially explained: **{cs.concept}** ({cs.awarded_marks:.1f}/{cs.max_marks:.1f} marks).")
                if cs.missing_keywords:
                    missing_concepts.append(
                        f"Elaboration on **{cs.concept}**: Expected technical terms were missing: {', '.join(cs.missing_keywords)}."
                    )
            elif cs.status == "Minimal Credit":
                missing_concepts.append(
                    f"Incomplete coverage of **{cs.concept}**: Mentioned briefly without technical precision."
                )
            else:  # Not Addressed
                missing_concepts.append(
                    f"Completely omitted: **{cs.concept}**."
                )

        # 2. Check for identifiable contradiction or unsupported claims
        student_lower = student_answer.lower()
        contradiction_checks = [
            (r"\btcp\b.*\b(unreliable|connectionless|no handshake)\b", "Claims TCP is connectionless or unreliable (dataset indicates TCP is connection-oriented with 3-way handshake)."),
            (r"\budp\b.*\b(connection-oriented|reliable delivery|guarantees delivery|three-way handshake)\b", "Claims UDP is connection-oriented or provides guaranteed delivery (dataset indicates UDP is connectionless and best-effort)."),
            (r"\bport 53\b.*\b(not dns|web server|http)\b", "Incorrect port association (dataset records UDP/TCP port 53 for DNS)."),
            (r"\bpacket filtering\b.*\b(layer 7 only|deep payload only)\b", "Confuses packet filtering with application proxies (dataset notes packet filtering inspects IP headers and port numbers)."),
        ]

        for pattern, err_msg in contradiction_checks:
            if re.search(pattern, student_lower):
                potential_errors.append(f"Potential discrepancy: {err_msg}")

        # If answer is very brief compared to question requirements
        if len(student_answer.split()) < 15 and score_result.percentage_score < 50:
            potential_errors.append("Answer is exceptionally brief; lacks required explanatory depth and structure.")

        # 3. Generate tailored recommendations
        if missing_concepts:
            recommendations.append(
                f"Prioritize revising the omitted concepts: {'; '.join([c.split(':')[0].replace('**', '') for c in missing_concepts[:3]])}."
            )
            recommendations.append(
                "Incorporate exact technical networking terminology (such as protocol names, layer numbers, and mechanisms) to maximize rubric points."
            )
        if potential_errors:
            recommendations.append(
                "Review the core definitions in the reference answer to correct technical inaccuracies."
            )
        if not recommendations:
            recommendations.append("Excellent performance! Your answer comprehensively covers the expected rubric criteria.")

        # 4. Synthesize Improved Student Answer grounded strictly in reference
        improved_answer = self._synthesize_improved_answer(
            student_answer=student_answer,
            reference_answer=reference_result.reference_answer,
            missing_concepts=missing_concepts
        )

        return FeedbackResult(
            strengths=strengths if strengths else ["No strong conceptual matches identified."],
            missing_concepts=missing_concepts if missing_concepts else ["All primary concepts were addressed."],
            potential_errors=potential_errors if potential_errors else ["No direct factual contradictions identified based on available dataset evidence."],
            recommendations=recommendations,
            reference_answer=reference_result.reference_answer,
            improved_student_answer=improved_answer,
            limitations=reference_result.limitations
        )

    def _synthesize_improved_answer(
        self,
        student_answer: str,
        reference_answer: str,
        missing_concepts: List[str]
    ) -> str:
        """
        Builds an improved version incorporating student text and missing reference concepts.
        """
        if not reference_answer:
            return student_answer

        # If student answer was already very comprehensive
        if not missing_concepts or len(student_answer.split()) > 100:
            return (
                f"{student_answer.strip()}\n\n"
                f"[Refinement based on Dataset Evidence]: To achieve full marks, ensure exact specification of: "
                f"{reference_answer}"
            )

        # For partial or brief answers, synthesize the student's foundation with dataset completion
        return (
            f"{student_answer.strip()}\n\n"
            f"[Comprehensive Dataset-Grounded Revision]:\n{reference_answer}"
        )
