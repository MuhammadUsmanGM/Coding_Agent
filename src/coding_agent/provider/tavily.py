# src/providers/tavily.py

import os
import requests
from typing import Dict, Optional
from functools import lru_cache
import hashlib

class TavilyWebSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        # Cache to store search results
        self._cache = {}

    def _generate_cache_key(self, query: str, max_results: int) -> str:
        """Generate a cache key based on query and max_results."""
        key_string = f"{query}_{max_results}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def search(self, query: str, max_results: int = 3) -> str:
        """Performs a web search and returns summarized snippets."""
        cache_key = self._generate_cache_key(query, max_results)
        
        # Check if result is already in cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        url = "https://api.tavily.com/search"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "query": query,
            "max_results": max_results,
            "include_links": True,
            "include_answer": True
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # Return the summary plus top links (adjust as per actual API response)
            answer = data.get("answer", "")
            links = "\n".join([result['url'] for result in data.get("results", [])])
            result = f"{answer}\n\nTop Links:\n{links}"
            
            # Cache the result
            self._cache[cache_key] = result
            return result
        except requests.exceptions.RequestException as e:
            error_msg = f"Error performing web search: {str(e)}"
            # Cache error results briefly to avoid repeated failed requests
            self._cache[cache_key] = error_msg
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error in web search: {str(e)}"
            self._cache[cache_key] = error_msg
            return error_msg
