"""
Unit tests for LLM Service
"""
import pytest
import os
from backend.app.services.llm_service import (
    LLMService,
    LLMProvider,
    OpenAIClient,
    AnthropicClient,
    DeepSeekClient
)


class TestLLMService:
    """Test suite for LLM Service"""

    def test_llm_provider_enum(self):
        """Test LLM provider enumeration"""
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.ANTHROPIC == "anthropic"
        assert LLMProvider.DEEPSEEK == "deepseek"

    def test_service_initialization_openai(self):
        """Test service initialization with OpenAI"""
        service = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")
        assert service.provider == LLMProvider.OPENAI
        assert service.model == "gpt-4o"

    def test_service_initialization_anthropic(self):
        """Test service initialization with Anthropic"""
        service = LLMService(provider=LLMProvider.ANTHROPIC, model="claude-sonnet-4-5")
        assert service.provider == LLMProvider.ANTHROPIC

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_generate_completion(self, llm_service):
        """Test completion generation"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'test successful' if you can read this."}
        ]

        response = await llm_service.generate(messages)

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_generate_with_temperature(self, llm_service):
        """Test generation with custom temperature"""
        messages = [{"role": "user", "content": "Hello"}]

        response = await llm_service.generate(
            messages,
            temperature=0.5,
            max_tokens=100
        )

        assert response is not None

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_streaming_response(self, llm_service):
        """Test streaming response generation"""
        messages = [{"role": "user", "content": "Count to 3"}]

        chunks = []
        async for chunk in await llm_service.generate(messages, stream=True):
            chunks.append(chunk)

        assert len(chunks) > 0

    def test_client_factory_pattern(self):
        """Test client creation based on provider"""
        # Test client instantiation
        openai_client = OpenAIClient(api_key="test-key", model="gpt-4o")
        assert openai_client.model == "gpt-4o"

        anthropic_client = AnthropicClient(api_key="test-key", model="claude-sonnet-4-5")
        assert anthropic_client.model == "claude-sonnet-4-5"

    @pytest.mark.asyncio
    async def test_error_handling_invalid_key(self):
        """Test error handling with invalid API key"""
        service = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")
        # Override with invalid key
        service.client.api_key = "invalid-key"

        messages = [{"role": "user", "content": "Test"}]

        with pytest.raises(Exception):
            await service.generate(messages)
