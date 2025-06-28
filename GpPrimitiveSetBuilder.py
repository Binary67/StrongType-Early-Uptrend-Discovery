import functools
import hashlib
import logging
import pickle
import random
from pathlib import Path
from typing import Any, Dict, Tuple

from deap import gp
from IndicatorFactory import IndicatorFactory
from StrongTypeRegistry import StrongTypeRegistry

GLOBAL_INDICATOR_FACTORY: IndicatorFactory | None = None


def _add(a: float, b: float) -> float:
    return a + b


def _sub(a: float, b: float) -> float:
    return a - b


def _mul(a: float, b: float) -> float:
    return a * b


def _safe_div(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0


def _rand_scalar() -> float:
    return random.random()


def _indicator_wrapper(Name: str, *Args: Any) -> Any:
    if GLOBAL_INDICATOR_FACTORY is None:
        raise RuntimeError("Indicator factory not set")
    return GLOBAL_INDICATOR_FACTORY.ComputeIndicator(Name, Args)


class GpPrimitiveSetBuilder:
    """Construct a typed primitive set for DEAP-based GP."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._typeMap: Dict[str, type] = {}

    def BuildPrimitiveSet(
        self, IndicatorFactory: IndicatorFactory, StrongTypeRegistry: StrongTypeRegistry
    ) -> gp.PrimitiveSetTyped:
        """Assemble primitive set for GP run."""
        # Create Python classes for each registered domain type
        for Name in StrongTypeRegistry.ListRegisteredTypes():
            Info = StrongTypeRegistry.GetTypeSignature(Name)
            Base = Info["BaseType"]
            try:
                NewClass = type(Name, (Base,), {"__module__": __name__})
            except TypeError:
                NewClass = type(Name, (object,), {"__module__": __name__})
            globals()[Name] = NewClass
            self._typeMap[Name] = NewClass

        ReturnType = self._typeMap.get("Scalar", float)
        PSet = gp.PrimitiveSetTyped("MAIN", [], ReturnType)

        Scalar = self._typeMap.get("Scalar", float)

        PSet.addPrimitive(_add, [Scalar, Scalar], Scalar, name="Add")
        PSet.addPrimitive(_sub, [Scalar, Scalar], Scalar, name="Sub")
        PSet.addPrimitive(_mul, [Scalar, Scalar], Scalar, name="Mul")
        PSet.addPrimitive(_safe_div, [Scalar, Scalar], Scalar, name="Div")

        PSet.addEphemeralConstant(
            "ScalarConst",
            _rand_scalar,
            Scalar,
        )

        global GLOBAL_INDICATOR_FACTORY
        GLOBAL_INDICATOR_FACTORY = IndicatorFactory
        self.AddFunctionNodes(PSet, IndicatorFactory)
        return PSet

    def AddTerminalNodes(self, PrimitiveSet: gp.PrimitiveSetTyped, Terminals: Dict[str, Tuple[Any, str]]) -> None:
        """Insert data terminals such as current PriceSeries into primitive set."""
        for Name in sorted(Terminals.keys()):
            Value, TypeName = Terminals[Name]
            TypeClass = self._typeMap.get(TypeName)
            if TypeClass is None:
                self._logger.error("Unknown terminal type: %s", TypeName)
                continue
            PrimitiveSet.addTerminal(Value, TypeClass, name=Name)

    def AddFunctionNodes(self, PrimitiveSet: gp.PrimitiveSetTyped, Factory: IndicatorFactory) -> None:
        """Add indicator functions into primitive set."""
        for FuncName in Factory.ListAvailableIndicators():
            try:
                Inputs, Output = Factory.GetIndicatorSignature(FuncName)
                ArgTypes = [self._typeMap[Typ] for Typ in Inputs]
                ReturnType = self._typeMap[Output]
            except KeyError:
                self._logger.warning("Skipping indicator %s due to unresolved types", FuncName)
                continue
            Func = functools.partial(_indicator_wrapper, FuncName)
            PrimitiveSet.addPrimitive(Func, ArgTypes, ReturnType, name=FuncName)

    def ValidatePrimitiveSet(self, PrimitiveSet: gp.PrimitiveSetTyped) -> None:
        """Confirm that primitive set obeys arity and typing constraints."""
        try:
            Expr = gp.genHalfAndHalf(PrimitiveSet, min_=0, max_=1)
            Tree = gp.PrimitiveTree(Expr)
            gp.compile(Tree, PrimitiveSet)
        except Exception as Exc:  # pragma: no cover - any exception fails validation
            raise ValueError("Primitive set validation failed") from Exc

    def ExportPrimitiveSet(self, PrimitiveSet: gp.PrimitiveSetTyped, OutputDir: Path) -> Path:
        """Persist primitive set definition for later reproducibility."""
        OutputDir.mkdir(parents=True, exist_ok=True)
        PathOut = OutputDir / "PrimitiveSet.pkl"
        with open(PathOut, "wb") as Handle:
            pickle.dump(PrimitiveSet, Handle, protocol=5)
        Digest = hashlib.sha256(PathOut.read_bytes()).hexdigest()
        (OutputDir / "PrimitiveSet.sha256").write_text(Digest)
        return PathOut
