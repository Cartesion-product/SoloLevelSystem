"""Pluggable LLM Provider abstraction layer."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()


def get_chat_model(provider: str | None = None, **kwargs):
    """Factory for LangChain ChatModel instances (used by v2 Agent nodes).

    Args:
        provider: Override provider name. Defaults to config LLM_PROVIDER.
        **kwargs: Extra kwargs forwarded to the ChatModel constructor
                  (e.g. temperature, model).
    """
    provider = provider or settings.LLM_PROVIDER

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=kwargs.pop("model", settings.ANTHROPIC_MODEL),
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            **kwargs,
        )
    if provider == "deepseek":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=kwargs.pop("model", settings.DEEPSEEK_MODEL),
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            **kwargs,
        )
    # Default: openai
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=kwargs.pop("model", settings.OPENAI_MODEL),
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        **kwargs,
    )


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


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str):
        import anthropic
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        # Anthropic expects system prompt separately
        system = None
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_messages.append(m)

        params: dict[str, Any] = {
            "model": self.model,
            "messages": user_messages or [{"role": "user", "content": "Hello"}],
            "max_tokens": kwargs.pop("max_tokens", 4096),
        }
        if system:
            params["system"] = system
        params.update({k: v for k, v in kwargs.items() if k in ("temperature", "top_p")})

        response = await self.client.messages.create(**params)
        return response.content[0].text if response.content else ""

    async def stream_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        system = None
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_messages.append(m)

        params: dict[str, Any] = {
            "model": self.model,
            "messages": user_messages or [{"role": "user", "content": "Hello"}],
            "max_tokens": kwargs.pop("max_tokens", 4096),
        }
        if system:
            params["system"] = system
        params.update({k: v for k, v in kwargs.items() if k in ("temperature", "top_p")})

        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text


def get_llm_provider() -> BaseLLMProvider:
    """Factory function to create the configured LLM provider."""
    if settings.LLM_PROVIDER == "anthropic":
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.ANTHROPIC_MODEL,
        )
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
