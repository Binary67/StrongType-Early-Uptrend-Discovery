import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from StrongTypeRegistry import StrongTypeRegistry, TypeMismatchError


def test_register_type_and_list():
    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    Registry.RegisterType(
        "PriceSeries",
        list,
        lambda x: all(isinstance(v, (int, float)) for v in x),
        "USD",
        "List of prices",
    )
    Types = Registry.ListRegisteredTypes()
    assert Types == ["PriceSeries", "Scalar"]


def test_duplicate_or_invalid_name():
    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: True)
    try:
        Registry.RegisterType("Scalar", float, lambda x: True)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for duplicate type")
    try:
        Registry.RegisterType("invalid", float, lambda x: True)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid name")


def test_validate_type_compatibility_logs_warning(caplog):
    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: isinstance(x, float))
    Registry.RegisterType("PriceSeries", list, lambda x: True)
    Registry._compatibility["PriceSeries"] = {"Scalar"}
    with caplog.at_level(logging.WARNING):
        assert Registry.ValidateTypeCompatibility("PriceSeries", "Scalar")
    assert any("Type downgrade" in Record.message for Record in caplog.records)
    assert not Registry.ValidateTypeCompatibility("Scalar", "PriceSeries")


def test_get_type_signature_immutable():
    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: True, "USD")
    Info = Registry.GetTypeSignature("Scalar")
    Info["Units"] = "EUR"
    Original = Registry.GetTypeSignature("Scalar")
    assert Original["Units"] == "USD"


def test_enforce_type_on_argument():
    Registry = StrongTypeRegistry()
    Registry.RegisterType("Scalar", float, lambda x: x > 0)
    assert Registry.EnforceTypeOnArgument(1.0, "Scalar") == 1.0
    try:
        Registry.EnforceTypeOnArgument(-1.0, "Scalar")
    except TypeMismatchError:
        pass
    else:
        raise AssertionError("Expected TypeMismatchError")
