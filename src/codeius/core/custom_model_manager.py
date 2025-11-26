"""
Custom Model Manager for Codeius AI Coding Agent
Handles user-added custom models
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path


class CustomModelManager:
    """
    Manages user-added custom models, storing them in a JSON file
    and providing methods to add, retrieve, and manage them.
    """
    
    def __init__(self, models_file: str = "custom_models.json"):
        self.models_file = models_file
        self.custom_models = self.load_custom_models()

    def load_custom_models(self) -> Dict[str, Dict[str, str]]:
        """Load custom models from the JSON file."""
        if os.path.exists(self.models_file):
            try:
                with open(self.models_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_custom_models(self):
        """Save custom models to the JSON file."""
        try:
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_models, f, indent=2)
        except IOError as e:
            print(f"Error saving custom models: {e}")

    def add_model(self, name: str, api_key: str, base_url: str, model: str) -> bool:
        """Add a new custom model."""
        # Validate required fields
        if not all([name, api_key, base_url, model]):
            return False

        # Store the model details
        self.custom_models[name] = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
        
        # Save to file
        self.save_custom_models()
        return True

    def get_model(self, name: str) -> Optional[Dict[str, str]]:
        """Get details for a specific custom model."""
        return self.custom_models.get(name)

    def list_models(self) -> List[str]:
        """List all custom model names."""
        return list(self.custom_models.keys())

    def remove_model(self, name: str) -> bool:
        """Remove a custom model."""
        if name in self.custom_models:
            del self.custom_models[name]
            self.save_custom_models()
            return True
        return False

    def update_model(self, name: str, api_key: Optional[str] = None, 
                     base_url: Optional[str] = None, model: Optional[str] = None) -> bool:
        """Update an existing custom model."""
        if name not in self.custom_models:
            return False

        if api_key is not None:
            self.custom_models[name]["api_key"] = api_key
        if base_url is not None:
            self.custom_models[name]["base_url"] = base_url
        if model is not None:
            self.custom_models[name]["model"] = model

        self.save_custom_models()
        return True


# Global instance of the custom model manager
custom_model_manager = CustomModelManager()