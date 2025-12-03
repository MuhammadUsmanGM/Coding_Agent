"""
Context manager for intelligent context window management.
"""
import re
from typing import List, Dict

class ContextManager:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count (approximation: 4 chars per token)
        For production, use tiktoken library
        """
        return len(text) // 4
    
    def truncate_context(self, messages: List[Dict], max_tokens: int = None) -> List[Dict]:
        """Truncate messages to fit within token limit, keeping most recent"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        total_tokens = 0
        truncated = []
        
        # Keep most recent messages
        for msg in reversed(messages):
            content = msg.get('content', '') or str(msg)
            msg_tokens = self.count_tokens(content)
            
            if total_tokens + msg_tokens > max_tokens:
                break
            
            truncated.insert(0, msg)
            total_tokens += msg_tokens
        
        return truncated
    
    def summarize_conversation(self, messages: List[Dict], max_length=200) -> str:
        """Generate a conversation summary"""
        if not messages:
            return "Empty conversation"
        
        if len(messages) <= 3:
            first_msg = messages[0].get('user', '')[:100]
            return f"Chat about: {first_msg}"
        
        first_topic = messages[0].get('user', '')[:80]
        last_topic = messages[-1].get('user', '')[:80]
        
        summary = f"Conversation with {len(messages)} exchanges. "
        summary += f"Started: {first_topic}... "
        summary += f"Recent: {last_topic}..."
        
        return summary[:max_length]
    
    def select_relevant_context(self, current_query: str, history: List[Dict], 
                               max_tokens: int = 2000) -> List[Dict]:
        """
        Select most relevant messages from history
        Uses simple keyword matching
        """
        if not history:
            return []
        
        query_words = set(current_query.lower().split())
        
        # Score each message by keyword overlap
        scored_messages = []
        for msg in history:
            user_text = msg.get('user', '').lower()
            ai_text = msg.get('ai', '').lower()
            all_text = user_text + ' ' + ai_text
            
            msg_words = set(all_text.split())
            overlap = len(query_words & msg_words)
            
            scored_messages.append((overlap, msg))
        
        # Sort by relevance
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        
        # Select messages until token limit
        selected = []
        total_tokens = 0
        
        for score, msg in scored_messages:
            content = msg.get('user', '') + msg.get('ai', '')
            msg_tokens = self.count_tokens(content)
            
            if total_tokens + msg_tokens > max_tokens:
                break
            
            selected.append(msg)
            total_tokens += msg_tokens
        
        # Return in chronological order
        return sorted(selected, key=lambda x: history.index(x))

# Singleton instance
context_manager = ContextManager()
