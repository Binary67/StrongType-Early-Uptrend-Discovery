import logging
import pickle
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from deap import base, gp, tools
from joblib import Parallel, cpu_count, delayed
import random

from ConfigManager import ConfigManager
from GeneticOperatorSuite import GeneticOperatorSuite


class GeneticProgrammingEngine:
    """Orchestrate the GP evolution loop."""

    def __init__(
        self,
        PrimitiveSet: gp.PrimitiveSetTyped,
        OperatorSuite: GeneticOperatorSuite,
        FitnessEvaluator: Callable[[gp.PrimitiveTree], float],
        ConfigPath: str = "Config.yaml",
    ) -> None:
        self._pset = PrimitiveSet
        self._operator_suite = OperatorSuite
        self._evaluate = FitnessEvaluator
        self._logger = logging.getLogger(__name__)
        self._config = ConfigManager(ConfigPath).LoadConfig()
        self._hall_of_fame = tools.HallOfFame(1)
        Seed = int(self._config.get("RandomSeed", 42))
        self._rng = random.Random(Seed)
        self._fitness_class = type("FitnessMax", (base.Fitness,), {"weights": (1.0,)})
        self._callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._stats_history: List[Dict[str, Any]] = []

    def RunEvolution(
        self, InitialPopulation: List[gp.PrimitiveTree], Generations: int, Callbacks: List[Callable[[str, Dict[str, Any]], None]]
    ) -> tools.HallOfFame:
        """Execute the main evolution loop."""
        self._callbacks = Callbacks
        Population = InitialPopulation
        for Ind in Population:
            if not hasattr(Ind, "fitness") or not isinstance(Ind.fitness, base.Fitness):
                OldVals = getattr(getattr(Ind, "fitness", None), "values", (0.0,))
                Ind.fitness = self._fitness_class()
                Ind.fitness.values = OldVals
        self.IntegrateCallbacks("evolution_start", {"Population": Population})
        try:
            for GenIndex in range(Generations):
                WallStart = time.time()
                CpuStart = time.process_time()
                self.IntegrateCallbacks("generation_start", {"Generation": GenIndex, "Population": Population})
                Stats = self.UpdatePopulationStats(Population, GenIndex)
                if self.CheckTerminationCriteria(Stats, GenIndex, Generations):
                    break
                Population = self.AdvanceGeneration(Population)
                WallDuration = time.time() - WallStart
                CpuDuration = time.process_time() - CpuStart
                self._logger.info(
                    "Generation %d completed in %.2fs (CPU %.2fs)",
                    GenIndex,
                    WallDuration,
                    CpuDuration,
                )
                self.IntegrateCallbacks(
                    "generation_end",
                    {"Generation": GenIndex, "Population": Population, "Stats": Stats},
                )
                self.PersistCheckpoint(Population, GenIndex, Path("Checkpoints"))
        except KeyboardInterrupt:
            self._logger.warning("Evolution interrupted by user")
        self.IntegrateCallbacks("evolution_end", {"Population": Population})
        return self._hall_of_fame

    def AdvanceGeneration(self, Population: List[gp.PrimitiveTree]) -> List[gp.PrimitiveTree]:
        """Produce the next population using genetic operators."""
        Offspring = self.ApplyGeneticOperators(Population)
        Jobs = min(int(self._config.get("CpuCores", cpu_count())), cpu_count())
        Fitnesses = Parallel(n_jobs=Jobs, prefer="threads")(
            delayed(self._evaluate)(Ind) for Ind in Offspring
        )
        for Ind, Fit in zip(Offspring, Fitnesses):
            try:
                Ind.fitness.values = (Fit,)
            except AttributeError:
                Ind.fitness = self._fitness_class()
                Ind.fitness.values = (Fit,)
        self._hall_of_fame.update(Offspring)
        return Offspring

    def ApplyGeneticOperators(self, Population: List[gp.PrimitiveTree]) -> List[gp.PrimitiveTree]:
        """Apply selection, crossover and mutation."""
        EliteCount = int(self._config.get("EliteCount", 1))
        TournamentSize = int(self._config.get("TournamentSize", 3))
        MaxDepth = int(self._config.get("MaxDepth", 3))
        CxProb = float(self._config.get("CrossoverProb", 0.9))
        MutProb = float(self._config.get("MutationProb", 0.1))
        Elites = self._operator_suite.ElitismSelection(Population, EliteCount)
        Offspring: List[gp.PrimitiveTree] = []
        while len(Offspring) < len(Population) - EliteCount:
            if self._rng.random() < CxProb and len(Population) >= 2:
                Parent1 = self._operator_suite.TournamentSelection(Population, TournamentSize)
                Parent2 = self._operator_suite.TournamentSelection(Population, TournamentSize)
                Child1, Child2 = self._operator_suite.TypedCrossover(Parent1, Parent2, MaxDepth)
                Offspring.extend([Child1, Child2])
            else:
                Parent = self._operator_suite.TournamentSelection(Population, TournamentSize)
                Mutant = self._operator_suite.TypedMutation(Parent, MutProb)
                Offspring.append(Mutant)
        Offspring = Offspring[: len(Population) - EliteCount]
        NewPopulation = self._operator_suite.ReplacePopulation(Offspring, Elites, len(Population))
        return NewPopulation

    def UpdatePopulationStats(self, Population: List[gp.PrimitiveTree], GenerationIndex: int) -> Dict[str, Any]:
        """Compute and emit population statistics."""
        FitnessVals = [getattr(getattr(Ind, "fitness", None), "values", (0.0,))[0] for Ind in Population]
        AvgFitness = float(sum(FitnessVals) / len(FitnessVals)) if FitnessVals else 0.0
        Diversity = len({str(Ind) for Ind in Population}) / float(len(Population) or 1)
        AvgDepth = float(sum(len(Ind) for Ind in Population) / float(len(Population) or 1))
        Stats = {
            "Generation": GenerationIndex,
            "AverageFitness": AvgFitness,
            "Diversity": Diversity,
            "AverageSize": AvgDepth,
        }
        self._stats_history.append(Stats)
        try:
            # Example placeholder for Prometheus; network errors ignored.
            pass
        except Exception as Exc:  # pragma: no cover - network
            self._logger.debug("Prometheus push failed: %s", Exc)
        return Stats

    def CheckTerminationCriteria(self, Stats: Dict[str, Any], GenerationIndex: int, Generations: int) -> bool:
        """Determine whether evolution should end."""
        TargetFitness = float(self._config.get("TargetFitness", float("inf")))
        DiversityThreshold = float(self._config.get("MinDiversity", 0.0))
        if GenerationIndex + 1 >= Generations:
            return True
        if Stats["AverageFitness"] >= TargetFitness:
            return True
        if Stats["Diversity"] <= DiversityThreshold:
            return True
        return False

    def IntegrateCallbacks(self, EventName: str, Context: Dict[str, Any]) -> None:
        """Safely execute user-supplied callbacks."""
        for Callback in self._callbacks:
            try:
                Callback(EventName, Context)
            except Exception as Exc:  # pragma: no cover - user code
                self._logger.error("Callback %s failed: %s", EventName, Exc)

    def PersistCheckpoint(self, Population: List[gp.PrimitiveTree], GenerationIndex: int, OutputDir: Path) -> Path:
        """Atomically write a checkpoint file."""
        OutputDir.mkdir(parents=True, exist_ok=True)
        TempPath = OutputDir / f"checkpoint_{GenerationIndex}.pkl.tmp"
        FinalPath = OutputDir / f"checkpoint_{GenerationIndex}.pkl"
        CheckData = {
            "Generation": GenerationIndex,
            "Population": [
                {
                    "Expression": str(Ind),
                    "Fitness": getattr(getattr(Ind, "fitness", None), "values", ()),
                }
                for Ind in Population
            ],
        }
        with open(TempPath, "wb") as File:
            pickle.dump(CheckData, File)
        TempPath.replace(FinalPath)
        return FinalPath

