"""Entrypoint for the LLM Council desktop GUI."""

import asyncio
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from qasync import QEventLoop

from .config import APP_NAME, LOG_FILE, ensure_dirs


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

    engine = QQmlApplicationEngine()
    qml_path = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        logging.error("Failed to load QML UI from %s", qml_path)
        return 1

    logging.info("GUI started; backend expected at http://localhost:8001 by default")

    with loop:
        loop.run_forever()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
