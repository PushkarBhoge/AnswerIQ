"""
Module for discovering, loading, and normalizing local .parquet datasets.
Grounded exclusively in the project's data directory.
"""

import os
import glob
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import pandas as pd


@dataclass
class DatasetRecord:
    source_id: str
    source_file: str
    row_index: int
    question: str
    answer: str
    expected_concepts: Optional[str] = None
    keywords: Optional[str] = None
    max_marks: Optional[float] = None
    rubric: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_retrieval_text(self) -> str:
        """Returns clean text representation used for indexing and similarity comparison."""
        parts = []
        if self.question:
            parts.append(f"Question: {self.question}")
        if self.answer:
            parts.append(f"Answer: {self.answer}")
        if self.expected_concepts:
            parts.append(f"Concepts: {self.expected_concepts}")
        if self.keywords:
            parts.append(f"Keywords: {self.keywords}")
        return "\n".join(parts) if parts else "No content available"


class DatasetLoaderError(Exception):
    """Raised when dataset discovery or loading fails."""
    pass


class DatasetLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.records: List[DatasetRecord] = []
        self.loaded_files: List[str] = []

    def discover_files(self) -> List[str]:
        if not os.path.exists(self.data_dir):
            raise DatasetLoaderError(
                f"Data directory '{self.data_dir}' does not exist. "
                f"Please ensure the data folder is present with at least one .parquet file."
            )
        pattern = os.path.join(self.data_dir, "*.parquet")
        files = glob.glob(pattern)
        if not files:
            raise DatasetLoaderError(
                f"No .parquet files found inside '{self.data_dir}'. "
                f"Please place your dataset (.parquet) inside the data folder."
            )
        return sorted(files)

    def _normalize_column_name(self, col: str) -> str:
        return col.strip().lower().replace(" ", "_").replace("-", "_")

    def _find_column(self, df_cols: Dict[str, str], candidates: List[str]) -> Optional[str]:
        for candidate in candidates:
            if candidate in df_cols:
                return df_cols[candidate]
        return None

    def load_dataset(self) -> List[DatasetRecord]:
        files = self.discover_files()
        records: List[DatasetRecord] = []
        loaded_files: List[str] = []

        for file_path in files:
            file_name = os.path.basename(file_path)
            try:
                df = pd.read_parquet(file_path)
            except Exception as e:
                # Log or handle corrupted file without crashing entire loader
                print(f"[DatasetLoader] Warning: Failed to read {file_name}: {e}")
                continue

            if df.empty:
                continue

            normalized_col_map = {self._normalize_column_name(c): c for c in df.columns}

            # Map possible column candidates
            q_col = self._find_column(normalized_col_map, ["question", "prompt", "query", "input", "problem"])
            a_col = self._find_column(normalized_col_map, ["answer", "reference_answer", "response", "output", "completion", "context", "text", "content"])
            concepts_col = self._find_column(normalized_col_map, ["expected_concepts", "concepts", "key_concepts", "rubric_concepts"])
            keywords_col = self._find_column(normalized_col_map, ["keywords", "key_terms", "terms", "tags"])
            marks_col = self._find_column(normalized_col_map, ["max_marks", "marks", "points", "total_marks"])
            rubric_col = self._find_column(normalized_col_map, ["rubric", "scoring_guide", "criteria"])

            for idx, row in df.iterrows():
                # Extract question
                raw_q = row[q_col] if q_col and pd.notna(row[q_col]) else ""
                q_text = str(raw_q).strip()

                # Extract answer / context
                raw_a = row[a_col] if a_col and pd.notna(row[a_col]) else ""
                a_text = str(raw_a).strip()

                # If no explicit question but answer/text chunk exists, use truncated text as fallback question representation
                if not q_text and a_text:
                    q_text = a_text[:120] + "..." if len(a_text) > 120 else a_text

                # Skip completely blank rows
                if not q_text and not a_text:
                    continue

                # Concepts
                exp_concepts = None
                if concepts_col and pd.notna(row[concepts_col]):
                    val = row[concepts_col]
                    exp_concepts = ", ".join(val) if isinstance(val, (list, tuple)) else str(val).strip()

                # Keywords
                kw = None
                if keywords_col and pd.notna(row[keywords_col]):
                    val = row[keywords_col]
                    kw = ", ".join(val) if isinstance(val, (list, tuple)) else str(val).strip()

                # Max marks
                max_m = None
                if marks_col and pd.notna(row[marks_col]):
                    try:
                        max_m = float(row[marks_col])
                    except (ValueError, TypeError):
                        max_m = None

                # Rubric
                rub = None
                if rubric_col and pd.notna(row[rubric_col]):
                    rub = str(row[rubric_col]).strip()

                source_id = f"{file_name}:row-{idx}"

                records.append(
                    DatasetRecord(
                        source_id=source_id,
                        source_file=file_name,
                        row_index=int(idx),
                        question=q_text,
                        answer=a_text,
                        expected_concepts=exp_concepts,
                        keywords=kw,
                        max_marks=max_m,
                        rubric=rub,
                        raw_metadata={k: str(v) for k, v in row.to_dict().items() if pd.notna(v)}
                    )
                )

            loaded_files.append(file_name)

        if not records:
            raise DatasetLoaderError(
                f"No usable records found across discovered parquet files: {files}. "
                f"Please ensure the files contain recognizable text/question/answer columns."
            )

        self.records = records
        self.loaded_files = loaded_files
        return records

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_records": len(self.records),
            "files": self.loaded_files,
            "data_directory": self.data_dir
        }
