import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DataLabel import DataLabel


def test_add_label_and_uptrend() -> None:
    Prices = pd.DataFrame({"Close": list(range(1, 21))})
    Labeler = DataLabel()
    Result = Labeler.AddLabel(Prices.copy())

    Ema12 = Prices["Close"].ewm(span=12, adjust=False).mean()
    Ema50 = Prices["Close"].ewm(span=50, adjust=False).mean()
    ExpectedUptrend = (Ema12 > Ema50).astype(int)
    pd.testing.assert_series_equal(Result["Uptrend"], ExpectedUptrend, check_names=False)

    FutureShifts = [ExpectedUptrend.shift(-i) for i in range(1, 11)]
    ExpectedLabel = pd.concat(FutureShifts, axis=1).max(axis=1).fillna(0).astype(int)
    pd.testing.assert_series_equal(Result["Label"], ExpectedLabel, check_names=False)
