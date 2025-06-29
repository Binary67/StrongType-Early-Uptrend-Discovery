import logging
import pandas as pd
from Indicator import Indicator


class DataLabel:
    """Add labeling for uptrend discovery."""

    def __init__(self, IndicatorLib: Indicator | None = None) -> None:
        self.IndicatorLib = IndicatorLib if IndicatorLib else Indicator()
        self.Logger = logging.getLogger(self.__class__.__name__)

    def AddLabel(self, Data: pd.DataFrame) -> pd.DataFrame:
        """Create a label column where 1 denotes EMA12 greater than EMA50."""
        Ema12 = self.IndicatorLib.EMA(Data["Close"], 12)
        Ema50 = self.IndicatorLib.EMA(Data["Close"], 50)
        Data["Label"] = (Ema12 > Ema50).astype(int)
        Positive = int(Data["Label"].sum())
        Total = len(Data)
        self.Logger.info(
            "Label column created with %d positives out of %d entries", Positive, Total
        )
        return Data
