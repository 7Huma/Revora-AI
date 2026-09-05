class LLMClient:
    """
    Lightweight LLM client abstraction.

    The default implementation is a deterministic mock so the
    application can run locally without an external LLM provider.
    """

    def __init__(self, provider: str = "mock", api_key: str = ""):
        self.provider = provider
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the configured provider.

        The current version uses a mock response. A real provider
        can be added later without changing callers of this class.
        """

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        return "Demo AI response. Connect an LLM provider for production reasoning."