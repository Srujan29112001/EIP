"""
VLM Service - Vision-Language Model Integration
Supports GPT-4V, LLaVA, and Gemini Vision for visual analysis
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import os
import base64
import httpx
from abc import ABC, abstractmethod
from io import BytesIO
from PIL import Image


class VLMProvider(str, Enum):
    """Supported VLM providers"""
    GPT4V = "gpt4v"
    LLAVA = "llava"
    GEMINI_VISION = "gemini_vision"


class BaseVLMClient(ABC):
    """Abstract base class for VLM clients"""

    @abstractmethod
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """Analyze image with VLM"""
        pass


class GPT4VisionClient(BaseVLMClient):
    """OpenAI GPT-4 Vision API client"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def _encode_image(self, image_data: bytes) -> str:
        """Encode image to base64"""
        return base64.b64encode(image_data).decode('utf-8')

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """
        Analyze image using GPT-4 Vision

        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            detail: Level of detail ("low", "high", "auto")

        Returns:
            Analysis result with insights
        """
        try:
            base64_image = self._encode_image(image_data)

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                            "detail": detail
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 1000
                    }
                )

                response.raise_for_status()
                data = response.json()

                return {
                    "analysis": data["choices"][0]["message"]["content"],
                    "model": self.model,
                    "provider": "gpt4v",
                    "tokens_used": data.get("usage", {})
                }

        except httpx.HTTPError as e:
            raise Exception(f"GPT-4V API error: {str(e)}")
        except Exception as e:
            raise Exception(f"VLM analysis failed: {str(e)}")

    async def analyze_chart(self, image_data: bytes) -> Dict[str, Any]:
        """Specialized method for chart analysis"""
        prompt = """
        Analyze this chart or graph and provide:
        1. Type of chart (bar, line, pie, etc.)
        2. Key trends and patterns
        3. Notable data points (highs, lows, outliers)
        4. Insights and implications
        5. Any concerns or red flags

        Provide a detailed analysis in a structured format.
        """
        return await self.analyze_image(image_data, prompt, detail="high")

    async def analyze_financial_document(self, image_data: bytes) -> Dict[str, Any]:
        """Specialized method for financial document analysis"""
        prompt = """
        Analyze this financial document and extract:
        1. Document type (balance sheet, P&L, cash flow, etc.)
        2. Key financial metrics and figures
        3. Period covered
        4. Notable trends
        5. Any red flags or concerns

        Provide detailed insights for investment decision-making.
        """
        return await self.analyze_image(image_data, prompt, detail="high")


class LLaVAClient(BaseVLMClient):
    """LLaVA (Open-source VLM) client"""

    def __init__(self, api_endpoint: str = "http://localhost:8000"):
        self.api_endpoint = api_endpoint

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """Analyze image using LLaVA"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {"image": ("image.jpg", image_data, "image/jpeg")}
                data = {"prompt": prompt}

                response = await client.post(
                    f"{self.api_endpoint}/analyze",
                    files=files,
                    data=data
                )

                response.raise_for_status()
                result = response.json()

                return {
                    "analysis": result.get("analysis", ""),
                    "model": "llava",
                    "provider": "llava",
                    "confidence": result.get("confidence", 0.0)
                }

        except Exception as e:
            raise Exception(f"LLaVA analysis failed: {str(e)}")


class GeminiVisionClient(BaseVLMClient):
    """Google Gemini Vision API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """Analyze image using Gemini Vision"""
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json={
                        "contents": [{
                            "parts": [
                                {"text": prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": base64_image
                                    }
                                }
                            ]
                        }]
                    }
                )

                response.raise_for_status()
                data = response.json()

                return {
                    "analysis": data["candidates"][0]["content"]["parts"][0]["text"],
                    "model": "gemini-pro-vision",
                    "provider": "gemini_vision"
                }

        except Exception as e:
            raise Exception(f"Gemini Vision analysis failed: {str(e)}")


class VLMService:
    """
    Vision-Language Model service for visual analysis
    Provides unified interface for multiple VLM providers
    """

    def __init__(
        self,
        provider: VLMProvider = VLMProvider.GPT4V,
        api_key: Optional[str] = None
    ):
        """
        Initialize VLM service

        Args:
            provider: VLM provider to use
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(self._get_env_key())
        self.client = self._create_client()

    def _get_env_key(self) -> str:
        """Get environment variable key for API"""
        mapping = {
            VLMProvider.GPT4V: "OPENAI_API_KEY",
            VLMProvider.LLAVA: "LLAVA_API_ENDPOINT",
            VLMProvider.GEMINI_VISION: "GOOGLE_API_KEY"
        }
        return mapping.get(self.provider, "")

    def _create_client(self) -> BaseVLMClient:
        """Create appropriate VLM client"""
        if self.provider == VLMProvider.GPT4V:
            if not self.api_key:
                raise ValueError("OpenAI API key required for GPT-4V")
            return GPT4VisionClient(api_key=self.api_key)

        elif self.provider == VLMProvider.LLAVA:
            endpoint = os.getenv("LLAVA_API_ENDPOINT", "http://localhost:8000")
            return LLaVAClient(api_endpoint=endpoint)

        elif self.provider == VLMProvider.GEMINI_VISION:
            if not self.api_key:
                raise ValueError("Google API key required for Gemini Vision")
            return GeminiVisionClient(api_key=self.api_key)

        else:
            raise ValueError(f"Unsupported VLM provider: {self.provider}")

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """
        Analyze image with VLM

        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            detail: Level of detail

        Returns:
            Analysis result
        """
        return await self.client.analyze_image(image_data, prompt, detail)

    async def analyze_chart(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze chart or graph"""
        if isinstance(self.client, GPT4VisionClient):
            return await self.client.analyze_chart(image_data)
        else:
            # Fallback for other providers
            prompt = "Analyze this chart and provide key insights, trends, and data points."
            return await self.analyze_image(image_data, prompt)

    async def analyze_financial_document(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze financial document"""
        if isinstance(self.client, GPT4VisionClient):
            return await self.client.analyze_financial_document(image_data)
        else:
            prompt = "Analyze this financial document and extract key metrics and insights."
            return await self.analyze_image(image_data, prompt)

    async def extract_table_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract table data from image"""
        prompt = """
        Extract all table data from this image.
        Return the data in a structured format (rows and columns).
        Include headers if present.
        """
        return await self.analyze_image(image_data, prompt, detail="high")

    async def answer_visual_question(
        self,
        image_data: bytes,
        question: str
    ) -> Dict[str, Any]:
        """Answer a question about an image"""
        return await self.analyze_image(image_data, question)

    async def compare_images(
        self,
        image1_data: bytes,
        image2_data: bytes,
        comparison_prompt: str = "Compare these two images and highlight the differences."
    ) -> Dict[str, Any]:
        """Compare two images (requires multi-image support)"""
        # Note: This requires a provider that supports multiple images
        # For now, analyze separately and compare in text
        result1 = await self.analyze_image(image1_data, "Describe this image in detail.")
        result2 = await self.analyze_image(image2_data, "Describe this image in detail.")

        return {
            "image1_analysis": result1,
            "image2_analysis": result2,
            "comparison": "Analysis completed separately. Consider using GPT-4V with multi-image support for direct comparison."
        }

    def validate_image(self, image_data: bytes) -> bool:
        """Validate that data is a valid image"""
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()
            return True
        except Exception:
            return False

    async def get_image_description(self, image_data: bytes) -> str:
        """Get a simple description of an image"""
        result = await self.analyze_image(
            image_data,
            "Provide a concise description of this image in 2-3 sentences."
        )
        return result.get("analysis", "")


# Convenience functions
async def analyze_business_chart(image_data: bytes) -> Dict[str, Any]:
    """Quick function to analyze a business chart"""
    service = VLMService(provider=VLMProvider.GPT4V)
    return await service.analyze_chart(image_data)


async def analyze_financial_image(image_data: bytes) -> Dict[str, Any]:
    """Quick function to analyze a financial document"""
    service = VLMService(provider=VLMProvider.GPT4V)
    return await service.analyze_financial_document(image_data)
