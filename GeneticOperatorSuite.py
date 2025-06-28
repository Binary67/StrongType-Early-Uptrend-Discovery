import copy
import logging
import random
from typing import Any, Dict, List, Tuple

from deap import gp

from ConfigManager import ConfigManager


class GeneticOperatorSuite:
    """Provide strongly typed genetic operators."""

    def __init__(self, PrimitiveSet: gp.PrimitiveSetTyped, ConfigPath: str = "Config.yaml") -> None:
        self._pset = PrimitiveSet
        self._config = ConfigManager(ConfigPath).LoadConfig()
        Seed = int(self._config.get("RandomSeed", 42))
        self._rng = random.Random(Seed)
        self._logger = logging.getLogger(__name__)
        self._subtree_pool: Dict[Any, List[gp.PrimitiveTree]] = {}

    def TypedCrossover(
        self,
        Parent1: gp.PrimitiveTree,
        Parent2: gp.PrimitiveTree,
        MaxDepth: int,
    ) -> Tuple[gp.PrimitiveTree, gp.PrimitiveTree]:
        """Crossover parents while preserving return types."""
        Off1 = copy.deepcopy(Parent1)
        Off2 = copy.deepcopy(Parent2)
        for _ in range(10):
            Idx1 = self._rng.randrange(len(Off1))
            RetType = getattr(Off1[Idx1], "ret", None)
            if RetType is None:
                continue
            Candidates = [i for i, Node in enumerate(Off2) if getattr(Node, "ret", None) == RetType]
            if not Candidates:
                continue
            Idx2 = self._rng.choice(Candidates)
            Slice1 = Off1.searchSubtree(Idx1)
            Slice2 = Off2.searchSubtree(Idx2)
            Seg1 = Off1[Slice1]
            Seg2 = Off2[Slice2]
            New1 = Off1[: Slice1.start] + Seg2 + Off1[Slice1.stop :]
            New2 = Off2[: Slice2.start] + Seg1 + Off2[Slice2.stop :]
            Tree1 = gp.PrimitiveTree(New1)
            Tree2 = gp.PrimitiveTree(New2)
            if Tree1.height <= MaxDepth and Tree2.height <= MaxDepth:
                return Tree1, Tree2
        return Off1, Off2

    def TypedMutation(
        self, Individual: gp.PrimitiveTree, MutationRate: float
    ) -> gp.PrimitiveTree:
        """Mutate node with compatible type."""
        Mutant = copy.deepcopy(Individual)
        if self._rng.random() > MutationRate:
            return Mutant
        Attempts = 0
        while Attempts < 10:
            Attempts += 1
            Idx = self._rng.randrange(len(Mutant))
            RetType = getattr(Mutant[Idx], "ret", None)
            if RetType is None:
                continue
            Pool = self._subtree_pool.setdefault(RetType, [])
            if Pool:
                Subtree = copy.deepcopy(self._rng.choice(Pool))
            else:
                Expr = gp.genGrow(self._pset, 0, 2, RetType)
                Subtree = gp.PrimitiveTree(Expr)
                Pool.append(Subtree)
            Slice = Mutant.searchSubtree(Idx)
            NewExpr = Mutant[: Slice.start] + Subtree + Mutant[Slice.stop :]
            NewTree = gp.PrimitiveTree(NewExpr)
            if NewTree.height <= len(Individual) * 2:
                self._subtree_pool[RetType].append(Subtree)
                return NewTree
        return Mutant

    def TournamentSelection(
        self, Population: List[gp.PrimitiveTree], TournamentSize: int
    ) -> gp.PrimitiveTree:
        """Return best individual among random subset."""
        Contenders = self._rng.sample(Population, TournamentSize)
        def _fitness(Ind: gp.PrimitiveTree) -> float:
            FitObj = getattr(Ind, "fitness", None)
            if FitObj is None:
                return 0.0
            return getattr(FitObj, "values", (0.0,))[0]

        Winner = max(
            Contenders,
            key=lambda Ind: (
                _fitness(Ind),
                -len(Ind),
            ),
        )
        return Winner

    def ElitismSelection(
        self, Population: List[gp.PrimitiveTree], EliteCount: int
    ) -> List[gp.PrimitiveTree]:
        """Return deep copies of top individuals."""
        Sorted = sorted(
            Population,
            key=lambda Ind: (
                getattr(getattr(Ind, "fitness", None), "values", (0.0,))[0],
                -len(Ind),
            ),
            reverse=True,
        )
        Elites = [copy.deepcopy(Ind) for Ind in Sorted[:EliteCount]]
        return Elites

    def ReplacePopulation(
        self,
        Offspring: List[gp.PrimitiveTree],
        Elites: List[gp.PrimitiveTree],
        MaxPopulationSize: int,
    ) -> List[gp.PrimitiveTree]:
        """Combine offspring and elites enforcing diversity."""
        NewPop: List[gp.PrimitiveTree] = []

        def _distance(A: gp.PrimitiveTree, B: gp.PrimitiveTree) -> float:
            S1 = str(A)
            S2 = str(B)
            Length = max(len(S1), len(S2))
            Diff = sum(
                Ch1 != Ch2
                for Ch1, Ch2 in zip(S1.ljust(Length), S2.ljust(Length))
            )
            return Diff / Length if Length else 0.0

        Threshold = 0.1
        for Ind in Elites + Offspring:
            if len(NewPop) >= MaxPopulationSize:
                break
            if all(_distance(Ind, Ex) > Threshold for Ex in NewPop):
                NewPop.append(Ind)
        while len(NewPop) < MaxPopulationSize and Offspring:
            Candidate = Offspring.pop()
            if all(_distance(Candidate, Ex) > Threshold for Ex in NewPop):
                NewPop.append(Candidate)
        return NewPop[:MaxPopulationSize]

    def AdaptiveOperatorProbabilities(self, OperatorStats: Dict[str, Any]) -> Dict[str, float]:
        """Adjust operator probabilities based on success rates."""
        CSucc = OperatorStats.get("CrossoverSuccess", 0)
        CTrials = OperatorStats.get("CrossoverTrials", 1)
        MSucc = OperatorStats.get("MutationSuccess", 0)
        MTrials = OperatorStats.get("MutationTrials", 1)
        CRate = CSucc / CTrials
        MRate = MSucc / MTrials
        Total = CRate + MRate
        if Total == 0:
            return {"CrossoverProb": 0.5, "MutationProb": 0.5}
        CProb = max(0.1, min(0.9, CRate / Total))
        MProb = 1.0 - CProb
        return {"CrossoverProb": CProb, "MutationProb": MProb}
