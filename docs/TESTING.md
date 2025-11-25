# Testing Guide

## Targets & thresholds
- Coverage gate: 90% on `gui/` (branch coverage enabled via `.coveragerc`).
- Run tests from repo root inside the uv-managed venv.

## Commands
- Backend + GUI tests with coverage:
  ```
  uv run pytest --cov=gui --cov-report=term-missing
  ```
- Frontend lint:
  ```
  cd frontend && npm run lint
  ```

## Notes
- Qt is forced headless for CI/CLI via `QT_QPA_PLATFORM=offscreen` in `conftest.py`.
- Data files in `data/conversations/` are gitignored; tests use in-memory fakes.
- When adding new GUI features, prefer small async fakes in tests and assert AppState/StreamStatus/StagePayloads transitions.

## Smoke flow (manual)
1) Start backend: `uv run python -m backend.main`.
2) Launch frontend: `cd frontend && npm run dev` (open http://localhost:5173).
3) Launch desktop GUI: `uv run python -m gui.app`.
4) Create a conversation, send a prompt, watch Stage 1–3 populate; verify aggregate rankings and title update, and try cancel/retry.
