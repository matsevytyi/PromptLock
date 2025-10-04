from MainLLM import RealLLMClient

def create_llm_client(provider: str, **kwargs) -> RealLLMClient:
    """
    Factory function to create LLM clients with recommended configurations.

    Examples:
        # Local Ollama
        client = create_llm_client("ollama", model="deepseek-coder:6.7b")

        # GitHub Models (free)
        client = create_llm_client("github", api_key="github_pat_xxx", model="gpt-4o-mini")

        # Groq (fast)
        client = create_llm_client("groq", api_key="gsk_xxx", model="llama-3.1-8b-instant")

        # OpenRouter (variety)
        client = create_llm_client("openrouter", api_key="sk-or-xxx", model="meta-llama/llama-3.1-8b-instruct:free")

        # LM Studio (local GUI)
        client = create_llm_client("lmstudio", model="deepseek-coder")
    """

    recommended_models = {
        "ollama": "deepseek-coder:6.7b",
        "github": "gpt-4o-mini", 
        "groq": "llama-3.1-8b-instant",
        "openrouter": "meta-llama/llama-3.1-8b-instruct:free",
        "lmstudio": "deepseek-coder",
        "openai": "gpt-4o-mini"
    }

    if "model" not in kwargs:
        kwargs["model"] = recommended_models.get(provider.lower(), "default")

    return RealLLMClient(provider=provider, **kwargs)