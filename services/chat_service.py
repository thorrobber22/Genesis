"""
Chat Service - Manages chat sessions and history
Date: 2025-06-07 14:02:41 UTC
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class ChatService:
    """Manage chat sessions and history"""
    
    def __init__(self):
        self.sessions_file = Path("data/chat_sessions.json")
        self.sessions = self._load_sessions()
    
    def _load_sessions(self) -> Dict:
        """Load chat sessions from file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_sessions(self):
        """Save chat sessions to file"""
        try:
            self.sessions_file.parent.mkdir(exist_ok=True)
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def create_session(self, title: Optional[str] = None) -> str:
        """Create new chat session"""
        session_id = datetime.now().isoformat()
        
        self.sessions[session_id] = {
            'id': session_id,
            'title': title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'created': session_id,
            'messages': [],
            'metadata': {}
        }
        
        self._save_sessions()
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to session"""
        if session_id not in self.sessions:
            session_id = self.create_session()
        
        message = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        
        self.sessions[session_id]['messages'].append(message)
        self._save_sessions()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get specific session"""
        return self.sessions.get(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent chat sessions"""
        sorted_sessions = sorted(
            self.sessions.values(),
            key=lambda x: x['created'],
            reverse=True
        )
        return sorted_sessions[:limit]
    
    def delete_session(self, session_id: str):
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
    
    def search_sessions(self, query: str) -> List[Dict]:
        """Search through all chat sessions"""
        results = []
        query_lower = query.lower()
        
        for session in self.sessions.values():
            # Search in messages
            for message in session['messages']:
                if query_lower in message['content'].lower():
                    results.append({
                        'session': session,
                        'message': message,
                        'match_type': 'content'
                    })
                    break
            
            # Search in title
            if query_lower in session['title'].lower():
                results.append({
                    'session': session,
                    'match_type': 'title'
                })
        
        return results
