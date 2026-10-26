"""
Semantic similarity module using sentence-transformers and cosine similarity.
Includes lazy loading, singleton caching, and robust fallback mechanisms.
"""

import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticMatcher:
    _instance = None
    _model = None
    _model_name = None
    _is_fallback = False

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = os.getenv("SEMANTIC_SIMILARITY_MODEL", model_name)
        self._initialize_model()

    @classmethod
    def get_instance(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    def _initialize_model(self):
        """Attempts to load SentenceTransformer; falls back gracefully if unavailable."""
        if SemanticMatcher._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            # Suppress excessive warning logs
            model = SentenceTransformer(self.model_name)
            SemanticMatcher._model = model
            SemanticMatcher._model_name = self.model_name
            SemanticMatcher._is_fallback = False
        except Exception as e:
            print(f"[SemanticMatcher] Notice: sentence-transformers neural model not loaded ({e}). "
                  f"Using robust TF-IDF semantic approximation fallback.")
            SemanticMatcher._is_fallback = True

    def _split_into_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        # Split on period, question mark, exclamation, or semicolon followed by whitespace/newline
        raw_sentences = re.split(r"(?<=[.?!;])\s+|\n+", text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]
        return sentences if sentences else [text.strip()]

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Computes cosine similarity between two text snippets."""
        t1, t2 = str(text1).strip(), str(text2).strip()
        if not t1 or not t2:
            return 0.0

        if not SemanticMatcher._is_fallback and SemanticMatcher._model is not None:
            try:
                embeddings = SemanticMatcher._model.encode([t1, t2], convert_to_numpy=True)
                sim = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
                return max(0.0, min(1.0, sim))
            except Exception:
                pass

        # TF-IDF Cosine Similarity Fallback
        try:
            vec = TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb")
            tfidf = vec.fit_transform([t1, t2])
            sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            return max(0.0, min(1.0, sim))
        except Exception:
            return 0.0

    def evaluate_concept_match(self, concept: str, student_answer: str) -> Dict[str, Any]:
        """
        Evaluates how well a specific expected concept is covered in the student answer.
        Compares both against individual student sentences and the full answer.
        """
        student_clean = str(student_answer).strip()
        if not student_clean:
            return {
                "similarity_score": 0.0,
                "best_matching_sentence": "",
                "is_covered": False
            }

        # 1. Whole answer similarity
        whole_sim = self.compute_similarity(concept, student_clean)

        # 2. Sentence-level granular similarity
        sentences = self._split_into_sentences(student_clean)
        best_sentence = ""
        best_sentence_sim = 0.0

        for s in sentences:
            sim = self.compute_similarity(concept, s)
            if sim > best_sentence_sim:
                best_sentence_sim = sim
                best_sentence = s

        # Combine whole-answer context and granular sentence match
        final_score = max(whole_sim * 0.85, best_sentence_sim)

        return {
            "similarity_score": round(final_score, 4),
            "best_matching_sentence": best_sentence if best_sentence_sim > 0.25 else "",
            "is_covered": final_score >= 0.45
        }
