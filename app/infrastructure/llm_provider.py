"""Pluggable LLM Provider abstraction layer."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Send messages and return the complete response."""
        ...

    @abstractmethod
    async def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        """Send messages and yield response chunks."""
        ...


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


def get_llm_provider() -> BaseLLMProvider:
    """Factory function to create the configured LLM provider."""
    if settings.LLM_PROVIDER == "deepseek":
        return DeepSeekProvider(
            api_key=settings.DEEPSEEK_API_KEY,
            model=settings.DEEPSEEK_MODEL,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    # Default to OpenAI
    return OpenAIProvider(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        base_url=settings.OPENAI_BASE_URL,
    )
