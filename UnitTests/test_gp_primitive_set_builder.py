import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from GpPrimitiveSetBuilder import GpPrimitiveSetBuilder
from IndicatorFactory import IndicatorFactory
from StrongTypeRegistry import StrongTypeRegistry


def _sma(series: list[float], length: int) -> float:
    return sum(series[-length:]) / length


def _setup() -> tuple[StrongTypeRegistry, IndicatorFactory]:
    registry = StrongTypeRegistry()
    registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    registry.RegisterType("PriceSeries", list, lambda x: True)
    registry.RegisterType("WindowLength", int, lambda x: x > 0)
    factory = IndicatorFactory(registry)
    factory.RegisterIndicatorFunction(
        "SMA", _sma, ("PriceSeries", "WindowLength"), "Scalar"
    )
    return registry, factory


def test_build_and_export(tmp_path: Path) -> None:
    registry, factory = _setup()
    builder = GpPrimitiveSetBuilder()
    pset = builder.BuildPrimitiveSet(factory, registry)
    builder.AddTerminalNodes(
        pset,
        {"B": ([1.0, 2.0], "PriceSeries"), "A": (1.0, "Scalar")},
    )
    builder.ValidatePrimitiveSet(pset)
    path = builder.ExportPrimitiveSet(pset, tmp_path)
    assert path.is_file()
    digest_path = tmp_path / "PrimitiveSet.sha256"
    assert digest_path.is_file()
    names = [t.name for t in pset.terminals[builder._typeMap["PriceSeries"]]]
    assert names == ["B"]
