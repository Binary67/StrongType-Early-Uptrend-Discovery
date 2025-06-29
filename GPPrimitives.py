import logging
import random
from dataclasses import dataclass

import pandas as pd
from deap import gp

from Indicator import Indicator


@dataclass
class PriceSeries:
    Values: pd.Series

    def __repr__(self) -> str:
        ValuesList = self.Values.tolist()
        return f"PriceSeries(pd.Series({ValuesList}))"


@dataclass
class IndicatorSeries:
    Values: pd.Series

    def __repr__(self) -> str:
        ValuesList = self.Values.tolist()
        return f"IndicatorSeries(pd.Series({ValuesList}))"


@dataclass
class WindowLength:
    Value: int


@dataclass
class Scalar:
    Value: float


class GPPrimitives:
    """Create strong typed primitives for genetic programming."""

    def __init__(self, IndicatorLib: Indicator | None = None) -> None:
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.IndicatorLib = IndicatorLib if IndicatorLib else Indicator()
        self.PrimitiveSet = gp.PrimitiveSetTyped(
            "MAIN", [PriceSeries], IndicatorSeries
        )
        self.PrimitiveSet.renameArguments(ARG0="ClosePrice")
        self.PrimitiveSet.context.update(
            {
                "pd": pd,
                "IndicatorSeries": IndicatorSeries,
                "PriceSeries": PriceSeries,
                "WindowLength": WindowLength,
                "Scalar": Scalar,
            }
        )
        self._RegisterOperators()
        self._RegisterIndicators()
        self._RegisterTerminals()
        self.Logger.info("Primitive set initialized with %s primitives", sum(len(v) for v in self.PrimitiveSet.primitives.values()))

    # --- Operator implementations ---
    @staticmethod
    def _Extract(Value: Scalar | IndicatorSeries) -> pd.Series | float:
        if isinstance(Value, Scalar):
            return Value.Value
        return Value.Values

    @staticmethod
    def IdentityPrice(Price: PriceSeries) -> PriceSeries:
        """Return the price series unchanged."""
        return Price

    @staticmethod
    def IdentityLength(Length: WindowLength) -> WindowLength:
        """Return the window length unchanged."""
        return Length

    @staticmethod
    def AddScalar(A: Scalar, B: Scalar) -> Scalar:
        return Scalar(A.Value + B.Value)

    @staticmethod
    def AddSeries(A: IndicatorSeries, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Values + B.Values)

    @staticmethod
    def AddSeriesScalar(A: IndicatorSeries, B: Scalar) -> IndicatorSeries:
        return IndicatorSeries(A.Values + B.Value)

    @staticmethod
    def AddScalarSeries(A: Scalar, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Value + B.Values)

    @staticmethod
    def SubScalar(A: Scalar, B: Scalar) -> Scalar:
        return Scalar(A.Value - B.Value)

    @staticmethod
    def SubSeries(A: IndicatorSeries, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Values - B.Values)

    @staticmethod
    def SubSeriesScalar(A: IndicatorSeries, B: Scalar) -> IndicatorSeries:
        return IndicatorSeries(A.Values - B.Value)

    @staticmethod
    def SubScalarSeries(A: Scalar, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Value - B.Values)

    @staticmethod
    def MulScalar(A: Scalar, B: Scalar) -> Scalar:
        return Scalar(A.Value * B.Value)

    @staticmethod
    def MulSeries(A: IndicatorSeries, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Values * B.Values)

    @staticmethod
    def MulSeriesScalar(A: IndicatorSeries, B: Scalar) -> IndicatorSeries:
        return IndicatorSeries(A.Values * B.Value)

    @staticmethod
    def MulScalarSeries(A: Scalar, B: IndicatorSeries) -> IndicatorSeries:
        return IndicatorSeries(A.Value * B.Values)

    @staticmethod
    def SafeDivScalar(A: Scalar, B: Scalar) -> Scalar:
        Den = 1e-6 if B.Value == 0 else B.Value
        return Scalar(A.Value / Den)

    @staticmethod
    def SafeDivSeries(A: IndicatorSeries, B: IndicatorSeries) -> IndicatorSeries:
        Den = B.Values.replace(0, 1e-6)
        return IndicatorSeries(A.Values / Den)

    @staticmethod
    def SafeDivSeriesScalar(A: IndicatorSeries, B: Scalar) -> IndicatorSeries:
        Den = 1e-6 if B.Value == 0 else B.Value
        return IndicatorSeries(A.Values / Den)

    @staticmethod
    def SafeDivScalarSeries(A: Scalar, B: IndicatorSeries) -> IndicatorSeries:
        Den = B.Values.replace(0, 1e-6)
        return IndicatorSeries(A.Value / Den)

    # --- Indicator wrappers ---
    def _WrapEma(self, Price: PriceSeries, Length: WindowLength) -> IndicatorSeries:
        Result = self.IndicatorLib.EMA(Price.Values, Length.Value)
        return IndicatorSeries(Result)

    def _WrapSma(self, Price: PriceSeries, Length: WindowLength) -> IndicatorSeries:
        Result = self.IndicatorLib.SMA(Price.Values, Length.Value)
        return IndicatorSeries(Result)

    def _RegisterOperators(self) -> None:
        P = self.PrimitiveSet
        # Addition
        P.addPrimitive(self.AddSeries, [IndicatorSeries, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.AddSeriesScalar, [IndicatorSeries, Scalar], IndicatorSeries)
        P.addPrimitive(self.AddScalarSeries, [Scalar, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.AddScalar, [Scalar, Scalar], Scalar)
        # Subtraction
        P.addPrimitive(self.SubSeries, [IndicatorSeries, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.SubSeriesScalar, [IndicatorSeries, Scalar], IndicatorSeries)
        P.addPrimitive(self.SubScalarSeries, [Scalar, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.SubScalar, [Scalar, Scalar], Scalar)
        # Multiplication
        P.addPrimitive(self.MulSeries, [IndicatorSeries, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.MulSeriesScalar, [IndicatorSeries, Scalar], IndicatorSeries)
        P.addPrimitive(self.MulScalarSeries, [Scalar, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.MulScalar, [Scalar, Scalar], Scalar)
        # Safe Division
        P.addPrimitive(self.SafeDivSeries, [IndicatorSeries, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.SafeDivSeriesScalar, [IndicatorSeries, Scalar], IndicatorSeries)
        P.addPrimitive(self.SafeDivScalarSeries, [Scalar, IndicatorSeries], IndicatorSeries)
        P.addPrimitive(self.SafeDivScalar, [Scalar, Scalar], Scalar)
        # Price series identity
        P.addPrimitive(self.IdentityPrice, [PriceSeries], PriceSeries)
        P.addPrimitive(self.IdentityLength, [WindowLength], WindowLength)

    def _RegisterIndicators(self) -> None:
        P = self.PrimitiveSet
        P.addPrimitive(self._WrapEma, [PriceSeries, WindowLength], IndicatorSeries, name="EMA")
        P.addPrimitive(self._WrapSma, [PriceSeries, WindowLength], IndicatorSeries, name="SMA")

    def _RegisterTerminals(self) -> None:
        self.PrimitiveSet.addEphemeralConstant(
            "RandScalar", lambda: Scalar(random.uniform(-1.0, 1.0)), Scalar
        )
        self.PrimitiveSet.addEphemeralConstant(
            "RandWindow", lambda: WindowLength(random.randint(2, 50)), WindowLength
        )
        # Placeholder indicator series terminal for tree generation
        self.PrimitiveSet.addTerminal(
            IndicatorSeries(pd.Series([0.0])),
            IndicatorSeries,
        )

    def GetPrimitiveSet(self) -> gp.PrimitiveSetTyped:
        return self.PrimitiveSet
