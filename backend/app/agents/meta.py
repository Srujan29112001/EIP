"""The meta agents — infrastructure made VISIBLE as board members.

rag_memory (L1): the retrieval layer as an agent. The BM25 RAG engine already
ranks evidence per-specialist and recalls similar past runs; this agent puts
that work on stage — it indexes the board, reports coverage, and posts the
retrieval digest every specialist will draw from.

outcome_tracker (L5): the calibration layer as an agent. Reads the graded
track record (outcomes the user recorded) and reports the platform's own
GO hit-rate + whether learned weights are active — accountability, in the run.
"""
from __future__ import annotations

from .base import Ctx
from ..memory import store
from ..memory.rag import BM25Index


async def rag_memory(ctx: Ctx) -> None:
    aid, layer = "rag_memory", "L1"
    await ctx.start(aid, layer)
    ev = ctx.state.evidence
    docs = sum(1 for e in ev if str(e.get("agent")) == "doc_analyst")
    mem = sum(1 for e in ev if str(e.get("text", "")).startswith("MEMORY:"))
    sourced = sum(1 for e in ev if (e.get("source") or {}).get("url"))
    # build the index once here so coverage is honest (same engine the
    # per-agent evidence_digest(query=…) reads use)
    try:
        idx = BM25Index([str(e.get("text") or "") for e in ev])
        vocab = len(idx.df)
    except Exception:
        vocab = 0
    await ctx.emit.log(aid, f"retrieval online — {len(ev)} evidence items indexed (BM25, "
                            f"{vocab} terms): {sourced} live-sourced · {docs} from your documents "
                            f"· {mem} recalled from memory", "ok" if ev else "warn")
    await ctx.emit.log(aid, "every specialist now reads its own most-relevant slice of this board, "
                            "not the first-N items", "muted")
    await ctx.finish(aid, layer, {
        "verdict_line": f"{len(ev)} items indexed — per-agent relevance retrieval active",
        "indexed": len(ev), "sourced": sourced, "docs": docs, "memory": mem,
        "degraded": False,
    })


async def outcome_tracker(ctx: Ctx) -> None:
    aid, layer = "outcome_tracker", "L5"
    await ctx.start(aid, layer)
    tr = await store.track_record()
    cal = {}
    try:
        cal = await store.dimension_calibration()
    except Exception:
        pass
    if tr.get("graded"):
        hit = tr.get("go_hit_rate")
        await ctx.emit.log(aid, f"track record: {tr['graded']} graded outcome(s) · "
                                f"GO hit-rate {int(hit * 100)}%" if hit is not None else
                                f"track record: {tr['graded']} graded outcome(s)", "info")
        if cal:
            await ctx.emit.log(aid, "learned weights fed back into the weighing engine: "
                               + ", ".join(f"{k}×{v}" for k, v in cal.items()), "info")
    else:
        await ctx.emit.log(aid, "no graded outcomes yet — record what you decide on the History "
                                "page and the board starts calibrating itself", "muted")
    await ctx.finish(aid, layer, {
        "verdict_line": (f"{tr.get('graded', 0)} outcomes graded · "
                         + (f"GO hit-rate {int((tr.get('go_hit_rate') or 0) * 100)}%"
                            if tr.get("go_hit_rate") is not None else "calibration pending")),
        "graded": tr.get("graded", 0), "tracked": tr.get("tracked", 0),
        "go_hit_rate": tr.get("go_hit_rate"), "learned_weights": cal, "degraded": False,
    })
