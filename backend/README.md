---
title: EIP Backend
emoji: 🧠
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# EIP — Money Intelligence OS · backend

FastAPI + SSE multi-agent pipeline (founder / trader / wealth boards).

- Health: `GET /api/health`
- Run: `POST /api/run` (SSE stream)
- History: `GET /api/runs`
- Grounded chat: `POST /api/ask`

Secrets (Settings → Variables and secrets): add any of
`EIP_GROQ_API_KEY`, `EIP_GOOGLE_API_KEY`, `EIP_ANTHROPIC_API_KEY`, … to give the
server default engines. Users can always bring their own keys per-run from the UI.

Note: run history (SQLite) is ephemeral on the free tier — it resets when the
Space restarts. Analyses themselves always stream live to the client.
