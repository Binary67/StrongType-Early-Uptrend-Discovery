import logging
from typing import List

from deap import gp

from ConfigManager import ConfigManager
from GPPrimitives import GPPrimitives, IndicatorSeries


class GPPopulation:
    """Generate a population of GP formulas."""

    def __init__(self, Primitives: GPPrimitives, Config: ConfigManager | None = None) -> None:
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.Primitives = Primitives
        self.Config = Config if Config else ConfigManager()
        Params = self.Config.GetParams()
        self.PopulationSize: int = Params.get("PopulationSize", 10)
        self.MaxDepth: int = Params.get("MaxDepth", 3)
        self.Population: List[gp.PrimitiveTree] = []

    def Generate(self) -> List[gp.PrimitiveTree]:
        """Create the GP population using half-and-half initialization."""
        Pset = self.Primitives.GetPrimitiveSet()
        self.Population = [
            gp.PrimitiveTree(
                gp.genHalfAndHalf(pset=Pset, min_=1, max_=self.MaxDepth, type_=IndicatorSeries)
            )
            for _ in range(self.PopulationSize)
        ]
        for Formula in self.Population[: min(5, len(self.Population))]:
            self.Logger.info("Generated formula: %s", Formula)
        return self.Population
