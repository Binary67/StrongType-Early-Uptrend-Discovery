import logging
import os
from datetime import datetime

class LoggerSetup:
    """Configure application-wide logging."""

    def __init__(self, Directory: str = "Logs") -> None:
        self.Directory = Directory
        os.makedirs(self.Directory, exist_ok=True)

    def InitializeLogger(self) -> str:
        """Initialise the root logger and manage log rotation.

        Returns:
            str: Path to the log file for this run.
        """
        Timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        LogFile = os.path.join(self.Directory, f"log_{Timestamp}.log")

        Logger = logging.getLogger()
        if Logger.hasHandlers():
            Logger.handlers.clear()
        Logger.setLevel(logging.INFO)

        Formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(module)s:%(funcName)s] - %(message)s"
        )
        FileHandler = logging.FileHandler(LogFile, encoding="utf-8")
        FileHandler.setFormatter(Formatter)
        Logger.addHandler(FileHandler)

        self._PruneOldLogs()
        return LogFile

    def _PruneOldLogs(self) -> None:
        """Keep at most five log files, deleting the oldest if necessary."""
        Files = [
            os.path.join(self.Directory, F)
            for F in os.listdir(self.Directory)
            if F.endswith(".log")
        ]
        if len(Files) <= 5:
            return
        Files.sort(key=os.path.getmtime)
        for FilePath in Files[:-5]:
            try:
                os.remove(FilePath)
            except OSError:
                # Log the error if the file cannot be deleted
                logging.getLogger(__name__).exception(
                    "Failed to remove old log %s", FilePath
                )
