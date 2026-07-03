"""Run API: POST /api/run streams the whole pipeline as SSE (Helix consumeSSE pattern)."""
from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from fastapi import HTTPException

from ..agents.registry import ROSTER
from ..core.llm_gateway import EngineConfig, Gateway, local_models
from ..graphs.trading import run_trading
from ..graphs.venture import run_venture
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
    depth: str = "pulse"                 # pulse | board | war_room
    agents_enabled: list[str] = Field(default_factory=list)  # empty = full scope for depth
    # trader mode
    symbol: str = ""
    trading_style: str = "swing"         # intraday | swing | position | options_edu
    capital: float = 100000.0
    risk_pct: float = 1.0
    engine: dict[str, Any] = Field(default_factory=dict)


# Strong references: asyncio only weak-refs tasks, so a run could be GC'd mid-flight.
_TASKS: set[asyncio.Task] = set()


@router.post("/run")
async def run(req: RunRequest) -> StreamingResponse:
    run_id = uuid.uuid4().hex[:12]
    emitter = Emitter()
    pipeline = run_trading if req.mode == "trader" else run_venture
    task = asyncio.create_task(pipeline(run_id, req.model_dump(), emitter))
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


@router.get("/runs")
async def runs_history(limit: int = 50) -> list[dict[str, Any]]:
    return await store.list_runs(min(limit, 200))


@router.get("/runs/{run_id}")
async def run_detail(run_id: str) -> dict[str, Any]:
    rec = await store.get_run(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    return rec
