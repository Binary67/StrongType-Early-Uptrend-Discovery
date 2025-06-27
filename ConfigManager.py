import os
import yaml  # type: ignore
from typing import Any, Dict


class ConfigManager:
    """Handle reading and writing YAML configuration files."""

    def __init__(self, ConfigPath: str = "config.yaml") -> None:
        self.ConfigPath = ConfigPath
        if not os.path.isfile(self.ConfigPath):
            with open(self.ConfigPath, "w", encoding="utf-8") as File:
                yaml.safe_dump({}, File)

    def LoadConfig(self) -> Dict[str, Any]:
        """Return the YAML configuration as a dictionary."""
        with open(self.ConfigPath, "r", encoding="utf-8") as File:
            Data = yaml.safe_load(File) or {}
        return Data

    def UpdateConfig(self, Updates: Dict[str, Any]) -> None:
        """Update the configuration file with the supplied values."""
        Config = self.LoadConfig()
        Config.update(Updates)
        with open(self.ConfigPath, "w", encoding="utf-8") as File:
            yaml.safe_dump(Config, File)
