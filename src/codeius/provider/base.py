# src/providers/base.py

class ProviderBase:
    """
    Abstract base class for LLM providers.
    """
    def chat(self, messages, max_tokens=2048):
        raise NotImplementedError("Subclasses must implement chat()")
