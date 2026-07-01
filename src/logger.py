import logging
import os
import platform
import sys
from datetime import datetime
from typing import Optional

import pygame


class GameLogger:
    """Write structured game events to a rolling daily log file."""

    def __init__(self, log_dir: Optional[str] = None) -> None:
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        self._setup_logger()

    def _setup_logger(self) -> None:
        self.logger = logging.getLogger("pixelclash")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        formatter = logging.Formatter("%(message)s")
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def _write(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        self.logger.log(getattr(logging, level), line)

    def info(self, message: str) -> None:
        """Log an informational message."""
        self._write("INFO", message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._write("WARNING", message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._write("ERROR", message)

    def exception(self, message: str, exc_info: bool = True) -> None:
        """Log an exception traceback."""
        self._write("ERROR", message)
        self.logger.exception(message, exc_info=exc_info)


def setup_crash_logger(log_dir: Optional[str] = None) -> str:
    """Install a crash hook that writes uncaught exceptions to a timestamped file."""
    log_dir = log_dir or os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    crash_path = os.path.join(log_dir, f"crash_{timestamp}.log")

    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        with open(crash_path, "w", encoding="utf-8") as handle:
            handle.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            handle.write(f"Python version: {sys.version}\n")
            handle.write(f"pygame version: {pygame.__version__}\n")
            handle.write(f"Operating System: {platform.platform()}\n\n")
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=handle)

        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
    return crash_path
