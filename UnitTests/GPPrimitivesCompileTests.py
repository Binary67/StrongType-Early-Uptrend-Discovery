import sys
from pathlib import Path
import pandas as pd
from deap import gp

sys.path.append(str(Path(__file__).resolve().parents[1]))

from GPPrimitives import GPPrimitives, IndicatorSeries
from EvaluateFitness import EvaluateFitness


def test_compile_indicator_terminal() -> None:
    Data = pd.DataFrame({"Close": [1, 2, 3], "Label": [0, 1, 0]})
    Prims = GPPrimitives()
    terminal = Prims.PrimitiveSet.terminals[IndicatorSeries][0]
    tree = gp.PrimitiveTree([terminal])
    # Ensure compilation works
    func = gp.compile(expr=tree, pset=Prims.PrimitiveSet)
    assert func is not None
    evaluator = EvaluateFitness(Data, Prims)
    fitness = evaluator.ComputeFitness(tree)
    assert 0.0 <= fitness <= 1.0
