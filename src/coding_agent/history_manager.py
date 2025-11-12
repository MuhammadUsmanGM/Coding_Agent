"""
Module for managing conversation history
"""
import os
import datetime
from pathlib import Path
from typing import Dict, Any


class HistoryManager:
    """Manages saving and loading conversation history"""
    
    def __init__(self, history_dir: str = "history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
    
    def save_conversation(self, prompt: str, response: str) -> str:
        """
        Save a conversation (prompt and response) to a text file
        Returns the path of the created file
        """
        # Create a filename based on timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"conversation_{timestamp}.txt"
        filepath = self.history_dir / filename
        
        # Write the prompt and response to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Prompt:\n{prompt}\n")
            f.write(f"Response:\n{response}\n")
        
        return str(filepath)
    
    def get_recent_conversations(self, limit: int = 10) -> list:
        """Get a list of recent conversation files"""
        files = list(self.history_dir.glob("conversation_*.txt"))
        # Sort by modification time, newest first
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return [str(f) for f in files[:limit]]
    
    def load_conversation(self, filepath: str) -> Dict[str, Any]:
        """Load a conversation from a file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing - in a more sophisticated implementation, 
        # you might want to use a more structured format
        lines = content.split('\n')
        timestamp = "Unknown"
        prompt = ""
        response = ""
        
        current_section = None
        for line in lines:
            if line.startswith("Timestamp:"):
                timestamp = line.split(":", 1)[1].strip()
            elif line == "Prompt:":
                current_section = "prompt"
            elif line == "Response:":
                current_section = "response"
            elif current_section == "prompt":
                prompt += line + "\n"
            elif current_section == "response":
                response += line + "\n"
        
        return {
            "timestamp": timestamp,
            "prompt": prompt.strip(),
            "response": response.strip(),
            "filepath": filepath
        }