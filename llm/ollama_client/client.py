import httpx

from backend.config import get_settings


class OllamaClient:
    async def generate(self, prompt: str, model: str | None = None) -> str:
        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={"model": model or settings.ollama_model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception:
            return (
                "Narrative unavailable from local Ollama. Review the top risk features "
                "and graph links shown in the case workspace."
            )
