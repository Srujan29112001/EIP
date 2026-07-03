"""Run API: POST /api/run streams the whole pipeline as SSE (Helix consumeSSE pattern)."""
from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..agents.registry import ROSTER
from ..core.llm_gateway import EngineConfig, Gateway, local_models
from ..graphs.venture import run_venture
from ..core.events import Emitter

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
    engine: dict[str, Any] = Field(default_factory=dict)


# Strong references: asyncio only weak-refs tasks, so a run could be GC'd mid-flight.
_TASKS: set[asyncio.Task] = set()


@router.post("/run")
async def run(req: RunRequest) -> StreamingResponse:
    run_id = uuid.uuid4().hex[:12]
    emitter = Emitter()
    task = asyncio.create_task(run_venture(run_id, req.model_dump(), emitter))
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
