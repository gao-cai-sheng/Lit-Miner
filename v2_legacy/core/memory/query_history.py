
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

HISTORY_FILE = Path("data/query_history.json")

class QueryHistory:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        """Ensure the history file exists"""
        if not HISTORY_FILE.parent.exists():
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load(self) -> List[Dict]:
        """Load history from file"""
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, history: List[Dict]):
        """Save history to file"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def add_entry(self, query: str, papers_count: int, tags: List[str] = None):
        """Add a new query entry"""
        history = self._load()
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "papers_count": papers_count,
            "tags": tags or [],
            "status": "completed"
        }
        
        # Insert at beginning
        history.insert(0, entry)
        
        # Keep last 100 entries
        if len(history) > 100:
            history = history[:100]
            
        self._save(history)
        return entry

    def get_entries(self, limit: int = 20) -> List[Dict]:
        """Get recent entries"""
        history = self._load()
        return history[:limit]

    def clear(self):
        """Clear all history"""
        self._save([])

    def delete_entry(self, entry_id: str):
        """Delete a specific entry"""
        history = self._load()
        history = [h for h in history if h["id"] != entry_id]
        self._save(history)
