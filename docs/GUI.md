# Desktop GUI (PySide6/QML)

## What it is
- Native Qt Quick client that reuses the FastAPI backend.
- Stage-aware streaming UI (Stage 1 responses, Stage 2 rankings + aggregates, Stage 3 final) with cancel/retry and inline error banner.
- Settings modal to change backend URL and optional API key; persisted to `~/.llm-council/config.json`.

## Files
- `gui/app.py` – Qt + qasync bootstrap; loads QML and wires bridge.
- `gui/bridge.py` – QObject exposed to QML (conversations, stream status, stage data, send/cancel, saveSettings).
- `gui/api.py` – HTTPX REST + SSE client; supports config updates.
- `gui/state.py` – AppState + StreamStatus + StagePayloads; handles SSE events, titles, errors.
- `gui/stream.py` – StreamRunner with cancel + retry/backoff.
- `gui/ui/Main.qml` – QML layout (rail, chat, stage sections, input, settings popup).
- `gui/persistence.py` – load/save settings.

## Running the GUI
1) Start backend in another terminal:
   ```
   uv run python -m backend.main
   ```
2) Launch the GUI from repo root:
   ```
   uv run python -m gui.app
   ```
3) Use the Settings button (top-right) to set the backend URL and API key if they differ from defaults.

## Streaming UX
- Status pill shows current stage; spinner while in-flight.
- Error banner appears if SSE fails or backend returns `error` event; cancel stops the stream and marks state cancelled.
- Stage sections populate as events arrive; aggregate rankings render a simple bar per model.

## Settings & persistence
- Stored at `~/.llm-council/config.json`:
  ```json
  {"backend_url": "http://localhost:8001", "api_key": "sk-...", "theme": "dark"}
  ```
- Save via Settings modal; bridge updates AppState and HTTP clients live.

## Testing
- Headless Qt enabled via `conftest.py` (`QT_QPA_PLATFORM=offscreen`).
- Run GUI + backend tests with coverage:
  ```
  uv run pytest --cov=gui --cov-report=term-missing
  ```
- Coverage gate is 90% (see `.coveragerc`); current suite exercises bridge/state/stream retry paths.

## Troubleshooting
- If the GUI window stays empty, check QML load errors in stdout and ensure `PySide6` is installed (`uv sync`).
- SSE hangs: verify backend at the URL shown under “Backend:” in the rail; adjust in Settings and retry.
- Titles not updating: confirm Stage 3/title events arriving in backend logs.
