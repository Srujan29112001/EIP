"""Hybrid LLM gateway — one code path across local GPU and every major cloud API.

Tiers (per MASTER_PLAN §6.2):
  t1 mechanical  → local first          (parsing, extraction, formatting)
  t2 analysis    → local-heavy / cheap  (domain agent narratives)
  t3 reasoning   → cloud flagship       (crucible, synthesis, verdict)

STRICT routing (zero silent fallbacks — the app must be testable): every call
resolves to exactly ONE provider+model. Key rotation happens only WITHIN that
provider (throughput, not masking). On failure the agent runs its deterministic
core, visibly "reduced depth", carrying the exact reason in degraded_reason.
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
from .specialists import specialist_model, specialization_of

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
    # provider → up to 16 keys, rotated when one exhausts mid-run (the "never
    # dies half-way" feature). Keys are tried in order; an exhausted key is
    # cooled and the next takes over automatically.
    api_keys_multi: dict[str, list[str]] = field(default_factory=dict)
    agent_routes: dict[str, str] = field(default_factory=dict)  # agent_id → "provider:model"
    # class → "provider:model": pin a whole specialty to a provider+model, e.g.
    # {"reasoning": "anthropic:claude-sonnet-4-5", "quant": "openai:o4-mini"}.
    # Applies to every agent of that class; a per-agent route still overrides it.
    class_routes: dict[str, str] = field(default_factory=dict)
    temperature: float | None = None  # global override (per-call default when None)
    max_tokens_cap: int = 0           # 0 = no cap; else clamp every call
    # specialist routing: each agent's task class (reasoning/quant/research/
    # creative/extraction) picks the best-fitting model on the active provider
    # instead of one general model for every job. Explicit routes still win.
    specialized: bool = True


@dataclass
class LLMResult:
    text: str
    route: str = ""                  # e.g. "ollama:qwen3:4b" | "anthropic:claude-…" | "none"
    tokens: int = 0
    error: str = ""                  # why the call failed (401 bad key, 429, 404 model…) — "" on success

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
    # compute="cloud" is "My API keys": user keys ONLY, so a bad key fails
    # loudly instead of being silently rescued by the server's env key.
    if env and cfg.compute != "cloud":
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

    # precedence: per-agent route → per-CLASS route → per-tier request route → env route.
    # user_pin = a provider the USER deliberately chose (one-engine / per-class /
    # per-agent). env route is a server default, not a user choice.
    cls = specialization_of(agent) if agent else ""
    user_pin = (parse(cfg.agent_routes.get(agent, "")) if agent else None) \
        or (parse(cfg.class_routes.get(cls, "")) if cls else None) \
        or parse(cfg.routes.get(tier, ""))
    explicit = user_pin or parse(getattr(settings, f"{tier}_route", ""))

    # ── STRICT ROUTING: exactly ONE candidate, never a silent hop ─────────────
    # Zero fallbacks by design (the app must be TESTABLE): each call resolves to
    # one provider and one model. If that call fails, the agent reports WHY and
    # shows "reduced depth" — it never quietly switches provider or model.
    if explicit:
        return [explicit]

    local = ("ollama", settings.local_model)
    if cfg.compute == "demo":
        return []
    if cfg.compute == "local":
        return [local] if ollama_up else []

    def model_for(p: str) -> str:
        # explicit user model for their provider → specialist class model →
        # tier default. This picks the ONE model; there is no sibling swap.
        if cfg.model and p == cfg.provider:
            return cfg.model
        if cfg.specialized and agent:
            sm = specialist_model(agent, p)
            if sm:
                return sm
        return FAST_MODELS.get(p, DEFAULT_MODELS[p]) if tier in ("t1", "t2") else DEFAULT_MODELS[p]

    def pick(clouds: list[str]) -> str:
        # prefer OpenRouter for the code & reasoning specialties — its catalog
        # carries genuine fine-tunes (dedicated coders, R1-class reasoners) that
        # the general providers don't. Only when the user hasn't pinned a
        # provider, and only in specialized mode; otherwise honor their order.
        if (cfg.specialized and not cfg.provider and "openrouter" in clouds
                and cls in ("code", "reasoning")):
            return "openrouter"
        return clouds[0]

    # HYBRID: a DELIBERATE tiered split — local GPU does the high-volume,
    # lower-stakes work (t1 mechanical + t2 analysis: parsing, extraction,
    # domain narratives, keeping private data on your machine), the cloud
    # frontier does the hard reasoning/synthesis (t3: crucible, verdict,
    # reporter). No cross-tier fallback: if the local model is down, the local
    # tiers show reduced-depth (honest) rather than silently spilling to cloud.
    if cfg.compute == "hybrid":
        if tier in ("t1", "t2"):
            return [local] if ollama_up else []
        clouds = _available_cloud(cfg)
        return [(pick(clouds), model_for(pick(clouds)))] if clouds else []

    # AUTO: best available — prefer the local GPU for t1/t2 when it's running
    # (a primary choice, not a fallback), otherwise the cloud handles them.
    if cfg.compute == "auto" and ollama_up and tier in ("t1", "t2"):
        return [local]

    clouds = _available_cloud(cfg)
    if not clouds:
        return [local] if (cfg.compute == "auto" and ollama_up) else []
    chosen = pick(clouds)  # user's provider if pinned; else OpenRouter for
    return [(chosen, model_for(chosen))]  # code/reasoning specialists, else first keyed


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



def _scrub(res: LLMResult) -> LLMResult:
    """Reasoning models (R1/QwQ/Qwen-think, gpt-oss) may emit <think>…</think>
    traces — strip them so findings and reports stay clean prose."""
    if res.text and "<think" in res.text:
        res.text = re.sub(r"<think>.*?</think>", "", res.text, flags=re.S).strip()
        # an unterminated think block would otherwise swallow the whole answer
        res.text = re.sub(r"<think>.*\Z", "", res.text, flags=re.S).strip()
    return res

class Gateway:
    def __init__(self, cfg: EngineConfig | None = None) -> None:
        self.cfg = cfg or EngineConfig()
        self._ollama_up: bool | None = None
        # why each agent's call failed — keyed by agent id so concurrent calls
        # never clobber each other. Ctx.finish attaches it to the "reduced
        # depth" output so failures are diagnosable, never silent.
        self._errors: dict[str, str] = {}
        self.last_error: str = ""

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
        """STRICT: one resolved provider+model per call, zero silent fallbacks.
        Rotates across the resolved provider's OWN keys (throughput, not
        masking) and rides out brief 429s; on failure it returns the REASON in
        LLMResult.error so the agent can show exactly what broke."""
        if self.cfg.temperature is not None:
            temperature = max(0.0, min(1.5, self.cfg.temperature))
        if self.cfg.max_tokens_cap:
            max_tokens = min(max_tokens, self.cfg.max_tokens_cap)
        self.last_error = ""
        if agent:
            self._errors.pop(agent, None)   # clear stale error; a success leaves it clear

        def failed(reason: str) -> LLMResult:
            self.last_error = reason
            if agent:
                self._errors[agent] = reason
            return LLMResult(text="", route="none", error=reason)

        plan = _route_plan(tier, self.cfg, await self._local_ok(), agent)
        if not plan:
            if self.cfg.compute == "demo":
                return failed("demo mode - deterministic cores only, no AI calls")
            if self.cfg.compute == "local":
                return failed("local mode - Ollama not reachable at " + settings.ollama_url)
            if self.cfg.compute == "hybrid" and tier in ("t1", "t2"):
                return failed("hybrid mode - local model (Ollama) not running; local-tier "
                              "agents (extraction/analysis) need it. Start Ollama or use Auto.")
            if self.cfg.compute == "hybrid":
                return failed("hybrid mode - no cloud key for the reasoning tier; add one for t3 agents")
            return failed("no engine available - add an API key or start Ollama")

        provider, model = plan[0]
        tag = f"{provider}:{model}"

        if provider in ("ollama", "lmstudio"):
            try:
                res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature)
                if res.ok:
                    res.route = tag
                    return _scrub(res)
                return failed(f"{tag} returned empty output")
            except Exception as e:
                return failed(f"{tag} - {type(e).__name__}: {str(e)[:120]}")

        keys = _all_keys(provider, self.cfg)
        if not keys:
            return failed(f"{provider}: no API key provided for the selected engine")

        fresh = [k for k in keys if not _key_cooling(provider, k)]
        # ROUND-ROBIN: start each call at a different key so N keys share the
        # load evenly from the first request (multi-key throughput, same provider)
        if len(fresh) > 1:
            global _KEY_RR
            _KEY_RR += 1
            off = _KEY_RR % len(fresh)
            fresh = fresh[off:] + fresh[:off]

        errors: list[str] = []
        for key in fresh:
            for attempt in (0, 1):
                try:
                    async with _CLOUD_SEM:
                        await _pace(provider, key)
                        res = await _dispatch(provider, model, self.cfg, system, user,
                                              max_tokens, temperature, key=key)
                    if res.ok:
                        res.route = tag
                        return _scrub(res)
                    errors.append("empty output")
                    break
                except httpx.HTTPStatusError as e:
                    code = e.response.status_code
                    if code == 429:
                        # honor Retry-After; brief in-place retry, else park THIS
                        # key and let the next key of the SAME provider take over
                        ra = e.response.headers.get("retry-after", "")
                        cool = 30.0
                        try:
                            cool = max(5.0, min(90.0, float(ra)))
                        except (TypeError, ValueError):
                            pass
                        if attempt == 0 and cool <= 6.0:
                            await asyncio.sleep(cool)
                            continue
                        _cool_key(provider, key, cool)
                        errors.append("429 rate-limited")
                        break
                    body = ""
                    try:
                        body = " ".join(e.response.text[:140].split())
                    except Exception:
                        pass
                    if code in (401, 403):
                        # this key is bad — another key of the same provider may work
                        errors.append(f"{code} unauthorized - invalid key or no credits ({body})")
                        break
                    # 400/404/422…: the MODEL/request is rejected — no key fixes that
                    return failed(f"{tag} - HTTP {code} model/request rejected ({body})")
                except Exception as e:
                    # network/timeout — transient; the next key gets its own try
                    errors.append(f"{type(e).__name__}: {str(e)[:100]}")
                    break

        # every key is cooling → bounded wait for the soonest, ONE more try on
        # the SAME provider+model (rate-limit persistence, never a swap)
        if not fresh and keys:
            key = keys[0]
            ktag = _key_tag(provider, key)
            wait = max(0.5, min(20.0, _KEY_COOLDOWN.get(ktag, 0.0) - asyncio.get_event_loop().time()))
            await asyncio.sleep(wait)
            try:
                async with _CLOUD_SEM:
                    res = await _dispatch(provider, model, self.cfg, system, user, max_tokens, temperature, key=key)
                if res.ok:
                    res.route = tag
                    return _scrub(res)
            except Exception as e:
                errors.append(f"{type(e).__name__}")
            return failed(f"{tag} - all {len(keys)} key(s) rate-limited/cooling")

        detail = errors[-1] if errors else "no working key"
        n_bad = len(errors)
        return failed(f"{tag} - {detail}" + (f" (tried {n_bad} key{'s' if n_bad > 1 else ''})" if n_bad > 1 else ""))

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
