"""
Gemini AI Reference Generator using the official google-genai SDK.
Synthesizes dataset-grounded reference answers, expected concepts, and rubrics
strictly from retrieved local dataset evidence.
"""

import os
import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.question_retriever import RetrievedRecord

# Load environment variables from .env
load_dotenv()


class GeminiError(Exception):
    """Base exception for Gemini operations."""
    pass


class GeminiConfigError(GeminiError):
    """Raised when Gemini API key or model configuration is missing or invalid."""
    pass


class GeminiAPIError(GeminiError):
    """Raised when the Gemini API request fails or times out."""
    pass


class GeminiParsingError(GeminiError):
    """Raised when Gemini returns malformed or non-compliant output."""
    pass


@dataclass
class ExpectedConcept:
    concept: str
    keywords: List[str]
    marks_weight: float
    evidence_sources: List[str] = field(default_factory=list)


@dataclass
class GeminiReferenceResult:
    status: str  # "sufficient_evidence", "limited_evidence", "insufficient_evidence"
    reference_answer: str
    concepts: List[ExpectedConcept]
    source_ids: List[str]
    limitations: List[str]
    raw_response: Dict[str, Any] = field(default_factory=dict)


class GeminiReferenceGenerator:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self._validate_config()
        self.client = genai.Client(api_key=self.api_key)

    def _validate_config(self):
        if not self.api_key or self.api_key in ("your_api_key", "your_gemini_api_key_here", "PLACEHOLDER"):
            raise GeminiConfigError(
                "Gemini API key is not configured. Please set a valid 'GEMINI_API_KEY' in your .env file."
            )
        if not self.model:
            self.model = "gemini-2.5-flash"

    def generate_reference_and_rubric(
        self,
        question: str,
        retrieved_records: List[RetrievedRecord],
        max_marks: float
    ) -> GeminiReferenceResult:
        """
        Generates reference answer and expected rubric concepts strictly using retrieved evidence.
        """
        if not retrieved_records:
            return GeminiReferenceResult(
                status="insufficient_evidence",
                reference_answer="",
                concepts=[],
                source_ids=[],
                limitations=["No dataset records were retrieved to support this question."]
            )

        # Build grounded evidence context blocks
        valid_source_ids = [r.source_id for r in retrieved_records]
        evidence_text_blocks = []
        for i, rec in enumerate(retrieved_records, 1):
            r = rec.record
            block = (
                f"--- EVIDENCE RECORD {i} ---\n"
                f"Source ID: {rec.source_id}\n"
                f"File: {rec.source_file} (Row: {rec.row_index})\n"
                f"Dataset Question: {r.question}\n"
                f"Dataset Answer: {r.answer}\n"
            )
            if r.expected_concepts:
                block += f"Dataset Concepts: {r.expected_concepts}\n"
            if r.keywords:
                block += f"Dataset Keywords: {r.keywords}\n"
            if r.rubric:
                block += f"Dataset Rubric: {r.rubric}\n"
            evidence_text_blocks.append(block)

        evidence_payload = "\n".join(evidence_text_blocks)

        prompt = f"""You are the authoritative evaluation engine for AnswerIQ, an academic Computer Networking evaluation system.

STRICT DATASET-ONLY POLICY:
1. Ground your entire output EXCLUSIVELY in the provided EVIDENCE RECORDS below.
2. DO NOT use outside computer networking knowledge, external assumptions, or general training data to invent answers or concepts.
3. If the provided evidence records do NOT contain sufficient information to answer the question, you MUST set "status": "insufficient_evidence", explain the gap in "limitations", and keep "reference_answer": "".
4. Every expected concept MUST cite the specific "Source ID" from which it is derived.
5. The sum of "marks_weight" across all concepts should equal {max_marks} (or proportional weights).

USER QUESTION:
{question}

MAXIMUM MARKS:
{max_marks}

PROVIDED DATASET EVIDENCE RECORDS:
{evidence_payload}

REQUIRED JSON OUTPUT FORMAT:
{{
  "status": "sufficient_evidence", // "sufficient_evidence" | "limited_evidence" | "insufficient_evidence"
  "reference_answer": "Comprehensive answer synthesized strictly from the retrieved evidence records.",
  "concepts": [
    {{
      "concept": "Specific expected concept directly supported by the evidence",
      "keywords": ["essential", "technical", "keywords"],
      "marks_weight": 1.0,
      "evidence_sources": ["filename.parquet:row-X"]
    }}
  ],
  "source_ids": ["filename.parquet:row-X"],
  "limitations": ["Any note on missing aspects in the dataset"]
}}
"""

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for strict factual adherence
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            response_text = response.text.strip() if response.text else ""
            if not response_text:
                raise GeminiParsingError("Gemini returned an empty response.")

            # Parse JSON
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as je:
                # Attempt regex cleanup if wrapped in markdown code fence
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                else:
                    raise GeminiParsingError(f"Failed to parse Gemini response as JSON: {je}")

            # Validate schema
            status = data.get("status", "insufficient_evidence")
            reference_answer = str(data.get("reference_answer", "")).strip()
            raw_concepts = data.get("concepts", [])
            source_ids = data.get("source_ids", [])
            limitations = data.get("limitations", [])

            # Filter and sanitize concepts
            parsed_concepts: List[ExpectedConcept] = []
            for c in raw_concepts:
                c_name = str(c.get("concept", "")).strip()
                if not c_name:
                    continue
                kws = [str(k).strip() for k in c.get("keywords", []) if str(k).strip()]
                weight = float(c.get("marks_weight", 1.0))
                # Validate evidence source against actual retrieved records
                ev_sources = [
                    s for s in c.get("evidence_sources", [])
                    if s in valid_source_ids
                ]
                if not ev_sources and valid_source_ids:
                    # Default to the primary retrieved record if model didn't format exact source ID
                    ev_sources = [valid_source_ids[0]]

                parsed_concepts.append(
                    ExpectedConcept(
                        concept=c_name,
                        keywords=kws,
                        marks_weight=weight,
                        evidence_sources=ev_sources
                    )
                )

            # Sanitize source_ids
            verified_sources = [s for s in source_ids if s in valid_source_ids]
            if not verified_sources:
                verified_sources = valid_source_ids

            return GeminiReferenceResult(
                status=status,
                reference_answer=reference_answer,
                concepts=parsed_concepts,
                source_ids=verified_sources,
                limitations=limitations,
                raw_response=data
            )

        except GeminiError:
            raise
        except Exception as e:
            raise GeminiAPIError(f"Gemini API request failed: {str(e)}")
