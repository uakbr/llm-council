"""Entrypoint for the LLM Council desktop GUI."""

import asyncio
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from qasync import QEventLoop

from .api import CouncilAPI
from .bridge import QmlBridge
from .config import APP_NAME, LOG_FILE, ensure_dirs
from .controller import GUIController
from .persistence import load_settings
from .state import AppState
from .stream import StreamRunner


def setup_logging() -> None:
    """Configure basic file logging for the GUI."""
    ensure_dirs()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """Start the Qt/QML application."""
    setup_logging()
    app = QGuiApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    app.aboutToQuit.connect(loop.stop)

    settings = load_settings()
    state = AppState(settings.backend_url, settings.api_key)
    api = CouncilAPI(base_url=state.backend_url, api_key=settings.api_key)
    controller = GUIController(api, state)
    stream_runner = StreamRunner(api, state)
    bridge = QmlBridge(controller, stream_runner, state)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)
    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        logging.error("Failed to load QML UI from %s", qml_path)
        return 1

    logging.info("GUI started; backend expected at http://localhost:8001 by default")

    with loop:
        loop.run_forever()

    # Ensure HTTP client closes cleanly even after loop teardown
    asyncio.run(api.aclose())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
