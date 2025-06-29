import copy
import logging
import random
from functools import partial
from typing import List

from deap import base, creator, gp, tools

from EvaluateFitness import EvaluateFitness

# Create DEAP classes once to avoid redefinition errors
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)


class GPOperations:
    """Perform genetic programming operations on a population."""

    def __init__(
        self,
        Evaluator: EvaluateFitness,
        CrossoverProb: float = 0.5,
        MutationProb: float = 0.2,
        TournamentSize: int = 3,
    ) -> None:
        self.Evaluator = Evaluator
        self.CrossoverProb = CrossoverProb
        self.MutationProb = MutationProb
        self.TournamentSize = TournamentSize
        self.PrimitiveSet = self.Evaluator.Primitives.GetPrimitiveSet()
        self.Logger = logging.getLogger(self.__class__.__name__)

    def _WrapPopulation(self, Population: List[gp.PrimitiveTree]) -> List[creator.Individual]:
        Individuals = [creator.Individual(Ind) for Ind in Population]
        for Ind, Tree in zip(Individuals, Population):
            Fitness = self.Evaluator.ComputeFitness(Tree)
            Ind.fitness.values = (Fitness,)
        return Individuals

    def RunGeneration(self, Population: List[gp.PrimitiveTree]) -> List[gp.PrimitiveTree]:
        """Evolve ``Population`` by one generation."""
        Individuals = self._WrapPopulation(Population)
        Best = tools.selBest(Individuals, 1)[0]
        self.Logger.info("Best fitness: %f", Best.fitness.values[0])

        Selected = tools.selTournament(
            Individuals, len(Individuals), tournsize=self.TournamentSize
        )
        Offspring = [copy.deepcopy(Ind) for Ind in Selected]

        for Index in range(1, len(Offspring), 2):
            if random.random() < self.CrossoverProb:
                gp.cxOnePoint(Offspring[Index - 1], Offspring[Index])

        for Index in range(len(Offspring)):
            if random.random() < self.MutationProb:
                Expr = partial(gp.genFull, min_=0, max_=2)
                Offspring[Index], = gp.mutUniform(
                    Offspring[Index],
                    Expr,
                    self.PrimitiveSet,
                )
                if hasattr(Offspring[Index].fitness, "values"):
                    del Offspring[Index].fitness.values

        NewPopulation = [gp.PrimitiveTree(Ind) for Ind in Offspring]
        return NewPopulation
