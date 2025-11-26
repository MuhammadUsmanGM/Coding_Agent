# src/providers/multiprovider.py

class MultiProvider:
    """
    Wrapper to automatically switch between LLM providers on quota/rate failures.
    """
    def __init__(self, providers):
        self.providers = providers  # [GroqProvider(), GoogleProvider()]
        self.current = 0
        self.use_specific = False  # Flag to use a specific provider instead of rotating

    def chat(self, messages, max_tokens=2048):
        if self.use_specific and len(self.providers) > 0:
            # Use only the current provider (specifically selected)
            try:
                return self.providers[self.current].chat(messages, max_tokens)
            except RuntimeError as e:
                raise e
        else:
            # Original behavior: try all providers in rotation
            tried = 0
            last_exception = None
            total = len(self.providers)
            while tried < total:
                try:
                    return self.providers[self.current].chat(messages, max_tokens)
                except RuntimeError as e:
                    last_exception = e
                    self.current = (self.current + 1) % total
                    tried += 1
            raise RuntimeError(f"All providers failed: {last_exception}")

    def set_provider(self, index):
        """Set a specific provider by index"""
        if 0 <= index < len(self.providers):
            self.current = index
            self.use_specific = True
        else:
            raise ValueError(f"Provider index {index} is out of range")
