"""
Conversation management service for the CodingAgent.
Separates the conversation handling logic from the main agent class.
"""
from typing import Dict, Any, List, Optional
from coding_agent.history_manager import HistoryManager
from coding_agent.config import config_manager
from coding_agent.logger import agent_logger


class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.history_manager = HistoryManager()
        self.config = config_manager.get_agent_config()
        
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.history.append({"role": role, "content": content})
        
        # Apply history limit to prevent memory issues
        if len(self.history) > self.config.conversation_history_limit:
            self.history = self.history[-self.config.conversation_history_limit:]
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get the current conversation context with system prompt."""
        return self.history[:]
    
    def reset_history(self) -> None:
        """Reset the conversation history."""
        self.history = []
        agent_logger.app_logger.info("Conversation history reset")
        
    def save_conversation(self, user_input: str, agent_response: str) -> None:
        """Save the conversation to persistent storage."""
        self.history_manager.save_conversation(user_input, agent_response)