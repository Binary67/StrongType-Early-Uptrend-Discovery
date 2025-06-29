import sys
from pathlib import Path
import pandas as pd
import random

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ConfigManager import ConfigManager
from DataLabel import DataLabel
from EvaluateFitness import EvaluateFitness
from GPPrimitives import GPPrimitives
from GPPopulation import GPPopulation
from GPOperations import GPOperations
from deap import gp


def test_run_generation_returns_population(tmp_path) -> None:
    Data = pd.DataFrame({"Close": list(range(1, 21))})
    Labeler = DataLabel()
    Labeled = Labeler.AddLabel(Data.copy())

    ConfigPath = tmp_path / "config.yaml"
    Config = ConfigManager(ConfigFile=str(ConfigPath))
    Config.UpdateParams(PopulationSize=4)

    Prims = GPPrimitives()
    PopulationGen = GPPopulation(Prims, Config)
    random.seed(0)
    Population = PopulationGen.Generate()

    Evaluator = EvaluateFitness(Labeled, Prims)
    Ops = GPOperations(Evaluator, CrossoverProb=0.7, MutationProb=0.2)
    NewPopulation = Ops.RunGeneration(Population)

    assert len(NewPopulation) == len(Population)
    assert all(isinstance(Ind, gp.PrimitiveTree) for Ind in NewPopulation)

