# src/providers/custom.py

import os
import requests
from typing import Dict, Any, Optional
from .base import ProviderBase

class CustomProvider(ProviderBase):
    def __init__(self, name: str, api_key: str, base_url: str, model: str):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, messages, max_tokens=2048):
        """Make a request to the custom model API."""
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
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                status_code = e.response.status_code
                if status_code == 429:
                    raise RuntimeError(f"Rate limit exceeded for {self.name}")
                elif status_code == 401:
                    raise RuntimeError(f"Unauthorized access for {self.name} - check your API key")
                elif status_code == 404:
                    raise RuntimeError(f"Model {self.model} not found at {self.name}")
                else:
                    raise RuntimeError(f"API error from {self.name}: {response.text}")
            else:
                raise RuntimeError(f"Network error when connecting to {self.name}: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response format from {self.name}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error calling {self.name}: {str(e)}")