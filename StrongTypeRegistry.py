import logging
import re
from copy import deepcopy
from typing import Any, Callable, Dict, List, Set


class TypeMismatchError(Exception):
    """Raised when a value fails runtime type enforcement."""


class StrongTypeRegistry:
    """Registry for domain types and compatibility rules."""

    NamePattern = re.compile(r"[A-Z][A-Za-z0-9]+")

    def __init__(self) -> None:
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._compatibility: Dict[str, Set[str]] = {}
        self._logger = logging.getLogger(__name__)

    def RegisterType(
        self,
        TypeName: str,
        BasePythonType: type,
        ValidationFn: Callable[[Any], bool],
        Units: str = "",
        Description: str = "",
    ) -> None:
        """Add a new type with validation constraints."""
        if TypeName in self._registry:
            raise ValueError(f"Duplicate TypeName: {TypeName}")
        if not self.NamePattern.fullmatch(TypeName):
            raise ValueError(f"Invalid TypeName: {TypeName}")
        self._registry[TypeName] = {
            "BaseType": BasePythonType,
            "ValidationFn": ValidationFn,
            "Units": Units,
            "Description": Description,
        }
        self._compatibility.setdefault(TypeName, {TypeName})

    def ValidateTypeCompatibility(self, SourceType: str, TargetType: str) -> bool:
        """Return True if SourceType can be used where TargetType is expected."""
        if SourceType not in self._registry or TargetType not in self._registry:
            return False
        Allowed = self._compatibility.get(SourceType, set())
        if TargetType not in Allowed:
            return False
        if SourceType != TargetType:
            self._logger.warning(
                "Type downgrade from %s to %s", SourceType, TargetType
            )
        return True

    def GetTypeSignature(self, TypeName: str) -> Dict[str, Any]:
        """Return a deep copy of the registered metadata."""
        if TypeName not in self._registry:
            raise KeyError(TypeName)
        return deepcopy(self._registry[TypeName])

    def EnforceTypeOnArgument(self, Value: Any, ExpectedType: str) -> Any:
        """Ensure that Value conforms to the expected registered type."""
        if ExpectedType not in self._registry:
            raise KeyError(ExpectedType)
        Info = self._registry[ExpectedType]
        BaseType = Info["BaseType"]
        ValidationFn = Info["ValidationFn"]
        if not isinstance(Value, BaseType) or not ValidationFn(Value):
            raise TypeMismatchError(
                f"Expected {ExpectedType} but got {type(Value).__name__}"
            )
        return Value

    def ListRegisteredTypes(self) -> List[str]:
        """Return all registered type names sorted alphabetically."""
        return sorted(self._registry.keys())
