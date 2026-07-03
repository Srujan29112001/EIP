"""Hybrid LLM gateway — one code path across local GPU and every major cloud API.

Tiers (per MASTER_PLAN §6.2):
  t1 mechanical  → local first          (parsing, extraction, formatting)
  t2 analysis    → local-heavy / cheap  (domain agent narratives)
  t3 reasoning   → cloud flagship       (crucible, synthesis, verdict)

Degradation ladder: requested route → any available cloud → local → "" (caller
falls back to its deterministic core). The app must never blank on a missing key.
"""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any

import httpx
import orjson

from .config import DEFAULT_MODELS, settings

Tier = str  # "t1" | "t2" | "t3"


@dataclass
class EngineConfig:
    """Per-run engine selection, sent by the UI (Settings / intake step 3)."""
    compute: str = "auto"            # auto | local | cloud | hybrid | demo
    provider: str = ""               # preferred cloud provider id
    api_key: str = ""                # BYOK from the UI (never persisted)
    model: str = ""                  # explicit model override
    routes: dict[str, str] = field(default_factory=dict)  # tier → "provider:model"


@dataclass
class LLMResult:
    text: str
    route: str = ""                  # e.g. "ollama:qwen3:4b" | "anthropic:claude-…" | "none"
    tokens: int = 0

    @property
    def ok(self) -> bool:
        return bool(self.text.strip())


def _key_for(provider: str, cfg: EngineConfig) -> str:
    if cfg.provider == provider and cfg.api_key:
        return cfg.api_key
    return getattr(settings, f"{provider}_api_key", "")


def _available_cloud(cfg: EngineConfig) -> list[str]:
    order = ["anthropic", "openai", "google", "groq", "deepseek", "openrouter"]
    if cfg.provider in order:  # user's pick first
        order.remove(cfg.provider)
        order.insert(0, cfg.provider)
    return [p for p in order if _key_for(p, cfg)]


async def _ollama_alive() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as c:
            r = await c.get(f"{settings.ollama_url}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def local_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get(f"{settings.ollama_url}/api/tags")
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def _route_plan(tier: Tier, cfg: EngineConfig, ollama_up: bool) -> list[tuple[str, str]]:
    """Ordered (provider, model) candidates for a tier."""
    plan: list[tuple[str, str]] = []

    def parse(route: str) -> tuple[str, str] | None:
        if ":" not in route:
            return None
        p, m = route.split(":", 1)
        return (p.strip(), m.strip())

    # explicit route (request beats env)
    explicit = parse(cfg.routes.get(tier, "")) or parse(getattr(settings, f"{tier}_route", ""))
    if explicit:
        plan.append(explicit)

    clouds = _available_cloud(cfg)
    local = ("ollama", settings.local_model)

    if cfg.compute == "demo":
        return []
    if cfg.compute == "local":
        return plan + ([local] if ollama_up else [])
    # a user model override applies ONLY to the provider it was chosen for —
    # sending e.g. an Anthropic model name to Groq guarantees 404s on fallback
    def model_for(p: str) -> str:
        return cfg.model if (cfg.model and p == cfg.provider) else DEFAULT_MODELS[p]

    if cfg.compute == "cloud":
        return plan + [(p, model_for(p)) for p in clouds]

    # auto / hybrid: t1,t2 prefer local; t3 prefers cloud
    if tier in ("t1", "t2"):
        if ollama_up:
            plan.append(local)
        plan += [(p, model_for(p)) for p in clouds]
    else:
        plan += [(p, model_for(p)) for p in clouds]
        if ollama_up:
            plan.append(local)
    return plan


# ── provider calls ────────────────────────────────────────────────────────────

async def _call_openai_compat(base: str, key: str, model: str, system: str, user: str,
                              max_tokens: int, temperature: float) -> LLMResult:
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else [])
        + [{"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post(f"{base}/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        j = r.json()
        return LLMResult(
            text=j["choices"][0]["message"]["content"] or "",
            tokens=int(j.get("usage", {}).get("total_tokens", 0)),
        )


async def _call_anthropic(key: str, model: str, system: str, user: str,
                          max_tokens: int, temperature: float) -> LLMResult:
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    payload: dict[str, Any] = {
        "model": model, "max_tokens": max_tokens, "temperature": temperature,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        payload["system"] = system
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
        r.raise_for_status()
        j = r.json()
        usage = j.get("usage", {})
        return LLMResult(
            text="".join(b.get("text", "") for b in j.get("content", [])),
            tokens=int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0)),
        )


async def _call_google(key: str, model: str, system: str, user: str,
                       max_tokens: int, temperature: float) -> LLMResult:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post(url, json=payload)
        r.raise_for_status()
        j = r.json()
        parts = j.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return LLMResult(
            text="".join(p.get("text", "") for p in parts),
            tokens=int(j.get("usageMetadata", {}).get("totalTokenCount", 0)),
        )


_OPENAI_COMPAT_BASES = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}


async def _dispatch(provider: str, model: str, cfg: EngineConfig, system: str, user: str,
                    max_tokens: int, temperature: float) -> LLMResult:
    if provider == "ollama":
        return await _call_openai_compat(f"{settings.ollama_url}/v1", "", model, system, user, max_tokens, temperature)
    if provider == "lmstudio":
        return await _call_openai_compat(f"{settings.lmstudio_url}/v1", "", model, system, user, max_tokens, temperature)
    if provider == "anthropic":
        return await _call_anthropic(_key_for(provider, cfg), model, system, user, max_tokens, temperature)
    if provider == "google":
        return await _call_google(_key_for(provider, cfg), model, system, user, max_tokens, temperature)
    if provider in _OPENAI_COMPAT_BASES:
        return await _call_openai_compat(_OPENAI_COMPAT_BASES[provider], _key_for(provider, cfg),
                                         model, system, user, max_tokens, temperature)
    raise ValueError(f"unknown provider: {provider}")


# ── public API ────────────────────────────────────────────────────────────────

# process-wide: cloud providers rate-limit per key, not per run
_CLOUD_SEM = asyncio.Semaphore(3)


class Gateway:
    def __init__(self, cfg: EngineConfig | None = None) -> None:
        self.cfg = cfg or EngineConfig()
        self._ollama_up: bool | None = None

    async def _local_ok(self) -> bool:
        if self._ollama_up is None:
            self._ollama_up = await _ollama_alive()
        return self._ollama_up

    async def status(self) -> dict[str, Any]:
        return {
            "local": await self._local_ok(),
            "local_model": settings.local_model,
            "cloud": _available_cloud(self.cfg),
            "compute": self.cfg.compute,
        }

    async def complete(self, tier: Tier, system: str, user: str,
                       max_tokens: int = 1200, temperature: float = 0.4) -> LLMResult:
        """Walk the degradation ladder. Returns LLMResult(ok=False) if nothing worked."""
        plan = _route_plan(tier, self.cfg, await self._local_ok())
        for provider, model in plan:
            for attempt in (0, 1, 2):
                try:
                    if provider in ("ollama", "lmstudio"):
                        res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature)
                    else:
                        # gate cloud concurrency — a parallel 8-agent wave on a
                        # free-tier key otherwise 429s half the board
                        async with _CLOUD_SEM:
                            res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature)
                    if res.ok:
                        res.route = f"{provider}:{model}"
                        return res
                    break
                except httpx.HTTPStatusError as e:
                    # rate limit: back off before falling down the ladder
                    if e.response.status_code == 429 and attempt < 2:
                        await asyncio.sleep(3.0 * (attempt + 1))
                        continue
                    break
                except Exception:
                    break
        return LLMResult(text="", route="none")

    async def structured(self, tier: Tier, system: str, user: str, schema_hint: str,
                         max_tokens: int = 1200) -> tuple[dict[str, Any] | None, LLMResult]:
        """JSON-schema-shaped output with one repair retry, then regex extraction."""
        prompt = (
            f"{user}\n\nRespond with ONLY a JSON object matching exactly this shape "
            f"(no markdown fences, no commentary):\n{schema_hint}"
        )
        res = await self.complete(tier, system, prompt, max_tokens=max_tokens, temperature=0.2)
        for attempt in range(2):
            data = _extract_json(res.text)
            if data is not None:
                return data, res
            if attempt == 0 and res.ok:
                res = await self.complete(
                    tier, system,
                    f"Convert this into ONLY the valid JSON object described "
                    f"({schema_hint}). Text:\n{res.text[:3000]}",
                    max_tokens=max_tokens, temperature=0.0,
                )
        return None, res


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = orjson.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except Exception:
                    return None
    return None
