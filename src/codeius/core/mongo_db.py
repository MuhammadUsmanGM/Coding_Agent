import os
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Optional, Any
import uuid

class MongoManager:
    """Manages MongoDB connection and operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.sessions = None
        
    def connect(self, uri: str = "mongodb://localhost:27017/codeius"):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(uri)
            self.db = self.client.get_default_database()
            self.users = self.db.users
            self.sessions = self.db.sessions
            
            # Create indexes
            self.users.create_index("username", unique=True)
            self.users.create_index("email", unique=True)
            self.sessions.create_index("user_id")
            self.sessions.create_index("updated_at")
            
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {str(e)}")
            # Fallback or re-raise depending on requirements
            raise e

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email"""
        if self.users is None: return None
        return self.users.find_one({"email": email})

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Find user by ID"""
        if self.users is None: return None
        return self.users.find_one({"id": user_id})

    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        if self.users is None: return None
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        new_user = {
            "id": user_id,
            "email": user_data.get("email"),
            "username": user_data.get("username", user_data.get("email").split("@")[0]),
            "picture": user_data.get("picture"),
            "created_at": now,
            "updated_at": now,
            "settings": {},
            "api_keys": {} # Encrypted keys
        }
        
        self.users.insert_one(new_user)
        return new_user

    def update_user_settings(self, user_id: str, settings: Dict) -> bool:
        """Update user settings"""
        if self.users is None: return False
        
        result = self.users.update_one(
            {"id": user_id},
            {"$set": {"settings": settings, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # Session management methods can be added here
    # ...

# Singleton instance
mongo_manager = MongoManager()
