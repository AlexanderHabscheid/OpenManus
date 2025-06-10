"""
LLM provider implementations for different backends.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import aiohttp


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize DeepSeek provider."""
        self.api_key = config["llm"].get("api_key")
        self.api_base = config["llm"].get("api_base", "https://api.deepseek.com/v1")
        self.model = config["llm"].get("model", "deepseek-chat")

        if not self.api_key:
            raise ValueError("DeepSeek API key is required")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate text using DeepSeek API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stop": stop,
            }

            async with session.post(
                f"{self.api_base}/chat/completions", headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error: {error_text}")

                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using DeepSeek API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "deepseek-embedding",  # Use appropriate embedding model
                "input": text,
            }

            async with session.post(
                f"{self.api_base}/embeddings", headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error: {error_text}")

                result = await response.json()
                return result["data"][0]["embedding"]


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI provider."""
        self.api_key = config["llm"].get("api_key")
        self.model = config["llm"].get("model", "gpt-4")

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Generate text using OpenAI API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stop": stop,
            }

            async with session.post(
                "https://api.openai.com/v1/chat/completions", headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {error_text}")

                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {"model": "text-embedding-ada-002", "input": text}

            async with session.post(
                "https://api.openai.com/v1/embeddings", headers=headers, json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {error_text}")

                result = await response.json()
                return result["data"][0]["embedding"]


def get_llm_provider(config: Dict[str, Any]) -> LLMProvider:
    """Get LLM provider based on configuration."""
    provider = config["llm"].get("provider", "openai").lower()

    if provider == "deepseek":
        return DeepSeekProvider(config)
    elif provider == "openai":
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
