import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from Indicator import Indicator


def test_registration_and_sma() -> None:
    Series = pd.Series([1, 2, 3, 4, 5])
    Ind = Indicator()
    assert "SMA" in Ind.GetRegisteredIndicators()
    Result = Ind.SMA(Series, 3)
    Expected = Series.rolling(window=3).mean()
    pd.testing.assert_series_equal(Result, Expected)


def test_custom_registration() -> None:
    Series = pd.Series([1, 2, 3])
    Ind = Indicator()

    def Zero(PriceSeries: pd.Series) -> pd.Series:
        return PriceSeries * 0

    Ind.RegisterIndicator("ZERO", Zero)
    assert "ZERO" in Ind.GetRegisteredIndicators()
    ZeroFunc = Ind.GetIndicator("ZERO")
    Result = ZeroFunc(Series)
    Expected = pd.Series([0, 0, 0])
    pd.testing.assert_series_equal(Result, Expected)
