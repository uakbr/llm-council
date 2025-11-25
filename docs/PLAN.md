# Desktop GUI Plan

## Goals
- Slick, modern, intuitive desktop client that mirrors the web UX.
- Stream stage-by-stage events with clear progress and minimal latency.
- Easy install/start (macOS/Win/Linux) without terminals when packaged.
- Keep backend as the single source of business logic.

## UX Outline
- Splash → API key check → Home.
- Home: recent conversations list + New Conversation CTA.
- Conversation view: left rail with conversations; main chat with stage sections (Stage 1 cards, Stage 2 rankings + aggregates, Stage 3 final); live status pill; sticky input with send/stop.
- Loading/streaming: pulsing stage chips, cancel button, error banner on failures.
- Settings modal: backend URL + API key (done); theme + shortcuts TBD.
- Accessibility: focus outlines, high contrast, reduced-motion option.

## Visual Direction
- Qt Quick (QML) + PySide6; neutral dark theme, cyan/amber accents.
- Expressive typography (bundled open-source fonts); light motion with respect for reduced-motion.

## Architecture (GUI)
- `gui/app.py`: Qt + qasync bootstrap.
- `gui/api.py`: httpx REST + SSE client with retries/cancel; live config updates.
- `gui/state.py`: app-wide state store (StreamStatus, StagePayloads).
- `gui/controller.py`: orchestrates API calls and state.
- `gui/models.py`: typed DTOs.
- `gui/persistence.py`: settings in `~/.llm-council`.
- `gui/ui/`: QML components and themes.
- `gui/bridge.py`: QObject bridge for QML.

## Loading & Streaming
- SSE events mapped to UI stages (`stage1_start/complete`, `stage2_complete`, `stage3_complete`, `title_complete`, `complete`).
- Cancellation closes SSE + marks stream cancelled; retry/backoff in `StreamRunner`.
- Errors surface to state and QML banner; settings allow backend URL/API key changes.

## Packaging & Testing
- Packaging: PyInstaller/briefcase bundles per OS with fonts/QML assets.
- Tests: pytest + pytest-qt/asyncio for API, state, controller, SSE harness; coverage target ≥90%.
- Smoke: mocked SSE feed for deterministic UI runs.

## Phased Delivery
1) Bind controller/state to QML; render live conversations and stage progress. **(Done)**
2) Cancel/retry, status pill, settings modal (backend URL/API key), error banner. **(Done)**
3) Add charts for Stage 2 aggregate rankings; polish visuals; add screenshots/docs. **(In progress)**
4) Package per platform; add smoke scripts and troubleshooting. **(Next)**
