# LLM Council

Run multiple LLMs as a “council,” let them critique each other anonymously, and deliver a synthesized final answer. Stack: FastAPI backend, React frontend, PySide6/QML desktop client.

## How It Works (Stages)
1. **Stage 1 – First opinions:** council models answer independently.
2. **Stage 2 – Peer review:** models see anonymized peers (“Response A/B/C…”) and return evaluations plus a strict `FINAL RANKING`.
3. **Stage 3 – Synthesis:** chairman model writes the final answer; aggregate rankings are computed from Stage 2.

## Prereqs
- Python ≥3.10 (repo pins 3.10 via `.python-version`)
- uv (`brew install uv`)
- Node (LTS) for the frontend
- OpenRouter API key (`OPENROUTER_API_KEY=sk-or-v1-...`)

## Setup
1) Install Python deps (uv manages `.venv`):
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
4) (Desktop) Settings live at `~/.llm-council/config.json` and can be changed in the GUI Settings modal.

## Run
**One-shot (backend + frontend):**
```bash
./start.sh
```

**Manual:**
- Backend: `uv run python -m backend.main` (port 8001)
- Frontend: `cd frontend && npm run dev` (port 5173) → open http://localhost:5173
- Desktop GUI: `uv run python -m gui.app` (connects to backend URL shown in the rail; adjust via Settings)

## Desktop GUI (current state)
- Live streaming wired (Stage 1/2/3, aggregate rankings, title events).
- Cancel/retry with backoff; error banner on failures.
- Settings modal for backend URL and optional API key; persists to `~/.llm-council/config.json`.

## Config & Ports
- Models: `backend/config.py` (`COUNCIL_MODELS`, `CHAIRMAN_MODEL`).
- Ports: backend 8001, frontend 5173. If you change them, update CORS in `backend/main.py`, the base URL in `frontend/src/api.js`, and GUI settings.
- Data: JSON in `data/conversations/` (gitignored).
- Desktop settings: `~/.llm-council/config.json` (backend URL, API key, theme).

## Testing
- Coverage gate is 90% on `gui/`:
  ```bash
  uv run pytest --cov=gui --cov-report=term-missing
  ```
- Frontend lint:
  ```bash
  cd frontend && npm run lint
  ```
- Smoke flow: run backend, frontend, and desktop GUI; create a conversation, send a prompt, observe Stage 1–3, aggregate rankings, title update, and try cancel/retry.

## Repo Map
- `backend/` – FastAPI service, council orchestration, OpenRouter client, JSON storage.
- `frontend/` – React/Vite UI.
- `gui/` – Desktop client (PySide6/QML) with API/state/stream/bridge/persistence layers.
- `docs/ARCHITECTURE.md` – system overview.
- `docs/PLAN.md` – current desktop GUI plan.
- `docs/GUI.md` – desktop GUI deep dive.
- `docs/TESTING.md` – testing/coverage guide.
- `CHECKLIST.md` – live status of done/doing/next.
- `AGENTS.md` – repo working agreements.

## Dev Notes
- Run backend from repo root so relative imports work.
- `.env` is required; keep API keys private.
- Qt runs headless in tests via `QT_QPA_PLATFORM=offscreen`.
- Markdown rendering uses `.markdown-content` wrapper for spacing (frontend).

## Roadmap
- Add Stage 2 aggregate charts and visual polish with screenshots.
- Package desktop app (PyInstaller/briefcase) per OS.
- Add mocked streaming harness and troubleshooting docs.
