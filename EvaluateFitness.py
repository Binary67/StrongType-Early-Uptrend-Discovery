import logging

import pandas as pd
from deap import gp

from GPPrimitives import GPPrimitives, PriceSeries


class EvaluateFitness:
    """Evaluate fitness of GP individuals against labeled data."""

    def __init__(self, Data: pd.DataFrame, Primitives: GPPrimitives) -> None:
        self.Data = Data
        self.Primitives = Primitives
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.PrimitiveSet = self.Primitives.GetPrimitiveSet()

    def _ApplyFormula(self, Formula: gp.PrimitiveTree) -> pd.Series:
        """Return the series produced by ``Formula`` when applied to ``Close`` prices."""
        try:
            Func = gp.compile(expr=Formula, pset=self.PrimitiveSet)
        except Exception as Error:  # pragma: no cover - log compilation errors
            self.Logger.error("Compilation failed: %s", Error)
            return pd.Series(0, index=self.Data.index)
        try:
            Result = Func(PriceSeries(self.Data["Close"]))
        except Exception as Error:  # pragma: no cover - log evaluation errors
            self.Logger.error("Evaluation failed: %s", Error)
            return pd.Series(0, index=self.Data.index)
        Raw = GPPrimitives._Extract(Result)
        if isinstance(Raw, float):
            Raw = pd.Series([Raw] * len(self.Data), index=self.Data.index)
        return pd.Series(Raw, index=self.Data.index)

    def ComputeFitness(self, Formula: gp.PrimitiveTree) -> float:
        """Compute accuracy of ``Formula`` predictions against labels."""
        Output = self._ApplyFormula(Formula)
        Prediction = (Output > 0).astype(int)
        Labels = self.Data["Label"].astype(int)
        Correct = (Prediction == Labels).sum()
        Fitness = Correct / len(Labels)
        self.Logger.info("Fitness computed: %f", Fitness)
        return float(Fitness)
