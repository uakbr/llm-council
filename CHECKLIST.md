# Execution Checklist

## Done
- Desktop GUI scaffold (PySide6/QML shell) with design preview.
- GUI data layer: models, state store, persistence, API + SSE client.
- README updated with GUI launch instructions.
- outline.md created with full implementation plan.
- Tests added for gui models/state/persistence/api with coverage target (90% via .coveragerc).
- pytest run (with coverage) passing locally at ~91% on gui modules.
- Tooling installed: Homebrew python@3.11, uv CLI; env recreated via `uv venv`/`uv sync`; tests executed with `uv run pytest`.
- Controller layer added to coordinate API/state and tested with async fakes.
- Docs cleaned and consolidated: new `docs/ARCHITECTURE.md`, `docs/PLAN.md`; root README refreshed; removed redundant CLAUDE.md and outline.md.
- AppState now tracks stage payloads (stage1/2/3, labels, titles) and keeps conversation titles in sync with streamed events.
- QML bridge (`gui/bridge.py`) exposes state/controller/stream to the UI; Main.qml now binds to live conversations, streaming status, stage data, and send/stop actions.
- Added bridge/state tests; full suite passes with ~92% coverage (`uv run pytest --cov=gui --cov-report=term-missing`).
- Streaming hardened: retry/backoff in `StreamRunner`, error propagation into state, and QML error banner; coverage now ~94% overall.
- Settings modal added: backend URL + API key fields wired to persistence and live API/state updates.
- Docs refreshed: README rewritten, architecture/plan updated, new `docs/GUI.md` and `docs/TESTING.md` added.

## Doing
- Add charts/visual polish for Stage 2 aggregate rankings + doc screenshots.

## Next
- Package desktop app (PyInstaller/briefcase) per target OS.
- Add mocked streaming harness and end-to-end smoke tests.
- Update docs with screenshots and troubleshooting.
