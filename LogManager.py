import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import List


class LogManager:
    """Manage application logging with rotation and cleanup."""

    def __init__(self, LogsDir: str = "Logs") -> None:
        self.LogsDir = Path(LogsDir)
        self.LogsDir.mkdir(parents=True, exist_ok=True)
        Timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.LogFile = self.LogsDir / f"log_{Timestamp}.log"
        self._SetupLogger()
        self._CleanupOldLogs()

    def _SetupLogger(self) -> None:
        Formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
        )
        Handler = RotatingFileHandler(self.LogFile, maxBytes=1_000_000, backupCount=3)
        Handler.setFormatter(Formatter)
        RootLogger = logging.getLogger()
        RootLogger.handlers.clear()
        RootLogger.addHandler(Handler)
        RootLogger.setLevel(logging.INFO)

    def _CleanupOldLogs(self) -> None:
        LogFiles: List[Path] = sorted(
            self.LogsDir.glob("log_*.log"), key=lambda P: P.stat().st_mtime
        )
        Excess = len(LogFiles) - 5
        for File in LogFiles[: max(0, Excess)]:
            try:
                File.unlink()
            except OSError:
                pass
