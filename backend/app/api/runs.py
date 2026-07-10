"""Run API: POST /api/run streams the whole pipeline as SSE (Helix consumeSSE pattern)."""
from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from fastapi import Header, HTTPException, UploadFile

from ..agents.registry import ROSTER
from ..core.llm_gateway import EngineConfig, Gateway, local_models
from ..graphs.trading import run_trading
from ..graphs.venture import run_venture
from ..graphs.wealth import run_wealth
from ..core.events import Emitter
from ..memory import store

router = APIRouter(prefix="/api")


class RunRequest(BaseModel):
    mode: str = "founder"                # founder | trader | wealth (trader/wealth: later phases)
    situation: str = ""
    industry: str = ""
    geography: str = "India"
    stage: str = ""
    budget_band: str = ""
    team_size: str = ""
    uncertainty: str = ""
    depth: str = "pulse"                 # pulse | board | war_room (all modes)
    rounds: int = 0                      # 0 = auto (pulse→1, board/war_room→2 deliberation rounds)
    # founder extras
    target_customer: str = ""
    competitors: str = ""
    revenue_model: str = ""
    agents_enabled: list[str] = Field(default_factory=list)  # empty = full scope for depth
    # trader mode
    symbol: str = ""
    trading_style: str = "swing"         # intraday | swing | position | options_edu
    capital: float = 100000.0
    risk_pct: float = 1.0
    thesis: str = ""                     # trader: why are you even looking at this
    existing_position: float = 0.0       # shares already held
    # wealth mode
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    current_savings: float = 0.0
    age: int = 30
    risk_appetite: str = "moderate"      # conservative | moderate | aggressive
    city: str = ""
    goals: str = ""
    dependents: int = 0
    current_debt: float = 0.0            # outstanding loans total
    monthly_sip: float = 0.0             # already-automated investing
    # document intelligence (Phase 8): extracted client-side via POST /api/extract
    documents: list[dict[str, Any]] = Field(default_factory=list)
    # per-agent user briefs from the board picker ("here's what I want YOU to focus on")
    agent_context: dict[str, str] = Field(default_factory=dict)
    engine: dict[str, Any] = Field(default_factory=dict)


# Strong references: asyncio only weak-refs tasks, so a run could be GC'd mid-flight.
_TASKS: set[asyncio.Task] = set()


@router.post("/run")
async def run(req: RunRequest, x_eip_user: str | None = Header(default=None)) -> StreamingResponse:
    run_id = uuid.uuid4().hex[:12]
    emitter = Emitter()
    pipeline = (run_trading if req.mode == "trader"
                else run_wealth if req.mode == "wealth" else run_venture)
    payload = req.model_dump()
    if x_eip_user:
        payload["user_id"] = x_eip_user.strip()[:64]
        await store.get_or_create_user(payload["user_id"])
    task = asyncio.create_task(pipeline(run_id, payload, emitter))
    _TASKS.add(task)
    task.add_done_callback(_TASKS.discard)

    async def stream():
        try:
            async for chunk in emitter.sse():
                yield chunk
        finally:
            # client disconnected (or stream ended) — stop the pipeline, don't burn tokens
            task.cancel()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "X-Run-Id": run_id},
    )


@router.get("/health")
async def health() -> dict[str, Any]:
    status = await Gateway(EngineConfig()).status()
    return {"ok": True, "engine": status}


@router.get("/agents")
async def agents() -> list[dict[str, Any]]:
    return [a.__dict__ for a in ROSTER]


@router.get("/local-models")
async def local() -> dict[str, Any]:
    models = await local_models()
    return {"available": bool(models), "models": models}


@router.post("/extract")
async def extract_document(file: UploadFile) -> dict[str, Any]:
    """Upload → text. PDF via pypdf; txt/md/csv as-is. Full OCR (scans/images)
    arrives later in Phase 8 — this covers digital documents today."""
    raw = await file.read()
    name = file.filename or "document"
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(413, "file too large (15MB max)")
    text = ""
    if name.lower().endswith(".pdf"):
        try:
            import io as _io

            from pypdf import PdfReader
            reader = PdfReader(_io.BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages[:40])
        except Exception:
            raise HTTPException(422, "could not read this PDF (scanned/encrypted? OCR lands in Phase 8)")
    else:
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            raise HTTPException(422, "unsupported file type — PDF, TXT, MD or CSV")
    text = text.strip()
    if not text:
        raise HTTPException(422, "no extractable text — if this is a scan, OCR lands later in Phase 8")
    return {"name": name, "text": text[:20000], "chars": len(text)}


class AskRequest(BaseModel):
    run_id: str
    question: str
    engine: dict[str, Any] = Field(default_factory=dict)


@router.post("/ask")
async def ask_the_board(req: AskRequest) -> dict[str, Any]:
    """Grounded Q&A: answers ONLY from the chosen run's evidence and outputs."""
    rec = await store.get_run(req.run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    st = rec["state"]
    context = {
        "situation": rec.get("situation"),
        "verdict": st.get("verdict"),
        "dimensions": st.get("dimensions"),
        "agent_verdicts": {k: v.get("verdict_line") for k, v in (st.get("outputs") or {}).items()
                           if isinstance(v, dict) and v.get("verdict_line")},
        "evidence": [e.get("text") for e in (st.get("evidence") or [])[:24]],
        "red_team_attacks": [a.get("attack") for a in (st.get("conflicts") or [])[:5] if isinstance(a, dict)],
    }
    cfg = EngineConfig(**{k: v for k, v in (req.engine or {}).items()
                          if k in EngineConfig.__dataclass_fields__})
    res = await Gateway(cfg).complete(
        "t3",
        "You are the board's spokesperson. Answer ONLY from the run context provided — if the answer "
        "is not in it, say so and suggest what to re-run. Cite which agent or evidence item supports "
        "each claim (e.g. 'per the Fact Checker…'). Never invent numbers. Educational, never advice.",
        f"RUN CONTEXT:\n{context}\n\nQUESTION: {req.question}",
        max_tokens=700,
    )
    if res.ok:
        return {"answer": res.text, "route": res.route, "grounded": True}
    return {"answer": "No model is reachable right now — the board can't speak, but its written record "
                      "above stands. Add an API key (or start Ollama) and ask again.",
            "route": "none", "grounded": False}


@router.get("/runs")
async def runs_history(limit: int = 50, x_eip_user: str | None = Header(default=None)) -> list[dict[str, Any]]:
    return await store.list_runs(min(limit, 200), (x_eip_user or "").strip() or None)


@router.get("/me")
async def me(x_eip_user: str | None = Header(default=None),
             x_eip_email: str | None = Header(default=None)) -> dict[str, Any]:
    """Anonymous-first identity: the client sends a stable id, we return the
    account + tier. No password — managed auth is the documented upgrade."""
    uid = (x_eip_user or "").strip()[:64]
    if not uid:
        return {"user_id": None, "tier": "free", "tier_info": store.TIERS["free"], "runs": 0}
    return await store.get_or_create_user(uid, (x_eip_email or "").strip()[:120] or None)


@router.get("/runs/{run_id}")
async def run_detail(run_id: str) -> dict[str, Any]:
    rec = await store.get_run(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    rec["outcome"] = await store.get_outcome(run_id)
    return rec


# ── Phase 9: outcome tracking ─────────────────────────────────────────────────

class OutcomeRequest(BaseModel):
    decision: str = "pending"   # proceeded | declined | modified | pending
    status: str = "too_early"   # good | mixed | bad | too_early
    note: str = ""


@router.post("/runs/{run_id}/outcome")
async def record_outcome(run_id: str, req: OutcomeRequest) -> dict[str, Any]:
    if await store.get_run(run_id) is None:
        raise HTTPException(404, "run not found")
    ok = await store.save_outcome(run_id, req.decision, req.status, req.note)
    if not ok:
        raise HTTPException(500, "could not record outcome")
    return {"ok": True, "outcome": await store.get_outcome(run_id)}


@router.get("/track-record")
async def track_record() -> dict[str, Any]:
    """The platform's own calibration — how the board's verdicts aged."""
    return await store.track_record()
