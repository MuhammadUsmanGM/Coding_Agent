"""
Response caching with simple in-memory cache
(Redis can be added later for production)
"""
import hashlib
import json
import time
from typing import Optional, Dict

class CacheManager:
    def __init__(self, ttl=3600):
        """
        Initialize cache manager
        ttl: Time to live in seconds (default 1 hour)
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = ttl
    
    def generate_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response"""
        key = self.generate_key(prompt, model)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry['timestamp'] > self.ttl:
                del self.cache[key]
                return None
            
            return entry['response']
        
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """Cache response"""
        key = self.generate_key(prompt, model)
        
        self.cache[key] = {
            'prompt': prompt,
            'response': response,
            'model': model,
            'timestamp': time.time()
        }
        
        # Limit cache size to 1000 entries
        if len(self.cache) > 1000:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
    
    def invalidate(self, prompt: str, model: str):
        """Invalidate cache for specific prompt"""
        key = self.generate_key(prompt, model)
        if key in self.cache:
            del self.cache[key]
    
    def clear_all(self):
        """Clear all cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': 1000,
            'ttl': self.ttl
        }

# Singleton
cache_manager = CacheManager()
