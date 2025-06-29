import sys
from pathlib import Path
import pandas as pd
import random

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DataLabel import DataLabel
from GPPrimitives import GPPrimitives
from GPPopulation import GPPopulation
from ConfigManager import ConfigManager
from EvaluateFitness import EvaluateFitness


def test_compute_fitness_range(tmp_path) -> None:
    Prices = pd.DataFrame({"Close": list(range(1, 21))})
    Labeler = DataLabel()
    Data = Labeler.AddLabel(Prices.copy())
    ConfigPath = tmp_path / "config.yaml"
    Config = ConfigManager(ConfigFile=str(ConfigPath))
    Config.UpdateParams(PopulationSize=1)
    Prims = GPPrimitives()
    PopulationGen = GPPopulation(Prims, Config)
    random.seed(0)
    Population = PopulationGen.Generate()
    Evaluator = EvaluateFitness(Data, Prims)
    Fitness = Evaluator.ComputeFitness(Population[0])
    assert 0.0 <= Fitness <= 1.0
