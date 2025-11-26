# src/providers/groq.py

import os
import requests
from .base import ProviderBase
from codeius.core.performance import rate_limit

class GroqProvider(ProviderBase):
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.model = model or os.getenv("GROQ_API_MODEL", "llama3-70b-8192")

    @rate_limit(max_calls=10, time_window=60) # 10 calls per minute
    def chat(self, messages, max_tokens=2048):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        response = requests.post(url, headers=headers, json=payload)
        try:
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if response.status_code == 429 or "rate limit" in response.text.lower():
                raise RuntimeError("Groq quota/rate limit exceeded")
            raise RuntimeError(f"Groq API error: {e}")
