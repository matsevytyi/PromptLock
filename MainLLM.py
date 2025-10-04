from typing import Dict, Any, List
import requests
import datetime

class RealLLMClient:
    """
    Real LLM client supporting multiple providers:
    - Ollama (local)
    - GitHub Models (remote)
    - Groq (remote)
    - OpenRouter (remote)
    - LM Studio (local)
    - OpenAI (remote)
    """

    def __init__(self, provider="ollama", **kwargs):
        self.provider = provider.lower()
        self.session_count = 0
        self.generation_history = []

        # Provider-specific configuration
        if self.provider == "ollama":
            self.base_url = kwargs.get("base_url", "http://localhost:11434")
            self.model = kwargs.get("model", "deepseek-coder:6.7b")
            self.api_key = None

        elif self.provider == "github":
            self.base_url = "https://models.github.ai/inference"
            self.api_key = kwargs.get("api_key")
            self.model = kwargs.get("model", "gpt-4o-mini")
            if not self.api_key:
                raise ValueError("GitHub Models requires api_key (GitHub PAT)")

        elif self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
            self.api_key = kwargs.get("api_key")
            self.model = kwargs.get("model", "llama-3.1-8b-instant")
            if not self.api_key:
                raise ValueError("Groq requires api_key")

        elif self.provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = kwargs.get("api_key")
            self.model = kwargs.get("model", "meta-llama/llama-3.1-8b-instruct:free")
            if not self.api_key:
                raise ValueError("OpenRouter requires api_key")

        elif self.provider == "lmstudio":
            self.base_url = kwargs.get("base_url", "http://127.0.0.1:1234/v1")
            self.model = kwargs.get("model", "deepseek-coder")
            self.api_key = None

        elif self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            self.api_key = kwargs.get("api_key")
            self.model = kwargs.get("model", "gpt-4o-mini")
            if not self.api_key:
                raise ValueError("OpenAI requires api_key")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using the configured LLM provider."""
        self.session_count += 1

        try:
            if self.provider == "ollama":
                response = self._ollama_generate(prompt, **kwargs)
            else:
                response = self._openai_compatible_generate(prompt, **kwargs)

            # Store generation history
            self.generation_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": self.provider,
                "model": self.model,
                "prompt_length": len(prompt),
                "response_length": len(response["response"]),
                "success": True
            })

            return response

        except Exception as e:
            # Log failed generation
            self.generation_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "provider": self.provider,
                "model": self.model,
                "prompt_length": len(prompt),
                "error": str(e),
                "success": False
            })
            raise

    def _ollama_generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate using Ollama API."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate", 
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 4000),
                        "top_p": kwargs.get("top_p", 0.9)
                    }
                },
                timeout=kwargs.get("timeout", 120)
            )
            response.raise_for_status()
            return {"response": response.json()["response"]}

        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")

    def _openai_compatible_generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate using OpenAI-compatible API."""
        headers = {
            "Content-Type": "application/json",
        }

        # Add authentication headers based on provider
        if self.provider in ["github", "groq", "openrouter", "openai"]:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Special headers for specific providers
        if self.provider == "github":
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        elif self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/your-repo"  # Required by OpenRouter

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000),
            "top_p": kwargs.get("top_p", 0.9)
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=kwargs.get("timeout", 120)
            )
            response.raise_for_status()

            result = response.json()
            return {"response": result["choices"][0]["message"]["content"]}

        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to {self.provider} at {self.base_url}")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"{self.provider} request timed out")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError(f"Invalid API key for {self.provider}")
            elif response.status_code == 403:
                raise ValueError(f"Access forbidden - check your {self.provider} permissions")
            elif response.status_code == 429:
                raise ValueError(f"Rate limit exceeded for {self.provider}")
            else:
                raise RuntimeError(f"{self.provider} API error: {e}")
        except Exception as e:
            raise RuntimeError(f"{self.provider} generation failed: {e}")

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about generation history."""
        successful_generations = [g for g in self.generation_history if g.get("success", False)]
        failed_generations = [g for g in self.generation_history if not g.get("success", False)]

        stats = {
            "provider": self.provider,
            "model": self.model,
            "total_generations": self.session_count,
            "successful_generations": len(successful_generations),
            "failed_generations": len(failed_generations),
            "success_rate": len(successful_generations) / self.session_count if self.session_count > 0 else 0,
        }

        if successful_generations:
            avg_prompt_length = sum(g["prompt_length"] for g in successful_generations) / len(successful_generations)
            avg_response_length = sum(g["response_length"] for g in successful_generations) / len(successful_generations)

            stats.update({
                "avg_prompt_length": avg_prompt_length,
                "avg_response_length": avg_response_length,
                "last_successful": successful_generations[-1]["timestamp"]
            })

        if failed_generations:
            stats["recent_errors"] = [g["error"] for g in failed_generations[-3:]]

        return stats

    def test_connection(self) -> bool:
        """Test if the LLM provider is accessible."""
        try:
            test_response = self.generate("Hello, respond with 'OK'", timeout=30)
            return "response" in test_response and len(test_response["response"]) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
