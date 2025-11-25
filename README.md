# LLM Council

![llmcouncil](header.jpg)

Run multiple LLMs as a “council,” let them critique each other anonymously, and deliver a synthesized final answer. Backend = FastAPI + OpenRouter; Frontend = React; Desktop client = PySide6/QML.

## What Happens
1. **Stage 1 – First opinions:** every model answers independently.
2. **Stage 2 – Peer review:** models see anonymized peers (“Response A/B/C”) and return evaluations + a strict `FINAL RANKING`.
3. **Stage 3 – Synthesis:** chairman model writes the final answer; aggregate rankings are computed.

## Quick Start
Prereqs: Python ≥3.10, Node (LTS), uv (`brew install uv`), OpenRouter API key.

1) Install Python deps:
```bash
uv sync
```
2) Install frontend deps:
```bash
cd frontend && npm install && cd ..
```
3) Add `.env` at repo root:
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

## Run
**One-shot:**  
```bash
./start.sh
```

**Manual:**  
- Backend: `uv run python -m backend.main` (port 8001)  
- Frontend: `cd frontend && npm run dev` (port 5173)  
Open http://localhost:5173

## Desktop GUI (Preview)
PySide6/QML client that reuses the backend:
```bash
uv run python -m gui.app
```
Current UI is a wired design shell; data layer/controller are ready. Streaming hooks and controls are being connected.

## Testing
Coverage-gated tests (target ≥90% on gui/):
```bash
uv run pytest --cov=gui --cov-report=term-missing
```
Backend tests run alongside and currently pass.

## Config & Ports
- Models in `backend/config.py` (`COUNCIL_MODELS`, `CHAIRMAN_MODEL`).
- Backend port 8001; Frontend 5173. Update CORS origins in `backend/main.py` and `frontend/src/api.js` if you change ports.
- Data stored in `data/conversations/` (gitignored).

## Repo Map
- `backend/` – FastAPI service, council orchestration, OpenRouter client, JSON storage.
- `frontend/` – React/Vite UI.
- `gui/` – Desktop client (PySide6/QML) with API/state/controller/persistence layers.
- `docs/ARCHITECTURE.md` – condensed system overview.
- `docs/PLAN.md` – current desktop GUI plan snapshot.
- `CHECKLIST.md` – live status of done/doing/next.
- `AGENTS.md` – repo working agreements.

## Dev Notes
- Run backend from repo root so relative imports work.
- `.env` is required; keep API keys private.
- Markdown rendering uses `.markdown-content` wrapper for spacing.

## Roadmap (short)
- Wire GUI to live SSE streaming (stage chips, rankings chart, cancel/retry).
- Package desktop app (PyInstaller/briefcase) per OS.
- Add mocked streaming harness + screenshots/troubleshooting in docs.

## Desktop GUI (preview)

A Qt Quick desktop client scaffold now lives in `gui/`. It reuses the FastAPI backend and will stream stage events as the UI is completed.

1) Install deps (PySide6 + qasync are already in `pyproject.toml`):
```bash
uv sync
```
2) Start the backend in one terminal:
```bash
uv run python -m backend.main
```
3) Launch the GUI in another:
```bash
uv run python -m gui.app
```

The current QML view is a design shell; networking, streaming, and settings will hook into the new `gui/api.py`, `gui/state.py`, and `gui/persistence.py` modules next.

## Testing

Run the Python test suite with coverage (targets 90%+ on `gui/`):
```bash
uv run pytest --cov=gui --cov-report=term-missing
```
