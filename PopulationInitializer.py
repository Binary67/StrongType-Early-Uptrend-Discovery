import logging
import random
from typing import Any, Callable, List, Set

from joblib import Parallel, cpu_count, delayed
from deap import gp

from ConfigManager import ConfigManager
from StrongTypeRegistry import StrongTypeRegistry


class PopulationInitializer:
    """Generate and sanitise an initial GP population."""

    def __init__(self, Registry: StrongTypeRegistry, ConfigPath: str = "Config.yaml") -> None:
        self._registry = Registry
        self._config = ConfigManager(ConfigPath).LoadConfig()
        self._logger = logging.getLogger(__name__)
        self._primitive_set: gp.PrimitiveSetTyped | None = None
        self._max_depth = 2

    def GenerateInitialPopulation(
        self,
        PrimitiveSet: gp.PrimitiveSetTyped,
        PopulationSize: int,
        MaxDepth: int,
    ) -> List[gp.PrimitiveTree]:
        """Return a list of typed individuals."""
        self._primitive_set = PrimitiveSet
        self._max_depth = MaxDepth
        Seed = int(self._config.get("RandomSeed", 42))
        random.seed(Seed)
        Population: List[gp.PrimitiveTree] = []
        Depths = list(range(1, MaxDepth + 1)) or [1]
        Methods = [gp.genGrow, gp.genFull]
        ValidTypes: Set[str] = set(self._registry.ListRegisteredTypes())
        while len(Population) < PopulationSize:
            Depth = Depths[len(Population) % len(Depths)]
            Method = Methods[len(Population) % 2]
            Expr = Method(PrimitiveSet, min_=1, max_=Depth)
            Individual = gp.PrimitiveTree(Expr)
            if not self._TreeIsValid(Individual, ValidTypes):
                continue
            try:
                gp.compile(Individual, PrimitiveSet)
            except Exception:
                self._logger.debug("Discarded invalid individual")
                continue
            Population.append(Individual)
        return Population

    def EnforceStrongTypingOnPopulation(self, Population: List[gp.PrimitiveTree]) -> List[gp.PrimitiveTree]:
        """Replace non-compliant individuals and report counts."""
        if self._primitive_set is None:
            raise RuntimeError("Primitive set not initialized")
        Clean: List[gp.PrimitiveTree] = []
        Replaced = 0
        ValidTypes: Set[str] = set(self._registry.ListRegisteredTypes())
        for Ind in Population:
            if not self._TreeIsValid(Ind, ValidTypes):
                Replacement = self.GenerateInitialPopulation(
                    self._primitive_set, 1, self._max_depth
                )[0]
                Clean.append(Replacement)
                Replaced += 1
                continue
            try:
                gp.compile(Ind, self._primitive_set)
            except Exception:
                Replacement = self.GenerateInitialPopulation(
                    self._primitive_set, 1, self._max_depth
                )[0]
                Clean.append(Replacement)
                Replaced += 1
                continue
            Clean.append(Ind)
        if Replaced:
            self._logger.info("Replaced %d non-compliant individuals", Replaced)
        return Clean

    def EvaluateInitialFitness(
        self,
        Population: List[gp.PrimitiveTree],
        FitnessEvaluator: Callable[[gp.PrimitiveTree], Any],
    ) -> None:
        """Compute fitness in parallel and attach to individuals."""
        Jobs = min(int(self._config.get("CpuCores", cpu_count())), cpu_count())
        Results = Parallel(n_jobs=Jobs, prefer="threads")(
            delayed(FitnessEvaluator)(Ind) for Ind in Population
        )
        for Ind, Fit in zip(Population, Results):
            try:
                Ind.fitness.values = (Fit,)
            except AttributeError:
                Ind.fitness = type("Fitness", (), {"values": (Fit,)})()
    def DeduplicateIndividuals(
        self, Population: List[gp.PrimitiveTree]
    ) -> List[gp.PrimitiveTree]:
        """Remove structurally identical individuals."""
        Unique: List[gp.PrimitiveTree] = []
        Seen: Set[str] = set()
        for Ind in Population:
            Key = str(Ind)
            if Key not in Seen:
                Unique.append(Ind)
                Seen.add(Key)
        return Unique

    def SeedPopulationWithKnownStrategies(
        self,
        Population: List[gp.PrimitiveTree],
        SeedStrategies: List[str],
    ) -> List[gp.PrimitiveTree]:
        """Inject predefined strategies into the population."""
        if self._primitive_set is None:
            raise RuntimeError("Primitive set not initialized")
        for Expr in SeedStrategies:
            try:
                Tree = gp.PrimitiveTree.from_string(Expr, self._primitive_set)
                gp.compile(Tree, self._primitive_set)
                Population.append(Tree)
            except Exception:
                self._logger.error("Failed to seed strategy: %s", Expr)
        return Population

    def _TreeIsValid(self, Tree: gp.PrimitiveTree, Allowed: Set[str]) -> bool:
        for Node in Tree:
            if getattr(Node, "ret", None) is None:
                return False
            if Node.ret.__name__ not in Allowed:
                return False
        return True
