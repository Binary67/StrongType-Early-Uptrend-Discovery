import os
import sys

import copy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from deap import gp

from GpPrimitiveSetBuilder import GpPrimitiveSetBuilder
from IndicatorFactory import IndicatorFactory
from StrongTypeRegistry import StrongTypeRegistry
from PopulationInitializer import PopulationInitializer


def _sma(series: list[float], length: int) -> float:
    return sum(series[-length:]) / length


def _setup() -> tuple[StrongTypeRegistry, gp.PrimitiveSetTyped]:
    registry = StrongTypeRegistry()
    registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    registry.RegisterType("PriceSeries", list, lambda x: True)
    registry.RegisterType("WindowLength", int, lambda x: x > 0)
    factory = IndicatorFactory(registry)
    factory.RegisterIndicatorFunction(
        "SMA", _sma, ("PriceSeries", "WindowLength"), "Scalar"
    )
    builder = GpPrimitiveSetBuilder()
    pset = builder.BuildPrimitiveSet(factory, registry)
    builder.AddTerminalNodes(pset, {"Series": ([1.0, 2.0, 3.0], "PriceSeries"), "Len": (2, "WindowLength")})
    builder.ValidatePrimitiveSet(pset)
    return registry, pset


def test_generate_population_size() -> None:
    registry, pset = _setup()
    init = PopulationInitializer(registry)
    pop = init.GenerateInitialPopulation(pset, 3, 2)
    assert len(pop) == 3
    for ind in pop:
        gp.compile(ind, pset)


def test_enforce_strong_typing_replaces_invalid() -> None:
    registry, pset = _setup()
    init = PopulationInitializer(registry)
    pop = init.GenerateInitialPopulation(pset, 2, 2)
    pop[0][0].ret = int  # corrupt type
    clean = init.EnforceStrongTypingOnPopulation(pop)
    assert len(clean) == 2
    assert clean[0][0].ret is not int


def test_evaluate_initial_fitness() -> None:
    registry, pset = _setup()
    init = PopulationInitializer(registry)
    pop = init.GenerateInitialPopulation(pset, 2, 2)

    def evaluate(_tree: gp.PrimitiveTree) -> float:
        return 1.0

    init.EvaluateInitialFitness(pop, evaluate)
    for ind in pop:
        assert ind.fitness.values == (1.0,)


def test_deduplicate_individuals() -> None:
    registry, pset = _setup()
    init = PopulationInitializer(registry)
    pop = init.GenerateInitialPopulation(pset, 1, 2)
    dup = pop + [copy.deepcopy(pop[0])]
    unique = init.DeduplicateIndividuals(dup)
    assert len(unique) == 1


def test_seed_population_with_known_strategies() -> None:
    registry, pset = _setup()
    init = PopulationInitializer(registry)
    pop = init.GenerateInitialPopulation(pset, 1, 2)
    size_before = len(pop)
    pop = init.SeedPopulationWithKnownStrategies(pop, ["SMA(Series, Len)"])
    assert len(pop) == size_before + 1
    gp.compile(pop[-1], pset)
