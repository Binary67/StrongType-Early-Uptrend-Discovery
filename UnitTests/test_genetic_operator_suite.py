import os
import sys
import copy
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from deap import gp

from GeneticOperatorSuite import GeneticOperatorSuite
from GpPrimitiveSetBuilder import GpPrimitiveSetBuilder
from IndicatorFactory import IndicatorFactory
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


def _assign_fitness(pop: List[gp.PrimitiveTree], values: List[float]) -> None:
    for ind, val in zip(pop, values):
        ind.fitness = type("Fitness", (), {})()
        ind.fitness.values = (val,)


def test_typed_crossover_and_mutation() -> None:
    _, pset = _setup()
    op = GeneticOperatorSuite(pset)
    ind1 = gp.PrimitiveTree(gp.genFull(pset, 1, 1))
    ind2 = gp.PrimitiveTree(gp.genFull(pset, 1, 1))
    child1, child2 = op.TypedCrossover(ind1, ind2, 3)
    gp.compile(child1, pset)
    gp.compile(child2, pset)
    mutant = op.TypedMutation(ind1, 1.0)
    gp.compile(mutant, pset)
    assert str(mutant) != str(ind1)


def test_tournament_and_elitism() -> None:
    _, pset = _setup()
    op = GeneticOperatorSuite(pset)
    pop = [gp.PrimitiveTree(gp.genFull(pset, 1, 1)) for _ in range(3)]
    _assign_fitness(pop, [1.0, 1.0, 2.0])
    # make one tree longer for tie-break
    pop[0].insert(0, pop[0][0])
    winner = op.TournamentSelection(pop, 2)
    assert winner.fitness.values == (2.0,)
    elites = op.ElitismSelection(pop, 2)
    assert len(elites) == 2
    elites[0][0] = pop[0][0]
    assert str(elites[0]) != str(pop[0])


def test_replace_population_and_adaptive_probs() -> None:
    _, pset = _setup()
    op = GeneticOperatorSuite(pset)
    off = [gp.PrimitiveTree(gp.genFull(pset, 1, 1)) for _ in range(3)]
    elites = [copy.deepcopy(ind) for ind in off[:1]]
    new_pop = op.ReplacePopulation(off, elites, 2)
    assert len(new_pop) == 2
    probs = op.AdaptiveOperatorProbabilities(
        {"CrossoverSuccess": 2, "CrossoverTrials": 4, "MutationSuccess": 1, "MutationTrials": 4}
    )
    assert 0.1 <= probs["CrossoverProb"] <= 0.9
    assert abs(sum(probs.values()) - 1.0) < 1e-6
