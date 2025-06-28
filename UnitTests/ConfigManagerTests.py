import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ConfigManager import ConfigManager


def test_create_and_update_config(tmp_path) -> None:
    ConfigPath = tmp_path / "ConfigParams.yaml"
    Manager = ConfigManager(ConfigFile=str(ConfigPath))
    assert ConfigPath.exists()
    Params = Manager.GetParams()
    assert Params["TickerSymbol"] == "AAPL"
    Manager.UpdateParams(TickerSymbol="MSFT")
    ParamsUpdated = Manager.GetParams()
    assert ParamsUpdated["TickerSymbol"] == "MSFT"
