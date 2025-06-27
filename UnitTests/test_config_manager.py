import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ConfigManager import ConfigManager


def test_config_creation(tmp_path):
    ConfigPath = tmp_path / "test.yaml"
    ConfigManager(ConfigPath)
    assert ConfigPath.is_file()


def test_config_update_and_load(tmp_path):
    ConfigPath = tmp_path / "test.yaml"
    Manager = ConfigManager(ConfigPath)
    Manager.UpdateConfig({"Key": "Value"})
    Data = Manager.LoadConfig()
    assert Data["Key"] == "Value"
