import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from GPPrimitives import GPPrimitives, IndicatorSeries, Scalar, WindowLength


def test_add_series_and_scalar() -> None:
    SeriesA = IndicatorSeries(pd.Series([1, 2, 3]))
    SeriesB = IndicatorSeries(pd.Series([3, 2, 1]))
    SValA = Scalar(1.0)
    SValB = Scalar(2.0)
    Prims = GPPrimitives()
    ResSeries = Prims.AddSeries(SeriesA, SeriesB)
    pd.testing.assert_series_equal(ResSeries.Values, pd.Series([4, 4, 4]))
    ResScalar = Prims.AddScalar(SValA, SValB)
    assert ResScalar.Value == 3.0


def test_primitive_set_contains_ema() -> None:
    Prims = GPPrimitives()
    HasEma = any(
        Prim.name == "EMA" for Prim in Prims.PrimitiveSet.primitives[IndicatorSeries]
    )
    assert HasEma


def test_rand_window_ephemeral_range() -> None:
    Prims = GPPrimitives()
    Terminal = Prims.PrimitiveSet.terminals[WindowLength][0]
    SampleLen = Terminal().value.Value
    assert 2 <= SampleLen <= 50

