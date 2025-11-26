# src/providers/google.py

import os
import requests
from .base import ProviderBase
from codeius.core.performance import rate_limit

class GoogleProvider(ProviderBase):
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.base_url = base_url or os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.model = model or os.getenv("GOOGLE_API_MODEL", "gemini-1.5-flash")

    @rate_limit(max_calls=10, time_window=60) # 10 calls per minute
    def chat(self, messages, max_tokens=2048):
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        # Convert OpenAI-style messages to Gemini content objects
        contents = []
        for m in messages:
            # Gemini only cares about user and "content"
            if m["role"] == "user":
                contents.append({"parts": [{"text": m["content"]}], "role": "user"})
            elif m["role"] == "system":
                # Optionally include, or skip
                contents.append({"parts": [{"text": m["content"]}], "role": "user"})
            else:
                # Gemini doesn't support assistant role in the input
                continue

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens
            }
        }
        response = requests.post(url, json=payload)
        try:
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if response.status_code == 429 or "rate limit" in response.text.lower():
                raise RuntimeError("Google quota/rate limit exceeded")
            raise RuntimeError(f"Google API error: {e}")
