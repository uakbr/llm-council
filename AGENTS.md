# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service with council orchestration (`council.py`), OpenRouter client (`openrouter.py`), config (`config.py`), and JSON storage helpers (`storage.py`). Run backend code from the repo root so the relative imports work.
- Data lives in `data/conversations/` (gitignored, created on demand).
- `frontend/`: React + Vite app (`src/App.jsx` entry, `src/components/*` for chat stages, `src/api.js` targets http://localhost:8001).
- `start.sh` spins up both servers; `README.md` and `CLAUDE.md` capture architecture notes.

## Setup & Environment
- Python 3.10+ with [uv](https://docs.astral.sh/uv/); Node (LTS) for the frontend.
- Create `.env` in the repo root: `OPENROUTER_API_KEY=sk-or-v1-...` (never commit).
- Ports: backend 8001, frontend 5173; update both `backend/main.py` CORS origins and `frontend/src/api.js` if you change them.

## Build, Test, and Development Commands
- Install backend deps: `uv sync`.
- Run backend: `uv run python -m backend.main` (from project root).
- Frontend deps: `cd frontend && npm install`.
- Dev servers: `./start.sh` (both), or separately `uv run python -m backend.main` and `cd frontend && npm run dev`.
- Frontend checks: `npm run lint`; production build: `npm run build`.

## Coding Style & Naming Conventions
- Python: follow PEP 8 (4-space indents, snake_case), keep async patterns, type hints, and docstrings consistent with existing modules; prefer relative imports within `backend`.
- Config/constants in `config.py` stay ALL_CAPS; keep model lists and API URLs centralized there.
- JavaScript/React: ESLint flat config is enabled; use functional components, PascalCase for components, camelCase for props/state, and keep semicolons as in current files. Markdown rendering should stay wrapped in `.markdown-content` for spacing.

## Testing Guidelines
- No automated tests yet; at minimum run `npm run lint` before pushing.
- Smoke test the flow: start both services, create a conversation, send a sample prompt, and verify Stage 1/2/3 tabs render and aggregate rankings appear without console errors.
- If you touch storage, confirm JSON files still land in `data/conversations/` and reload correctly.

## Commit & Pull Request Guidelines
- Commits in this repo use short, imperative summaries (e.g., “readme tweaks”, “Label maker add”); follow that style and keep scope focused.
- PRs should note what changed, how to run/verify (commands above), any env/config updates, and UI-facing changes (screenshots or brief clips appreciated). Link issues when relevant.

## Security & Configuration Tips
- Treat `OPENROUTER_API_KEY` and conversation JSON as sensitive; the `.gitignore` already excludes `.env` and `data/`.
- Avoid logging secrets; scrub API responses before sharing.
- When adding models or changing ports, update `config.py`, `main.py` CORS origins, and `src/api.js` together to prevent mismatches.
