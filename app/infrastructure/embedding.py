"""Embedding service abstraction layer."""

from abc import ABC, abstractmethod

import httpx
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...

    async def embed_single(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider using Ollama's local REST API."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        results = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model, "input": text},
                )
                response.raise_for_status()
                data = response.json()
                results.append(data["embeddings"][0])
        return results


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Factory function to create the configured embedding provider."""
    if settings.EMBEDDING_PROVIDER == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.EMBEDDING_MODEL,
        )
    if settings.EMBEDDING_PROVIDER == "deepseek":
        return OpenAIEmbeddingProvider(
            api_key=settings.DEEPSEEK_API_KEY,
            model=settings.EMBEDDING_MODEL,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    return OpenAIEmbeddingProvider(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OPENAI_BASE_URL,
    )
