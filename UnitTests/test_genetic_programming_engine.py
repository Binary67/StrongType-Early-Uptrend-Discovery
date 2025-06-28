import os
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from deap import gp

from GeneticProgrammingEngine import GeneticProgrammingEngine
from GeneticOperatorSuite import GeneticOperatorSuite
from GpPrimitiveSetBuilder import GpPrimitiveSetBuilder
from IndicatorFactory import IndicatorFactory
from PopulationInitializer import PopulationInitializer
from StrongTypeRegistry import StrongTypeRegistry


def _sma(series: List[float], length: int) -> float:
    return sum(series[-length:]) / length


def _setup() -> tuple[StrongTypeRegistry, gp.PrimitiveSetTyped]:
    registry = StrongTypeRegistry()
    registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    registry.RegisterType("PriceSeries", list, lambda x: True)
    registry.RegisterType("WindowLength", int, lambda x: x > 0)
    factory = IndicatorFactory(registry)
    factory.RegisterIndicatorFunction(
        "SMA",
        _sma,
        ("PriceSeries", "WindowLength"),
        "Scalar",
    )
    builder = GpPrimitiveSetBuilder()
    pset = builder.BuildPrimitiveSet(factory, registry)
    builder.AddTerminalNodes(
        pset,
        {"Series": ([1.0, 2.0, 3.0], "PriceSeries"), "Len": (2, "WindowLength")},
    )
    builder.ValidatePrimitiveSet(pset)
    return registry, pset


def test_run_evolution() -> None:
    registry, pset = _setup()
    initializer = PopulationInitializer(registry)
    pop = initializer.GenerateInitialPopulation(pset, 4, 2)
    initializer.EvaluateInitialFitness(pop, lambda _t: 0.0)
    ops = GeneticOperatorSuite(pset)

    def eval_func(tree: gp.PrimitiveTree) -> float:
        return float(len(tree))

    engine = GeneticProgrammingEngine(pset, ops, eval_func)
    hof = engine.RunEvolution(pop, 2, [])
    assert len(hof) >= 1
