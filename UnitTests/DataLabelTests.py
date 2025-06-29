import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from DataLabel import DataLabel


def test_add_label() -> None:
    Prices = pd.DataFrame({"Close": [1, 2, 3, 4, 5]})
    Labeler = DataLabel()
    Result = Labeler.AddLabel(Prices.copy())
    Ema12 = Prices["Close"].ewm(span=12, adjust=False).mean()
    Ema50 = Prices["Close"].ewm(span=50, adjust=False).mean()
    Expected = (Ema12 > Ema50).astype(int)
    pd.testing.assert_series_equal(Result["Label"], Expected, check_names=False)
