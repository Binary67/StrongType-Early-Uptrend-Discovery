import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import logging

sys.path.append(str(Path(__file__).resolve().parents[1]))

from LogManager import LogManager


def test_log_manager_rotation() -> None:
    with TemporaryDirectory() as TempDir:
        TempPath = Path(TempDir)
        for _ in range(7):
            LogManager(LogsDir=TempDir)
        LogFiles = list(TempPath.glob("log_*.log"))
        assert len(LogFiles) == 5


def test_log_contains_module_and_function() -> None:
    with TemporaryDirectory() as TempDir:
        Manager = LogManager(LogsDir=TempDir)
        Logger = logging.getLogger("TestLogger")

        def SampleFunction() -> None:
            Logger.info("sample message")

        SampleFunction()
        Content = Path(Manager.LogFile).read_text()
        assert "TestLogger" in Content
        assert "SampleFunction" in Content
