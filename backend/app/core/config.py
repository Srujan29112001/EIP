"""Central settings. Every value optional — zero-config demo mode is a feature."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchor to backend/.env regardless of the CWD uvicorn was launched from.
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EIP_", env_file=_ENV_FILE, extra="ignore")

    # local inference
    ollama_url: str = "http://localhost:11434"
    lmstudio_url: str = "http://localhost:1234"
    local_model: str = "qwen3:4b"

    # cloud keys (BYOK — may also arrive per-request from the UI)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    deepseek_api_key: str = ""
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    mistral_api_key: str = ""
    xai_api_key: str = ""

    # explicit tier routes, "provider:model" (model may itself contain ':')
    t1_route: str = ""
    t2_route: str = ""
    t3_route: str = ""

    cors_origins: str = "http://localhost:3000,https://eip.vercel.app"


settings = Settings()

# Default model per cloud provider (July 2026 lineups; overridable per request).
DEFAULT_MODELS: dict[str, str] = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-5-mini",
    "google": "gemini-2.5-flash",
    "deepseek": "deepseek-chat",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "deepseek/deepseek-chat",
    "mistral": "mistral-large-latest",
    "xai": "grok-4",
}

# Cheaper/faster sibling per provider for mechanical & analysis tiers (t1/t2).
# Free-tier quotas are usually MUCH larger on these (e.g. groq 8b-instant has
# ~5× the daily tokens of 70b) — this is what lets a 30-agent board actually
# get narrated on free keys instead of collapsing to deterministic fallbacks.
FAST_MODELS: dict[str, str] = {
    "anthropic": "claude-haiku-4-5",
    "openai": "gpt-5-mini",
    "google": "gemini-2.5-flash-lite",
    "deepseek": "deepseek-chat",
    "groq": "llama-3.1-8b-instant",
    "openrouter": "deepseek/deepseek-chat",
    "mistral": "mistral-small-latest",
    "xai": "grok-3-mini",
}
