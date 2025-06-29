import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ConfigManager import ConfigManager
from GPPrimitives import GPPrimitives
from GPPopulation import GPPopulation


def test_generate_population(tmp_path) -> None:
    ConfigPath = tmp_path / "ConfigParams.yaml"
    Manager = ConfigManager(ConfigFile=str(ConfigPath))
    Prims = GPPrimitives()
    Pop = GPPopulation(Prims, Manager)
    Result = Pop.Generate()
    assert len(Result) == Manager.GetParams()["PopulationSize"]
