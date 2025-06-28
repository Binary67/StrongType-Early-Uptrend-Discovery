import logging
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from IndicatorFactory import IndicatorFactory, UnknownIndicatorError
from StrongTypeRegistry import StrongTypeRegistry, TypeMismatchError


def _Sma(Series: list[float], Length: int) -> float:
    return sum(Series[-Length:]) / Length


def _Slow(Series: list[float], Length: int) -> float:
    time.sleep(0.01)
    return _Sma(Series, Length)


def _SetupRegistry() -> StrongTypeRegistry:
    Registry = StrongTypeRegistry()
    Registry.RegisterType("PriceSeries", list, lambda x: all(isinstance(v, (int, float)) for v in x))
    Registry.RegisterType("WindowLength", int, lambda x: isinstance(x, int) and x > 0)
    Registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    return Registry


def test_register_and_list():
    Registry = _SetupRegistry()
    Factory = IndicatorFactory(Registry)
    Factory.RegisterIndicatorFunction(
        "SMA", _Sma, ("PriceSeries", "WindowLength"), "Scalar"
    )
    assert Factory.ListAvailableIndicators() == ["SMA"]
    Inputs, Output = Factory.GetIndicatorSignature("SMA")
    assert Inputs == ("PriceSeries", "WindowLength")
    assert Output == "Scalar"


def test_compute_indicator_success():
    Registry = _SetupRegistry()
    Factory = IndicatorFactory(Registry)
    Factory.RegisterIndicatorFunction(
        "SMA", _Sma, ("PriceSeries", "WindowLength"), "Scalar"
    )
    Result = Factory.ComputeIndicator("SMA", ([1.0, 2.0, 3.0], 3))
    assert isinstance(Result, float)


def test_compute_indicator_type_mismatch():
    Registry = _SetupRegistry()
    Factory = IndicatorFactory(Registry)
    Factory.RegisterIndicatorFunction(
        "SMA", _Sma, ("PriceSeries", "WindowLength"), "Scalar"
    )
    try:
        Factory.ComputeIndicator("SMA", (123, 1))
    except TypeMismatchError:
        pass
    else:
        raise AssertionError("Expected TypeMismatchError")


def test_unknown_indicator():
    Registry = _SetupRegistry()
    Factory = IndicatorFactory(Registry)
    try:
        Factory.GetIndicatorSignature("MISSING")
    except UnknownIndicatorError:
        pass
    else:
        raise AssertionError("Expected UnknownIndicatorError")


def test_execution_warning(caplog):
    Registry = _SetupRegistry()
    Factory = IndicatorFactory(Registry)
    Factory.RegisterIndicatorFunction(
        "SLOW", _Slow, ("PriceSeries", "WindowLength"), "Scalar"
    )
    Factory.PerformanceThreshold = 0.0
    with caplog.at_level(logging.WARNING):
        Factory.ComputeIndicator("SLOW", ([1.0, 2.0, 3.0], 1))
    assert any("SLOW" in Record.message for Record in caplog.records)
