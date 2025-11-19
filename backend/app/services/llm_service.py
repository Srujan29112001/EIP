"""
LLM Service - Multi-provider LLM integration
Supports OpenAI, Anthropic, and DeepSeek
"""
from typing import Dict, Any, Optional, List, AsyncGenerator
from enum import Enum
import os
import httpx
import json
from abc import ABC, abstractmethod


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate completion from LLM"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate completion using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            if stream:
                return self._stream_generate(client, headers, payload)
            else:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

    async def _stream_generate(
        self,
        client: httpx.AsyncClient,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream generation from OpenAI"""
        async with client.stream('POST', self.base_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError:
                        continue


class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) API client"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate completion using Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Convert OpenAI-style messages to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        if system_message:
            payload["system"] = system_message

        async with httpx.AsyncClient(timeout=60.0) as client:
            if stream:
                return self._stream_generate(client, headers, payload)
            else:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"]

    async def _stream_generate(
        self,
        client: httpx.AsyncClient,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream generation from Anthropic"""
        async with client.stream('POST', self.base_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = line[6:]
                    try:
                        chunk = json.loads(data)
                        if chunk.get('type') == 'content_block_delta':
                            if 'delta' in chunk and 'text' in chunk['delta']:
                                yield chunk['delta']['text']
                    except json.JSONDecodeError:
                        continue


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API client (OpenAI-compatible)"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate completion using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            if stream:
                return self._stream_generate(client, headers, payload)
            else:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

    async def _stream_generate(
        self,
        client: httpx.AsyncClient,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream generation from DeepSeek"""
        async with client.stream('POST', self.base_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError:
                        continue


class LLMService:
    """
    Main LLM service that manages multiple providers
    Provides a unified interface for LLM interactions
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM service

        Args:
            provider: LLM provider to use
            api_key: API key (if None, reads from environment)
            model: Model name (if None, uses default for provider)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key_from_env(provider)
        self.model = model or self._get_default_model(provider)
        self.client = self._create_client()

    def _get_api_key_from_env(self, provider: LLMProvider) -> str:
        """Get API key from environment variable"""
        env_keys = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY"
        }
        key = os.getenv(env_keys.get(provider))
        if not key:
            raise ValueError(f"API key not found for provider {provider}")
        return key

    def _get_default_model(self, provider: LLMProvider) -> str:
        """Get default model for provider"""
        default_models = {
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.ANTHROPIC: "claude-sonnet-4-5-20250929",
            LLMProvider.DEEPSEEK: "deepseek-chat"
        }
        return default_models.get(provider, "gpt-4o")

    def _create_client(self) -> BaseLLMClient:
        """Create appropriate client based on provider"""
        clients = {
            LLMProvider.OPENAI: OpenAIClient,
            LLMProvider.ANTHROPIC: AnthropicClient,
            LLMProvider.DEEPSEEK: DeepSeekClient
        }
        client_class = clients.get(self.provider)
        if not client_class:
            raise ValueError(f"Unsupported provider: {self.provider}")
        return client_class(self.api_key, self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate completion from LLM

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text or async generator for streaming
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return await self.client.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate completion with conversation history

        Args:
            messages: List of messages in format [{"role": "user"|"assistant"|"system", "content": "..."}]
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text or async generator for streaming
        """
        return await self.client.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )


# Factory function for easy creation
def create_llm_service(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMService:
    """
    Factory function to create LLM service

    Args:
        provider: Provider name ('openai', 'anthropic', 'deepseek')
        api_key: Optional API key
        model: Optional model name

    Returns:
        LLMService instance
    """
    provider_enum = LLMProvider(provider)
    return LLMService(provider=provider_enum, api_key=api_key, model=model)
