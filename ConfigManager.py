import yaml  # type: ignore
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manage reading and writing of configuration parameters."""

    def __init__(self, ConfigFile: str = "ConfigParams.yaml") -> None:
        self.ConfigFile = Path(ConfigFile)
        if not self.ConfigFile.exists():
            self._CreateDefaultConfig()

    def _CreateDefaultConfig(self) -> None:
        DefaultParams = {
            "TickerSymbol": "AAPL",
            "StartDate": "2024-01-01",
            "EndDate": "2024-01-31",
            "Interval": "1d",
            "PopulationSize": 10,
            "MaxDepth": 3,
        }
        self.ConfigFile.write_text(yaml.safe_dump(DefaultParams))

    def GetParams(self) -> Dict[str, Any]:
        return yaml.safe_load(self.ConfigFile.read_text())

    def UpdateParams(self, **Params: Any) -> None:
        Current = self.GetParams()
        Current.update(Params)
        self.ConfigFile.write_text(yaml.safe_dump(Current))
