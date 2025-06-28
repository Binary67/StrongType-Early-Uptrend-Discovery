import logging
import inspect
import time
from typing import Any, Callable, Dict, List, Tuple

from StrongTypeRegistry import StrongTypeRegistry, TypeMismatchError


class UnknownIndicatorError(Exception):
    """Raised when referencing an unregistered indicator."""


class IndicatorFactory:
    """Provide strongly typed technical indicator functions."""

    PerformanceThreshold = 0.5  # seconds

    def __init__(self, Registry: StrongTypeRegistry) -> None:
        self._typeRegistry = Registry
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(__name__)

    def RegisterIndicatorFunction(
        self,
        FuncName: str,
        Implementation: Callable,
        InputTypes: Tuple[str, ...],
        OutputType: str,
    ) -> None:
        """Add a new indicator with its type signature."""
        if FuncName in self._registry:
            raise ValueError(f"Duplicate indicator: {FuncName}")

        for TypeName in InputTypes + (OutputType,):
            self._typeRegistry.GetTypeSignature(TypeName)

        if len(inspect.signature(Implementation).parameters) != len(InputTypes):
            raise ValueError("Implementation arity mismatch")

        Cache: Dict[Tuple[Any, ...], Any] = {}

        def _Wrapper(*Args: Any) -> Any:
            Key = tuple(
                tuple(Item) if isinstance(Item, list) else Item for Item in Args
            )
            if Key not in Cache:
                Cache[Key] = Implementation(*Args)
            return Cache[Key]

        Cached = _Wrapper
        self._registry[FuncName] = {
            "Impl": Cached,
            "Inputs": InputTypes,
            "Output": OutputType,
        }

    def GetIndicatorSignature(self, FuncName: str) -> Tuple[Tuple[str, ...], str]:
        """Return the type signature for the indicator."""
        Info = self._registry.get(FuncName)
        if Info is None:
            raise UnknownIndicatorError(FuncName)
        return Info["Inputs"], Info["Output"]

    def ComputeIndicator(self, FuncName: str, Args: Tuple[Any, ...]) -> Any:
        """Execute the indicator after enforcing types."""
        Info = self._registry.get(FuncName)
        if Info is None:
            raise UnknownIndicatorError(FuncName)

        if len(Args) != len(Info["Inputs"]):
            raise ValueError("Incorrect number of arguments")

        Validated: List[Any] = []
        for Arg, Expected in zip(Args, Info["Inputs"]):
            try:
                Validated.append(
                    self._typeRegistry.EnforceTypeOnArgument(Arg, Expected)
                )
            except (TypeMismatchError, KeyError) as Exc:
                self._logger.error("Type enforcement failed for %s: %s", FuncName, Exc)
                raise

        Start = time.perf_counter()
        Result = Info["Impl"](*Validated)
        Duration = time.perf_counter() - Start
        if Duration > self.PerformanceThreshold:
            self._logger.warning("%s execution took %.3f seconds", FuncName, Duration)

        self._typeRegistry.EnforceTypeOnArgument(Result, Info["Output"])
        return Result

    def ListAvailableIndicators(self) -> List[str]:
        """Return a list of registered indicator names."""
        return sorted(self._registry.keys())

