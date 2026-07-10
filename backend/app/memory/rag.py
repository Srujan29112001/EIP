"""RAG — retrieval-augmented generation over the evidence board + past runs.

Zero-dependency lexical retrieval (BM25). Chosen deliberately over embedding
models: it runs on the HF free CPU tier with no downloads, no keys, and no
network calls, and for the short, keyword-dense claims on the evidence board
lexical ranking is strong. The upgrade path to vector embeddings (pgvector /
Qdrant + a cloud embedding endpoint) is documented in the README and slots in
behind the same two functions.

What this fixes: before RAG, every agent got the FIRST-N evidence items
(arrival order). Now each agent retrieves the items MOST RELEVANT to its own
question — the tax agent sees tax evidence, the banker sees credit evidence —
and past runs become recallable memory instead of dead rows.
"""
from __future__ import annotations

import math
import re
from typing import Any

_TOKEN = re.compile(r"[a-z0-9]{2,}")
_STOP = frozenset(
    "the a an and or of to in for on with is are was be as at by it its this "
    "that from into over under not no if then than but so we you your i".split())


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class BM25Index:
    """Classic Okapi BM25 (k1=1.5, b=0.75) over short documents."""

    def __init__(self, docs: list[str]) -> None:
        self.docs = docs
        self.toks = [_tokens(d) for d in docs]
        self.n = len(docs)
        self.avg = (sum(len(t) for t in self.toks) / self.n) if self.n else 0.0
        self.df: dict[str, int] = {}
        for toks in self.toks:
            for t in set(toks):
                self.df[t] = self.df.get(t, 0) + 1

    def scores(self, query: str) -> list[float]:
        q = _tokens(query)
        out = [0.0] * self.n
        if not q or not self.n:
            return out
        for term in q:
            df = self.df.get(term)
            if not df:
                continue
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for i, toks in enumerate(self.toks):
                tf = toks.count(term)
                if not tf:
                    continue
                denom = tf + 1.5 * (1 - 0.75 + 0.75 * len(toks) / (self.avg or 1))
                out[i] += idf * (tf * 2.5) / denom
        return out

    def top(self, query: str, k: int) -> list[int]:
        """Indices of the top-k docs for the query; ties keep original order."""
        s = self.scores(query)
        ranked = sorted(range(self.n), key=lambda i: (-s[i], i))
        # keep only docs with a non-zero match; pad with originals to k
        hits = [i for i in ranked if s[i] > 0][:k]
        if len(hits) < k:
            hits += [i for i in range(self.n) if i not in set(hits)][: k - len(hits)]
        return hits


def rank_evidence(evidence: list[dict[str, Any]], query: str, limit: int) -> list[dict[str, Any]]:
    """The per-agent RAG read of the evidence board: the `limit` items most
    relevant to `query` (agent id + its task + brief keywords), instead of the
    first `limit` by arrival order. Falls back to arrival order gracefully."""
    if not evidence:
        return []
    if not query or len(evidence) <= limit:
        return evidence[:limit]
    try:
        idx = BM25Index([str(e.get("text") or "") for e in evidence])
        return [evidence[i] for i in idx.top(query, limit)]
    except Exception:
        return evidence[:limit]


def recall_similar(runs: list[dict[str, Any]], situation: str, mode: str, k: int = 2) -> list[dict[str, Any]]:
    """Cross-run memory: the k most similar PAST runs (same mode) to this
    situation, by BM25 over their stored briefs — the board remembers."""
    pool = [r for r in runs if r.get("mode") == mode and (r.get("situation") or "").strip()]
    if not pool or not situation.strip():
        return []
    try:
        idx = BM25Index([str(r["situation"]) for r in pool])
        scores = idx.scores(situation)
        ranked = sorted(range(len(pool)), key=lambda i: -scores[i])
        return [pool[i] for i in ranked[:k] if scores[i] > 0.5]
    except Exception:
        return []
