# EIP — The Money Intelligence OS

**Tell it your situation — an idea, a stock, a salary — and a transparent board of ~40 specialist AI agents researches it with real live data, argues about it, audits your biases, and hands you a weighted, sourced decision. While you watch every step.**

| Mode | Question it answers |
|---|---|
| 🚀 **Founder** | "Should I build this? How?" |
| 📈 **Trader** | "Should I buy/sell/hold? When?" *(analytics + paper trading — never advice, never execution)* |
| 💰 **Wealth** | "What do I do with the money I have?" |

## Why it's different

- **No naked numbers** — every figure carries a live source or an explicit "estimate" flag.
- **Glass box** — watch all agents fire: their prompts, their logs, their confidence, their arguments.
- **The Crucible** — a built-in red team, devil's advocate, and bias auditor attack every thesis (including your framing).
- **Runs on your GPU** — full local privacy mode (Ollama), or bring your own API key for any major provider, or hybrid. Works with **zero keys** in demo mode.

## Architecture

- `frontend/` — Next.js 16 · React 19 · Tailwind v4 · SSE-streamed live pipeline studio
- `backend/` — FastAPI · LangGraph pipelines · hybrid LLM gateway (local + cloud) · deterministic analysis cores
- `legacy/` — the previous generation of this project (38 prototype agents, Streamlit, big-data scaffolding), archived for reference
- `MASTER_PLAN.md` — the full product & architecture plan; `docs/BUILD_LOG.md` — phase-by-phase progress

## Run it

```bash
# backend
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev   # http://localhost:3000
```

No API keys? It runs in **demo mode**. Local GPU? Install [Ollama](https://ollama.com) and `ollama pull qwen3:4b`. Cloud? Add a key in Settings (Anthropic / OpenAI / Google / DeepSeek / Groq / OpenRouter).

> EIP provides analytics and education, not investment advice. It is not SEBI-registered. Decisions and outcomes are yours.
