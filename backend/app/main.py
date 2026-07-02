"""EIP backend — FastAPI entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.runs import router as runs_router
from .core.config import settings

app = FastAPI(title="EIP — Money Intelligence OS", version="2.0.0-phase1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router)


@app.get("/")
async def root() -> dict:
    return {"app": "EIP", "docs": "/docs", "health": "/api/health"}
