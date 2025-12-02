"""
Database manager for conversation history and session management.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class ConversationDB:
    def __init__(self, db_path='conversations.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                token_count INTEGER,
                model_used TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME,
                title TEXT,
                summary TEXT
            )
        ''')
        
        # Create indices for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON conversations(session_id, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_active_sessions ON sessions(last_active DESC)')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, session_id: str, user_message: str, ai_response: str, 
                         token_count: int = 0, model_used: str = 'default'):
        """Save a conversation exchange"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (session_id, user_message, ai_response, token_count, model_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_message, ai_response, token_count, model_used))
        
        # Update session last_active
        cursor.execute('''
            INSERT INTO sessions (session_id, last_active)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET last_active = ?
        ''', (session_id, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, ai_response, timestamp, model_used, token_count
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'user': row[0],
                'ai': row[1],
                'timestamp': row[2],
                'model': row[3],
                'tokens': row[4]
            })
        
        conn.close()
        return messages
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, created_at, last_active, title, summary
            FROM sessions
            ORDER BY last_active DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'created': row[1],
                'last_active': row[2],
                'title': row[3] or f"Session {row[0][:8]}",
                'summary': row[4] or 'No summary'
            })
        
        conn.close()
        return sessions
    
    def update_session_summary(self, session_id: str, summary: str, title: str = None):
        """Update session summary and title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if title:
            cursor.execute('''
                UPDATE sessions
                SET summary = ?, title = ?
                WHERE session_id = ?
            ''', (summary, title, session_id))
        else:
            cursor.execute('''
                UPDATE sessions
                SET summary = ?
                WHERE session_id = ?
            ''', (summary, session_id))
        
        conn.commit()
        conn.close()
    
    def get_session_summary(self, session_id: str) -> Optional[str]:
        """Get summary for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT summary FROM sessions WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None

    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for messages matching the query across all sessions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use LIKE for simple search (can upgrade to FTS5 later)
        search_term = f"%{query}%"
        
        cursor.execute('''
            SELECT 
                c.id, c.session_id, c.user_message, c.ai_response, c.timestamp,
                s.title as session_name
            FROM conversations c
            JOIN sessions s ON c.session_id = s.session_id
            WHERE c.user_message LIKE ? OR c.ai_response LIKE ?
            ORDER BY c.timestamp DESC
            LIMIT ?
        ''', (search_term, search_term, limit))
        
        results = []
        for row in cursor.fetchall():
            # Add user message match
            if query.lower() in row[2].lower():
                results.append({
                    'id': row[0],
                    'session_id': row[1],
                    'text': row[2],
                    'sender': 'user',
                    'timestamp': row[4],
                    'session_name': row[5]
                })
            
            # Add AI response match
            if query.lower() in row[3].lower():
                results.append({
                    'id': f"{row[0]}_ai",
                    'session_id': row[1],
                    'text': row[3],
                    'sender': 'ai',
                    'timestamp': row[4],
                    'session_name': row[5]
                })
                
        conn.close()
        return results[:limit]  # Re-limit after splitting
    
    def delete_session(self, session_id: str):
        """Delete a session and its conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        
        conn.commit()
        conn.close()

# Singleton instance
conversation_db = ConversationDB()
