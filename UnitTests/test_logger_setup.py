import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from LoggerSetup import LoggerSetup


def test_initialize_logger_creates_file(tmp_path):
    LogSetup = LoggerSetup(str(tmp_path))
    Path = LogSetup.InitializeLogger()
    assert os.path.isfile(Path)


def test_log_rotation(tmp_path):
    LogSetup = LoggerSetup(str(tmp_path))
    for _ in range(6):
        LogSetup.InitializeLogger()
        time.sleep(0.001)
    Logs = [f for f in os.listdir(tmp_path) if f.endswith('.log')]
    assert len(Logs) == 5
