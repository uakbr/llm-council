# Architecture (Backend, Frontend, Desktop GUI)

## Core Flow
1. User sends a prompt.
2. **Stage 1**: Council models reply in parallel.
3. **Stage 2**: Models see anonymized peers (“Response A/B/C…”) and return evaluations + a strict `FINAL RANKING:` block.
4. Aggregate rankings are computed client-side from parsed rankings + label mapping.
5. **Stage 3**: Chairman model synthesizes a final answer from Stages 1–2.

## Backend (FastAPI)
- Entrypoint: `backend/main.py` (CORS for localhost:5173/3000; health, list/create convo, message, streaming endpoints).
- Council logic: `backend/council.py` (`stage1_collect_responses`, `stage2_collect_rankings`, `stage3_synthesize_final`, `calculate_aggregate_rankings`, `parse_ranking_from_text`, `generate_conversation_title`, `run_full_council`).
- OpenRouter client: `backend/openrouter.py` (`query_model`, `query_models_parallel`).
- Config: `backend/config.py` (models, ports, API base).
- Storage: `backend/storage.py` (JSON in `data/conversations/`, helpers to add user/assistant messages, list, update title).

## Frontend (React + Vite)
- Entry: `frontend/src/App.jsx`.
- Components: `components/Stage1.jsx`, `Stage2.jsx`, `Stage3.jsx`, `ChatInterface.jsx`.
- API target: `frontend/src/api.js` -> `http://localhost:8001`.
- Styling: `.markdown-content` wrapper for markdown spacing; light theme by default.

## Desktop GUI (PySide6 / QML)
- Entrypoint: `gui/app.py` (Qt + qasync loop; loads `gui/ui/Main.qml`).
- Data layer: `gui/api.py` (REST + SSE client, runtime-configurable URL/API key), `gui/models.py` (typed DTOs), `gui/state.py` (AppState + StreamStatus + StagePayloads), `gui/controller.py` (orchestration), `gui/persistence.py` (settings).
- Streaming runner: `gui/stream.py` (cancel + retry/backoff; forwards SSE events to state).
- Qt bridge: `gui/bridge.py` (QObject exposing conversations, stage data, send/cancel, saveSettings to QML).
- UI: `gui/ui/Main.qml` (bound to bridge/state; stage sections, aggregate ranking bars, error banner, settings modal).

## Data & Storage
- Conversations: JSON files in `data/conversations/` (gitignored).
- Metadata (label_to_model, aggregate rankings) returned via API and stored with assistant message; not persisted separately.

## Ports & Config
- Backend: 8001 (FastAPI).
- Frontend: 5173 (Vite).
- Update ports consistently in `backend/main.py` (CORS) and `frontend/src/api.js` if changed.

## Error Handling & Resilience
- Stage queries tolerate individual model failures; proceed with successes.
- Ranking parser falls back to any “Response X” order if strict format fails.
- SSE streaming endpoint emits stage start/complete + title + complete/error events; GUI stream runner retries transient errors and surfaces failures to an error banner.

## Future Considerations
- Token-level streaming per model (currently stage-level).
- UI selection of council/chairman models.
- Export/share conversations; metrics over time.
