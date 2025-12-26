"""
Conversation Manager - Handle multi-turn dialogue state
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ConversationManager:
    """Manage conversation history and state"""
    
    def __init__(self, storage_dir: str = "data/conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[Dict] = None
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        return session_id
    
    def add_message(
        self,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None
    ):
        """Add a message to current session"""
        if not self.current_session:
            self.create_session()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if sources:
            message["sources"] = sources
        
        self.current_session["messages"].append(message)
    
    def get_history(self, last_n: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        if not self.current_session:
            return []
        
        messages = self.current_session["messages"]
        return messages[-last_n:] if len(messages) > last_n else messages
    
    def save_session(self):
        """Save current session to disk"""
        if not self.current_session:
            return
        
        session_id = self.current_session["session_id"]
        file_path = self.storage_dir / f"{session_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)
    
    def load_session(self, session_id: str) -> bool:
        """Load a saved session"""
        file_path = self.storage_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.current_session = json.load(f)
        
        return True
    
    def list_sessions(self) -> List[Dict]:
        """List all saved sessions"""
        sessions = []
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    sessions.append({
                        "session_id": session["session_id"],
                        "created_at": session["created_at"],
                        "message_count": len(session["messages"])
                    })
            except Exception:
                continue
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return sessions
    
    def clear_current_session(self):
        """Clear current session (start fresh)"""
        self.current_session = None
    
    def get_session_summary(self) -> Optional[str]:
        """Get a brief summary of current session"""
        if not self.current_session or not self.current_session["messages"]:
            return None
        
        first_user_msg = next(
            (m["content"] for m in self.current_session["messages"] if m["role"] == "user"),
            None
        )
        
        if first_user_msg:
            # Return first 50 chars of first question
            return first_user_msg[:50] + ("..." if len(first_user_msg) > 50 else "")
        
        return "New conversation"


if __name__ == "__main__":
    # Test conversation manager
    manager = ConversationManager()
    
    # Create session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")
    
    # Add messages
    manager.add_message("user", "What causes periodontitis?")
    manager.add_message("assistant", "Based on the literature...", sources=[{"title": "Paper 1"}])
    manager.add_message("user", "How to treat it?")
    
    # Get history
    history = manager.get_history()
    print(f"\nHistory ({len(history)} messages):")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Save
    manager.save_session()
    print(f"\nSession saved to: {manager.storage_dir / f'{session_id}.json'}")
    
    # List sessions
    sessions = manager.list_sessions()
    print(f"\nAll sessions: {len(sessions)}")
