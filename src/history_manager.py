"""
History Manager module for AnswerIQ.
Saves and retrieves student answer evaluations persistently in data/history.json.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

HISTORY_FILE = os.path.join("data", "history.json")


class HistoryManager:
    def __init__(self, file_path: str = HISTORY_FILE):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_all(self) -> List[Dict[str, Any]]:
        """Loads all history records, newest first."""
        self._ensure_file_exists()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Sort descending by timestamp
                    return sorted(data, key=lambda x: x.get("timestamp_epoch", 0), reverse=True)
                return []
        except Exception as e:
            print(f"[HistoryManager] Error reading {self.file_path}: {e}")
            return []

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Finds a specific evaluation record by ID."""
        records = self.load_all()
        for r in records:
            if r.get("id") == record_id:
                return r
        return None

    def save_record(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Saves an evaluation result to the JSON history.
        Returns the generated record ID.
        """
        records = self.load_all()

        now = datetime.now()
        timestamp_epoch = time.time()
        record_id = f"eval_{int(timestamp_epoch)}_{len(records) + 1}"

        # Create compact summary for listing in addition to full payload
        history_item = {
            "id": record_id,
            "timestamp": now.strftime("%b %d, %Y • %I:%M %p"),
            "timestamp_epoch": timestamp_epoch,
            "question": evaluation_result.get("question", ""),
            "student_answer": evaluation_result.get("student_answer", ""),
            "max_marks": evaluation_result.get("max_marks", 0.0),
            "awarded_marks": evaluation_result.get("awarded_marks", 0.0),
            "percentage_score": evaluation_result.get("percentage_score", 0.0),
            "status": evaluation_result.get("status", "insufficient_evidence"),
            "status_message": evaluation_result.get("status_message", ""),
            "evaluation_result": evaluation_result
        }

        records.insert(0, history_item)

        # Cap history to most recent 100 entries to prevent unbounded growth
        if len(records) > 100:
            records = records[:100]

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[HistoryManager] Error writing to {self.file_path}: {e}")

        return record_id

    def clear_all(self) -> bool:
        """Clears all history entries."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            return True
        except Exception as e:
            print(f"[HistoryManager] Error clearing history: {e}")
            return False
