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
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

import httpx
import orjson

from .config import DEFAULT_MODELS, FAST_MODELS, settings

Tier = str  # "t1" | "t2" | "t3"


@dataclass
class EngineConfig:
    """Per-run engine selection, sent by the UI (Settings / intake step 3)."""
    compute: str = "auto"            # auto | local | cloud | hybrid | demo
    provider: str = ""               # preferred cloud provider id
    api_key: str = ""                # BYOK from the UI (never persisted)
    model: str = ""                  # explicit model override
    routes: dict[str, str] = field(default_factory=dict)  # tier → "provider:model"
    api_keys: dict[str, str] = field(default_factory=dict)     # provider → key (multi-BYOK)
    # provider → up to 5 keys, rotated when one exhausts mid-run (the "never
    # dies half-way" feature). Keys are tried in order; an exhausted key is
    # cooled and the next takes over automatically.
    api_keys_multi: dict[str, list[str]] = field(default_factory=dict)
    agent_routes: dict[str, str] = field(default_factory=dict)  # agent_id → "provider:model"
    temperature: float | None = None  # global override (per-call default when None)
    max_tokens_cap: int = 0           # 0 = no cap; else clamp every call


@dataclass
class LLMResult:
    text: str
    route: str = ""                  # e.g. "ollama:qwen3:4b" | "anthropic:claude-…" | "none"
    tokens: int = 0

    @property
    def ok(self) -> bool:
        return bool(self.text.strip())


def _all_keys(provider: str, cfg: EngineConfig) -> list[str]:
    """Every key the user gave for this provider, in rotation order:
    the multi-key list first, then the single BYOK field, then the server env
    key — deduped, blanks dropped."""
    keys: list[str] = []
    keys.extend(k.strip() for k in (cfg.api_keys_multi.get(provider) or []))
    if cfg.api_keys.get(provider):
        keys.append(cfg.api_keys[provider].strip())
    if cfg.provider == provider and cfg.api_key:
        keys.append(cfg.api_key.strip())
    env = getattr(settings, f"{provider}_api_key", "")
    if env:
        keys.append(env.strip())
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _key_for(provider: str, cfg: EngineConfig) -> str:
    ks = _all_keys(provider, cfg)
    return ks[0] if ks else ""


# per-key cooldowns: an exhausted key is parked while its siblings keep working.
# keyed by "provider:sha1(key)[:8]" so raw keys never sit in a dict.
_KEY_COOLDOWN: dict[str, float] = {}


def _key_tag(provider: str, key: str) -> str:
    return f"{provider}:{hashlib.sha1(key.encode()).hexdigest()[:8]}"


def _key_cooling(provider: str, key: str) -> bool:
    return _KEY_COOLDOWN.get(_key_tag(provider, key), 0.0) > asyncio.get_event_loop().time()


def _cool_key(provider: str, key: str, seconds: float) -> None:
    now = asyncio.get_event_loop().time()
    tag = _key_tag(provider, key)
    _KEY_COOLDOWN[tag] = max(_KEY_COOLDOWN.get(tag, 0.0), now + seconds)


_KEY_RR = 0  # round-robin cursor so every key shares the load from the first call


def _available_cloud(cfg: EngineConfig) -> list[str]:
    order = ["anthropic", "openai", "google", "groq", "deepseek", "openrouter", "mistral", "xai"]
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


def _route_plan(tier: Tier, cfg: EngineConfig, ollama_up: bool, agent: str = "") -> list[tuple[str, str]]:
    """Ordered (provider, model) candidates for a tier (per-agent route wins)."""
    plan: list[tuple[str, str]] = []

    def parse(route: str) -> tuple[str, str] | None:
        if ":" not in route:
            return None
        p, m = route.split(":", 1)
        return (p.strip(), m.strip())

    # precedence: per-agent route → per-tier request route → env route
    explicit = (parse(cfg.agent_routes.get(agent, "")) if agent else None) \
        or parse(cfg.routes.get(tier, "")) or parse(getattr(settings, f"{tier}_route", ""))
    if explicit:
        plan.append(explicit)

    clouds = _available_cloud(cfg)
    local = ("ollama", settings.local_model)

    if cfg.compute == "demo":
        return []
    if cfg.compute == "local":
        return plan + ([local] if ollama_up else [])
    # preferred(p): the model to TRY FIRST for provider p. An explicit user
    # model choice ALWAYS wins for its provider, at every tier — no silent
    # downgrade. Otherwise t1/t2 ride the fast sibling, t3 the flagship.
    def preferred(p: str) -> str:
        if cfg.model and p == cfg.provider:
            return cfg.model
        return FAST_MODELS.get(p, DEFAULT_MODELS[p]) if tier in ("t1", "t2") else DEFAULT_MODELS[p]

    # cheap(p): the fast sibling — the resilient fallback if `preferred` is
    # rate-limited (e.g. user picked 70b but its small daily quota is spent →
    # keep the board narrated on 8b rather than failing).
    def cheap(p: str) -> str:
        return FAST_MODELS.get(p, DEFAULT_MODELS[p])

    def entries(ps: list[str]) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for p in ps:
            out.append((p, preferred(p)))
            if cheap(p) != preferred(p):
                out.append((p, cheap(p)))
        return out

    # rotate which keyed provider leads for t1/t2 so one free key's rate
    # limits don't starve every agent (t3 keeps the user's preferred order)
    if tier in ("t1", "t2") and len(clouds) > 1:
        global _ROTATE
        _ROTATE += 1
        clouds = clouds[_ROTATE % len(clouds):] + clouds[:_ROTATE % len(clouds)]

    if cfg.compute == "cloud":
        return plan + entries(clouds)

    # auto / hybrid: t1,t2 prefer local; t3 prefers cloud
    if tier in ("t1", "t2"):
        if ollama_up:
            plan.append(local)
        plan += entries(clouds)
    else:
        plan += entries(clouds)
        if ollama_up:
            plan.append(local)
    return plan


_ROTATE = 0


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
    "mistral": "https://api.mistral.ai/v1",
    "xai": "https://api.x.ai/v1",
}


async def _dispatch(provider: str, model: str, cfg: EngineConfig, system: str, user: str,
                    max_tokens: int, temperature: float, key: str | None = None) -> LLMResult:
    k = key if key is not None else _key_for(provider, cfg)
    if provider == "ollama":
        return await _call_openai_compat(f"{settings.ollama_url}/v1", "", model, system, user, max_tokens, temperature)
    if provider == "lmstudio":
        return await _call_openai_compat(f"{settings.lmstudio_url}/v1", "", model, system, user, max_tokens, temperature)
    if provider == "anthropic":
        return await _call_anthropic(k, model, system, user, max_tokens, temperature)
    if provider == "google":
        return await _call_google(k, model, system, user, max_tokens, temperature)
    if provider in _OPENAI_COMPAT_BASES:
        return await _call_openai_compat(_OPENAI_COMPAT_BASES[provider], k,
                                         model, system, user, max_tokens, temperature)
    raise ValueError(f"unknown provider: {provider}")


# ── public API ────────────────────────────────────────────────────────────────

# process-wide cloud concurrency: high enough that several keys work in
# parallel (per-key pacing is the real throttle), low enough to stay polite
_CLOUD_SEM = asyncio.Semaphore(6)

# provider → event-loop time until which it is cooling down after a 429.
# One rate-limited key must not eat every agent's retry budget — skip it,
# let the next provider (or the fast local model) answer instead.
_COOLDOWN: dict[str, float] = {}


def _cooling(provider: str) -> bool:
    return _COOLDOWN.get(provider, 0.0) > asyncio.get_event_loop().time()


def _cool(provider: str, seconds: float) -> None:
    now = asyncio.get_event_loop().time()
    _COOLDOWN[provider] = max(_COOLDOWN.get(provider, 0.0), now + seconds)


# pacer: minimum spacing between calls to the same provider — a steady drip
# stays inside free-tier tokens-per-minute windows where a burst 429-storms
_LAST_CALL: dict[str, float] = {}
_PACE_LOCK: dict[str, asyncio.Lock] = {}
_MIN_INTERVAL = 1.3  # seconds between calls per cloud provider


async def _pace(provider: str, key: str = "") -> None:
    # pace PER KEY, not per provider — so N keys each get their own 1.3s drip
    # and together deliver N× the throughput (the whole point of multi-key)
    tag = _key_tag(provider, key) if key else provider
    lock = _PACE_LOCK.setdefault(tag, asyncio.Lock())
    async with lock:
        now = asyncio.get_event_loop().time()
        wait = _LAST_CALL.get(tag, 0.0) + _MIN_INTERVAL - now
        if wait > 0:
            await asyncio.sleep(wait)
        _LAST_CALL[tag] = asyncio.get_event_loop().time()


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
                       max_tokens: int = 1200, temperature: float = 0.4,
                       agent: str = "") -> LLMResult:
        """Walk the degradation ladder. Returns LLMResult(ok=False) if nothing worked."""
        if self.cfg.temperature is not None:
            temperature = max(0.0, min(1.5, self.cfg.temperature))
        if self.cfg.max_tokens_cap:
            max_tokens = min(max_tokens, self.cfg.max_tokens_cap)
        plan = _route_plan(tier, self.cfg, await self._local_ok(), agent)
        all_cooling: list[tuple[str, str, str]] = []  # (provider, model, key) parked for last resort
        for provider, model in plan:
            if provider in ("ollama", "lmstudio"):
                try:
                    res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature)
                    if res.ok:
                        res.route = f"{provider}:{model}"
                        return res
                except Exception:
                    pass
                continue

            # rotate through EVERY key this provider has — when one is exhausted
            # (429) it's parked and the next takes over, so a run never dies
            # half-way as long as one fresh key remains anywhere.
            keys = _all_keys(provider, self.cfg)
            if not keys:
                continue
            fresh = [k for k in keys if not _key_cooling(provider, k)]
            if not fresh:
                all_cooling.append((provider, model, keys[0]))
                continue
            # ROUND-ROBIN: start each call at a different key so N keys share the
            # load evenly from the first request — 7 keys ≈ 7× the free-tier
            # requests/minute instead of hammering key #1 until it dies.
            if len(fresh) > 1:
                global _KEY_RR
                _KEY_RR += 1
                off = _KEY_RR % len(fresh)
                fresh = fresh[off:] + fresh[:off]
            for key in fresh:
                got_429 = False
                for attempt in (0, 1):
                    try:
                        async with _CLOUD_SEM:
                            await _pace(provider, key)
                            res = await _dispatch(provider, model, self.cfg, system, user,
                                                  max_tokens, temperature, key=key)
                        if res.ok:
                            res.route = f"{provider}:{model}"
                            return res
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 429:
                            # honor Retry-After when the provider tells us how long
                            ra = e.response.headers.get("retry-after", "")
                            cool = 30.0
                            try:
                                cool = max(5.0, min(90.0, float(ra)))
                            except (TypeError, ValueError):
                                pass
                            if attempt == 0 and cool <= 6.0:
                                await asyncio.sleep(cool)
                                continue
                            _cool_key(provider, key, cool)   # park this key, try the next
                            got_429 = True
                        break
                    except Exception:
                        break
                if not got_429:
                    break  # a non-rate-limit failure won't be cured by another key

        # every provider/key was rate-limited — wait out the soonest and try once
        if all_cooling:
            provider, model, key = all_cooling[0]
            tag = _key_tag(provider, key)
            wait = max(0.5, min(20.0, _KEY_COOLDOWN.get(tag, 0.0) - asyncio.get_event_loop().time()))
            await asyncio.sleep(wait)
            try:
                async with _CLOUD_SEM:
                    res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature, key=key)
                if res.ok:
                    res.route = f"{provider}:{model}"
                    return res
            except Exception:
                pass
        return LLMResult(text="", route="none")

    async def structured(self, tier: Tier, system: str, user: str, schema_hint: str,
                         max_tokens: int = 1200, agent: str = "") -> tuple[dict[str, Any] | None, LLMResult]:
        """JSON-schema-shaped output with one repair retry, then regex extraction."""
        prompt = (
            f"{user}\n\nRespond with ONLY a JSON object matching exactly this shape "
            f"(no markdown fences, no commentary):\n{schema_hint}"
        )
        res = await self.complete(tier, system, prompt, max_tokens=max_tokens, temperature=0.2, agent=agent)
        for attempt in range(2):
            data = _extract_json(res.text)
            if data is not None:
                return data, res
            if attempt == 0 and res.ok:
                res = await self.complete(
                    tier, system,
                    f"Convert this into ONLY the valid JSON object described "
                    f"({schema_hint}). Text:\n{res.text[:3000]}",
                    max_tokens=max_tokens, temperature=0.0, agent=agent,
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
